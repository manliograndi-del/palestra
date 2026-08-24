# Palestra — memoria di progetto

Leggi tutto questo file prima di toccare qualsiasi cosa.

## Chi è l'utente e come lavora

Manlio. **Non legge il codice** e non usa il terminale. Verifica il lavoro in un solo
modo: apre l'indirizzo pubblicato sul telefono e guarda se l'app funziona ancora.

Conseguenze operative:
- Non chiedergli di leggere un diff. Spiega **cosa cambia per lui**, non come.
- Non lasciare mai il repo in uno stato non funzionante fra una sessione e l'altra.
- Prima di modifiche che toccano i dati salvati, digli di scaricare il backup.
- Scrivi in italiano.

## Cos'è

App per seguire il programma di allenamento in palestra. Spunta le serie mentre le fa,
e a ogni serie completata parte da sola il recupero di un minuto. Registra i carichi
e li ripropone la volta dopo.

Pubblicato su GitHub Pages: `https://manliograndi-del.github.io/palestra/`
(tutto minuscolo). **Il 2026-08-18 l'API GitHub dava Pages disattivo su questa
repository**: se le modifiche non arrivano sul telefono è la prima cosa da controllare
(Settings → Pages → Deploy from a branch → main / root). Finché il service worker
serviva dalla cache l'app si apriva lo stesso, e la cosa poteva passare inosservata.

## La scheda

Redatta da Sofia Pilan, chinesiologa sportiva, per Virgin Active. È scritta nella
costante `SCHEDA` dentro `index.html`. Due giorni alternati, recupero 1' fra le serie.

**Un solo programma dal 2026-08-18**, chiesto da Manlio: lui in palestra fa tutto in
una seduta sola, quindi i due giorni alternati non servivano. Prima erano Giorno 1 e
Giorno 2, con un selettore in cima e l'alternanza automatica: **il selettore non c'è
più**, `SCHEDA` ha la sola chiave `1` e `S.giorno` vale sempre 1.

Struttura chiesta da lui: una sola attività aerobica in apertura (la camminata), tutti
i pesi di fila in mezzo, 15' di cyclette in chiusura. La bici ellittica che stava a
metà seduta è uscita.

**Il programma** — Tapis roulant 15' (aumenta gradualmente la pendenza) · Abductor 4×20 ·
Adductor 3×12 · Leg press 4×10 · Chest press 3×12 · Low row 4×15 · Chest incline 3×10 ·
Upper back 3×10 · Vertical traction 4×12 · Leg extension 3×10 · Leg curl 3×12 ·
Cyclette 15'. **Totale 34 serie.**

L'ordine originale della chinesiologa erano due giorni distinti, con i blocchi aerobici
alternati ai pesi. Esercizi, serie e ripetizioni sono i suoi e non sono stati toccati:
è cambiato solo come sono distribuiti.

Se Manlio dice che la scheda è cambiata, modifica `SCHEDA` e ricontrolla i totali.

## Vincoli tecnici — non negoziabili senza chiederglielo

1. **Un solo file**: tutta l'app sta in `index.html`.
2. **Nessun build, nessun framework, nessun npm.** JavaScript semplice.
3. **Nessuna dipendenza esterna a runtime.** Deve funzionare senza rete: in palestra
   il segnale è pessimo. Caratteri di sistema, niente CDN.
   **Unica eccezione, dal 2026-08-24:** la libreria di Google per il permesso di Drive.
   Si carica **solo** quando lui tocca "Collega Google Drive" o quando la copia
   automatica parte ad app già avviata — **mai all'avvio**. Senza rete fallisce in
   silenzio e la Palestra funziona come sempre. Provato: ad app aperta e non
   collegata, le chiamate di rete sono zero.
4. **Mobile prima di tutto.** Si usa con le mani sudate, in piedi, fra una serie e
   l'altra: bersagli grandi, niente gesti fini, niente menu annidati.

## Come sono salvati i dati

`localStorage`, con questi prefissi:

- `palestra.config` → `{pesiPrec:{...}, riposo, schermo, ultimo, schedaV, drive}`
  `drive` è `{on, id, ultimo, rev}`: collegato o no, il file su Drive, quando è partita
  l'ultima copia e il segnaposto per capire se qualcun altro l'ha toccata. **Il permesso
  di Google non si salva mai**: vive in memoria (`GTOK`), dura un'ora, si richiede.
  `pesiPrec` è il carico per esercizio, aggiornato **mentre si scrive**: serve poco e
  non va usato come "ultima volta", perché dopo due tasti non ricorda più da dove eri
  partito. Il riferimento vero è `S.pesiRif`, ricalcolato da `calcolaRiferimenti()`
  leggendo l'ultima seduta con data precedente a oggi.
  `ultimo` è l'ultimo giorno svolto: serve a proporre l'altro all'apertura.
- `palestra.indice` → `{"2026-08-17": {giorno,serie,tot,volume}, ...}`
- `palestra.s.YYYY-MM-DD` → `{giorno, fatte:{"i-j":true}, pesi, cardio, volume}`

`fatte` usa la chiave `"<indice esercizio>-<numero serie>"`, e `cardio` l'indice secco.
Se riordini gli esercizi dentro `SCHEDA`, **le sedute passate diventano illeggibili**:
gli indici non corrispondono più. Se devi riordinare, scrivi anche la migrazione.

I riordini del 2026-08-18 ne hanno una, **a catena**: `SCHEDA_V` (3), `RINUMERA_2`,
`RINUMERA_3`, `rinumera()` e `migraSedute()`. Chi è fermo alla versione 1 passa dalla 2
e arriva alla 3 in un colpo solo. Il numero raggiunto resta in `palestra.config` come
`schedaV`.
**Attenzione:** quel numero va scritto anche da `salvaCfg()` e da `ripristina()`. Se lo
dimentichi, la migrazione riparte al prossimo avvio e sposta le spunte una seconda
volta, rovinando le sedute. Un backup senza `schedaV` è di prima dei riordini e va
migrato; uno che ce l'ha no.
Le sedute vecchie dicono ancora `giorno:2`: lo storico legge `SCHEDA[v.giorno]||SCHEDA[1]`
apposta, non togliere quel fallback.

**Attenzione:** sull'origine `manliograndi-del.github.io` vive anche l'app Diario, e le
due condividono lo stesso `localStorage`. La separazione è data **solo dal prefisso**.
Non usare mai chiavi senza prefisso `palestra.`.

## Decisioni di progetto già prese, con la ragione

- **Il timer usa l'orologio di sistema**, non un contatore che scala. Salva l'istante di
  fine (`T.fine = Date.now() + sec*1000`) e ricalcola. Se il telefono sospende la pagina,
  al ritorno il tempo mostrato è quello vero. **Non sostituirlo con un contatore
  decrementale**: è la ragione per cui funziona.
- **Wake lock** (`navigator.wakeLock`) tiene lo schermo acceso durante l'allenamento.
  È l'unico modo perché il segnale acustico parta davvero. Interruttore in Impostazioni.
  Il telefono lo rilascia da solo quando la pagina va in secondo piano: c'è un ascolto
  su `release` che azzera `WL`, altrimenti al ritorno non verrebbe più richiesto.
- **Al risveglio l'app si ridisegna sempre** (`alRisveglio`, su `visibilitychange` e
  `pageshow`), non solo quando è cambiato il giorno. Manlio l'ha trovata bloccata su uno
  schermo nero dopo averla lasciata in tasca: il telefono può sospendere o buttare via
  la pagina, e ridisegnarla la rimette in piedi. `tic()` inoltre non tocca più elementi
  che potrebbero non esserci: prima un errore ogni 200 ms avrebbe piantato tutto.
- **L'audio va sbloccato con un tocco** dell'utente: i browser bloccano l'AudioContext
  finché non c'è un gesto. Per questo c'è il pulsante "Fai suonare adesso" e per questo
  `sbloccaAudio()` viene chiamato quando parte un timer.
- Il segnale è vibrazione + tre bip a 880 Hz.
- **Il volume** è la somma di `kg × ripetizioni` sulle serie spuntate. Serve a dare un
  numero unico di confronto fra sedute.
- **La casella dei kg si presenta già col carico dell'ultima volta** (chiesto il
  2026-08-19: ribatterlo su dieci macchine era una scocciatura). Il numero proposto
  diventa il carico di oggi **solo quando spunti la prima serie** di quell'esercizio:
  finché non lo fai è una proposta, non un dato, e non entra né nel volume né nei
  Carichi. Il promemoria "ultima volta" ora compare solo se oggi hai messo un numero
  diverso — altrimenti ripeterebbe quello che c'è già nella casella.
- **Quarta voce nella barra: Carichi** (chiesta il 2026-08-19). Per ogni macchina, i
  chili dell'ultima volta, quanto sono cambiati dall'inizio e una lineetta
  dell'andamento; toccando l'esercizio si aprono tutte le volte con la differenza da
  quella prima. Ricostruita rileggendo le sedute a ogni disegno: sono poche e piccole,
  non serve una cache. Gli esercizi escono nell'ordine di `SCHEDA`, e solo quelli con
  almeno un peso segnato.
  I chili di ogni singola seduta erano **già** salvati (`pesi` dentro `palestra.s.*`) e
  già visibili nel dettaglio: lui chiedeva l'andamento nel tempo, non il singolo giorno.
- **Lo Storico si apre su un riepilogo mensile** (chiesto il 2026-08-18): calendario del
  mese con i giorni allenati in rosso, frecce per spostarsi, e sotto i totali del mese —
  allenamenti, serie, volume. Si naviga anche sui mesi vuoti fra il primo allenamento e
  il mese corrente: un mese senza rossi dice quanto uno pieno.
  I giorni rossi si toccano e aprono il dettaglio lì sotto; quelli senza allenamento sono
  `disabled`, e la differenza si vede (rosso pieno contro grigio spento) — non è un
  bersaglio muto come quelli che gli avevano fatto credere rotto il Diario.
  Il dettaglio di una seduta sta in `dettaglioSeduta()`, usata sia dal calendario sia
  dall'elenco sotto: se la cambi, cambiano tutti e due.
- Cambiare giorno con serie già spuntate era impedito di proposito, quando i giorni erano
  due. Ora il programma è unico e la scelta non esiste più.

## La copia su Google Drive

Aggiunta il 2026-08-24, uguale a quella del Diario e per la stessa ragione: i carichi
esistono solo dentro questo telefono, e sono **la cosa meno ricostruibile** che ha —
senza, in palestra non sa da dove ripartire.

Quando apre l'app, e un minuto dopo ogni spunta, il backup completo finisce nel suo
Drive come `palestra-backup.json`. Da un altro dispositivo: "Riprendi le sedute da
Drive", che passa dalla stessa strada del ripristino da file — **la migrazione
`schedaV` resta quella, non inventarne un'altra**: un backup senza `schedaV` viene
rinumerato al riavvio come è sempre stato.

**Due regole da non togliere mai.**
La prima: **se qui non c'è nessuna seduta, non si scrive su Drive.** Il caso da temere
è telefono nuovo più "Collega" premuto per primo: il vuoto di qui cancellerebbe la
copia buona di là e non resterebbe niente da cui riprendere. In quel caso ci si collega
e gli si dice di premere "Riprendi".
La seconda: **non si sovrascrive una copia toccata da qualcun altro.** Prima di
scrivere si chiede a Drive quando è stato modificato il file e lo si confronta con
`S.drive.rev`. Se non combaciano, di là c'è roba più nuova e ci si ferma. La via
d'uscita è "scollega e ricollega", che azzera il segnaposto.

**Stesso identificativo Google del Diario**, di proposito: l'indirizzo autorizzato è
`https://manliograndi-del.github.io`, che copre tutte e due le app, così non è servito
rimettere mano al pannello di Google. Per Drive le due app sono lo stesso programma:
si tengono separate **solo dal nome del file** (`palestra-backup.json` contro
`diario-backup.json`). Se ne aggiungi una terza, dalle un nome diverso.
Il permesso è `drive.file`: si tocca solo il file creato dall'app. Non allargarlo.
L'identificativo in chiaro dentro `index.html` **non è una chiave segreta**: negli
schemi da browser è pubblico e vale solo se chiamato dall'indirizzo autorizzato.

In `sw.js` c'è una riga che fa **ignorare al service worker tutto ciò che non è del
nostro indirizzo**: senza, una chiamata a Google andata storta si prenderebbe in cambio
la pagina dell'app.

## La seduta che arriva dall'orologio

Disegnata insieme a lui il 2026-08-24 e approvata schermata per schermata.
**La metà del telefono è provata qui; l'app da polso no** — in questa sessione non
c'è l'SDK di Android e i server da cui si scarica sono bloccati, quindi il codice
Kotlin non è mai stato compilato in locale. Lo compila GitHub (vedi sotto).

L'orologio **non parla con questa pagina**: apre un indirizzo sul telefono con la
seduta scritta dentro (`RemoteActivityHelper` di Wear OS, che apre una URL sul
telefono **senza bisogno di nessuna app installata sul telefono**). È il motivo per
cui il collegamento va in un senso solo: l'orologio racconta, il telefono decide.

    #orologio=1;2026-08-24;3-0,3-1,4-0;0,11
    versione ; data ; serie spuntate ; blocchi di cardio

Le serie usano **le stesse chiavi di qui** (`indice esercizio - numero serie`),
quindi l'app da polso deve avere **la stessa scheda nello stesso ordine**. Se
riordini `SCHEDA`, va rifatta anche di là: la versione in testa (`OROLOGIO_V`) serve
ad accorgersene invece di registrare spunte a caso.

Regole decise con lui:
- la seduta del polso **sostituisce** quella del telefono, con un riquadro di
  conferma che dice quante spunte verrebbero perse. Due elenchi mezzi pieni non si
  fondono da soli senza inventare;
- **i chili non si scrivono sull'orologio**, si vedono soltanto. Al momento di
  registrare, ogni esercizio spuntato prende il carico di riferimento (`pesiRif`) —
  la stessa regola del tocco sul telefono, e lo stesso numero che l'orologio gli ha
  mostrato. Senza quel pezzo una seduta fatta dal polso peserebbe **zero chili** e la
  pagina Carichi resterebbe vuota per quel giorno: trovato provando;
- l'indirizzo si ripulisce subito dopo (`pulisciOrologio`), altrimenti un
  ricaricamento rimetterebbe in mezzo la stessa proposta a giorni di distanza;
- c'è un ascolto su `hashchange`: se l'app è già aperta il telefono non la ricarica,
  cambia solo l'indirizzo, e senza quello il messaggio non comparirebbe mai.

## L'app da polso — cartella `orologio/`

Kotlin, **niente Compose**, una dipendenza sola (`wear-remote-interactions`, che
serve solo ad aprire una pagina sul telefono). La scelta è deliberata: il codice di
là non lo posso provare, quindi meno pezzi ci sono, meno cose si rompono. L'interfaccia
è costruita a mano con le View e **si ridisegna tutta a ogni tocco**, come fa la
Palestra sul telefono.

- **Gli indici di `SCHEDA` devono restare identici** a quelli di `index.html`: il
  messaggio usa le stesse chiavi `indice-serie`. Se riordini di qua, riordina di là e
  alza `OROLOGIO_V` **da tutte e due le parti**.
- **Lo stesso APK si installa anche sul telefono** (`uses-feature ... required="false"`).
  Sul telefono non c'è nessun polso a cui mandare la seduta, quindi apre la Palestra
  direttamente: è così che si prova tutta la catena senza orologio e senza cavi.
- I chili sull'orologio **non ci sono proprio**: non esiste un canale telefono→polso
  senza un'app installata sul telefono, e non ne vogliamo una. Li mette il telefono
  quando registra, prendendo quelli di riferimento.
- La seduta resta nelle SharedPreferences finché non è stata mandata: al cambio di
  giorno, se non è partita, viene riproposta invece che buttata.

**La compilazione la fa GitHub** (`.github/workflows/orologio.yml`) a ogni modifica
dentro `orologio/`, e pubblica sempre allo stesso indirizzo:
`https://github.com/manliograndi-del/palestra/releases/download/orologio/palestra-orologio.apk`
È l'unico modo di avere un APK da questa sessione. Se il file non si aggiorna, guarda
i log dell'azione prima di dare la colpa al telefono.

## Aspetto

**Rifatto il 2026-08-18 sul linguaggio visivo di Virgin Active**, su richiesta di
Manlio e partendo dalle schermate della loro app. Prima seguiva la famiglia visiva del
Diario: quella parentela non c'è più, e il Diario è rimasto chiaro e sobrio.

Nero, bianco, rosso. Palette in `:root`:
`--carta #000` · `--superficie #151515` · `--superficie2 #232323` · `--inchiostro #FFF`
`--tenue #9A9A9A` · `--linea #2E2E2E` · `--rosso #E4002B` (il rosso Virgin) ·
`--su-rosso #FFF` · `--raggio 16px`

`--blu`, `--senape` e `--verde` esistono ancora ma puntano tutti al rosso: erano
sparsi nel CSS e toglierli avrebbe voluto dire riscriverlo tutto. Non usarli per cose
nuove, usa `--rosso`.

**Il rosso è l'unico accento e significa "azione" o "fatto".** Non spenderlo per
decorare, o smette di voler dire qualcosa. Le serie completate sono pastiglie rosse
piene (prima erano verdi). Titoli in maiuscolo pesante, pulsanti a pastiglia
(`border-radius:99px`), riquadri a 16px, barra in basso con la voce attiva su fondo
rosso pieno.

**Niente font di Virgin**: è un carattere loro e caricarlo significherebbe dipendere
dalla rete, che in palestra non c'è. Si usano i caratteri di sistema spinti su peso
(800–900) e spaziatura negativa.

L'elemento centrale restano le pastiglie delle serie: una per serie, col numero di
ripetizioni dentro. Il timer sale dal basso come riquadro staccato.

## Prima di chiudere una sessione

1. **Alza il numero di versione della cache in `sw.js`** (`palestra-v8` → `palestra-v9`).
   Dal 2026-08-18 il service worker chiede la pagina prima alla rete, quindi una versione
   nuova arriva con un ricaricamento solo; il numero di cache va alzato lo stesso, governa
   la copia di riserva usata offline. La pulizia in `activate` tocca solo i nomi che
   iniziano per `palestra-`: prima cancellava anche la cache dell'app Diario.
2. Verifica che le pastiglie si spuntino, che il timer parta, che una seduta sopravviva
   a un ricaricamento.
3. Digli in italiano cosa vedrà di diverso, e che deve ricaricare due volte.

## File del repo

- `index.html` — tutta l'app
- `sw.js` — funzionamento offline; alzare il numero di cache a ogni rilascio
- `manifest.webmanifest` · `icon-192.png` · `icon-512.png`
