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
 * OROLOGIO_V da tutte e due le parti.
 */

private const val OROLOGIO_V = 2
private const val INDIRIZZO = "https://manliograndi-del.github.io/palestra/"
private const val RECUPERO_SEC = 60L

private class Es(val nome: String, val serie: Int, val rip: Int, val minuti: Int = 0) {
    val cardio: Boolean get() = serie == 0
}

private val SCHEDA = listOf(
    Es("Tapis roulant", 0, 0, 15),
    Es("Abductor", 4, 20),
    Es("Adductor", 3, 12),
    Es("Leg press", 4, 10),
    Es("Chest press", 3, 12),
    Es("Low row", 4, 15),
    Es("Chest incline", 3, 10),
    Es("Upper back", 3, 10),
    Es("Vertical traction", 4, 12),
    Es("Leg extension", 3, 10),
    Es("Leg curl", 3, 12),
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
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
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
                fermaTimer()
                pagina = if (dx < 0) minOf(pagina + 1, ultima) else maxOf(pagina - 1, 0)
                avviso = null
                confermaAzzera = false
                mostra()
                return true
            }
        })
        radice.setOnTouchListener { _, ev -> gesti.onTouchEvent(ev) }

        carica()
        mostra()
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
    private fun avanza() {
        pagina = minOf(pagina + 1, ultima)
        avviso = null
        confermaAzzera = false
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
        restano = RECUPERO_SEC
        timer = object : CountDownTimer(RECUPERO_SEC * 1000, 250) {
            override fun onTick(rimasti: Long) {
                restano = (rimasti + 999) / 1000
                mostra()
            }
            override fun onFinish() {
                timer = null
                vibra()
                mostra()
            }
        }.start()
        mostra()
    }

    private fun fermaTimer() {
        timer?.cancel()
        timer = null
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
        tv.layoutParams = lp
        return tv
    }

    private fun etichettaKg(i: Int): String {
        val v = kg[i] ?: return "— kg"
        val t = if (v % 1f == 0f) v.toInt().toString() else String.format(Locale.ITALY, "%.1f", v)
        return "$t kg"
    }

    private fun cambiaKg(i: Int, delta: Float) {
        val nuovo = ((kg[i] ?: 0f) + delta).coerceIn(0f, 300f)
        if (nuovo <= 0f) kg.remove(i) else kg[i] = nuovo
        salva(); vibraBreve(); mostra()
    }

    private fun rigaKg(i: Int): View {
        val riga = LinearLayout(this)
        riga.orientation = LinearLayout.HORIZONTAL
        riga.gravity = Gravity.CENTER
        val lp = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        lp.topMargin = dp(8f)
        riga.layoutParams = lp
        val meno = tasto("−", false)
        meno.setOnClickListener { cambiaKg(i, -2.5f) }
        meno.setOnLongClickListener { cambiaKg(i, -10f); true }
        val valore = testo(etichettaKg(i), 17f, Color.WHITE, true)
        valore.layoutParams = LinearLayout.LayoutParams(dp(86f), ViewGroup.LayoutParams.WRAP_CONTENT)
        val piu = tasto("+", false)
        piu.setOnClickListener { cambiaKg(i, +2.5f) }
        piu.setOnLongClickListener { cambiaKg(i, +10f); true }
        riga.addView(meno); riga.addView(valore); riga.addView(piu)
        return riga
    }

    private fun pastiglie(i: Int): View {
        val e = SCHEDA[i]
        val riga = LinearLayout(this)
        riga.orientation = LinearLayout.HORIZONTAL
        riga.gravity = Gravity.CENTER
        val lp = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        lp.topMargin = dp(12f)
        riga.layoutParams = lp
        val n = fatteEs(i)
        for (j in 0 until e.serie) {
            val p = TextView(this)
            p.text = (j + 1).toString()
            p.gravity = Gravity.CENTER
            p.setTextSize(TypedValue.COMPLEX_UNIT_SP, 13f)
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
            val plp = LinearLayout.LayoutParams(dp(30f), dp(30f))
            plp.marginStart = dp(3f); plp.marginEnd = dp(3f)
            p.layoutParams = plp
            riga.addView(p)
        }
        return riga
    }

    private fun colonna(): LinearLayout {
        val c = LinearLayout(this)
        c.orientation = LinearLayout.VERTICAL
        c.gravity = Gravity.CENTER
        val bordo = dp(26f)
        c.setPadding(bordo, dp(14f), bordo, dp(14f))
        c.layoutParams = FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT)
        return c
    }

    private fun mostra() {
        radice.removeAllViews()
        val c = colonna()

        if (avviso == "vecchia") {
            c.addView(testo("SEDUTA DI PRIMA", 12f, ROSSO, true))
            c.addView(testo(data, 15f, Color.WHITE, false, 6))
            c.addView(testo("${totaliFatte()} serie mai mandate", 15f, TENUE, false, 6))
            c.addView(testo("tocca a destra per mandarla,\na sinistra per buttarla", 12f, TENUE, false, 14))
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
            val n = totaliFatte()
            c.addView(testo(if (mandata) "MANDATA" else "FINITA", 12f, ROSSO, true))
            c.addView(testo("$n/${totaliSerie()}", 40f, Color.WHITE, true, 2))
            c.addView(testo(
                if (cardio.isEmpty()) "nessun cardio"
                else "${cardio.size} " + (if (cardio.size == 1) "blocco di cardio" else "blocchi di cardio"),
                13f, TENUE, false, 4))
            val t = tasto(if (mandata) "Manda di nuovo" else "Manda al telefono", true)
            t.setOnClickListener { manda() }
            val lp = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
            lp.topMargin = dp(14f)
            lp.gravity = Gravity.CENTER
            t.layoutParams = lp
            c.addView(t)
            val az = tasto(if (confermaAzzera) "Sicuro? Tocca: azzera" else "Azzera la seduta", false)
            az.setOnClickListener {
                if (confermaAzzera) { confermaAzzera = false; nuovoGiorno(); vibraBreve(); mostra() }
                else { confermaAzzera = true; mostra() }
            }
            val alp = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
            alp.topMargin = dp(10f)
            alp.gravity = Gravity.CENTER_HORIZONTAL
            az.layoutParams = alp
            c.addView(az)
            if (avviso != null) c.addView(testo(when (avviso) {
                "invio" -> "sto mandando…"
                "mandata" -> "arrivata al telefono"
                "niente" -> "non c'è niente da mandare"
                else -> "non ci sono riuscito"
            }, 12f, if (avviso == "errore") ROSSO else TENUE, false, 10))
            radice.addView(c)
            return
        }

        val i = pagina
        val e = SCHEDA[i]
        c.addView(testo("${i + 1} / ${SCHEDA.size}", 11f, TENUE, true))
        c.addView(testo(e.nome.uppercase(Locale.ITALY), 22f, Color.WHITE, true, 6))
        if (e.cardio) {
            c.addView(testo("${e.minuti} minuti", 15f, ROSSO, true, 4))
            val fatto = cardio.contains(i)
            c.addView(testo(if (fatto) "FATTO" else "tocca quando l'hai fatto",
                14f, if (fatto) ROSSO else TENUE, fatto, 12))
            if (fatto) c.addView(testo("tieni premuto per togliere", 10f, TENUE, false, 6))
        } else {
            c.addView(testo("${e.serie} × ${e.rip}", 16f, ROSSO, true, 4))
            c.addView(rigaKg(i))
            /* Il trattino da solo non si spiega: la prima volta va detto
               chiaro che i chili li metti tu, e come. Poi restano. */
            if (kg[i] == null)
                c.addView(testo("metti i chili col + · tieni premuto: 10 alla volta", 10f, TENUE, false, 2))
            c.addView(pastiglie(i))
            val n = fatteEs(i)
            c.addView(testo(
                if (n >= e.serie) "finito — tocca per andare avanti" else "$n su ${e.serie}",
                12f, TENUE, false, 10))
            if (n > 0) c.addView(testo("tieni premuto per togliere", 10f, TENUE, false, 4))
        }
        radice.addView(c)
    }

    private fun tasto(t: String, pieno: Boolean): TextView {
        val b = TextView(this)
        b.text = t
        b.gravity = Gravity.CENTER
        b.setTextSize(TypedValue.COMPLEX_UNIT_SP, 13f)
        b.setTypeface(Typeface.DEFAULT_BOLD)
        b.setTextColor(Color.WHITE)
        b.setPadding(dp(16f), dp(10f), dp(16f), dp(10f))
        val sf = android.graphics.drawable.GradientDrawable()
        sf.cornerRadius = dp(24f).toFloat()
        if (pieno) sf.setColor(ROSSO) else { sf.setColor(Color.TRANSPARENT); sf.setStroke(dp(2f), LINEA) }
        b.background = sf
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
