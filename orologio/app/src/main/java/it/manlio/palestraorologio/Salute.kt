package it.manlio.palestraorologio

import android.app.Activity
import android.graphics.Color
import android.health.connect.HealthConnectException
import android.health.connect.HealthConnectManager
import android.health.connect.InsertRecordsResponse
import android.health.connect.datatypes.ExerciseSessionRecord
import android.health.connect.datatypes.ExerciseSessionType
import android.health.connect.datatypes.Metadata
import android.health.connect.datatypes.Record
import android.os.Build
import android.os.Bundle
import android.os.OutcomeReceiver
import android.util.TypedValue
import android.widget.ScrollView
import android.widget.TextView
import java.time.Instant
import java.util.concurrent.Executors

/*
 * Gli allenamenti della Palestra dentro Google Health.
 *
 * Google Health — l'app che era Fitbit, quella che legge il Pixel Watch — non
 * sa niente delle chiavi della Palestra: legge **Connessione Salute**, il
 * magazzino di salute dentro Android. Questo file e' l'unico pezzo che puo'
 * scriverci, e il perche' sta tutto qui:
 *  - dalla pagina web non c'e' modo di parlare con Connessione Salute;
 *  - **su Wear OS Connessione Salute non esiste**, quindi nemmeno dal polso.
 * Resta questo APK, girando **sul telefono**. La Palestra web gli apre
 * palestra://salute con tutte le sedute dentro e lui le travasa.
 *
 * Da Android 14 Connessione Salute e' parte del sistema e si chiama
 * direttamente, senza librerie: e' il motivo per cui l'app continua ad avere
 * una dipendenza sola. Su Android 13 e precedenti era un'app a parte e
 * servirebbe la libreria di Google: in quel caso qui non si fa niente e il
 * telefono lo dice.
 *
 * Il segnaposto (clientRecordId) e' "palestra-<data>-<tipo>": **dipende dalla
 * data e non dall'orario**, cosi' rimandare gli stessi allenamenti aggiorna i
 * record di prima invece di sdoppiarli. Il pulsante si puo' premere quante
 * volte si vuole.
 */

/* Scritto a mano invece di leggerlo da HealthPermissions.WRITE_EXERCISE:
   quella costante esiste solo da Android 14, e questa stringa serve anche
   dove quella classe non c'e'. */
const val PERMESSO_SALUTE = "android.permission.health.WRITE_EXERCISE"

/* Un'attivita' da scrivere: tipo c = camminata, p = pesi, b = cyclette. */
private class Att(
    val tipo: String,
    val data: String,
    val inizio: Long,
    val minuti: Int,
    val serie: Int,
    val volume: Int
)

private val DATA_OK = Regex("^\\d{4}-\\d{2}-\\d{2}$")

object Salute {

    /* Il controllo sta qui e non dentro le funzioni che toccano Connessione
       Salute: quelle citano classi che su Android 13 non esistono, e vanno
       chiamate solo dopo che questa ha detto di si'. */
    fun disponibile(): Boolean = Build.VERSION.SDK_INT >= 34

    /* Scrive tutto e richiama `esito` con quante attivita' sono passate e, se
       e' andata male, con il motivo. */
    fun scrivi(act: Activity, d: String, esito: (Int, String?) -> Unit) {
        val att = leggi(d)
        if (att.isEmpty()) { esito(0, "niente"); return }
        val m = act.getSystemService(HealthConnectManager::class.java)
        if (m == null) { esito(0, "manca"); return }
        val elenco = ArrayList<Record>()
        att.forEach { elenco.add(record(it)) }
        Invio(act, m, elenco.chunked(50), esito).parti()
    }

    /* Il messaggio: record separati da ";", campi da ",".
         tipo , data , istante di inizio , minuti , serie , volume
       Quello che non torna si butta e basta: meglio mandare meno che scrivere
       spazzatura dentro la salute di qualcuno. */
    private fun leggi(d: String): List<Att> {
        val adesso = System.currentTimeMillis()
        val out = ArrayList<Att>()
        for (r in d.split(";")) {
            val a = r.split(",")
            if (a.size < 6) continue
            if (a[0] != "c" && a[0] != "p" && a[0] != "b") continue
            if (!DATA_OK.matches(a[1])) continue
            val inizio = a[2].toLongOrNull() ?: continue
            var min = a[3].toIntOrNull() ?: continue
            if (inizio < 1500000000000L || min < 1 || min > 600) continue
            /* Connessione Salute rifiuta quello che finisce nel futuro, e la
               seduta di oggi puo' avere una durata stimata che sfora: si
               taglia adesso. Se non resta nemmeno un minuto, si lascia stare. */
            if (inizio + min * 60000L > adesso) {
                min = ((adesso - inizio) / 60000L).toInt()
                if (min < 1) continue
            }
            out.add(Att(a[0], a[1], inizio, min,
                a[4].toIntOrNull() ?: 0, a[5].toIntOrNull() ?: 0))
        }
        return out
    }

    private fun record(a: Att): Record {
        val tipo = when (a.tipo) {
            "c" -> ExerciseSessionType.EXERCISE_SESSION_TYPE_WALKING
            "b" -> ExerciseSessionType.EXERCISE_SESSION_TYPE_BIKING_STATIONARY
            else -> ExerciseSessionType.EXERCISE_SESSION_TYPE_STRENGTH_TRAINING
        }
        val inizio = Instant.ofEpochMilli(a.inizio)
        val meta = Metadata.Builder()
            .setClientRecordId("palestra-" + a.data + "-" + a.tipo)
            .build()
        val b = ExerciseSessionRecord.Builder(
            meta, inizio, inizio.plusSeconds(a.minuti * 60L), tipo)
            .setTitle(when (a.tipo) {
                "c" -> "Camminata — Palestra"
                "b" -> "Cyclette — Palestra"
                else -> "Palestra"
            })
        if (a.tipo == "p" && a.serie > 0) {
            b.setNotes(a.serie.toString() + " serie" +
                (if (a.volume > 0) " · " + a.volume + " kg sollevati" else ""))
        }
        return b.build()
    }
}

/* A lotti di cinquanta, uno dopo l'altro: anni di sedute sono centinaia di
   record, e una scrittura sola cosi' grossa non si sa se passa. */
private class Invio(
    private val act: Activity,
    private val m: HealthConnectManager,
    private val lotti: List<List<Record>>,
    private val esito: (Int, String?) -> Unit
) : OutcomeReceiver<InsertRecordsResponse, HealthConnectException> {

    private val ex = Executors.newSingleThreadExecutor()
    private var i = 0
    private var fatti = 0

    fun parti() { prossimo() }

    private fun prossimo() {
        if (i >= lotti.size) { act.runOnUiThread { esito(fatti, null) }; return }
        m.insertRecords(lotti[i], ex, this)
    }

    override fun onResult(r: InsertRecordsResponse) {
        fatti += lotti[i].size
        i++
        prossimo()
    }

    override fun onError(e: HealthConnectException) {
        act.runOnUiThread { esito(fatti, "errore") }
    }
}

/* Connessione Salute pretende che l'app abbia una schermata da mostrare quando
   l'utente chiede "perche' questa app vuole i miei dati". Senza, il permesso
   non si puo' nemmeno chiedere. */
class PermessiSalute : Activity() {
    override fun onCreate(salvato: Bundle?) {
        super.onCreate(salvato)
        val t = TextView(this)
        t.setTextColor(Color.WHITE)
        t.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16f)
        t.setPadding(40, 40, 40, 40)
        t.text = "Palestra\n\n" +
            "Questa app scrive in Connessione Salute gli allenamenti che hai " +
            "spuntato nella Palestra: la camminata, i pesi e la cyclette, con " +
            "la data, l'ora e quanto sono durati.\n\n" +
            "Serve a far comparire gli allenamenti in Google Health.\n\n" +
            "Non legge nessun dato di salute e non manda niente fuori dal " +
            "telefono."
        val s = ScrollView(this)
        s.setBackgroundColor(Color.BLACK)
        s.addView(t)
        setContentView(s)
    }
}
