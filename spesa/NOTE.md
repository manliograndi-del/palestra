# Spesa — offerte dei supermercati

Progetto separato dalla Palestra, chiesto da Manlio il 2026-09-02.
Vive in questa cartella per non toccare `index.html`, che è l'app della palestra.

## Cosa vuole

**Non vuole che sia Claude a cercare i prodotti.** L'ha detto chiaramente a metà
lavoro: gli bastano **i volantini scaricati** da guardare da solo e uno strumento
per cercare a modo suo. La ricerca la fa lui.

**L'Excel non serve più**: il 2026-09-02 ha detto «il file Excel puoi anche non
farlo». `strumenti/build_xlsx.py` e `cache_vals.py` restano lì e funzionano, ma
non fanno più parte della consegna. Non rifarlo se non lo richiede.

**Vuole una pagina con dodici prodotti a scelta**, da cambiare e da allungare
con un «+». È la forma finale del lavoro.

**Zona:** Torino, quartiere Santa Rita (corso Siracusa). Il civico non serve.
Di Mercatò ci sono punti vendita vicini: via Filadelfia, via Gaidano, corso
Brunelleschi.

**Insegne:** MD · Eurospin · Carrefour Iper · Bennet · Ipercoop · Lidl
Il 2026-09-02 ha detto di **togliere Carrefour Market e mettere Ipercoop**.
Mercatò resta nell'elenco ma non si riesce a scaricare (sotto il perché).

**Prodotti che gli interessano sempre:** carne di bue in confezioni grandi,
tonno, salmone. Resta da chiarire quale salmone (affumicato, fresco o surgelato):
gliel'ho chiesto e non ha ancora risposto.

## Com'è andata il 2026-09-02

Consegnati: 8 PDF (277 pagine), `offerte-supermercati-torino.xlsx` con tre
fogli — guida, 24 prodotti suoi col prezzo al chilo, indice cercabile di tutte
le pagine — e **una pagina web pubblicata**, che è quello che ha chiesto per
ultimo: voleva un indirizzo da mandare **anche a sua moglie, da un altro posto**.

## L'indirizzo che conta è il sito, non l'artifact

Il 2026-09-03 Manlio ha detto: «questa pagina non deve essere un artefatto tuo,
voglio l'indirizzo internet della pagina». Ha ragione, e c'era già il posto
giusto: il sito della Palestra su GitHub Pages. La Spesa sta in una cartella
accanto.

    https://manliograndi-del.github.io/palestra/spesa/     ← QUESTO
    https://claude.ai/code/artifact/a6782ea0-6822-4026-87e7-705012966595  (secondario)

Il sito lo pubblica il ramo **`main`**, cartella `spesa/`: per mandare in linea
una modifica bisogna portarla lì, non basta il ramo di lavoro. **Toccare solo
dentro `spesa/`**: `index.html`, `sw.js` e il resto dell'app della palestra
stanno alla radice e non si toccano mai.

**La rinuncia, scelta da lui sapendola:** sul sito non c'è nessun server, quindi
la lista torna a essere una per telefono. La lista condivisa vive solo
sull'artifact. Se dicono che le liste non combaciano, è questo, non un baco.

### `CONDIVISA`: chi comanda, la pagina o il browser

Ogni copia porta una costante `CONDIVISA`. Dove è **vera** (solo l'artifact)
comanda la lista incorporata nella pagina: è quella che vedono tutti e viene
aggiornata ripubblicando. Dove è **falsa** (sito e file) comanda quella salvata
nel browser di chi apre, e la incorporata vale solo come punto di partenza.

Senza questa distinzione **sul sito le modifiche sparivano a ogni
ricaricamento**: la lista incorporata non è vuota, quindi vinceva sempre lei,
e lì non c'è niente che possa aggiornarla. Trovato rileggendo, prima che se ne
accorgesse Manlio.

**L'ordine delle sostituzioni è delicato.** Sia `riempi()` in Python sia
`documento()` in JavaScript devono riempire `__TEMPLATE__` **per ultimo**:
appena infilato, il modello porta dentro una copia di tutti gli altri
segnaposto, e da quel momento la sostituzione dopo trova quelli invece dei
veri. Successo davvero con `__CONDIVISA__`: veniva riempito dentro la copia e
la pagina rigenerata restava con un `__CONDIVISA__` scoperto, cioè rotta. Il
controllo in Node che rigenera tre volte e guarda cosa esce è l'unico modo per
accorgersene senza mandarla in mano a loro.

`pagina.py` sforna tre versioni dalla stessa fonte:

| file | dove va | differenza |
|---|---|---|
| `out/sito.html` | `spesa/index.html`, il sito | 219 KB, niente copia di sé (lì non potrà mai ripubblicarsi), ha manifest e service worker |
| `out/pagina.html` | l'artifact | 445 KB, con la copia di sé per la lista condivisa |
| `out/spesa-da-sola.html` | da mandare per posta | come il sito ma tutto in un file |

### MAI scrivere il tag di chiusura dello script per esteso

Il guaio peggiore di tutta la sessione, il 2026-09-03. In un **commento** dentro
lo script c'era il tag di chiusura scritto per esteso. Il browser lo cerca nel
testo e non gli importa che sia dentro un commento: ha chiuso lo script a metà.
**Tutte e tre le pagine sono uscite morte** — quella sul sito, quella di Claude
e il file — e quella di Claude era già in mano a Manlio.

Da fuori sembravano perfette: intestazione, riquadri, testi, tutto al posto
giusto. Mancavano solo i bottoni dei prodotti e i prezzi, perché il pezzo di
programma che li disegna stava dopo il taglio. È esattamente il tipo di guasto
che non si vede rileggendo il codice: l'ha visto Manlio aprendo il sito.

`pagina.py` adesso **non consegna un file senza averlo controllato**: spezza
ogni pagina dove la spezzerebbe il browser, passa ogni pezzo a `node --check` e
verifica che quello grosso contenga `function disegna`. Se non torna, si ferma
con un errore invece di scrivere il file. Provato rimettendo il guasto apposta:
lo prende.

Se devi nominare quel tag in un commento, scrivilo spezzato o giragli intorno a
parole. Vale anche per le stringhe: `racchiudi()` in Python e `documento()` in
JavaScript spezzano ogni `</` in `<\/` proprio per questo.

### L'iniziale maiuscola, e perché non bastava cambiare i dati

Manlio ha aggiunto quattro prodotti scrivendoli minuscoli e poi ha chiesto la
maiuscola. Io li ho messi maiuscoli in `lista.py` — e lui **continuava a
vederli minuscoli**, giustamente: sul sito comanda la lista salvata nel suo
browser, non quella incorporata nella pagina. Qualunque cosa pubblichi, i suoi
nomi restano i suoi.

Quindi la maiuscola la mette **la pagina**, non i dati: `maiuscola()` in
`pagina.py` agisce quando si aggiunge o si rinomina un prodotto **e** su ogni
lista letta dalla memoria, così le liste già salvate si sistemano da sole senza
che nessuno tocchi niente.

**Solo la prima lettera, e in JavaScript.** `text-transform: capitalize` del CSS
maiuscolizza ogni parola e storpierebbe «Olio d'oliva» in «Olio D'oliva».

La regola generale, che vale per ogni cosa del genere: **se il cambiamento deve
vedersi anche su una lista già salvata, va fatto nel codice della pagina, non
nei dati di partenza.** Altrimenti lo vedono solo i telefoni nuovi.
`strumenti/prova-maiuscole.js` prova esattamente questo: finge una lista salvata
coi nomi minuscoli e controlla come esce.

### `prova.js`: aprire la pagina per davvero, sempre

Il 2026-09-03 la pagina è uscita rotta **tre volte di fila**, e ogni volta
sembrava a posto da fuori:

1. un commento conteneva il tag di chiusura dello script scritto per esteso →
   script tagliato a metà, niente bottoni;
2. il blocco che accende la lista condivisa stava **prima** di
   `let lista = leggiLista()` → chiamava `disegna()` quando `lista` non esisteva
   ancora e moriva lì;
3. una mia sostituzione di testo aveva **cancellato `pagineDi`**: avevo
   rimpiazzato un pezzo di sorgente delimitandolo da due commenti, e quella
   funzione stava in mezzo. I bottoni comparivano, cliccandoli non usciva
   niente.

Nessuno dei tre si vedeva rileggendo il codice, e il controllo di sintassi ne
prendeva solo il primo. Li ha visti Manlio, aprendo il sito. Tre volte.

`strumenti/prova.js` apre la pagina in un browser finto (jsdom), **clicca ogni
bottone** e pretende che escano prezzi o pagine. Va lanciato su tutte e tre le
copie **prima di pubblicare**, sempre:

    cd /tmp/dom && npm install jsdom
    node prova.js .../out/sito.html
    node prova.js .../out/pagina.html
    node prova.js .../out/spesa-da-sola.html

Esce con errore se qualcosa non va. Il controllo dentro `pagina.py` (node
--check) resta, ma da solo non basta: una pagina può essere sintatticamente
perfetta e muta.

**Attenzione alle sostituzioni di testo su `pagina.py`**: delimitare un pezzo
da rimpiazzare con due commenti lontani cancella tutto quello che ci sta in
mezzo. È successo. Meglio sostituzioni corte e mirate, e comunque `prova.js`
dopo.

### Il service worker della Spesa è obbligatorio

`spesa/sw.js` non è un lusso. Quello della Palestra sta alla radice, il suo
scope copre anche `/palestra/spesa/`, e **senza rete servirebbe l'index.html
della Palestra al posto della Spesa** (guarda il suo `catch`: ricade su
`./index.html`). Uno registrato più in basso vince sul suo scope, quindi questo
toglie di mezzo il problema — e in più tiene la Spesa disponibile in negozio,
dove il segnale è pessimo. Se lo modifichi, **alza il numero di cache**
(`spesa-v1`), come per la Palestra.

Le icone sono un carrello rosso su fondo bianco, di proposito diverse da quelle
della Palestra che sono rosse piene: sulla schermata Home non si confondono.

**La pagina si chiama «Spesa»**, chiesto il 2026-09-03: è il `<title>`, cioè il
nome che si legge sotto l'icona quando la si installa sulla schermata Home del
telefono. Non cambiarlo per farlo più descrittivo — è il nome dell'app per
loro. L'icona è il carrello 🛒 e resta quella: si ritrova per l'icona.

**Le pagine pubblicate nascono private**: perché la moglie la apra, lui deve
condividerla dal menu della pagina stessa. Gliel'ho detto; se dice che lei non
la vede, è quasi sicuramente quello.

**La moglie non vive con lui** (detto il 2026-09-02): apre da un'altra casa, da
un altro telefono, e non ha niente di installato. Per questo esiste anche
`out/spesa-da-sola.html`, che `strumenti/pagina.py` scrive accanto alla pagina
pubblicata: è lo stesso identico contenuto ma con `<!doctype>`, `<head>` e
`<body>` attorno, perché quelli **il servizio li mette da sé alla pagina
pubblicata e il file grezzo non ce li ha**. Quel file si apre a doppio clic,
senza account e senza rete — i caratteri di Google non si caricano e scende ai
caratteri di sistema, tutto il resto funziona perché dati e codice sono dentro.
Si manda per posta o WhatsApp. **Non si perde niente rispetto al link**: la
lista sta comunque nel browser di chi apre, quindi era già una copia a testa.

La pagina la genera `strumenti/pagina.py` da `strumenti/dati.py` (i prezzi letti
a mano) e `strumenti/lista.py` (i dodici prodotti di partenza). Per aggiornarla
si ripubblica **lo stesso percorso di file** in una sessione che l'ha già
pubblicata, oppure si passa l'URL qui sopra come `url`: altrimenti esce un
artifact nuovo con un indirizzo diverso e il link della moglie muore.

### Com'è fatta la pagina, e perché

Manlio ha provato la prima versione e l'ha bocciata: «è brutto e non è comodo
da navigare», «così non si può vedere». Due cose da non rifare:

- **Niente tema scuro.** Il suo telefono è in modalità notte e la pagina gli si
  apriva nera. Adesso c'è **un solo tema chiaro**, sfondo bianco, e nel CSS
  **non esiste** il blocco `prefers-color-scheme: dark`. Se lo rimetti, si
  riapre nera da lui. Lo sfondo è dichiarato su `html` e su `body`, perché
  senza, la pagina prende quello di chi la ospita.
- **I prodotti sono bottoni in cima**, dentro una barra `sticky`: se ne tocca
  uno e la lista di sotto si riempie subito, già ordinata dal meno caro. Prima
  erano schede da aprire e chiudere una alla volta e per arrivare al tonno
  bisognava scorrere. Il «+ aggiungi» è l'ultimo bottone della fila.

Bersagli grandi (44-46 px) come nella Palestra: si usa in piedi, in negozio.

### La lista adesso vive DENTRO la pagina pubblicata

Cambiata il 2026-09-03. Manlio ha chiesto che la lista sia una sola per lui e
sua moglie, che ognuno possa aggiungere e togliere, e che le sue modifiche
arrivino anche a me senza doverle reincollare.

Si usa la capacità **`artifact`**, non `db`: `db` avrebbe reso l'artifact
interno all'organizzazione e la moglie non sarebbe più entrata (vedi sotto). Con
`artifact` la pagina, quando qualcuno tocca la lista, **ripubblica se stessa**
con la lista nuova dentro, e ogni schermo aperto si ricarica su quella.

**Il documento contiene una copia di se stesso.** `TEMPLATE` è il documento
intero con i due segnaposto `__LISTA__` e `__TEMPLATE__` ancora dentro, non
risolti: è quello che permette alla generazione dopo di rifare la stessa cosa.
`documento()` riempie **prima la lista e poi il modello** — al contrario, il
modello appena infilato porterebbe dentro un altro `__LISTA__` e verrebbe
riempito quello sbagliato.

Tre trappole, tutte già pagate:

1. **I segnaposto compaiono due volte**: quello vero in cima allo script e la
   stringa dentro `documento()` che serve a sostituirlo. `riempi()` in
   `pagina.py` usa `count=1` e JavaScript si ferma da solo alla prima. Senza,
   `documento()` si rompe e il file cresce di 200 KB inutili.
2. **`</script>` dentro la stringa chiuderebbe il tag per davvero**: si scrive
   `<\/`. Lo fanno sia `racchiudi()` in Python sia `documento()` in JavaScript,
   e devono restare d'accordo.
3. **Il documento ripubblicato deve essere intero** (doctype, head, body), che
   invece al file dato allo strumento Artifact li mette il servizio. Per questo
   il modello è `COMPLETO` e non `CORPO`.

Il punto fisso è provato: rigenerando tre volte il modello resta identico e il
documento non cresce (445 KB). Se tocchi questa parte, riprova così — è un
controllo che si fa in Node in un minuto e ti risparmia una pagina rotta in mano
a loro.

Chi apre in sola lettura riceve `not_writer`: le sue modifiche restano nel
browser e la riga di stato in cima glielo dice. La stessa cosa vale per il file
`spesa-da-sola.html`, dove `window.claude` non esiste proprio.

### `lista_attuale.py`: non cancellargli la lista

**Il pericolo grosso di tutta questa architettura.** L'aggiornamento
settimanale rigenera la pagina; se ripartisse da `lista.py` cancellerebbe la
lista che si sono fatti loro. Quindi prima si legge la pagina viva
(strumento Artifact, action "read"), si passa a `lista_attuale.py`, che scrive
`lista-attuale.json`, e `pagina.py` riparte da quello. `lista.py` serve solo la
prima volta.

Se la lista non si riesce a leggere, **fermarsi**: meglio prezzi vecchi che una
lista cancellata.

### Perché NON si è usata la memoria sul server (`db`)

`db` sarebbe più semplice da scrivere, ma **un artifact che dichiara `db`
diventa interno all'organizzazione** e non si condivide fuori. Sul piano Pro di
Manlio l'organizzazione è lui solo: la moglie resterebbe fuori, che è la cosa
che ha chiesto fin dall'inizio di poter fare. Per questo si è presa la strada
più scomoda della pagina che si ripubblica.

`localStorage` (chiave `spesa.lista.v1`) resta solo come ripiego, per la copia
che gira come file. Letture e scritture in try/catch: in navigazione privata la
memoria può mancare e la pagina deve funzionare lo stesso.

**Il baco che ha fatto venire fuori tutto**: Manlio aveva tolto la carta
igienica e se la ritrovava. Non era un baco nel togliere (provato in Node,
funziona): aveva **due copie**, il link e il file, ognuna con la sua memoria.
Togliere in una non toccava l'altra. Con la lista dentro la pagina il problema
non esiste più.

### Tutte e dodici le categorie hanno i prezzi

Il 2026-09-02 Manlio ha chiesto i prezzi anche per le nove categorie che avevo
messo io. Adesso `dati.py` ha **68 righe su 12 categorie**, tutte lette
guardando le pagine — nessuna inventata, nessuna dedotta dall'OCR.

Ogni prodotto di `lista.py` ha il campo `cat` che punta alla categoria di
`dati.py`. Il legame è esplicito e serve: cercando per testo, «olio» pescava i
tonni all'olio d'oliva e sembravano offerte sull'olio. Un prodotto aggiunto a
mano dalla pagina non ha categoria, ma se quello che scrive combacia col nome o
con una parola di uno dei dodici, `costruisci()` glielo attacca da sola.

**Le unità non sono tutte il chilo.** `UNITA` in `dati.py` dice per ogni
categoria come si confronta: chilo per carne, tonno, salmone, caffè, pasta,
pollo e formaggio; **litro** per latte e olio; **uovo**, **rotolo** e
**lavaggio** per le altre tre. Al chilo il detersivo darebbe un numero vero e
inutile. I detersivi stanno sotto i 20 centesimi a lavaggio, per questo `eur()`
nella pagina usa tre decimali sotto l'euro: con due diventavano tutti «0,14 €».

Due righe confrontano di proposito cose non identiche, e lo dicono nelle note:
l'ammorbidente Coccolino sta fra i detersivi (si usa in aggiunta, non al posto)
e il caffè in capsule sta col macinato (al chilo costa cinque volte tanto). E la
carta igienica Regina è «4 rotoloni pari a 12 rotoli»: il conto usa i 12
dichiarati sul pacco, e la nota dice quanto fa sui 4 veri.

### Più nomi per lo stesso prodotto

Chiesto da Manlio il 2026-09-02: «ci sono delle cose che possono essere salvate
con più di un nome». È il motivo per cui i dodici di partenza avevano già una
lista di `parole` — il volantino scrive «bovino» dove lui dice carne di bue, e
«lavatrice» dove dice detersivo. Fino a quel giorno però quel meccanismo era
solo mio: nella pagina non si vedeva e non si poteva usare.

Adesso nel campo si scrivono **più nomi separati da virgola** e `costruisci()`
li spezza: il primo diventa l'etichetta del bottone, tutti insieme sono i
termini di ricerca in OR. Gli altri nomi si vedono sotto il titolo come
pastiglie, e «Cambia nome» riapre il campo con tutti quanti dentro, separati da
virgola, così si correggono.

Se **uno qualsiasi** dei nomi scritti combacia con un prodotto di partenza (col
nome o con una delle sue parole), il prodotto si porta dietro anche la categoria
dei prezzi e le parole di quel seme. Così chi scrive «bovino» o «caffe» a mano
ritrova i prezzi invece delle sole pagine.

### `riaggancia()`: le liste salvate prima

Chi aveva già usato la pagina ha in `localStorage` una lista fatta quando solo
carne, tonno e salmone avevano i prezzi: quei prodotti sono salvati con
`cat: null` e, senza fare niente, resterebbero **senza prezzi per sempre** anche
dopo che i prezzi sono arrivati. `riaggancia()` gira su ogni prodotto letto
dalla memoria e, se non ha categoria, cerca un seme che combaci per nome o per
parola e gliela attacca — senza toccare i nomi che l'utente si è scelto. Un
prodotto aggiunto da lui che non corrisponde a niente resta senza, ed è giusto.

**Non togliere `riaggancia()`**: ogni volta che si aggiungono categorie nuove a
`dati.py` serve di nuovo, o chi ha la pagina in uso non le vede mai.

### «Ma io li ho cambiati nella pagina, perché devo ridirteli?»

Domanda di Manlio, ed è giusta. La risposta è che la lista sta in `localStorage`
sul suo telefono e **non torna indietro a chi ha fatto la pagina**: non esiste un
canale. L'unico modo per vederla davvero sarebbe la capacità `db`, che però
chiude la pagina dentro l'organizzazione e taglia fuori la moglie — vedi sopra.

Il rimedio è il riquadro **«Mandami la tua lista»** in fondo alla pagina: un
bottone impacchetta la lista in testo (nome più i nomi alternativi) e la copia,
lui la incolla in chat. È l'unico ponte che c'è, quindi **non toglierlo**: senza,
ogni volta bisogna chiedergli di riscrivere a mano quello che ha già scritto,
e infatti la seconda volta si è spazientito.

La `textarea` sotto il bottone **non è un di più**: negli artifact la scrittura
negli appunti può essere negata in silenzio, e in quel caso il testo deve
restare lì da selezionare a mano. Il `catch` scrive cosa fare.

### I volantini si rinnovano da soli

Chiesto il 2026-09-03: prendere il volantino nuovo **il giorno prima** che
scada il vecchio, e cancellare il vecchio **due giorni dopo** che è scaduto per
non farne collezione.

`VOLANTINI` in `dati.py` ha adesso un quinto campo, l'**ultimo giorno di
validità**. `pulisci.py` lo legge e dice cosa rinnovare e cosa buttare;
con `--fai` cancella davvero pagine, OCR e PDF. I due giorni di tolleranza
servono a poter ancora controllare l'offerta di ieri contro lo scontrino.

C'è una **Routine giornaliera** (`trig_01UMkRYxHXJfPBSEZLo7Snzb`, ogni giorno
alle 04:00 UTC) che apre una sessione nuova, esegue `pulisci.py` e, se non c'è
niente da fare, **si ferma senza scrivere a nessuno** — è il caso normale. Se
invece qualcosa scade, rifà il giro completo e ripubblica. Il prompt della
Routine contiene tutti i passi; è il posto da correggere se il giro cambia.

**I PDF non si accumulano da nessuna parte**: vivono nella cartella di lavoro
della sessione, che è temporanea e sparisce da sola. Le copie che ha Manlio sono
quelle nella chat, sul suo telefono, e quelle le cancella lui.

### L'aggiornamento delle offerte

Manlio ha chiesto che **anche la moglie possa aggiornare le offerte dal suo
telefono**. Non si può, e non è un limite da aggirare: aggiornare vuol dire
riscaricare i volantini, rifare l'OCR e rileggere le pagine a occhio. Una pagina
web non lo può fare — i siti dei supermercati non concedono CORS, e comunque i
prezzi grandi l'OCR non li legge.

Quello che invece funziona: **ripubblicando l'artifact, chi ha il link vede i
prezzi nuovi ricaricando**, senza che nessuno debba mandare niente a nessuno.
Nella pagina c'è una sezione che lo dice, con la data dei volantini letti
(campo `letto` in `pagina.py`, **da aggiornare a ogni giro**). Il file
`spesa-da-sola.html` invece resta fermo: è la copia di riserva, non il canale
di aggiornamento.

**Mercatò non c'è.** Il loro sito carica il volantino con JavaScript e non
espone né un PDF né le immagini delle pagine. VolantinoFacile ce l'ha ma serve
le pagine da `data.volantinofacile.it` con un identificativo per pagina non
prevedibile, e tutto ciò che non sia la copertina risponde 403. Da ritentare.

**L'Ipercoop di Torino è Nova Coop**, non la Coop nazionale: il volantino è
quello piemontese. Si prende da `novacoop.it`, che rimanda a
`negozi.volantinopiu.com/ccno-8001120004796.html` (punto vendita di via Livorno
49). Lì le pagine hanno indirizzi **prevedibili**, molto più comodi degli altri:

    https://resources.volantinopiu.it/flyer/2/8/4/8/0/pagine/<N>.jpg

cioè le cifre dell'identificativo del volantino separate da barre. Attenzione:
in quella pagina **il titolo di ogni volantino sta prima della sua immagine, non
dopo** — leggendolo al contrario ho scaricato per sbaglio il volantino degli
zaini di scuola e quello dei frigoriferi. Controllare sempre le parole che
l'OCR tira fuori: se saltano fuori «quaderni» e «zaino», è quello sbagliato.
Dei cinque volantini Nova Coop, quelli di spesa sono **Sottocosto** ed
**Extra offerte**.

**Da Ipercoop molti prezzi sono riservati ai soci Coop** e sul volantino ci sono
tutti e due, barrato e scontato. Nell'Excel e nella pagina ho messo il prezzo
soci scrivendolo nelle note, perché è quello che paga lui se ha la tessera.

## La rete

**Serve l'accesso di rete aperto.** Con l'impostazione predefinita (*Trusted*)
tutti i siti dei supermercati e tutti i portali di volantini rispondono
`EGRESS_BLOCKED`, Wikipedia compresa: passa solo la ricerca web, che gira
sull'infrastruttura di Anthropic. Manlio l'ha messa su **Full** quel giorno:
claude.ai/code → icona a nuvola sopra la casella del messaggio → ingranaggio
sull'ambiente → *Network access* → Full. **Vale dalla sessione dopo, non su
quella in corso.**

## Come si rifà

Gli strumenti sono in `strumenti/`. Serve `pip install pillow openpyxl` e
`apt-get install -y tesseract-ocr tesseract-ocr-ita`.

1. `scarica.sh` — pagine dei volantini da anteprimavolantino.it
2. `leggi.sh` — OCR di ogni pagina
3. `indice.py` — da OCR a `indice.json`
4. `pdf.py` — un PDF per volantino
5. `build_xlsx.py` — l'Excel
6. `cache_vals.py` — **obbligatorio dopo build_xlsx.py**, vedi sotto

**A ogni volantino nuovo** vanno aggiornate a mano tre cose: le date dentro
`scarica.sh`, quelle dentro `indice.py`, e la tabella `DATI` di `build_xlsx.py`
(quella è compilata a occhio leggendo le pagine, non si genera da sola).

Le pagine stanno su `anteprimavolantino.it/public/uploads/AAAA/MM/` col nome
`volantino-<insegna>-<AAAA-MM-GG>-p-<NN>.jpg`. **Il numero di pagina ha 2 cifre
per certi volantini e 5 per altri**, senza una logica: si guarda l'articolo
dell'insegna e si copia il nome della prima pagina.

## Trappole trovate provando

- **LibreOffice non funziona qui**: `soffice` parte ma dà "source file could not
  be loaded" su qualsiasi file, quindi `recalc.py` della skill xlsx va sempre in
  timeout. openpyxl scrive le formule senza il valore calcolato, e certi lettori
  (soprattutto da telefono) mostrerebbero la colonna del prezzo al chilo vuota.
  `cache_vals.py` infila il valore dentro l'XML accanto alla formula: si tengono
  tutti e due. **Va rilanciato ogni volta che si risalva il file con openpyxl**,
  perché il salvataggio butta via i valori.
- **`xargs -P` non funziona** su questa macchina per l'OCR: gira per nove minuti
  e produce file da zero byte. In sequenza fa 1,3 s a pagina e va benissimo.
  Per i download invece `xargs -P 12` va (sono in attesa di rete, non di CPU).
- **Il browser non passa dal proxy**: Chromium dà `ERR_CONNECTION_RESET` su
  qualsiasi HTTPS perché non c'è `certutil` per mettergli il certificato nello
  store NSS. Con `curl` va tutto. Non perderci tempo.
- **Bennet risponde 403 a curl** sul proprio sito (protezione anti-robot). Le
  sue pagine si prendono lo stesso da anteprimavolantino.
- **Nel codice Python non si scrive `all''olio`**: non è una stringa SQL, Python
  concatena e viene fuori `allolio`. Usare le virgolette doppie.

## Perché i riassunti online non bastano

Provati prima di scaricare i volantini, e **sbagliano**. Tre errori trovati
confrontandoli con la pagina vera:

- Lidl, rollata di bovino: scritto «7,99 al kg», in realtà 7,99 la confezione da
  600 g, cioè **13,32 al kg**
- Lidl, salmone: scritto «150 g a 8,99», in realtà **500 g** a 8,99
- Eurospin, macinato di bovino: scritto «6,99 al kg», sul volantino **8,99**

Le righe che nell'Excel restano di seconda mano sono segnate in giallo e dicono
"DA CONTROLLARE". Tutte le altre le ho lette una per una dalle pagine.

## Se un domani diventa un'app

Manlio non legge codice e verifica tutto aprendo una pagina sul telefono, quindi
il naturale seguito è una paginetta come la Palestra. **Il telefono non può
scaricarsi i volantini da solo**: i siti dei supermercati non concedono CORS e
servirebbe una libreria per i PDF che in negozio, senza rete, non si carica.
I dati vanno scritti qui dentro da Claude quando i volantini cambiano, e la
pagina si limita a mostrarli.
