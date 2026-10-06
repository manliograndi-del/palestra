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
più** e `SCHEDA` ha la sola chiave `1`.
Nella pulizia del 2026-08-29 è sparito anche `S.giorno`, che valeva 1 e basta e
faceva credere che ci fosse ancora qualcosa da scegliere: dove serviva l'indice
della scheda adesso c'è `SCHEDA[1]`. **Nelle sedute salvate il campo `giorno`
resta**, perché le sedute vecchie dicono ancora `giorno:2` e lo storico le legge
con `SCHEDA[v.giorno]||SCHEDA[1]`.

Struttura chiesta da lui: una sola attività aerobica in apertura (la camminata), tutti
i pesi di fila in mezzo, 15' di cyclette in chiusura. La bici ellittica che stava a
metà seduta è uscita.

**Il programma** — Tapis roulant 15' (aumenta gradualmente la pendenza) · Adductor 3×12 ·
Leg curl 3×12 · Abductor 4×20 · Chest press 3×12 · Low row 4×15 · Chest incline 3×10 ·
Upper back 3×10 · Vertical traction 4×12 · Leg press 4×10 · Leg extension 3×10 ·
Cyclette 15'. **Totale 34 serie.**

L'ordine originale della chinesiologa erano due giorni distinti, con i blocchi aerobici
alternati ai pesi. Esercizi, serie e ripetizioni sono i suoi e non sono stati toccati:
è cambiato solo come sono distribuiti.

**Leg press e Leg extension in fondo ai pesi** (chiesto il 2026-09-08), dopo Leg curl
invece che subito dopo Adductor: restano nello stesso ordine reciproco fra loro, si
sposta solo dove cade il blocco gambe rispetto al resto. `SCHEDA_V` è salito a 4, con
`RINUMERA_4` a fare da mappa. Tapis roulant e Cyclette restano agli estremi, quindi
non compaiono in quella mappa: nessun riordino le ha mai toccate.

**Adductor, Leg curl e Abductor in testa ai pesi** (chiesto il 2026-09-15), in
quest'ordine: prima i pesi si aprivano con Abductor e Adductor e il Leg curl stava in
mezzo, dopo Vertical traction. Tutto il resto scala di una posizione senza cambiare
ordine reciproco, Leg press e Leg extension restano in fondo. `SCHEDA_V` è salito a 5,
con `RINUMERA_5`, e `OROLOGIO_V` a 4 (è uno scambio fra esercizi dello stesso tipo:
vedi più sotto perché è obbligatorio).

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
- `palestra.indice` → `{"2026-08-17": {giorno,serie,tot,volume,minC}, ...}`
  `minC` sono **i minuti di cardio davvero fatti**, aggiunti il 2026-08-28. Non
  servono a niente qui dentro: **li legge il Diario**, che mostra la seduta accanto
  alla camminata e ne stima le calorie. Il Diario non conosce la `SCHEDA` e non può
  sapere che il tapis roulant dura 15', quindi il conto lo facciamo noi e di là
  arriva un numero già pronto. `minCardio()` lo calcola, `completaIndice()` lo
  riempie una volta sola per le sedute vecchie (aggiunge un campo, non tocca altro).
  **Non toglierlo**: senza, il pannello Palestra del Diario conterebbe solo i pesi.
- `palestra.s.YYYY-MM-DD` → `{giorno, fatte:{"i-j":true}, pesi, cardio, volume, ora, fine}`
  `ora` e `fine` sono gli istanti della prima e dell'ultima spunta, aggiunti il
  2026-10-06. **Non servono a niente dentro l'app**: li vuole Google Health, che un
  allenamento senza orario non sa dove metterlo. Nelle sedute di prima non ci sono e
  si ripiega su `SALUTE_ORA`. Sono due campi in più, non cambiano niente di quello
  che c'era.

`fatte` usa la chiave `"<indice esercizio>-<numero serie>"`, e `cardio` l'indice secco.
Se riordini gli esercizi dentro `SCHEDA`, **le sedute passate diventano illeggibili**:
gli indici non corrispondono più. Se devi riordinare, scrivi anche la migrazione.

I riordini del 2026-08-18, del 2026-09-08 e del 2026-09-15 ne hanno una, **a catena**:
`SCHEDA_V` (5), `RINUMERA_2`, `RINUMERA_3`, `RINUMERA_4`, `RINUMERA_5`, `rinumera()` e
`migraSedute()`. Chi è fermo alla versione 1 passa dalla 2, poi dalla 3, poi dalla 4 e
arriva alla 5 in un colpo solo, nella stessa chiamata. Il numero raggiunto resta in `palestra.config` come `schedaV`.
**Attenzione:** quel numero va scritto anche da `salvaCfg()` e da `ripristina()`. Se lo
dimentichi, la migrazione riparte al prossimo avvio e sposta le spunte una seconda
volta, rovinando le sedute. Un backup senza `schedaV` è di prima dei riordini e va
migrato; uno che ce l'ha no.
Le sedute vecchie dicono ancora `giorno:2`: lo storico legge `SCHEDA[v.giorno]||SCHEDA[1]`
apposta, non togliere quel fallback.

**Attenzione:** sull'origine `manliograndi-del.github.io` vive anche l'app Diario, e le
due condividono lo stesso `localStorage`. La separazione è data **solo dal prefisso**.
Non usare mai chiavi senza prefisso `palestra.`.

**Dal 2026-08-28 quella convivenza è diventata una funzione**: il Diario legge
`palestra.indice` per mostrare la seduta del giorno e stimarne le calorie. È una
lettura sola e in un senso solo — **il Diario non scrive mai dentro le chiavi
`palestra.`**, e la Palestra non sa nemmeno che il Diario esiste. Se cambi la forma
di `palestra.indice`, di là si rompe qualcosa: vai a guardare.

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
- **Lo Storico si apre sull'ultimo mese in cui ti sei allenato**, non sul mese di
  oggi. Il 2026-09-01 nel Diario questo ha fatto credere a Manlio di aver perso
  tutti i dati: il mese nuovo era ancora vuoto e il calendario si apriva lì. Qui
  vale lo stesso ed è anche più facile che capiti, perché in palestra non ci va
  tutti i giorni. **Non rimettere `S.mese||meseDi(oggiISO())`.**
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

## Che i dati non spariscano

**"Azzera la seduta di oggi" chiede conferma e si può annullare** (dal
2026-09-02). Prima cancellava tutto **con un tocco solo**, e stava in fondo alla
schermata dell'allenamento: quel giorno Manlio si è ritrovato la seduta
cancellata senza sapere come. Sull'orologio la doppia conferma c'era dal
2026-08-26, qui no. Adesso il primo tocco arma il tasto ("Sicuro? Tocca ancora
per azzerare", che si disarma da solo dopo 5 secondi), e dopo l'azzeramento
resta per 40 secondi un "Seduta azzerata — annulla" che rimette tutto,
cardio compreso. **Non togliere né la conferma né l'annulla**: si usa in piedi,
con le mani sudate.

**Svuotare e ricaricare devono essere la stessa riga** (`caricaGiorno()`).
`alRisveglio` al cambio di data azzerava le spunte in memoria e **non leggeva
quelle salvate**: la prima spunta successiva riscriveva la seduta del giorno con
quel poco rimasto in memoria, e un allenamento intero spariva. Adesso il cambio
di data passa sempre da `controllaData()`, che carica la seduta del giorno nuovo.

**Il giorno cambia anche mentre l'app è aperta**: un `setInterval` di 20 secondi
lo controlla, come fa il Diario. Prima ce ne accorgevamo solo al risveglio, e una
pagina lasciata aperta la sera scriveva l'allenamento del mattino dopo sotto la
data di ieri.


Le impostazioni si scrivono in **due copie** (`palestra.config` e
`palestra.config.bis`, dal 2026-09-02): se la prima è illeggibile si prende la
seconda e si riscrive la prima. L'indice si ricostruisce dalle sedute, questo
no. Nel Diario quel giorno Manlio ha perso proprio le impostazioni — gli
alimenti che si era salvato — mentre i giorni li aveva ripresi da Drive.

`ricostruisciIndice()` rimette in piedi l'elenco delle sedute leggendo i
`palestra.s.<data>`. Gira a ogni avvio e **aggiunge soltanto**. Nel Diario, il
2026-09-02, l'elenco dei giorni si è svuotato mentre le sedute di qui — stessa
memoria, stesso telefono — erano intatte: segno che a rovinarsi era stato
l'indice, non i dati. Se un giorno l'app sembra vuota, guarda lì per prima cosa.

`leggi()` distingue due guasti che prima confondeva: il browser che non dà la
memoria (`memOk` falso, problema di tutta l'app) e un singolo valore
illeggibile (il browser sta benissimo, si torna al valore di riserva). Prima
bastava un valore rovinato per far comparire "questo browser non permette il
salvataggio".

**Una copia su Drive in attesa parte subito se l'app se ne va** (`inPartenza`,
dal 2026-09-02). Nel Diario quel giorno una copia che stava aspettando il suo
minuto non è mai partita, perché l'app era sparita prima: il giorno segnato quel
giorno non c'era più da nessuna parte. Adesso l'attesa è di 25 secondi e la
copia in sospeso parte quando la pagina va in secondo piano o viene chiusa,
mentre è ancora viva e la richiesta fa in tempo.


`chiediMemoriaStabile()` chiede a Chrome di non buttare via i dati di questa app
(`navigator.storage.persist()`), dal 2026-09-02: quel giorno il **Diario** di
Manlio si è trovato vuoto sul telefono. Non è stata l'app — in nessuna delle due
c'è una riga che cancelli la memoria, verificato — ma la pulizia automatica del
browser o una cancellazione dei dati di navigazione. Per un'app installata sulla
schermata Home Chrome di solito accetta senza chiedere niente. **Non è una
garanzia**: il file di backup scaricato resta l'unica cosa che salva davvero.

Se ricapita, la strada del recupero è provata e funziona: Impostazioni →
"Collega Google Drive" (che con la palestra vuota **non sovrascrive niente** e
dice di premere Riprendi) → "Riprendi le sedute da Drive".

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
**Il progetto Google che tiene la chiave si chiama `Palestra` (`palestra-510722`)
dal 2026-10-05**; prima era `Diario`, e il nome ha contribuito a farglielo
cancellare per sbaglio. Non cancellarlo e non lasciarglielo cancellare: è
l'unico posto dove vive la chiave di tutte e due le app.
L'identificativo in chiaro dentro `index.html` **non è una chiave segreta**: negli
schemi da browser è pubblico e vale solo se chiamato dall'indirizzo autorizzato.

In `sw.js` c'è una riga che fa **ignorare al service worker tutto ciò che non è del
nostro indirizzo**: senza, una chiamata a Google andata storta si prenderebbe in cambio
la pagina dell'app.

**Il 2026-10-05 il collegamento a Drive si è rotto di colpo**, in tutte e due le
app insieme: Google rispondeva `deleted_client`. Non era il codice — era sparita
la chiave. Manlio, facendo pulizia dei progetti Google Cloud che gli sembravano
avanzi inutili, aveva cancellato il progetto **Diario**, che si chiama così ma
teneva in piedi **tutte e due** le app. Da lì in poi, la storia utile per la
prossima volta:
- il progetto si recupera da *Gestione risorse → Risorse in attesa di
  eliminazione* (30 giorni di tempo), e la chiave da *Credenziali → Ripristina
  credenziali eliminate*. **Tutti e due i ripristini sono riusciti e non è
  servito a niente**: continuava a dire `deleted_client`;
- il motivo è emerso provando a creare una chiave nuova nello stesso progetto:
  *"Il brand che stai cercando di modificare è stato eliminato"*. Il **brand** è
  la schermata di consenso, e quella il ripristino non la riporta indietro.
  Senza, nessuna chiave di quel progetto funziona, nemmeno quelle ripristinate.
  E ricrearla in un progetto ripristinato non riusciva;
- **la via d'uscita è stata un progetto nuovo da zero** (`palestra-510722`),
  dove tutto fila: abilitare Google Drive API, configurare il consenso, creare
  il client. **Se ricapita, non perdere tempo con i ripristini: progetto nuovo
  e via.** La procedura passo per passo è in una pagina a parte:
  https://claude.ai/artifact/4eJoq5KhrgL7DEEnLFE5Sg
- conseguenza da ricordare: con una chiave nuova il permesso `drive.file` non
  dà più accesso al vecchio `palestra-backup.json`, che resta nel Drive di
  Manlio ma invisibile all'app. L'app ne comincia uno nuovo. **Prima di
  cambiare chiave, digli di scaricare il backup** — dal telefono e, se c'è,
  anche il file da Drive.

**Il Diario è stato allineato lo stesso giorno** e porta la stessa identica
chiave: le due app continuano a condividerne una sola, come da agosto.
Verificato sulle pagine pubblicate di tutte e due.

**Durante tutto il guasto la Palestra ha funzionato normalmente**: le sedute
stanno nel telefono e l'orologio parla col telefono via Bluetooth. Si era fermata
solo la copia automatica. Vale la pena dirglielo subito quando succede, perché la
prima domanda che fa è se può andare ad allenarsi.

**`GOOGLE_ACCOUNT` dice a Google quale account usare** (`hint`, su
`initTokenClient` e ripetuto su `requestAccessToken`), dal 2026-09-10: quel
giorno Manlio ha attivato un secondo account Google sul telefono, e da lì in
poi Google fermava ogni volta a chiedere quale usare invece di andare dritto.
L'account è sempre lo stesso, `manlio.grandi@gmail.com`: non c'è motivo di
chiederlo ogni volta, quindi ora non lo chiede più — se quell'account è
presente sul telefono, la scelta si salta. **Se un giorno cambia l'account con
cui salva su Drive**, questa costante va cambiata (qui e nel Diario insieme,
sono due copie identiche dello stesso valore).

## Gli allenamenti in Google Health

Chiesto il 2026-10-06: “così Salute saprebbe gli esercizi fatti”.

**Com'è fatto il giro, e perché non può essere più corto.** Google Health — l'app
che era Fitbit, quella che legge il Pixel Watch; **si chiama così dal 19 maggio
2026** — non sa niente delle nostre chiavi: legge **Connessione Salute** (Health
Connect), il magazzino di salute dentro Android, e di lì mostra gli allenamenti
fatti da altre app. Scriverci si può solo da un'app Android:

- **dalla pagina web no**: da un browser non esiste alcun modo di parlare con
  Connessione Salute;
- **dal polso no**: su Wear OS Connessione Salute **non esiste**. Tutte le app
  fanno la stessa cosa — il polso manda al telefono e il telefono scrive.

Resta l'APK della Palestra girando **sul telefono**, quello che già travasa i
carichi. Quindi: la Palestra web impacchetta le sedute e apre
`palestra://salute?v=1&d=...`, l'APK le scrive, Google Health le legge.
Da Android 14 Connessione Salute è parte del sistema e si chiama diretta
(`android.health.connect`): **è il motivo per cui l'app da polso continua ad
avere una dipendenza sola**. Su Android 13 e precedenti era un'app a parte e
servirebbe la libreria di Google: in quel caso l'APK non fa niente e lo dice.

Ogni giornata di palestra diventa fino a **tre attività una dopo l'altra** —
camminata, pesi, cyclette — perché è così che Salute capisce il cardio, e perché
**due attività sovrapposte le rifiuta**. Il messaggio è un record per attività:
`tipo , data , istante di inizio , minuti , serie , volume` (tipo: `c`
camminata, `p` pesi, `b` cyclette). `saluteRecord()` e `saluteURL()` lo
costruiscono, `Salute.kt` lo legge.

**Il segnaposto è `palestra-<data>-<tipo>`** (`clientRecordId`), e dipende dalla
data, **non dall'orario**: rimandare gli stessi allenamenti aggiorna i record di
prima invece di sdoppiarli, quindi il pulsante si può premere quante volte si
vuole. Se un giorno lo si legasse all'ora, un cambio di `SALUTE_ORA` creerebbe
doppioni per ogni seduta vecchia.

**Delle sedute vecchie non sappiamo l'ora**, e un allenamento senza orario Salute
non lo accetta: si danno per fatte alle `SALUTE_ORA` (18:00). Da quel giorno le
sedute nuove portano `ora` e `fine` veri, quindi l'orario è quello giusto; la
durata dei pesi, dove gli orari mancano, è stimata in **due minuti per serie**
(un minuto di recupero più uno di esecuzione). Se Manlio dice che in Salute gli
allenamenti vecchi stanno all'ora sbagliata, si cambia `SALUTE_ORA` e si rimanda:
i record si aggiornano, non raddoppiano.

**Nell'APK il permesso è `android.permission.health.WRITE_EXERCISE` e basta**:
scrivere. Leggere non serve e un permesso in più non si chiede. Insieme al
permesso c'è `PermessiSalute`, una schermata che spiega perché l'app vuole quei
dati: **senza, Connessione Salute non lascia nemmeno chiedere il permesso**, non
è decorazione. I record vanno a lotti di cinquanta, perché anni di sedute sono
centinaia di record e una scrittura sola così grossa non si sa se passa.

Cosa **non** arriva in Salute: i chili per macchina. Non c'è un posto garantito
dove metterli, e il volume totale finisce nelle note dei pesi. Il posto dei
carichi resta la Palestra.

Quello che l'APK fa per Salute **gira solo sul telefono**, quindi questa
modifica si installa solo lì: **l'orologio può restare alla versione di prima**
e i chili sul polso non si perdono.

**Provato davvero il 2026-10-06, e funziona**: 54 attività scritte in un colpo
solo, e in Connessione Salute → Esercizio fisico compaiono come devono —
“Camminata — Palestra” 18:00-18:15, poi “Allenamento di forza · Palestra” con
sotto “27 serie · 12380 kg sollevati”. Le note dei pesi si vedono, quindi quel
posto per serie e volume è buono. I giorni in cui non aveva spuntato la
cyclette non hanno la terza attività: la seduta arriva com'era, non inventata.

Note pratiche emerse quel giorno:
- il travaso si fa dalla Palestra **aperta nel browser**, non serve che sia
  installata sulla schermata Home;
- Chrome chiede con quale app aprire `palestra://salute`: è *Palestra polso*.

**Scrivere non basta: Google Health deve avere il permesso di leggere**, ed è
qui che Manlio si è arenato per un'ora credendo che non fosse passato niente.
La prova sta in *Connessione Salute → Esercizio fisico → **Accesso***: sotto
“scrittura” c'è *Palestra polso* (noi), sotto “lettura” ci deve essere *Google
Health*. Se non c'è, in Google Health non si vede niente e sembra un guasto
nostro. Si dà da **Google Health → Connessioni (in alto a sinistra) → App
partner → Health Connect**, spuntando **“Dati su fitness e benessere”** e non
“Riepiloghi salute personali”, che è la storia clinica e non c'entra niente.

E soprattutto: alla fine di quel giro compare **“Accesso ai dati precedenti”**.
**Va acceso**, altrimenti Google Health vede solo gli ultimi 30 giorni e tutte
le sedute più vecchie restano invisibili pur essendo in Connessione Salute.
È la spiegazione del “manca tutto agosto”.

**Le calorie non le scriviamo noi**: le misura l'orologio dal battito, e una
nostra stima si sommerebbe a quella gonfiando il totale del giorno. Per la
stessa ragione le nostre attività hanno *Carico cardiaco 0*: non portano
battito, e il carico cardiaco Google lo calcola da quello.

**Ma c'è una condizione, scoperta il 2026-10-06 e da non dimenticare**: l'orologio
conta la palestra **solo se Manlio avvia l'allenamento dal polso**. Senza, giudica
dal movimento, e i pesi per lui sono quasi come stare seduti — nessun passo, battito
che sale a tratti. Lui se n'era accorto da solo: "ieri allenamento molto duro e non
l'ha contato per nulla", e aveva ragione. (Avevo provato a spiegarlo con la differenza
fra un giorno di palestra e la domenica, ma il confronto non reggeva: domenica era
bassa perché non era uscito di casa. **Lo scarto fra i suoi giorni è fatto dai passi**,
e una seduta di pesi ci sparisce dentro.)
**Scelta sua, quel giorno: avvia l'allenamento sull'orologio.** Quindi non si tocca
niente qui, e **non si comincino a scrivere calorie** senza prima chiedergli se ha
smesso di usare il modo allenamento — altrimenti si sommano.

## La seduta che arriva dall'orologio

Disegnata insieme a lui il 2026-08-24 e approvata schermata per schermata.
**La metà del telefono è provata qui; l'app da polso no** — in questa sessione non
c'è l'SDK di Android e i server da cui si scarica sono bloccati, quindi il codice
Kotlin non è mai stato compilato in locale. Lo compila GitHub (vedi sotto).

L'orologio **non parla con questa pagina**: apre un indirizzo sul telefono con la
seduta scritta dentro (`RemoteActivityHelper` di Wear OS, che apre una URL sul
telefono **senza bisogno di nessuna app installata sul telefono**). È il motivo per
cui il collegamento va in un senso solo: l'orologio racconta, il telefono decide.

    #orologio=3;2026-08-24;3-0,3-1,4-0;0,11;3:60,4:32.5
    versione ; data ; serie ; cardio ; chili per esercizio

Le serie usano **le stesse chiavi di qui** (`indice esercizio - numero serie`),
quindi l'app da polso deve avere **la stessa scheda nello stesso ordine**. Se
riordini `SCHEDA`, va rifatta anche di là e va alzato `OROLOGIO_V` da tutte e
due le parti.

**Dal 2026-09-08 si accetta solo la versione esatta**, non più "fino a
`OROLOGIO_V`". (`OROLOGIO_V` è 4 dal riordino del 2026-09-15.) Fino ad allora un bump serviva solo ad aggiungere un campo (i
chili, fra la 1 e la 2) senza toccare gli indici, quindi accettare anche le
versioni più vecchie era innocuo. Il riordino di quel giorno — Leg press e Leg
extension spostate, scambiando posto con altri esercizi dello stesso tipo
"serie" — ha reso il caso diverso: un orologio rimasto alla versione 2 manda
indici che *esistono ancora* nella scheda nuova ma *puntano a un altro
esercizio*, e i controlli di `leggiOrologio()` (tipo giusto, numero di serie in
range) non se ne accorgono perché tecnicamente sono tutti validi. Restringere
al match esatto è l'unico modo per far apparire "l'app dell'orologio è di una
versione diversa, aggiornala" invece di spuntare in silenzio l'esercizio
sbagliato. **Ogni volta che riordini `SCHEDA` scambiando fra loro due esercizi
dello stesso tipo, bump di `OROLOGIO_V` è obbligatorio**, non solo quando cambi
il formato del messaggio.

Regole decise con lui:
- la seduta del polso **sostituisce** quella del telefono, con un riquadro di
  conferma che dice quante spunte verrebbero perse. Due elenchi mezzi pieni non si
  fondono da soli senza inventare;
- **i chili si regolano sull'orologio con − e +** (deciso il 2026-08-26, ribaltando
  la scelta del giorno prima: provandola, Manlio ha detto subito che senza chili
  l'app da polso non serve — in palestra devi sapere quanto mettere sulla macchina).
  Vivono nelle SharedPreferences del polso, il reset della seduta **non li tocca**
  (sono la regolazione delle macchine, non la seduta) e viaggiano nel messaggio:
  per gli esercizi spuntati vincono su tutto. Dove mancano resta la vecchia regola,
  il carico di riferimento (`pesiRif`) — senza quel fallback una seduta dal polso
  peserebbe zero e i Carichi resterebbero vuoti: trovato provando;
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
- **`Salute.kt` è la parte di Google Health**, e gira **solo sul telefono**: vedi
  “Gli allenamenti in Google Health”. Non tocca niente di quello che si vede al
  polso, e usa l'API di sistema di Android 14, non una libreria: la dipendenza
  resta una sola.
- **Lo stesso APK si installa anche sul telefono** (`uses-feature ... required="false"`).
  Sul telefono non c'è nessun polso a cui mandare la seduta, quindi apre la Palestra
  direttamente: è così che si prova tutta la catena senza orologio e senza cavi.
- I chili sull'orologio hanno la loro copia. **Dal 2026-09-29 sul polso si
  leggono soltanto**: il − e il + non ci sono più, li ha fatti togliere Manlio
  dopo la prima seduta vera ("se li devo cambiare ricambio dal telefono").
  Erano anche loro a uscire dal bordo tondo — il + si vedeva a metà. Arrivano
  dal telefono con "Manda i carichi all'app": in Impostazioni della Palestra web,
  apre `palestra://carichi?d=1:40,3:60,...` (stesso formato indice:chili del
  messaggio di ritorno). L'APK — registrato su quello schema nel manifesto — li
  salva e, se gira sul telefono, li **inoltra all'orologio** con
  `RemoteActivityHelper`. È l'unico canale telefono→polso, e trasporta solo i
  carichi, una volta: le sedute continuano ad andare nel senso opposto.
  Manlio l'ha chiesto vedendo i trattini: "non riesce a caricare i chili
  dell'ultima volta". **Adesso è l'unico modo di metterli**, quindi se un
  giorno questo canale si rompe l'app da polso resta senza chili: non
  toglierlo senza rimettere prima un modo di scriverli sul polso.
  Sul polso i chili stanno in `kg_<indice>`, quindi **un riordino li lascia
  attaccati alla posizione, non all'esercizio**: dopo aver installato un APK
  riordinato vanno rimandati dal telefono con "Manda i carichi all'app" (fatto
  il 2026-09-15), oppure ritoccati con − e +. Sul telefono il problema non
  esiste, lì i pesi sono salvati per nome.
  **Questo canale non è versionato**, a differenza del messaggio di ritorno.
  Un riordino di `SCHEDA` gli fa lo stesso scherzo — un orologio non
  aggiornato può ricevere il peso giusto sull'esercizio sbagliato — ma qui il
  danno è più piccolo: è solo un numero già scritto che lui vede e corregge
  con − e +, non una spunta che si registra da sola. Non gli ho messo una
  versione per questo; se un giorno il danno sale (per esempio se i chili
  cominciassero a scrivere qualcosa da soli), va aggiunta anche qui.
- Sulla schermata finale c'è **"Azzera la seduta"** con doppia conferma (chiesto il
  2026-08-26): azzera spunte e cardio, **non i chili**. E il tocco a vuoto su quella
  schermata non fa niente: manda solo il tasto.

**Il 2026-09-29, dopo la prima seduta vera al polso, la ripaginazione per lo
schermo tondo.** Il quadrante è rotondo e stringe in alto e in basso: tutto
quello che era scritto con misure fisse finiva oltre il bordo. Le regole che
ne restano, da non perdere al prossimo ritocco:
- **le misure non si scrivono a mano.** La pastiglia di una serie si calcola
  da `larghezzaUtile()` (la larghezza vera dello schermo meno 14dp per lato)
  divisa per il numero di serie: così non esce né su un quadrante piccolo né
  con un esercizio da 4 serie. Verificato col conto su 200dp e 223dp, le due
  misure del Pixel Watch 3;
- **il nome dell'esercizio si rimpicciolisce da solo** (`titolo()`, una riga
  sola): "Vertical traction" è lungo il doppio di "Low row";
- **le scritte si tengono il loro margine, le pastiglie no.** Il bordo della
  colonna è stretto (14dp) perché le pastiglie stanno a metà schermo, dove il
  tondo è largo; sono le singole scritte ad avere un margine in più, perché
  stanno in alto e in basso dove si stringe;
- **quattro righe per schermata e non una di più.** Ogni riga aggiunta
  spingeva qualcosa fuori;
- **frecce ‹ › in fondo**, perché la sfogliata verso destra sull'orologio la
  prende il sistema per uscire dall'app e indietro non si tornava. Chiesto da
  lui: in palestra non fa sempre gli esercizi nell'ordine della scheda. Il
  numero di pagina sta fra le due frecce, non più in cima.
- `vaiA()` è **l'unico posto da cui si cambia pagina** (frecce, sfogliata,
  avanzamento automatico): ferma il recupero e salva dove sei. Dalla
  schermata della seduta rimasta indietro non si sfoglia via, o un
  allenamento intero sparirebbe con un dito storto.
- **Lo schermo resta acceso solo mentre scorre il recupero** (`FLAG_KEEP_SCREEN_ON`
  messo in `avviaTimer()` e tolto in `fermaTimer()`). Prima era acceso per tutto
  il tempo che l'app era aperta e svuotava la batteria in una seduta: "questo non
  me lo posso permettere". Durante il recupero serve, è l'unico momento in cui
  guardi senza toccare.
- **La pagina in cui sei viene salvata** insieme alla seduta: se il sistema
  chiude l'app quando lo schermo si spegne, riaprendola torni sull'esercizio
  che stavi facendo e non in testa alla scheda.
- La seduta resta nelle SharedPreferences finché non è stata mandata: al cambio di
  giorno, se non è partita, viene riproposta invece che buttata.

**Il 2026-10-06 la pagina dell'esercizio è stata rifatta sul suo disegno.**
Manlio ha fatto uno schizzo del quadrante tondo con il segmento in basso
tagliato in due dalle frecce, e ha chiesto: via le scritte piccole di servizio
("tieni premuto" e simili), le ripetizioni dentro i cerchietti al posto di
1 2 3 4, via la riga "3 × 12" che a quel punto ripeteva, i chili più grossi e
al centro. Cosa ne è rimasto nel codice:
- **nei cerchietti c'è il numero di ripetizioni**, non il numero della serie.
  Il numero della serie non serviva: la pastiglia è in posizione e si conta da
  sola. Le ripetizioni invece sono l'unica cosa che in palestra devi sapere;
- **i chili sono un solo pezzo di testo** (`kgGrandi()`), con il numero grande
  e `kg` reso al 40% da uno `RelativeSizeSpan`. Non sono due righe: lui ha
  chiesto `kg` "molto più piccolo", e due View separate non si allineano mai
  bene sul tondo. `etichettaKg()` non c'è più;
- **sotto c'è l'ora, in rosso e con i secondi** (`orologioDaPolso()` e
  `oraDiAdesso()`, `HH:mm:ss`): l'ha chiesta per sapere l'ora senza uscire
  dall'app. Va avanti con un `Handler` che ribatte ogni secondo (`ticOra`),
  avviato in `onResume()` e **tolto in `onPause()`**; `mostra()` azzera
  `oraVista` per prima cosa, altrimenti il battito scriverebbe dentro una
  View già buttata via;
- **le frecce sono due mezzelune che riempiono il segmento in basso**
  (`barraFrecce()`, alta il 22% dello schermo, ancorata in basso, con una
  linea di 1dp sopra e un divisorio di 1dp in mezzo). Sono bersagli enormi, ed
  è il punto: si premono con le mani sudate. Il numero di pagina è sparito da
  fra le frecce;
- **una freccia spenta resta `isClickable`**: così il tocco se lo prende lei e
  non arriva a quello che sta sopra. Senza, premere "avanti" sull'ultima
  pagina spuntava una serie.
Le misure sono tutte calcolate (`altezzaBarra()`, `spazioBarra()`), mai scritte
a mano: vale la regola del 2026-09-29.

**L'icona è nera con il bilanciere rosso** — `drawable/ic_sfondo.xml` (nero),
`drawable/ic_pesi.xml` (il bilanciere) e `mipmap-anydpi-v26/ic_launcher.xml`
che li mette insieme come icona adattiva, `monochrome` compreso. Il 2026-09-29
aveva chiesto **lo sfondo bianco**; il 2026-10-06 ha cambiato idea — "tutta
nera con i pesi rossi al centro" — ed è questa quella pubblicata. Il
motivo per cui prima "stava male" era un altro: l'icona era di tipo vecchio
(una `drawable` sola) e Android ci metteva sotto un piatto bianco di sistema.
Il bilanciere sta dentro la zona sicura (66 su 108), o il ritaglio tondo del
telefono gli mangia le estremità.

**Quella pagina non l'ho mai vista su uno schermo vero**: le misure sono
calcolate col conto, non guardate. Se dice che qualcosa esce dal bordo o sta
scomodo, i numeri da toccare sono `altezzaBarra()`, la dimensione in
`kgGrandi()` e il massimo di `titolo()` (abbassato da 20 a 18sp per far
posto all'ora).

### Da fare, chiesto il 2026-09-29 e rimandato da lui

Sono tre cose che Manlio ha visto usando l'app davvero e che ha rimandato
("alla prossima"), non perché non contino: quel giorno non aveva tempo di
rifare l'installazione, che è l'unico modo di provare una modifica al polso.

1. **I carichi che arrivano dal telefono devono sostituire tutto, non
   aggiungersi.** Lui aveva un Adductor a 2,5 kg sull'orologio — un valore
   messo col + quando il + c'era ancora — e "Manda i carichi all'app" non
   l'ha corretto. La ragione sta in `carichiOrologioURL()`: manda **solo gli
   esercizi per cui il telefono ha un numero maggiore di zero**, quindi un
   esercizio senza peso non compare nel messaggio e `gestisciIntent()`, che
   scrive solo le coppie che riceve, lascia intatto quello che c'era.
   Finché sul polso c'erano − e +, un numero sbagliato si correggeva lì;
   **da quando li abbiamo tolti non c'è più modo**, ed è un buco aperto dal
   cambiamento del 2026-09-29. Il telefono conosce i pesi di tutte le
   macchine, quindi il suo messaggio è la verità completa: `gestisciIntent()`
   deve **svuotare `kg` prima di applicarlo**, così gli esercizi non nominati
   tornano al trattino. **Attenzione a non farlo quando il messaggio è
   malformato o vuoto**, o un tocco sbagliato azzererebbe tutti i carichi.
   Resta un dubbio da sciogliere con lui: se quel 2,5 l'ha visto **dopo** la
   disinstallazione di quel giorno, la causa è un'altra, perché disinstallare
   porta via tutti i chili.
2. ~~L'icona dell'app va rifatta con lo sfondo bianco~~ — **fatta il
   2026-10-06**, ma nera con i pesi rossi: vedi qui sopra.
3. **La vibrazione di fine recupero se esce dall'app.** Oggi il recupero è un
   `CountDownTimer`, che vive solo finché il processo è sveglio: uscendo
   dall'app lo schermo si spegne, l'orologio può addormentarsi e la vibrazione
   arriva tardi o non arriva. Lui ha detto che non ha motivo di uscire durante
   il minuto, quindi **non farlo finché non lo chiede**; se servirà, la strada
   è una sveglia di sistema (`AlarmManager`), non tenere acceso lo schermo.

**Il 2026-09-29 l'app è stata installata davvero su un Pixel Watch 3** e tutta
la catena ha funzionato: carichi dal telefono al polso, spunte, seduta di
ritorno. L'installazione si fa dal computer con `adb` (opzioni sviluppatore →
Debug tramite Wi-Fi → `adb pair` con codice, poi `adb connect`, poi `adb install`).
Tre cose sono costate tempo e ricapiteranno: **`adb connect` da solo non basta
la prima volta**, ci vuole prima `adb pair` con il codice a sei cifre;
se l'orologio compare due volte in `adb devices` (una per indirizzo, una per
nome) l'installazione va indirizzata con `adb -s <indirizzo> install`; e
**ogni APK compilato da GitHub è firmato con una chiave diversa**, quindi
aggiornare sopra quello installato fallisce con `INSTALL_FAILED_UPDATE_INCOMPATIBLE`
e bisogna disinstallare prima (`adb uninstall it.manlio.palestraorologio`),
**perdendo i chili sul polso**, che vanno rimandati dal telefono. Si
risolverebbe firmando sempre con la stessa chiave, ma vorrebbe dire mettere un
file di firma in un repository pubblico: gliel'ho proposto il 2026-09-29 e non
ha ancora deciso — **non farlo senza il suo sì**.
La procedura completa è scritta in una pagina a parte:
https://claude.ai/artifact/UF1fk7CdumhiUhYXkoMf6d

Altre tre cose imparate reinstallando il 2026-10-06, da ripetere ogni volta:
- **la porta cambia** ogni volta che spegne e riaccende *Debug tramite Wi-Fi*,
  l'indirizzo no. Quindi il comando `adb connect` va riscritto con la porta che
  l'orologio mostra **in quel momento** (quel giorno era 45539, il giorno prima
  33855);
- **i comandi con l'indirizzo di esempio dentro non si danno**. Il 2026-09-29
  si è perso mezz'ora perché aveva copiato dalla mia pagina `192.168.1.47`
  invece del suo `192.168.1.92`, e l'errore che esce (`cannot connect`) sembra
  un guasto dell'orologio. Nella pagina della procedura ci sono dei
  segnaposto da riempire, non indirizzi veri: tienili così;
- **il file scaricato di nuovo non sovrascrive il vecchio**: Chrome lo chiama
  `palestra-orologio(1).apk`, e `adb install palestra-orologio.apk` installa
  di nuovo quello di prima. Digli di cancellare il vecchio prima di scaricare.

**La compilazione la fa GitHub** (`.github/workflows/orologio.yml`) a ogni modifica
dentro `orologio/`, e pubblica sempre allo stesso indirizzo:
`https://github.com/manliograndi-del/palestra/releases/download/orologio/palestra-orologio.apk`
È l'unico modo di avere un APK da questa sessione. Se il file non si aggiorna, guarda
i log dell'azione prima di dare la colpa al telefono.

**Il 2026-09-15 l'azione si è rotta da sola**, senza che nessuno l'avesse toccata:
`android-actions/setup-android` installa di suo il vecchio pacchetto `tools` dell'SDK,
che Google ha ritirato, e si fermava con "Failed to find package 'tools'" prima ancora
di compilare. Ora l'azione riceve `packages: 'platform-tools'` e i pezzi che servono
davvero arrivano dal passo successivo. Se un giorno si ferma di nuovo in quel punto,
**non è il codice Kotlin**: è un pezzo dell'SDK sparito dall'archivio di Google.

## Aspetto

**Rifatto il 2026-08-18 sul linguaggio visivo di Virgin Active**, su richiesta di
Manlio e partendo dalle schermate della loro app. Prima seguiva la famiglia visiva del
Diario: quella parentela non c'è più, e il Diario è rimasto chiaro e sobrio.

Nero, bianco, rosso. Palette in `:root`:
`--carta #000` · `--superficie #151515` · `--superficie2 #232323` · `--inchiostro #FFF`
`--tenue #9A9A9A` · `--linea #2E2E2E` · `--rosso #E4002B` (il rosso Virgin) ·
`--su-rosso #FFF` · `--raggio 16px`

`--blu`, `--senape` e `--verde` **non esistono più**: erano rimasti a puntare al
rosso dopo il cambio di aspetto, e il 2026-08-29 non li usava più nessuno. Se ti
serve un accento, è `--rosso`, ed è l'unico.

**Il rosso è l'unico accento e significa "azione" o "fatto".** Non spenderlo per
decorare, o smette di voler dire qualcosa. Le serie completate sono pastiglie rosse
piene (prima erano verdi). Titoli in maiuscolo pesante, pulsanti a pastiglia
(`border-radius:99px`), riquadri a 16px, barra in basso con la voce attiva su fondo
rosso pieno.

**Il 2026-10-06 Chrome si è impuntato a dire che la Palestra era installata**
quando Manlio l'aveva disinstallata: non riusciva più a rimetterla sulla
schermata Home, e l'unica cosa che gli offriva era “Crea scorciatoia”, che fa
l'icona col tondino di Chrome sopra. Un riavvio completo del telefono non è
bastato, e in Impostazioni → App la voce *Palestra* non c'era davvero: era
rimasto appeso **il ricordo dentro Chrome**, non l'app.

Chrome riconosce un'app installata dal campo `id` del manifest, non
dall'indirizzo. Quindi la via d'uscita è **cambiare quel nome d'identità**: con
un `id` nuovo l'app diventa una che non ha mai visto e torna a proporre
l'installazione vera. Da `"/palestra/index.html"` si è passati a
`"/palestra/app"`. **Non tocca i dati**: le sedute stanno attaccate
all'indirizzo del sito, non a quel nome, e un cambio di `id` non le sfiora.
Se ricapita si può rifare, ma **una volta sola per volta**: cambiarlo mentre
l'app è installata ne fa comparire due.
Attenzione: il service worker serve il manifest **prima dalla cache**, quindi
un `id` nuovo non si vede finché non si alza anche il numero di cache in
`sw.js`. Le due cose vanno insieme.

Nel `manifest.webmanifest` i colori della schermata di avvio erano rimasti
quelli chiari del Diario fino al 2026-09-02: aprendo l'app installata lampeggiava
un rettangolo color crema prima del nero. Adesso sono neri tutti e due. Se
ritocchi la palette, quel file non se ne accorge da solo.

**Niente font di Virgin**: è un carattere loro e caricarlo significherebbe dipendere
dalla rete, che in palestra non c'è. Si usano i caratteri di sistema spinti su peso
(800–900) e spaziatura negativa.

L'elemento centrale restano le pastiglie delle serie: una per serie, col numero di
ripetizioni dentro. Il timer sale dal basso come riquadro staccato.

## Prima di chiudere una sessione

1. **Alza il numero di versione della cache in `sw.js`** (`palestra-v11` → `palestra-v12`).
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
