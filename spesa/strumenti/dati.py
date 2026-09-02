# -*- coding: utf-8 -*-
"""I dati letti a mano dai volantini. Li usano sia l'Excel sia la pagina web.

Ogni riga: categoria, insegna, volantino, reparto, prodotto, formato,
quantità in kg, prezzo, pagina del PDF, fonte, note.
Il prezzo al chilo NON si scrive qui: si calcola prezzo/quantità, così non
può essere in disaccordo col prezzo.
"""
V = 'letto dal volantino'
D = 'DA CONTROLLARE (riassunto online)'

VOLANTINI = [
 # chiave, insegna, periodo, file PDF
 ('lidl',           'Lidl',           'dal 3 al 9 settembre (sottocosto fino al 12)', 'Lidl — 3-9 settembre.pdf'),
 ('eurospin',       'Eurospin',       'dal 24 agosto al 6 settembre',                 'Eurospin — 24 agosto-6 settembre.pdf'),
 ('md',             'MD',             'dal 25 agosto al 6 settembre',                 'MD — 25 agosto-6 settembre.pdf'),
 ('bennet',         'Bennet',         'dal 27 agosto al 9 settembre',                 'Bennet — 27 agosto-9 settembre.pdf'),
 ('ipercoop',       'Ipercoop',       'Sottocosto, dal 31 agosto al 9 settembre',     'Ipercoop Sottocosto — 31 agosto-9 settembre.pdf'),
 ('ipercoop_extra', 'Ipercoop',       'Extra offerte, dal 27 agosto al 9 settembre',  'Ipercoop Extra offerte — 27 agosto-9 settembre.pdf'),
 ('carriper20',     'Carrefour Iper', 'dal 20 agosto al 3 settembre',                 'Carrefour Iper — 20 agosto-3 settembre.pdf'),
 ('carriper04',     'Carrefour Iper', 'dal 4 settembre',                              'Carrefour Iper — dal 4 settembre.pdf'),
]

PRODOTTI = [
 # ---------------- CARNE DI BUE ----------------
 ("Carne di bue","MD","md","Surgelati","10 hamburger di bovino – Le Specialità di Beppe","750 g",0.750,4.99,3,V,"Surgelato. Il volantino stampa 6,65 al kg."),
 ("Carne di bue","Eurospin","eurospin","Macelleria","Macinato per ragù di bovino adulto","Confezione Famiglia, al kg",1,8.99,11,V,"È la confezione grande, il prezzo è già al chilo."),
 ("Carne di bue","Lidl","lidl","Macelleria","Macinato di bovino adulto Scottona","400 g",0.400,4.49,16,V,"Prima 5,99. Il volantino stampa 11,23 al kg."),
 ("Carne di bue","Carrefour Iper","carriper20","Macelleria","Costata di bovino adulto – da 3 kg in su","al kg, almeno 3 kg",1,11.90,1,D,"Sconto a quantità: sotto i 3 kg costa 13,90 al kg."),
 ("Carne di bue","Bennet","bennet","Surgelati","4 hamburger di carne bovina con bacon – Montana","400 g",0.400,4.79,10,V,"Surgelato, −20%, prima 5,99."),
 ("Carne di bue","Ipercoop","ipercoop_extra","Macelleria","Macinato di bovino – Fattorie Natura","800 g",0.800,9.90,14,V,"PREZZO SOCI (−20%). Senza tessera 12,38, cioè 15,48 al kg."),
 ("Carne di bue","Eurospin","eurospin","Macelleria","Maxi hamburger di scottona","200 g",0.200,2.49,11,V,"Il volantino stampa 12,45 al kg."),
 ("Carne di bue","Lidl","lidl","Macelleria","Rollata di bovino allo speck","600 g",0.600,7.99,16,V,"Attenzione: 7,99 è il prezzo della confezione, non al chilo."),
 ("Carne di bue","Bennet","bennet","Macelleria","Fettine di bovino adulto","al kg",1,13.99,None,D,"Sottocosto Freschi."),
 ("Carne di bue","Ipercoop","ipercoop_extra","Macelleria","Fettine di reale di bovino adulto – Fattorie Natura","al kg",1,16.38,14,V,"Etichetta «Conviene»."),
 ("Carne di bue","Eurospin","eurospin","Macelleria","Fettine sottili di bovino adulto","al kg",1,17.99,11,V,""),
 # ---------------- TONNO ----------------
 ("Tonno","Bennet","bennet","Dispensa","Tonno all'olio di oliva – Flotta Azzurra","840 g (12 × 70 g)",0.840,7.48,12,V,"−30%, prima 10,69. Confezione grande."),
 ("Tonno","MD","md","Dispensa","Tonno all'olio d'oliva – Poseidon","840 g (12 × 70 g)",0.840,7.79,1,V,"Prima 9,49. Confezione grande."),
 ("Tonno","Carrefour Iper","carriper04","Dispensa","Tonno all'olio di oliva – Rio Mare","960 g (12 × 80 g)",0.960,10.45,4,V,"Sottocosto −47%, prima 19,73. Confezione grande."),
 ("Tonno","Eurospin","eurospin","Dispensa","Filetti di tonno all'olio di oliva pinna gialla – Ondina","260 g",0.260,2.99,6,V,"Prima 4,29. Barattolo di vetro."),
 ("Tonno","Lidl","lidl","Sottocosto","Tonno in olio di oliva – Rio Mare","780 g (12 × 65 g)",0.780,9.99,1,V,"Sgocciolato fa 16,01 al kg. Sottocosto fino al 12 settembre."),
 ("Tonno","Ipercoop","ipercoop","Dispensa","Tonno Yellowfin in olio di oliva – Rio Mare","780 g (12 × 65 g)",0.780,10.89,3,V,"Sottocosto −30%, prima 15,57. Stesso prodotto del Lidl, ma più caro."),
 ("Tonno","Bennet","bennet","Dispensa","Filetti di tonno – Rio Mare","250 g",0.250,4.99,12,V,"−40%, prima 8,32."),
 ("Tonno","Bennet","bennet","Dispensa","Tonno in olio – Consorcio","175 g",0.175,3.99,12,V,"−50%, ma solo con la tessera Bennet Club."),
 # ---------------- SALMONE ----------------
 ("Salmone","Bennet","bennet","Pescheria","Filetto di salmone","al kg",1,17.69,None,D,"Sottocosto in copertina. Non valido nel Bennet di Alessandria."),
 ("Salmone","Lidl","lidl","Pesce","Filetto di salmone con pelle – Gastronomia di Mare","500 g",0.500,8.99,17,V,"Solo con carta Lidl Plus. Senza carta 10,49, cioè 20,98 al kg."),
 ("Salmone","Ipercoop","ipercoop","Freschi","Salmone scozzese affumicato – Icelander","100 g",0.100,1.99,4,V,"Sottocosto −50%, prima 3,98. Max 6 confezioni."),
 ("Salmone","MD","md","Freschi","Salmone affumicato","200 g",0.200,3.99,1,V,"Prima 5,49. Il volantino stampa 19,95 al kg."),
 ("Salmone","Ipercoop","ipercoop_extra","Freschi","Sashimi di salmone affumicato – Gimar","140 g",0.140,6.67,14,V,"PREZZO SOCI (−25%). Senza tessera 8,90, cioè 63,58 al kg."),
]

ORDINE = {'Carne di bue': 0, 'Tonno': 1, 'Salmone': 2}
PRODOTTI.sort(key=lambda p: (ORDINE[p[0]], p[7] / p[6]))
