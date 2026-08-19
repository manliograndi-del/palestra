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
4. **Mobile prima di tutto.** Si usa con le mani sudate, in piedi, fra una serie e
   l'altra: bersagli grandi, niente gesti fini, niente menu annidati.

## Come sono salvati i dati

`localStorage`, con questi prefissi:

- `palestra.config` → `{pesiPrec:{...}, riposo, schermo, ultimo}`
  `pesiPrec` è il carico dell'ultima volta per esercizio, mostrato come riferimento.
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

1. **Alza il numero di versione della cache in `sw.js`** (`palestra-v2` → `palestra-v3`).
   Dal 2026-08-18 il service worker chiede la pagina prima alla rete, quindi una versione
   nuova arriva con un ricaricamento solo; il numero di cache va alzato lo stesso, governa
   la copia di riserva usata offline. La pulizia in `activate` tocca solo i nomi che
   iniziano per `palestra-`: prima cancellava anche la cache dell'app Diario.
2. Verifica che le pastiglie si spuntino, che il timer parta, che una seduta sopravviva
   a un ricaricamento.
3. Digli in italiano cosa vedrà di diverso, e che deve ricaricare due volte.

## La pagina delle scuole — `scuole.html`

Cosa c'entra con la palestra: niente. Manlio ha portato il CSV dell'anagrafe
delle scuole statali del ministero (50.273 sedi, anno 2026/27) e ha chiesto una
scheda per riga, con tutti i dati, impaginata bene. Sta qui perché qui c'era già
un sito pubblicato: `https://manliograndi-del.github.io/palestra/scuole.html`.

**Non tocca l'app della palestra e non salva niente.** Nessuna chiave in
`localStorage`, nessuna modifica a `index.html`, `sw.js` o al manifest. Se un
giorno dà fastidio, si cancella il file e la palestra non se ne accorge.

Un file solo, come il resto: dentro ci sono anche i dati. Il CSV del ministero
pesa 13 MB perché ripete migliaia di volte gli stessi comuni e istituti; qui le
colonne ripetute diventano dizionari e ogni scuola è una riga di indici, così la
pagina sta in 4,5 MB e funziona anche senza rete. La pagina si costruisce da due
pezzi:

- `strumenti/scuole-modello.html` — la pagina vera (grafica e programma), con il
  segnaposto `/*DATI*/` dove finiscono i dati. **È qui che si modifica.**
- `strumenti/scuole-impacchetta.py` — legge il CSV ministeriale e scrive
  `scuole.html`: `python3 strumenti/scuole-impacchetta.py anagrafe.csv`

`scuole.html` è generato: non modificarlo a mano, si riscrive al primo lancio
dello script. Quando esce il CSV dell'anno nuovo basta rilanciare lo script.

Scelte già prese: il colore dice il grado di istruzione e nient'altro, dal più
chiaro (infanzia) al più scuro (secondaria di secondo grado); le tre famiglie
fuori scala (comprensivi, adulti, convitti) hanno tinte spente apposta. Il
ministero scrive tutto in maiuscolo e la pagina lo rimette in tondo, lasciando
stare le sigle (IC, ITIS, CPIA) e abbassando le preposizioni. Dove il ministero
non ha compilato un campo la scheda scrive «non depositata» invece di far finta
di niente; l'unica cosa ricostruita è la posta elettronica, che in 49.341 casi su
50.273 è `CODICEISTITUTO@istruzione.it`, e la scheda dichiara di averla ricavata.

## File del repo

- `index.html` — tutta l'app della palestra
- `sw.js` — funzionamento offline; alzare il numero di cache a ogni rilascio
- `manifest.webmanifest` · `icon-192.png` · `icon-512.png`
- `scuole.html` — anagrafe delle scuole statali (generato, vedi sopra)
- `strumenti/` — il modello e lo script che generano `scuole.html`
