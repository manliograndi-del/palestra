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
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
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
        if (u.scheme != "palestra" || u.host != "carichi") return
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
        tv.setAutoSizeTextTypeUniformWithConfiguration(11, 20, 1, TypedValue.COMPLEX_UNIT_SP)
        val lp = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        /* Il nome sta in alto, dove il tondo si stringe: gli serve più bordo
           delle pastiglie, che stanno in mezzo. */
        lp.marginStart = dp(12f); lp.marginEnd = dp(12f)
        tv.layoutParams = lp
        return tv
    }

    private fun etichettaKg(i: Int): String {
        val v = kg[i] ?: return "— kg"
        val t = if (v % 1f == 0f) v.toInt().toString() else String.format(Locale.ITALY, "%.1f", v)
        return "$t kg"
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
            p.text = (j + 1).toString()
            p.gravity = Gravity.CENTER
            p.setTextSize(TypedValue.COMPLEX_UNIT_SP, if (lato >= dp(38f)) 17f else 14f)
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

    /* Le frecce per spostarsi fra gli esercizi. Sull'orologio la sfogliata col
       dito verso destra e' presa dal sistema per uscire dall'app, quindi
       indietro non si poteva tornare: servono due tasti veri. In mezzo il
       numero della pagina, che prima stava in cima e rubava una riga. */
    private fun frecce(): View {
        val riga = LinearLayout(this)
        riga.orientation = LinearLayout.HORIZONTAL
        riga.gravity = Gravity.CENTER
        val lp = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        lp.topMargin = dp(6f)
        riga.layoutParams = lp

        val indietro = freccia("\u2039", pagina > 0)
        indietro.setOnClickListener { if (pagina > 0) vaiA(pagina - 1) }
        val conta = testo("${pagina + 1} / ${ultima + 1}", 12f, TENUE, true)
        conta.layoutParams = LinearLayout.LayoutParams(dp(58f), ViewGroup.LayoutParams.WRAP_CONTENT)
        val avanti = freccia("\u203a", pagina < ultima)
        avanti.setOnClickListener { if (pagina < ultima) vaiA(pagina + 1) }

        riga.addView(indietro); riga.addView(conta); riga.addView(avanti)
        return riga
    }

    private fun freccia(segno: String, attiva: Boolean): TextView {
        val b = TextView(this)
        b.text = segno
        b.gravity = Gravity.CENTER
        b.setTextSize(TypedValue.COMPLEX_UNIT_SP, 20f)
        b.setTypeface(Typeface.DEFAULT_BOLD)
        b.setTextColor(if (attiva) Color.WHITE else LINEA)
        val sf = android.graphics.drawable.GradientDrawable()
        sf.shape = android.graphics.drawable.GradientDrawable.OVAL
        sf.setColor(Color.TRANSPARENT)
        sf.setStroke(dp(2f), if (attiva) LINEA else Color.TRANSPARENT)
        b.background = sf
        b.layoutParams = LinearLayout.LayoutParams(dp(38f), dp(38f))
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

    private fun mostra() {
        radice.removeAllViews()
        val c = colonna()

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
            val n = totaliFatte()
            c.addView(testo(if (mandata) "MANDATA" else "FINITA", 11f, ROSSO, true))
            c.addView(testo("$n/${totaliSerie()}", 30f, Color.WHITE, true, 2))
            c.addView(testo(when (avviso) {
                "invio" -> "sto mandando…"
                "mandata" -> "arrivata al telefono"
                "niente" -> "non c'è niente da mandare"
                "errore" -> "non ci sono riuscito"
                else ->
                    if (cardio.isEmpty()) "nessun cardio"
                    else "${cardio.size} " + (if (cardio.size == 1) "blocco di cardio" else "blocchi di cardio")
            }, 11f, if (avviso == "errore") ROSSO else TENUE, false, 2))

            val t = tasto(if (mandata) "Manda di nuovo" else "Manda al telefono", true)
            t.setOnClickListener { manda() }
            val lp = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
            lp.topMargin = dp(10f)
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

            c.addView(frecce())
            radice.addView(c)
            return
        }

        /* La pagina di un esercizio, dall'alto: il nome, una riga sola con
           serie, ripetizioni e chili, le pastiglie grandi al centro, le frecce
           in fondo. Quattro righe e basta — ogni riga in più spingeva qualcosa
           oltre il bordo tondo. I chili qui si leggono soltanto: si cambiano
           dal telefono, con "Manda i carichi all'app". */
        val i = pagina
        val e = SCHEDA[i]
        c.addView(titolo(e.nome.uppercase(Locale.ITALY)))
        if (e.cardio) {
            c.addView(testo("${e.minuti} minuti", 15f, ROSSO, true, 6))
            val fatto = cardio.contains(i)
            c.addView(testo(if (fatto) "FATTO" else "tocca quando l'hai fatto",
                14f, if (fatto) ROSSO else TENUE, fatto, 14))
            c.addView(testo(if (fatto) "tieni premuto per togliere" else " ", 10f, TENUE, false, 6))
        } else {
            c.addView(testo("${e.serie} × ${e.rip}  ·  ${etichettaKg(i)}", 13f, TENUE, false, 6))
            c.addView(pastiglie(i))
            val n = fatteEs(i)
            c.addView(testo(
                when {
                    kg[i] == null -> "i chili arrivano dal telefono"
                    n >= e.serie -> "finito"
                    n > 0 -> "tieni premuto per togliere"
                    else -> "tocca per spuntare"
                }, 10f, TENUE, false, 6))
        }
        c.addView(frecce())
        radice.addView(c)
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
        salva()
    }
}
