# Spesa — ricerca prodotti nei volantini

Progetto separato dalla Palestra, chiesto da Manlio il 2026-09-02.
Vive in questa cartella per non toccare `index.html`, che è l'app della palestra.

## Cosa vuole

Cercare i prodotti che gli interessano dentro i volantini dei supermercati vicino
a casa, e dirgli dove costano meno.

**Zona:** Torino, quartiere Santa Rita (corso Siracusa).
Il civico non serve: i volantini sono per punto vendita o per provincia.

**Insegne da controllare:** MD · Eurospin · Carrefour · Bennet · Mercatò · Lidl

**Prodotti fissi (2026-09-02):**
- carne di bue / bovino adulto, **in confezioni grandi** (il prezzo utile è
  quello al kg, e le catene fanno sconti a scaglioni: Carrefour p.es. cala il
  prezzo al kg oltre i 3 kg — va confrontato quello, non il prezzo del pacco)
- tonno (in scatola)
- salmone (da chiarire: affumicato, filetti freschi o surgelato — cambiano
  prezzo e reparto)

Ogni tanto chiederà altre cose fuori lista.

## Il muro tecnico — leggi prima di ripartire

**L'ambiente in cui gira Claude Code ha la rete chiusa.** Provato il 2026-09-02:
tutti i siti dei supermercati e tutti i portali di volantini (VolantinoFacile,
DoveConviene, Kimbino, PromoQui) rispondono `EGRESS_BLOCKED`. Anche Wikipedia.
Passa solo la ricerca web, che gira sull'infrastruttura di Anthropic.

Quindi **non si può scaricare nessun PDF** finché l'ambiente resta così.

Per sbloccare: claude.ai/code → icona a nuvola sopra la casella del messaggio →
ingranaggio sull'ambiente → **Network access** → `Full`, oppure `Custom` con la
lista qui sotto e la spunta "Also include default list of common package
managers". Vale dalla sessione successiva, non su quella in corso.

    *.lidl.it
    *.eurospin.it
    *.mdspa.it
    *.carrefour.it
    *.bennet.com
    *.mymercato.it
    *.volantinofacile.it
    *.doveconviene.it
    *.promoqui.it
    *.kimbino.it

## Perché la sola ricerca web non basta

Provata il 2026-09-02. Restituisce qualche prezzo vero ma di seconda mano, preso
da siti che riassumono i volantini, e **si sbaglia**: a una domanda su Eurospin
ha risposto con prezzi di Eurospar e di Lidl, e ha mescolato un volantino
scaduto con quello in corso. Non è materiale su cui mandare qualcuno a fare la
spesa. Serve il PDF.

## Come dovrebbe finire (non ancora deciso con lui)

Manlio non legge codice e verifica tutto aprendo una pagina sul telefono. Quindi
il risultato utile è una **paginetta come la Palestra**, con la lista divisa per
supermercato e il prezzo al kg, che apre in negozio. I dati li scriverebbe Claude
in un file dentro questa cartella quando i volantini cambiano: il telefono non può
leggere i PDF dei supermercati da solo (CORS li blocca, e servirebbe una libreria
esterna che in negozio, senza rete, non si carica).
