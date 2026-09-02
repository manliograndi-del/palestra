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

    https://claude.ai/code/artifact/a6782ea0-6822-4026-87e7-705012966595

**Le pagine pubblicate nascono private**: perché la moglie la apra, lui deve
condividerla dal menu della pagina stessa. Gliel'ho detto; se dice che lei non
la vede, è quasi sicuramente quello.

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

### Perché la lista sta nel browser e non sul server

La memoria condivisa delle pagine pubblicate (capacità `db`) sarebbe la cosa
giusta — lista sola, aggiornata per tutti e due — ma **un artifact che dichiara
`db` diventa interno all'organizzazione** e non si può condividere fuori. Sul
piano Pro di Manlio l'organizzazione è lui solo, quindi la moglie resterebbe
fuori, che è esattamente quello che aveva chiesto di poter fare.

Perciò la lista vive in `localStorage` (chiave `spesa.lista.v1`), una copia per
telefono: il link si condivide con chiunque, e ognuno se la regola. Il prezzo è
che le modifiche di lui non arrivano a lei. **Se un domani dice che vuole la
lista condivisa davvero, si passa a `db` — ma va detto prima che così la moglie
non entra più.** Letture e scritture sono in try/catch: in navigazione privata
la memoria può mancare e la pagina deve funzionare lo stesso, ripartendo dai
dodici predefiniti.

### Le offerte lette a mano coprono solo tre categorie

Ogni prodotto della lista ha un campo `cat`, e ce l'hanno **solo carne di bue,
tonno e salmone**: sono le uniche categorie di cui ho letto i prezzi pagina per
pagina. Per gli altri nove la pagina mostra soltanto in quali pagine dei
volantini compare la parola. Senza quel legame la ricerca per testo pescava i
«tonni all'olio d'oliva» dentro il prodotto «olio d'oliva» e sembravano offerte
sull'olio. Se un domani si leggono a mano altre categorie, si aggiunge la
categoria in `dati.py` e la si mette nel `cat` di `lista.py`.

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
