# Spesa — offerte dei supermercati

Progetto separato dalla Palestra, chiesto da Manlio il 2026-09-02.
Vive in questa cartella per non toccare `index.html`, che è l'app della palestra.

## Cosa vuole

**Non vuole che sia Claude a cercare i prodotti.** L'ha detto chiaramente a metà
lavoro: gli bastano **i volantini scaricati** da guardare da solo e **un Excel
delle offerte** da filtrare a modo suo. La ricerca la fa lui.

**Zona:** Torino, quartiere Santa Rita (corso Siracusa). Il civico non serve.
Di Mercatò ci sono punti vendita vicini: via Filadelfia, via Gaidano, corso
Brunelleschi.

**Insegne:** MD · Eurospin · Carrefour · Bennet · Mercatò · Lidl

**Prodotti che gli interessano sempre:** carne di bue in confezioni grandi,
tonno, salmone. Resta da chiarire quale salmone (affumicato, fresco o surgelato):
gliel'ho chiesto e non ha ancora risposto.

## Com'è andata il 2026-09-02

Consegnati: 7 PDF (242 pagine in tutto) e `offerte-supermercati-torino.xlsx`
con tre fogli — guida, 23 prodotti suoi col prezzo al chilo, e l'indice
cercabile di tutte le pagine.

**Mercatò non c'è.** Il loro sito carica il volantino con JavaScript e non
espone né un PDF né le immagini delle pagine. VolantinoFacile ce l'ha ma serve
le pagine da `data.volantinofacile.it` con un identificativo per pagina non
prevedibile, e tutto ciò che non sia la copertina risponde 403. Da ritentare.

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
