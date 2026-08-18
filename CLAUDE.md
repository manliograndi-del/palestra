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

App per seguire la scheda di allenamento in palestra. Spunta le serie mentre le fa,
e a ogni serie completata parte da sola il recupero di un minuto. Registra i carichi
e li ripropone la volta dopo.

Pubblicato su GitHub Pages: `https://manliograndi-del.github.io/Palestra/`

## La scheda

Redatta da Sofia Pilan, chinesiologa sportiva, per Virgin Active. È scritta nella
costante `SCHEDA` dentro `index.html`. Due giorni alternati, recupero 1' fra le serie.

**Giorno 1** — Tapis roulant 15' (aumenta gradualmente la pendenza) · Abductor 4×20 ·
Adductor 3×12 · Leg press 4×10 · Bici ellittica 10' · Chest press 3×12 · Low row 4×15 ·
Cyclette 15'. Totale 18 serie.

**Giorno 2** — Cyclette 10' (aumenta gradualmente la resistenza) · Chest incline 3×10 ·
Upper back 3×10 · Vertical traction 4×12 · Bici ellittica 10' · Leg extension 3×10 ·
Leg curl 3×12 · Camminata in salita 20'. Totale 16 serie.

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

`fatte` usa la chiave `"<indice esercizio>-<numero serie>"`. Se riordini gli esercizi
dentro `SCHEDA`, **le sedute passate diventano illeggibili**: gli indici non
corrispondono più. Se devi riordinare, scrivi anche la migrazione.

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
- **L'audio va sbloccato con un tocco** dell'utente: i browser bloccano l'AudioContext
  finché non c'è un gesto. Per questo c'è il pulsante "Fai suonare adesso" e per questo
  `sbloccaAudio()` viene chiamato quando parte un timer.
- Il segnale è vibrazione + tre bip a 880 Hz.
- **Il volume** è la somma di `kg × ripetizioni` sulle serie spuntate. Serve a dare un
  numero unico di confronto fra sedute.
- Cambiare giorno con serie già spuntate è impedito di proposito: mescolerebbe due schede
  nella stessa seduta.

## Aspetto

Stessa famiglia visiva dell'app Diario, di proposito. Palette in `:root`:
`--carta #E9ECE6` · `--superficie #FFF` · `--inchiostro #141B18` · `--tenue #5B6661`
`--linea #CDD3CB` · `--blu #1F4A6B` · `--senape #C08411` · `--rosso #A3341F` ·
`--verde #2E6B4F` (serie completate)

L'elemento centrale sono le pastiglie delle serie: una per serie, col numero di
ripetizioni dentro, verdi quando fatte. Il timer sale dal basso e occupa la fascia
inferiore. Sobrio, strumentale, niente decorazioni.

## Prima di chiudere una sessione

1. **Alza il numero di versione della cache in `sw.js`** (`palestra-v1` → `palestra-v2`).
   Se non lo fai, il telefono serve la versione vecchia e la modifica sembra sparita.
2. Verifica che le pastiglie si spuntino, che il timer parta, che una seduta sopravviva
   a un ricaricamento.
3. Digli in italiano cosa vedrà di diverso, e che deve ricaricare due volte.

## File del repo

- `index.html` — tutta l'app
- `sw.js` — funzionamento offline; alzare il numero di cache a ogni rilascio
- `manifest.webmanifest` · `icon-192.png` · `icon-512.png`
