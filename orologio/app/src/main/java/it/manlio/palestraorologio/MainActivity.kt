package it.manlio.palestraorologio

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.Typeface
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.CountDownTimer
import android.os.Handler
import android.os.Looper
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.text.Spannable
import android.text.SpannableString
import android.text.style.RelativeSizeSpan
import android.util.TypedValue
import android.view.GestureDetector
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.TextView
import androidx.wear.remote.interactions.RemoteActivityHelper
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.Executors

/*
 * Palestra da polso.
 *
 * Fa una cosa sola: mostra un esercizio alla volta, si tocca lo schermo per
 * spuntare una serie, si scorre di lato per cambiare esercizio. Alla fine manda
 * la seduta al telefono aprendogli un indirizzo — l'orologio racconta, il
 * telefono decide.
 *
 * Regole decise con Manlio il 2026-08-24:
 *  - tutto lo schermo è il pulsante: a mani sudate non si mira niente;
 *  - i chili qui non si scrivono. Li mette il telefono, prendendo quelli
 *    dell'ultima volta, quando registra la seduta;
 *  - il recupero parte da solo a ogni serie e vibra al polso;
 *  - si scorre avanti e indietro liberamente;
 *  - il cardio è una spunta sola;
 *  - la seduta resta qui finché non è stata mandata: se te ne dimentichi, te
 *    la ripropone.
 *
 * ATTENZIONE: gli indici degli esercizi devono restare **identici** a quelli
 * della SCHEDA dentro index.html della Palestra, perché il messaggio usa le
 * stesse chiavi "indice-serie". Se di là riordinano, qui va rifatto e va alzato
 * OROLOGIO_V da tutte e due le parti — **anche quando l'ordine dei campi nel
 * messaggio non cambia**: uno scambio fra due esercizi dello stesso tipo (dal
 * 2026-09-08, Leg press e Leg extension spostate in fondo ai pesi; dal
 * 2026-09-15, Adductor, Leg curl e Abductor in testa) lascia indici che
 * restano tutti validi ma puntano a un altro esercizio, e un telefono
 * aggiornato non avrebbe modo di accorgersene senza il controllo sulla
 * versione.
 *
 * I chili qui stanno in "kg_<indice>": un riordino li lascia attaccati alla
 * posizione, non all'esercizio. Dopo un aggiornamento come questo si rimandano
 * dal telefono con "Manda i carichi all'app", oppure si ritoccano con - e +.
 */

private const val OROLOGIO_V = 4
private const val INDIRIZZO = "https://manliograndi-del.github.io/palestra/"
private const val RECUPERO_SEC = 60L
/* il numero con cui ci si riconosce la risposta al permesso di Salute */
private const val CHIEDI_SALUTE = 7

private class Es(val nome: String, val serie: Int, val rip: Int, val minuti: Int = 0) {
    val cardio: Boolean get() = serie == 0
}

private val SCHEDA = listOf(
    Es("Tapis roulant", 0, 0, 15),
    Es("Adductor", 3, 12),
    Es("Leg curl", 3, 12),
    Es("Abductor", 4, 20),
    Es("Chest press", 3, 12),
    Es("Low row", 4, 15),
    Es("Chest incline", 3, 10),
    Es("Upper back", 3, 10),
    Es("Vertical traction", 4, 12),
    Es("Leg press", 4, 10),
    Es("Leg extension", 3, 10),
    Es("Cyclette", 0, 0, 15)
)

private val ROSSO = Color.parseColor("#E4002B")
private val TENUE = Color.parseColor("#9A9A9A")
private val LINEA = Color.parseColor("#3A3A3A")

class MainActivity : Activity() {

    private lateinit var pref: SharedPreferences
    private lateinit var radice: FrameLayout
    private lateinit var gesti: GestureDetector

    private val fatte = HashSet<String>()
    private val cardio = HashSet<Int>()
    /* I chili vivono anche qui, regolati con − e + (tenendo premuto ±10):
       senza, in palestra non sapresti quanto mettere sulla macchina, e l'app
       da polso sarebbe inutile. Viaggiano dentro il messaggio, così il
       telefono registra questi e non i suoi. Il reset non li tocca: sono la
       regolazione delle macchine, non la seduta. */
    private val kg = HashMap<Int, Float>()
    private var confermaAzzera = false
    private var data = ""
    private var mandata = false
    private var pagina = 0
    private var timer: CountDownTimer? = null
    private var restano = 0L
    private var avviso: String? = null

    /* **L'orologio in fondo alla schermata**, chiesto il 2026-10-06: mentre ti
       alleni l'app copre tutto il quadrante, e senza questo per sapere che ore
       sono dovevi uscire. Ha i secondi perché è anche il modo di cronometrare
       un recupero a occhio quando non usi il timer.

       Si aggiorna **solo quella scritta**, una volta al secondo, e **solo
       mentre l'app è davanti**: ridisegnare tutta la schermata ogni secondo
       sarebbe stato uno spreco, e farlo a schermo spento peggio. Parte in
       onResume e si ferma in onPause. */
    private var oraVista: TextView? = null
    private val battito = Handler(Looper.getMainLooper())
    private val ticOra = object : Runnable {
        override fun run() {
            oraVista?.text = oraDiAdesso()
            battito.postDelayed(this, 1000L)
        }
    }

    private fun oraDiAdesso(): String =
        SimpleDateFormat("HH:mm:ss", Locale.ITALY).format(Date())
    /* Gli allenamenti in attesa di finire in Connessione Salute, e quanti ce
       ne sono andati: vivono solo il tempo di questa schermata. */
    private var saluteD: String? = null
    private var saluteN = 0

    private val ultima: Int get() = SCHEDA.size   // l'ultima pagina è il riepilogo

    override fun onCreate(salvato: Bundle?) {
        super.onCreate(salvato)
        /* Lo schermo resta acceso **solo mentre scorre il recupero**, non per
           tutto il tempo che l'app e' aperta: tenerlo sempre acceso svuotava
           la batteria dell'orologio in una seduta. Durante il recupero serve
           davvero, perche' e' l'unico momento in cui guardi senza toccare. */
        pref = getSharedPreferences("palestra", Context.MODE_PRIVATE)
        radice = FrameLayout(this)
        radice.setBackgroundColor(Color.BLACK)
        setContentView(radice)

        gesti = GestureDetector(this, object : GestureDetector.SimpleOnGestureListener() {
            override fun onDown(e: MotionEvent): Boolean = true
            override fun onSingleTapUp(e: MotionEvent): Boolean { tocco(); return true }
            override fun onLongPress(e: MotionEvent) { annullaUltimo() }
            override fun onFling(e1: MotionEvent?, e2: MotionEvent, vx: Float, vy: Float): Boolean {
                if (e1 == null) return false
                val dx = e2.x - e1.x
                val dy = e2.y - e1.y
                if (Math.abs(dx) < 60f || Math.abs(dx) < Math.abs(dy)) return false
                vaiA(if (dx < 0) pagina + 1 else pagina - 1)
                return true
            }
        })
        radice.setOnTouchListener { _, ev -> gesti.onTouchEvent(ev) }

        carica()
        gestisciIntent(intent)
        mostra()
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        gestisciIntent(intent)
        mostra()
    }

    /* I carichi che arrivano dalla Palestra del telefono: palestra://carichi?d=1:40,3:60
       Stesso formato indice:kg del messaggio di ritorno. Sul telefono, oltre a
       tenerli, li inoltriamo all'orologio collegato — è l'unico canale
       telefono→polso, e va in quel senso una volta sola: i chili poi vivono di là. */
    private fun gestisciIntent(int: Intent?) {
        val u = int?.data ?: return
        if (u.scheme != "palestra") return
        when (u.host) {
            "carichi" -> carichiDalTelefono(u)
            "salute" -> saluteDalTelefono(u)
        }
    }

    private fun carichiDalTelefono(u: Uri) {
        val d = u.getQueryParameter("d") ?: return
        var n = 0
        d.split(",").forEach { coppia ->
            val a = coppia.split(":")
            if (a.size == 2) {
                val i = a[0].toIntOrNull()
                val v = a[1].toFloatOrNull()
                if (i != null && v != null && i in SCHEDA.indices && SCHEDA[i].serie > 0 && v > 0f && v <= 300f) {
                    kg[i] = v; n++
                }
            }
        }
        if (n == 0) return
        salva(); vibraBreve()
        pagina = 1          // si apre sul primo esercizio coi pesi, così i chili si vedono subito
        avviso = null
        if (!packageManager.hasSystemFeature(PackageManager.FEATURE_WATCH)) {
            try {
                RemoteActivityHelper(this).startRemoteActivity(
                    Intent(Intent.ACTION_VIEW).addCategory(Intent.CATEGORY_BROWSABLE).setData(u))
            } catch (e: Exception) { /* nessun orologio collegato: pazienza */ }
        }
    }

    /* Gli allenamenti che la Palestra web manda da palestra://salute, da
       portare in Connessione Salute. Succede **solo sul telefono**: sul polso
       Connessione Salute non esiste. Il grosso del lavoro sta in Salute.kt. */
    private fun saluteDalTelefono(u: Uri) {
        val d = u.getQueryParameter("d") ?: return
        saluteD = d
        saluteN = 0
        if (!Salute.disponibile()) { avviso = "salute-vecchio"; return }
        if (checkSelfPermission(PERMESSO_SALUTE) != PackageManager.PERMISSION_GRANTED) {
            avviso = "salute-chiedo"
            requestPermissions(arrayOf(PERMESSO_SALUTE), CHIEDI_SALUTE)
            return
        }
        saluteScrivi()
    }

    private fun saluteScrivi() {
        val d = saluteD ?: return
        avviso = "salute-invio"
        Salute.scrivi(this, d) { n, errore ->
            saluteN = n
            avviso = when (errore) {
                null -> "salute-fatto"
                "niente" -> "salute-niente"
                "manca" -> "salute-vecchio"
                else -> "salute-errore"
            }
            if (errore == null) saluteD = null
            mostra()
        }
    }

    /* **La via d'uscita se la finestra del permesso non compare.** Su
       Android 14 i permessi di salute li gestisce Connessione Salute, e non
       e' detto che la richiesta normale apra una finestra: puo' tornare
       negata senza chiedere niente. In quel caso la schermata offre di
       aprire Connessione Salute, dove il permesso si da' a mano; quando si
       torna qui, se adesso c'e', si riprende da dove si era fermato senza
       dover ritoccare niente. */
    override fun onResume() {
        super.onResume()
        battito.removeCallbacks(ticOra)
        battito.post(ticOra)
        if (avviso == "salute-negato" && saluteD != null && Salute.disponibile() &&
            checkSelfPermission(PERMESSO_SALUTE) == PackageManager.PERMISSION_GRANTED) {
            saluteScrivi()
            mostra()
        }
    }

    override fun onRequestPermissionsResult(
        codice: Int, permessi: Array<out String>, esiti: IntArray) {
        super.onRequestPermissionsResult(codice, permessi, esiti)
        if (codice != CHIEDI_SALUTE) return
        if (esiti.isNotEmpty() && esiti[0] == PackageManager.PERMISSION_GRANTED) saluteScrivi()
        else { avviso = "salute-negato"; mostra() }
    }

    /* ---------- memoria ---------- */

    private fun oggi(): String =
        SimpleDateFormat("yyyy-MM-dd", Locale.ITALY).format(Date())

    private fun carica() {
        data = pref.getString("data", "") ?: ""
        fatte.clear(); fatte.addAll(pref.getStringSet("fatte", emptySet()) ?: emptySet())
        cardio.clear()
        (pref.getStringSet("cardio", emptySet()) ?: emptySet()).forEach { cardio.add(it.toInt()) }
        mandata = pref.getBoolean("mandata", false)
        pagina = pref.getInt("pagina", 0).coerceIn(0, ultima)
        kg.clear()
        for (i in SCHEDA.indices) {
            val v = pref.getFloat("kg_$i", 0f)
            if (v > 0f) kg[i] = v
        }

        if (data.isEmpty()) { data = oggi(); return }
        if (data == oggi()) return

        /* È un altro giorno. Se quella di prima non è mai stata mandata la
           teniamo e la proponiamo, altrimenti si riparte puliti. */
        if (fatte.isEmpty() && cardio.isEmpty()) { nuovoGiorno(); return }
        if (mandata) nuovoGiorno()
        else avviso = "vecchia"
    }

    private fun nuovoGiorno() {
        fatte.clear(); cardio.clear(); mandata = false; data = oggi(); pagina = 0
        salva()
    }

    private fun salva() {
        val ed = pref.edit()
            .putString("data", data)
            .putStringSet("fatte", HashSet(fatte))
            .putStringSet("cardio", HashSet(cardio.map { it.toString() }))
            .putBoolean("mandata", mandata)
            /* Dove sei arrivato: se il sistema chiude l'app quando lo schermo
               si spegne, riaprendola torni sull'esercizio che stavi facendo e
               non in testa alla scheda. */
            .putInt("pagina", pagina)
        for (i in SCHEDA.indices) ed.putFloat("kg_$i", kg[i] ?: 0f)
        ed.apply()
    }

    private fun fatteEs(i: Int): Int {
        val e = SCHEDA[i]
        var n = 0
        for (j in 0 until e.serie) if (fatte.contains("$i-$j")) n++
        return n
    }

    private fun totaliFatte(): Int {
        var n = 0
        for (i in SCHEDA.indices) n += fatteEs(i)
        return n
    }

    private fun totaliSerie(): Int {
        var n = 0
        for (e in SCHEDA) n += e.serie
        return n
    }

    /* ---------- il tocco ---------- */

    /* Il tocco **va sempre avanti**: spunta, e quando non c'è più niente da
       spuntare passa all'esercizio dopo. La prima versione accendeva e spegneva
       "fatto" a ogni tocco, e Manlio ha visto l'app rimbalzare fra due
       schermate: un tocco che a volte disfa quello che hai appena fatto non è
       un tocco, è una trappola. Per correggere si **tiene premuto**. */
    private fun avanza() { vaiA(pagina + 1) }

    /* L'unico posto da cui si cambia pagina: frecce, sfogliata e avanzamento
       automatico passano tutti di qui, cosi' non c'e' modo di spostarsi
       dimenticandosi di fermare il recupero o di salvare dove sei. */
    private fun vaiA(nuova: Int) {
        /* Dalla schermata della seduta rimasta indietro non si sfoglia via:
           lì c'è un allenamento intero che aspetta di essere mandato o
           buttato, e deve deciderlo lui con i due tasti. */
        if (avviso == "vecchia") return
        fermaTimer()
        pagina = nuova.coerceIn(0, ultima)
        avviso = null
        confermaAzzera = false
        salva()
        mostra()
    }

    private fun tocco() {
        if (avviso == "vecchia") return          // lì decidono i due tasti
        if (avviso?.startsWith("salute") == true) return   // lì c'è un tasto solo
        if (timer != null) { fermaTimer(); mostra(); return }

        if (pagina == ultima) return   // qui decidono i tasti, un tocco a vuoto non manda niente

        val i = pagina
        val e = SCHEDA[i]
        if (e.cardio) {
            if (!cardio.contains(i)) { cardio.add(i); mandata = false; salva(); vibraBreve() }
            avanza()
            return
        }
        val n = fatteEs(i)
        if (n >= e.serie) { avanza(); return }    // esercizio finito: si va avanti
        fatte.add("$i-$n")
        mandata = false
        salva()
        avviaTimer()
    }

    /* Tenere premuto toglie l'ultima cosa segnata su questa schermata. */
    private fun annullaUltimo() {
        if (pagina == ultima) return
        val i = pagina
        val e = SCHEDA[i]
        var tolto = false
        if (e.cardio) { tolto = cardio.remove(i) }
        else {
            val n = fatteEs(i)
            if (n > 0) { fatte.remove("$i-${n - 1}"); tolto = true }
        }
        if (tolto) { salva(); vibraBreve() }
        fermaTimer()
        mostra()
    }

    /* ---------- recupero ---------- */

    private fun avviaTimer() {
        fermaTimer()
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        restano = RECUPERO_SEC
        timer = object : CountDownTimer(RECUPERO_SEC * 1000, 250) {
            override fun onTick(rimasti: Long) {
                restano = (rimasti + 999) / 1000
                mostra()
            }
            override fun onFinish() {
                timer = null
                window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
                vibra()
                mostra()
            }
        }.start()
        mostra()
    }

    private fun fermaTimer() {
        timer?.cancel()
        timer = null
        window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
    }

    private fun vibraBreve() { vibraCon(longArrayOf(0, 35)) }

    private fun vibra() { vibraCon(longArrayOf(0, 220, 140, 220, 140, 380)) }

    private fun vibraCon(tempi: LongArray) {
        try {
            val v: Vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                val vm = getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
                vm.defaultVibrator
            } else {
                @Suppress("DEPRECATION")
                getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
            }
            v.vibrate(VibrationEffect.createWaveform(tempi, -1))
        } catch (e: Exception) { /* senza vibrazione si vive */ }
    }

    /* ---------- il messaggio al telefono ---------- */

    private fun indirizzoSeduta(): String {
        val s = fatte.joinToString(",")
        val c = cardio.sorted().joinToString(",")
        val p = kg.entries.sortedBy { it.key }.joinToString(",") {
            "${it.key}:" + (if (it.value % 1f == 0f) it.value.toInt().toString()
                            else String.format(Locale.US, "%.1f", it.value))
        }
        return INDIRIZZO + "#orologio=" + OROLOGIO_V + ";" + data + ";" + s + ";" + c + ";" + p
    }

    private fun manda() {
        confermaAzzera = false
        if (fatte.isEmpty() && cardio.isEmpty()) { avviso = "niente"; mostra(); return }
        val intento = Intent(Intent.ACTION_VIEW)
            .addCategory(Intent.CATEGORY_BROWSABLE)
            .setData(Uri.parse(indirizzoSeduta()))
        val alPolso = packageManager.hasSystemFeature(PackageManager.FEATURE_WATCH)
        try {
            if (alPolso) {
                val futuro = RemoteActivityHelper(this).startRemoteActivity(intento)
                futuro.addListener({
                    runOnUiThread { mandata = true; salva(); avviso = "mandata"; mostra() }
                }, Executors.newSingleThreadExecutor())
                avviso = "invio"
            } else {
                /* Sul telefono non c'è nessun polso a cui mandarla: la pagina si
                   apre qui. È il modo in cui si prova tutta la catena senza
                   orologio e senza cavi. */
                intento.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                startActivity(intento)
                mandata = true; salva()
                avviso = "mandata"
            }
        } catch (e: Exception) {
            avviso = "errore"
        }
        mostra()
    }

    /* ---------- disegno ----------
       Si ridisegna tutto da capo a ogni tocco, come fa la Palestra sul telefono:
       è la scelta che le impedisce di restare a metà. */

    private fun dp(v: Float): Int =
        TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, resources.displayMetrics).toInt()

    private fun testo(t: String, sp: Float, colore: Int, grassetto: Boolean, sopra: Int = 0): TextView {
        val tv = TextView(this)
        tv.text = t
        tv.setTextSize(TypedValue.COMPLEX_UNIT_SP, sp)
        tv.setTextColor(colore)
        tv.gravity = Gravity.CENTER
        if (grassetto) tv.setTypeface(Typeface.DEFAULT_BOLD)
        val lp = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        lp.topMargin = dp(sopra.toFloat())
        lp.marginStart = dp(10f); lp.marginEnd = dp(10f)
        tv.layoutParams = lp
        return tv
    }

    /* Il nome dell'esercizio su una riga sola, che si rimpicciolisce da sola
       fino a entrare: "Vertical traction" e' lungo il doppio di "Low row" e su
       uno schermo tondo la differenza si vede tutta. */
    private fun titolo(t: String): TextView {
        val tv = TextView(this)
        tv.text = t
        tv.gravity = Gravity.CENTER
        tv.maxLines = 1
        tv.setTextColor(Color.WHITE)
        tv.setTypeface(Typeface.DEFAULT_BOLD)
        tv.setAutoSizeTextTypeUniformWithConfiguration(11, 18, 1, TypedValue.COMPLEX_UNIT_SP)
        val lp = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        /* Il nome sta in alto, dove il tondo si stringe: gli serve più bordo
           delle pastiglie, che stanno in mezzo. */
        lp.marginStart = dp(12f); lp.marginEnd = dp(12f)
        tv.layoutParams = lp
        return tv
    }

    /* I chili: il numero è quello che leggi da un metro, **"kg" è solo
       l'unità** e non deve rubargli spazio — chiesto il 2026-10-06, scritto
       meno della metà. Una riga sola con due dimensioni dentro, non due righe. */
    private fun kgGrandi(i: Int): TextView {
        val v = kg[i]
        val numero = when {
            v == null -> "\u2014"
            v % 1f == 0f -> v.toInt().toString()
            else -> String.format(Locale.ITALY, "%.1f", v)
        }
        val tutto = "$numero kg"
        val sp = SpannableString(tutto)
        sp.setSpan(RelativeSizeSpan(0.40f), numero.length, tutto.length,
            Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
        val t = TextView(this)
        t.text = sp
        t.gravity = Gravity.CENTER
        t.maxLines = 1
        t.setTextSize(TypedValue.COMPLEX_UNIT_SP, 24f)
        t.setTextColor(Color.WHITE)
        t.setTypeface(Typeface.DEFAULT_BOLD)
        val lp = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        lp.topMargin = dp(4f)
        t.layoutParams = lp
        return t
    }

    /* L'ora corrente, in fondo. Il riferimento resta in `oraVista` perché è
       l'unica cosa che si aggiorna da sola, senza ridisegnare il resto. */
    private fun orologioDaPolso(): TextView {
        val t = testo(oraDiAdesso(), 15f, ROSSO, true, 8)
        oraVista = t
        return t
    }

    private fun pastiglie(i: Int): View {
        val e = SCHEDA[i]
        val riga = LinearLayout(this)
        riga.orientation = LinearLayout.HORIZONTAL
        riga.gravity = Gravity.CENTER
        val lp = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        lp.topMargin = dp(8f)
        riga.layoutParams = lp
        val n = fatteEs(i)
        /* Le pastiglie sono la cosa che si tocca, quindi prendono tutto lo
           spazio che c'e': la misura si calcola sulla larghezza vera dello
           schermo invece di essere scritta a mano, cosi' non possono uscire
           fuori ne' su un quadrante piccolo ne' con un esercizio da 4 serie.
           Stanno al centro, dove il tondo e' piu' largo. */
        val lato = (larghezzaUtile() / e.serie - dp(6f)).coerceIn(dp(24f), dp(46f))
        for (j in 0 until e.serie) {
            val p = TextView(this)
            /* Dentro il cerchietto ci vanno **le ripetizioni**, non il numero
               della serie: chiesto il 2026-10-06. Quante serie hai fatto si
               vede dal colore — pieno rosso è fatta — e quante ne restano dal
               numero di cerchietti. Il numero d'ordine non diceva niente che
               non fosse già sotto gli occhi, e costava la riga "3 × 12". */
            p.text = e.rip.toString()
            p.gravity = Gravity.CENTER
            p.setTextSize(TypedValue.COMPLEX_UNIT_SP, if (lato >= dp(38f)) 15f else 12f)
            p.setTypeface(Typeface.DEFAULT_BOLD)
            val fatto = j < n
            p.setTextColor(if (fatto) Color.WHITE else TENUE)
            val sfondo = android.graphics.drawable.GradientDrawable()
            sfondo.shape = android.graphics.drawable.GradientDrawable.OVAL
            if (fatto) sfondo.setColor(ROSSO) else {
                sfondo.setColor(Color.TRANSPARENT)
                sfondo.setStroke(dp(2f), if (j == n) Color.WHITE else LINEA)
            }
            p.background = sfondo
            val plp = LinearLayout.LayoutParams(lato, lato)
            plp.marginStart = dp(3f); plp.marginEnd = dp(3f)
            p.layoutParams = plp
            riga.addView(p)
        }
        return riga
    }

    /* Quanto spazio c'e' davvero in orizzontale a meta' schermo. Il bordo di
       14dp e' la sicurezza sul tondo: li' in mezzo il cerchio e' al massimo
       della sua larghezza, quindi e' abbondante. */
    private fun larghezzaUtile(): Int = resources.displayMetrics.widthPixels - dp(14f) * 2

    /* **La barra delle frecce**, disegnata da Manlio il 2026-10-06: una riga
       orizzontale taglia il tondo vicino al fondo, e il mezzaluna che resta
       sotto è diviso in due da una riga verticale — a sinistra indietro, a
       destra avanti. Come i tasti di un cronometro.

       È l'unico modo di avere bersagli grandi su uno schermo tondo: lì sotto
       non ci sta niente altro, e due mezzi segmenti si prendono tutta la
       larghezza invece di due cerchietti da 38dp in mezzo allo spazio.

       L'altezza è il 22% dello schermo, non un numero fisso: a quella
       profondità il cerchio è ancora largo l'83%, e i due simboli — che
       stanno a un quarto e a tre quarti della larghezza — cadono dentro il
       tondo con margine su tutti e due i formati del Pixel Watch 3.

       **Le due metà prendono il tocco anche quando sono spente**, altrimenti
       passerebbe sotto e spunterebbe una serie: toccare una freccia morta non
       deve mai fare qualcos'altro. */
    private fun altezzaBarra(): Int =
        (resources.displayMetrics.heightPixels * 0.22f).toInt().coerceIn(dp(40f), dp(58f))

    private fun barraFrecce(): View {
        val fuori = LinearLayout(this)
        fuori.orientation = LinearLayout.VERTICAL
        val flp = FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, altezzaBarra())
        flp.gravity = Gravity.BOTTOM
        fuori.layoutParams = flp

        val taglio = View(this)
        taglio.setBackgroundColor(LINEA)
        taglio.layoutParams = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, dp(1f))
        fuori.addView(taglio)

        val riga = LinearLayout(this)
        riga.orientation = LinearLayout.HORIZONTAL
        riga.layoutParams = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f)

        val indietro = mezzaFreccia("\u25c1", pagina > 0)
        indietro.setOnClickListener { if (pagina > 0) vaiA(pagina - 1) }

        val divisorio = View(this)
        divisorio.setBackgroundColor(LINEA)
        divisorio.layoutParams = LinearLayout.LayoutParams(
            dp(1f), ViewGroup.LayoutParams.MATCH_PARENT)

        val avanti = mezzaFreccia("\u25b7", pagina < ultima)
        avanti.setOnClickListener { if (pagina < ultima) vaiA(pagina + 1) }

        riga.addView(indietro); riga.addView(divisorio); riga.addView(avanti)
        fuori.addView(riga)
        return fuori
    }

    private fun mezzaFreccia(segno: String, attiva: Boolean): TextView {
        val b = TextView(this)
        b.text = segno
        b.gravity = Gravity.CENTER
        b.setTextSize(TypedValue.COMPLEX_UNIT_SP, 22f)
        b.setTextColor(if (attiva) Color.WHITE else LINEA)
        b.isClickable = true
        b.layoutParams = LinearLayout.LayoutParams(
            0, ViewGroup.LayoutParams.MATCH_PARENT, 1f)
        return b
    }

    private fun colonna(): LinearLayout {
        val c = LinearLayout(this)
        c.orientation = LinearLayout.VERTICAL
        c.gravity = Gravity.CENTER
        /* Il bordo largo serviva a tenere le scritte dentro il tondo, ma
           stringeva anche le pastiglie, che invece stanno a metà schermo dove
           spazio ce n'è: ora il bordo è stretto e sono le singole scritte a
           tenersi il loro margine. */
        val bordo = dp(14f)
        c.setPadding(bordo, dp(10f), bordo, dp(10f))
        c.layoutParams = FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT)
        return c
    }

    /* Dove c'è la barra delle frecce il contenuto si tiene alla larga, o le
       finirebbe sopra: il centro della colonna si alza di conseguenza. */
    private fun spazioBarra(c: LinearLayout) {
        c.setPadding(c.paddingLeft, c.paddingTop, c.paddingRight, altezzaBarra() + dp(6f))
    }

    private fun mostra() {
        radice.removeAllViews()
        /* Le viste di prima sono appena state buttate: il riferimento
           all'orologio non vale più finché non lo rimette la pagina che ce
           l'ha. Senza questo, il battito scriverebbe su una vista morta. */
        oraVista = null
        val c = colonna()

        /* La schermata di Google Health. Si vede **sul telefono**, non al
           polso: è il telefono che apre palestra://salute. */
        if (avviso?.startsWith("salute") == true) {
            c.addView(testo("GOOGLE HEALTH", 11f, ROSSO, true))
            val male = avviso == "salute-errore" || avviso == "salute-vecchio" ||
                       avviso == "salute-negato"
            c.addView(testo(when (avviso) {
                "salute-invio", "salute-chiedo" -> "\u2026"
                "salute-fatto" -> saluteN.toString()
                else -> "\u2014"
            }, 30f, if (male) ROSSO else Color.WHITE, true, 2))
            c.addView(testo(when (avviso) {
                "salute-chiedo" -> "sto chiedendo il permesso"
                "salute-invio" -> "sto scrivendo\u2026"
                "salute-fatto" ->
                    if (saluteN == 1) "attivit\u00e0 scritta in Connessione Salute"
                    else "attivit\u00e0 scritte in Connessione Salute"
                "salute-niente" -> "non c'era niente da scrivere"
                "salute-negato" -> "serve il permesso: daglielo e torna qui"
                "salute-vecchio" -> "questo telefono non ha Connessione Salute"
                else -> "non ci sono riuscito"
            }, 11f, TENUE, false, 2))

            if (avviso == "salute-negato") {
                val perm = tasto("Apri Connessione Salute", true)
                perm.setOnClickListener {
                    try {
                        startActivity(Intent("android.health.connect.action.MANAGE_HEALTH_PERMISSIONS")
                            .putExtra(Intent.EXTRA_PACKAGE_NAME, packageName)
                            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
                    } catch (e: Exception) { avviso = "salute-errore"; mostra() }
                }
                val plp = LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
                plp.topMargin = dp(12f)
                plp.gravity = Gravity.CENTER_HORIZONTAL
                perm.layoutParams = plp
                c.addView(perm)
            }

            val t = tasto(if (avviso == "salute-negato") "Lascia stare" else "Torna alla Palestra",
                          avviso != "salute-negato")
            t.setOnClickListener {
                avviso = null
                try {
                    startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(INDIRIZZO))
                        .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
                } catch (e: Exception) { /* nessun browser: resta qui */ }
                mostra()
            }
            val tlp = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
            tlp.topMargin = dp(12f)
            tlp.gravity = Gravity.CENTER_HORIZONTAL
            t.layoutParams = tlp
            c.addView(t)
            radice.addView(c)
            return
        }

        if (avviso == "vecchia") {
            c.addView(testo("SEDUTA DI PRIMA", 11f, ROSSO, true))
            c.addView(testo(data, 15f, Color.WHITE, true, 4))
            c.addView(testo("${totaliFatte()} serie mai mandate", 12f, TENUE, false, 4))
            val r = LinearLayout(this)
            r.orientation = LinearLayout.HORIZONTAL
            r.gravity = Gravity.CENTER
            val lp = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
            lp.topMargin = dp(14f)
            r.layoutParams = lp
            val butta = tasto("Butta", false)
            butta.setOnClickListener { avviso = null; nuovoGiorno(); mostra() }
            val manda = tasto("Manda", true)
            manda.setOnClickListener { avviso = null; manda() }
            r.addView(butta); r.addView(manda)
            c.addView(r)
            radice.addView(c)
            return
        }

        if (timer != null) {
            c.addView(testo("RECUPERO", 12f, ROSSO, true))
            c.addView(testo(String.format(Locale.ITALY, "0:%02d", restano), 46f, Color.WHITE, true, 4))
            c.addView(testo("tocca per saltare", 12f, TENUE, false, 8))
            radice.addView(c)
            return
        }

        if (pagina == ultima) {
            /* L'ultima schermata deve far vedere **tutti e due** i tasti: prima
               "Azzera" finiva oltre il bordo tondo e non si capiva nemmeno se
               ci fosse. Quindi numeri più piccoli, una riga di riepilogo sola,
               e la riga dell'esito al posto di quella del cardio invece che in
               aggiunta. La freccia per tornare indietro resta in fondo. */
            spazioBarra(c)
            val n = totaliFatte()
            c.addView(testo("$n/${totaliSerie()}", 26f, Color.WHITE, true))
            /* Una riga sola per lo stato, perché con la barra delle frecce in
               fondo lo spazio è quello che è: l'esito di un invio prende il
               posto del riepilogo invece di aggiungersi, e "già mandata" dice
               quello che prima diceva l'etichetta in cima. */
            c.addView(testo(when (avviso) {
                "invio" -> "sto mandando…"
                "mandata" -> "arrivata al telefono"
                "niente" -> "non c'è niente da mandare"
                "errore" -> "non ci sono riuscito"
                else ->
                    if (mandata) "già mandata al telefono"
                    else if (cardio.isEmpty()) "nessun cardio"
                    else "${cardio.size} " + (if (cardio.size == 1) "blocco di cardio" else "blocchi di cardio")
            }, 11f, if (avviso == "errore") ROSSO else TENUE, false, 3))

            val t = tasto(if (mandata) "Manda di nuovo" else "Manda al telefono", true)
            t.setOnClickListener { manda() }
            val lp = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
            lp.topMargin = dp(8f)
            lp.gravity = Gravity.CENTER_HORIZONTAL
            t.layoutParams = lp
            c.addView(t)

            val az = tasto(if (confermaAzzera) "Sicuro? Tocca" else "Azzera la seduta", false)
            az.setOnClickListener {
                if (confermaAzzera) { confermaAzzera = false; nuovoGiorno(); vibraBreve(); mostra() }
                else { confermaAzzera = true; mostra() }
            }
            val alp = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
            alp.topMargin = dp(6f)
            alp.gravity = Gravity.CENTER_HORIZONTAL
            az.layoutParams = alp
            c.addView(az)

            radice.addView(c)
            radice.addView(barraFrecce())
            return
        }

        /* **La pagina di un esercizio, rifatta il 2026-10-06 su un disegno suo.**
           Tre cose sole: il nome, i chili grossi al centro, i cerchietti delle
           serie col numero di ripetizioni dentro. In fondo la barra delle
           frecce.

           Sono sparite tutte le scritte piccole di istruzioni — "tieni premuto
           per togliere", "tocca per spuntare", "i chili arrivano dal telefono":
           erano spiegazioni per la prima volta, e lui l'app la usa da un mese.
           Occupavano la riga che serviva ai chili per essere leggibili in piedi
           con le mani sudate. **Non rimetterle.**

           È sparita anche la riga "3 × 12": le ripetizioni adesso stanno dentro
           i cerchietti, e quante serie siano lo dice il numero di cerchietti.

           I chili qui si leggono soltanto: si cambiano dal telefono, con
           "Manda i carichi all'app". */
        spazioBarra(c)
        val i = pagina
        val e = SCHEDA[i]
        c.addView(titolo(e.nome.uppercase(Locale.ITALY)))
        if (e.cardio) {
            c.addView(testo("${e.minuti} minuti", 24f, Color.WHITE, true, 6))
            if (cardio.contains(i)) c.addView(testo("FATTO", 13f, ROSSO, true, 8))
        } else {
            c.addView(kgGrandi(i))
            c.addView(pastiglie(i))
        }
        c.addView(orologioDaPolso())
        radice.addView(c)
        radice.addView(barraFrecce())
    }

    private fun tasto(t: String, pieno: Boolean): TextView {
        val b = TextView(this)
        b.text = t
        b.gravity = Gravity.CENTER
        b.setTextSize(TypedValue.COMPLEX_UNIT_SP, 13f)
        b.setTypeface(Typeface.DEFAULT_BOLD)
        b.setTextColor(Color.WHITE)
        b.maxLines = 1
        b.setPadding(dp(14f), dp(9f), dp(14f), dp(9f))
        val sf = android.graphics.drawable.GradientDrawable()
        sf.cornerRadius = dp(24f).toFloat()
        if (pieno) sf.setColor(ROSSO) else { sf.setColor(Color.TRANSPARENT); sf.setStroke(dp(2f), LINEA) }
        b.background = sf
        b.maxWidth = larghezzaUtile()
        val lp = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        lp.marginStart = dp(4f); lp.marginEnd = dp(4f)
        b.layoutParams = lp
        return b
    }

    override fun onPause() {
        super.onPause()
        battito.removeCallbacks(ticOra)
        salva()
    }
}
