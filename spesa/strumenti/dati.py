# -*- coding: utf-8 -*-
"""I dati letti a mano dai volantini, uno per uno, guardando le pagine.

Ogni riga:
  categoria, insegna, chiave del volantino, reparto, prodotto, formato,
  quantità, prezzo, pagina del PDF, fonte, note

Il prezzo per unità NON si scrive qui: si calcola prezzo/quantità, così non
può mai essere in disaccordo col prezzo. L'unità la decide la categoria
(UNITA qui sotto): il latte si confronta al litro, le uova all'uovo, la carta
igienica al rotolo e il detersivo al lavaggio. Confrontare tutto al chilo
darebbe numeri veri ma inutili.

Fonte V = letto dal volantino. Fonte D = preso da un riassunto online e mai
verificato: nella pagina esce marcato «da controllare», perché di riassunti
sbagliati ne ho già trovati tre.
"""
V = 'letto dal volantino'
D = 'DA CONTROLLARE (riassunto online)'

# categoria -> (unità al singolare per l'etichetta, nome della quantità)
UNITA = {
 'Carne di bue':   ('al kg',        'kg'),
 'Tonno':          ('al kg',        'kg'),
 'Salmone':        ('al kg',        'kg'),
 'Caffè':          ('al kg',        'kg'),
 'Pasta':          ('al kg',        'kg'),
 'Pollo':          ('al kg',        'kg'),
 'Formaggio':      ('al kg',        'kg'),
 'Latte':          ('al litro',     'litri'),
 "Olio d'oliva":   ('al litro',     'litri'),
 'Uova':           ("all'uovo",     'uova'),
 'Carta igienica': ('al rotolo',    'rotoli'),
 'Detersivo':      ('a lavaggio',   'lavaggi'),
 'Suino':          ('al kg',        'kg'),
}

# chiave, insegna, periodo leggibile, nome del PDF, ULTIMO GIORNO DI VALIDITA
# L'ultimo giorno serve a due cose: sapere quando andare a prendere il volantino
# nuovo (il giorno prima), e buttare via il vecchio due giorni dopo, come ha
# chiesto Manlio per non ritrovarsi una collezione. Se non e stampato sul
# volantino si mette la stima e si scrive «stimato» nel periodo.
VOLANTINI = [
 ('lidl',           'Lidl',           'dal 3 al 9 settembre (sottocosto fino al 12)', 'Lidl — 3-9 settembre.pdf',                       '2026-09-12'),
 ('eurospin',       'Eurospin',       'dal 24 agosto al 6 settembre',                 'Eurospin — 24 agosto-6 settembre.pdf',           '2026-09-06'),
 ('md',             'MD',             'dal 25 agosto al 6 settembre',                 'MD — 25 agosto-6 settembre.pdf',                 '2026-09-06'),
 ('bennet',         'Bennet',         'dal 27 agosto al 9 settembre',                 'Bennet — 27 agosto-9 settembre.pdf',             '2026-09-09'),
 ('ipercoop',       'Ipercoop',       'Sottocosto, dal 31 agosto al 9 settembre',     'Ipercoop Sottocosto — 31 agosto-9 settembre.pdf','2026-09-09'),
 ('ipercoop_extra', 'Ipercoop',       'Extra offerte, dal 27 agosto al 9 settembre',  'Ipercoop Extra offerte — 27 agosto-9 settembre.pdf','2026-09-09'),
 ('carriper20',     'Carrefour Iper', 'dal 20 agosto al 3 settembre',                 'Carrefour Iper — 20 agosto-3 settembre.pdf',     '2026-09-03'),
 ('carriper04',     'Carrefour Iper', 'dal 4 settembre (fine stimata)',               'Carrefour Iper — dal 4 settembre.pdf',           '2026-09-17'),
]

PRODOTTI = [
 # ------------------------------- CARNE DI BUE (kg) -------------------------------
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
 # ------------------------------- TONNO (kg) -------------------------------
 ("Tonno","Bennet","bennet","Dispensa","Tonno all'olio di oliva – Flotta Azzurra","840 g (12 × 70 g)",0.840,7.48,12,V,"−30%, prima 10,69. Confezione grande."),
 ("Tonno","MD","md","Dispensa","Tonno all'olio d'oliva – Poseidon","840 g (12 × 70 g)",0.840,7.79,1,V,"Prima 9,49. Confezione grande."),
 ("Tonno","Carrefour Iper","carriper04","Dispensa","Tonno all'olio di oliva – Rio Mare","960 g (12 × 80 g)",0.960,10.45,4,V,"Sottocosto −47%, prima 19,73. Confezione grande."),
 ("Tonno","Eurospin","eurospin","Dispensa","Filetti di tonno all'olio di oliva pinna gialla – Ondina","260 g",0.260,2.99,6,V,"Prima 4,29. Barattolo di vetro."),
 ("Tonno","Lidl","lidl","Sottocosto","Tonno in olio di oliva – Rio Mare","780 g (12 × 65 g)",0.780,9.99,1,V,"Sgocciolato fa 16,01 al kg. Sottocosto fino al 12 settembre."),
 ("Tonno","Ipercoop","ipercoop","Dispensa","Tonno Yellowfin in olio di oliva – Rio Mare","780 g (12 × 65 g)",0.780,10.89,3,V,"Sottocosto −30%, prima 15,57. Stesso pacco del Lidl, ma più caro."),
 ("Tonno","Bennet","bennet","Dispensa","Filetti di tonno – Rio Mare","250 g",0.250,4.99,12,V,"−40%, prima 8,32."),
 ("Tonno","Bennet","bennet","Dispensa","Tonno in olio – Consorcio","175 g",0.175,3.99,12,V,"−50%, ma solo con la tessera Bennet Club."),
 # ------------------------------- SALMONE (kg) -------------------------------
 ("Salmone","Bennet","bennet","Pescheria","Filetto di salmone","al kg",1,17.69,None,D,"Sottocosto in copertina. Non valido nel Bennet di Alessandria."),
 ("Salmone","Lidl","lidl","Pesce","Filetto di salmone con pelle – Gastronomia di Mare","500 g",0.500,8.99,17,V,"Solo con carta Lidl Plus. Senza carta 10,49, cioè 20,98 al kg."),
 ("Salmone","Ipercoop","ipercoop","Freschi","Salmone scozzese affumicato – Icelander","100 g",0.100,1.99,4,V,"Sottocosto −50%, prima 3,98. Max 6 confezioni."),
 ("Salmone","MD","md","Freschi","Salmone affumicato","200 g",0.200,3.99,1,V,"Prima 5,49. Il volantino stampa 19,95 al kg."),
 ("Salmone","Ipercoop","ipercoop_extra","Freschi","Sashimi di salmone affumicato – Gimar","140 g",0.140,6.67,14,V,"PREZZO SOCI (−25%). Senza tessera 8,90, cioè 63,58 al kg."),
 # ------------------------------- CAFFÈ (kg) -------------------------------
 ("Caffè","Ipercoop","ipercoop","Dispensa","Caffè macinato Crema e Gusto – Lavazza","1 kg (4 × 250 g)",1,9.90,2,V,"Sottocosto −50%, prima 19,90. Max 3 confezioni."),
 ("Caffè","Ipercoop","ipercoop_extra","Dispensa","Caffè macinato per moka classico – Illy","250 g",0.250,5.69,6,V,"Etichetta «Conviene»."),
 ("Caffè","Eurospin","eurospin","Colazione","Capsule caffè espresso/cortado – Don Jerez","100 g, compatibili Dolce Gusto",0.100,2.59,3,V,"Prima 3,59. Sono capsule: al chilo costano molto più del macinato."),
 ("Caffè","Ipercoop","ipercoop_extra","Dispensa","Capsule compatibili Nespresso – Starbucks","57 g",0.057,2.99,6,V,"Capsule."),
 ("Caffè","Ipercoop","ipercoop_extra","Dispensa","Caffè solubile Gold – Nescafé","100 g",0.100,5.49,6,V,"PREZZO SOCI. È solubile, non macinato."),
 # ------------------------------- LATTE (litri) -------------------------------
 ("Latte","MD","md","Dispensa","Valigetta latte parzialmente scremato – Malga Paradiso","6 litri (6 × 1 l)",6,4.19,1,V,"Prima 5,10. Il volantino stampa 0,70 al litro."),
 ("Latte","Lidl","lidl","Sottocosto","Latte UHT Bontà e Leggerezza 1,2% – Parmalat","1 litro",1,0.79,1,V,"Sottocosto fino al 12 settembre."),
 ("Latte","Ipercoop","ipercoop","Dispensa","Latte UHT parzialmente scremato – Granarolo","4 litri (4 × 1 l)",4,3.99,4,V,"Sottocosto −49%, prima 7,96. Max 6 confezioni."),
 # ------------------------------- PASTA (kg) -------------------------------
 ("Pasta","Ipercoop","ipercoop","Dispensa","Pasta di semola formati classici – Barilla","500 g",0.500,0.48,3,V,"Sottocosto −50%, prima 0,97. Max 20 confezioni."),
 ("Pasta","MD","md","Freschi","Pasta fresca orecchiette o trofie – Ca' Bianca","1 kg",1,1.29,3,V,"Prima 1,99."),
 ("Pasta","MD","md","Freschi","Pasta sfoglia rettangolare","550 g (2 × 275 g)",0.550,1.69,3,V,"Prima 2,69."),
 ("Pasta","Bennet","bennet","Freschi","Gnocchetti freschi – Patamore","500 g",0.500,1.78,8,V,"−40%, prima 2,98."),
 ("Pasta","Bennet","bennet","Freschi","Pasta fresca all'uovo – Bennet","250 g",0.250,0.96,8,V,"−35% con la tessera Bennet Club."),
 ("Pasta","Ipercoop","ipercoop","Freschi","Pasta fresca ripiena Antica Bottega – Fini","250 g",0.250,1.79,4,V,"Sottocosto −51%, prima 3,69."),
 ("Pasta","Bennet","bennet","Freschi","Pasta fresca ripiena Sfogliagrezza – Giovanni Rana","250 g",0.250,2.59,8,V,"−35%, prima 3,99."),
 # ------------------------------- OLIO D'OLIVA (litri) -------------------------------
 ("Olio d'oliva","Carrefour Iper","carriper04","Dispensa","Olio extravergine di oliva Terre Antiche – Dante","1 litro",1,3.89,4,V,"Sottocosto −57%, prima 9,05."),
 ("Olio d'oliva","Ipercoop","ipercoop","Dispensa","Olio extravergine di oliva Classico – Monini","1 litro",1,4.59,3,V,"Sottocosto −51%, prima 9,49. Max 4 confezioni."),
 ("Olio d'oliva","Bennet","bennet","Dispensa","Olio extravergine di oliva grezzo Il Casolare – Farchioni","1 litro",1,7.99,12,V,"−33%, prima 11,93."),
 # ------------------------------- POLLO (kg) -------------------------------
 ("Pollo","Eurospin","eurospin","Macelleria","Cordon bleu di pollo e tacchino","490 g",0.490,1.99,11,V,"Il volantino stampa 4,06 al kg."),
 ("Pollo","Ipercoop","ipercoop_extra","Macelleria","Alette arrosto di pollo – Origine Coop","450 g",0.450,2.19,14,V,"Da polli allevati senza antibiotici."),
 ("Pollo","Lidl","lidl","Macelleria","Pollo allevato all'aperto Campese – Amadori","al kg",1,5.99,16,V,"Senza uso di antibiotici."),
 ("Pollo","MD","md","Surgelati","Nuggets di pollo – Tyson","1 kg",1,6.49,3,V,"Surgelato. Prima 7,99."),
 ("Pollo","Lidl","lidl","Macelleria","Petto di pollo intero","al kg",1,6.79,16,V,"−18%, prima 8,29."),
 ("Pollo","Eurospin","eurospin","Macelleria","Petto di pollo a fette","Confezione Famiglia, al kg",1,7.99,11,V,""),
 ("Pollo","Ipercoop","ipercoop_extra","Macelleria","Tagliata di petto di pollo SQ","400 g",0.400,3.73,14,V,"PREZZO SOCI (−25%). Senza tessera 4,98, cioè 12,45 al kg."),
 ("Pollo","Ipercoop","ipercoop_extra","Macelleria","Sottilissime di petto di pollo – AIA","al kg",1,12.54,14,V,"−30%, prima 17,92."),
 ("Pollo","Ipercoop","ipercoop_extra","Surgelati","La Viennese cotoletta di pollo – AIA","300 g",0.300,3.99,14,V,"Etichetta «Conviene»."),
 # ------------------------------- FORMAGGIO (kg) -------------------------------
 ("Formaggio","MD","md","Freschi","Mozzarelle in busta – Reggia","1 kg (8 × 125 g)",1,4.49,1,V,"Prima 5,49."),
 ("Formaggio","Ipercoop","ipercoop","Freschi","Sottilette Classiche","400 g",0.400,1.89,4,V,"Sottocosto −43%, prima 3,34."),
 ("Formaggio","Ipercoop","ipercoop","Freschi","Mozzarella Santa Lucia – Galbani","375 g (3 × 125 g)",0.375,2.09,4,V,"Sottocosto −52%, prima 4,40."),
 ("Formaggio","Lidl","lidl","Sottocosto","Mozzarella 100% latte italiano – Granarolo","375 g (3 × 125 g)",0.375,2.29,1,V,"Sottocosto fino al 12 settembre."),
 ("Formaggio","Ipercoop","ipercoop","Freschi","Philadelphia formaggio fresco","350 g",0.350,2.19,4,V,"Sottocosto −39%, prima 3,64."),
 ("Formaggio","Bennet","bennet","Freschi","Mascarpone – Granarolo","500 g",0.500,3.58,8,V,"−40%, prima 5,97."),
 ("Formaggio","Ipercoop","ipercoop","Freschi","Grana Padano DOP 16 mesi – GranTerre","700 g",0.700,7.99,4,V,"Sottocosto −42%, prima 13,90. Max 3 confezioni."),
 ("Formaggio","Bennet","bennet","Freschi","Parmigiano Reggiano – Bennet","500 g",0.500,12.87,8,V,"−19% con la tessera Bennet Club."),
 # ------------------------------- UOVA (uova) -------------------------------
 ("Uova","Bennet","bennet","Freschi","10 uova fresche medie da allevamento a terra – Ovonovo","10 uova",10,2.99,8,V,"−25%, prima 3,99. È l'unica offerta sulle uova che ho trovato."),
 # ------------------------------- CARTA IGIENICA (rotoli) -------------------------------
 ("Carta igienica","MD","md","Cura casa","4 rotoloni carta igienica – Regina","4 rotoloni, dichiarati pari a 12 rotoli",12,2.89,18,V,"Prima 3,29. Il conto al rotolo usa i 12 dichiarati sul pacco: sui 4 rotoloni veri fa 0,72 l'uno."),
 ("Carta igienica","Ipercoop","ipercoop","Cura casa","Carta igienica Scottonelle – Scottex","18 rotoli",18,4.99,5,V,"Sottocosto −50%, prima 9,98. Max 3 confezioni."),
 # ------------------------------- DETERSIVO (lavaggi) -------------------------------
 ("Detersivo","Ipercoop","ipercoop","Cura casa","Ammorbidente concentrato – Coccolino","87 lavaggi (1,827 l)",87,3.19,5,V,"Sottocosto −54%, prima 6,99. È ammorbidente, non detersivo: si usa in aggiunta."),
 ("Detersivo","Ipercoop","ipercoop","Cura casa","Detersivo per lavatrice in polvere Power – Dash+","105 misurini (5,25 kg)",105,14.90,5,V,"Sottocosto −50%, prima 29,80. Max 2 confezioni."),
 ("Detersivo","Ipercoop","ipercoop","Cura casa","Detersivo liquido per lavatrice Base – Dash","75 lavaggi (3 × 25)",75,10.90,5,V,"Sottocosto −50%, prima 21,80."),
 ("Detersivo","Ipercoop","ipercoop","Cura casa","Detersivo per lavastoviglie Platinum Plus – Fairy","71 capsule",71,10.90,5,V,"Sottocosto −50%, prima 21,80. È per la lavastoviglie."),
 ("Detersivo","MD","md","Cura casa","24 Fresh Caps 3 in 1 per lavatrice – Actiff","24 capsule",24,4.29,18,V,"Prima 4,89."),
 ("Detersivo","MD","md","Cura casa","24 capsule per lavatrice bouquet floreale – DAT5","24 capsule",24,4.29,18,V,"Prima 4,99."),
 # ------------------------------- SUINO (kg) -------------------------------
 # Ci stanno sia i tagli freschi sia i salumi: sono tutti maiale, e il formato
 # di ogni riga dice cos'e. Se un domani vuole separarli, basta una categoria in piu.
 ("Suino","Lidl","lidl","Macelleria","Bocconcini di salsiccia","250 g",0.250,1.69,16,V,"−21%, prima 2,15. Il volantino stampa 6,76 al kg."),
 ("Suino","Eurospin","eurospin","Macelleria","Braciole di coppa di suino","al kg",1,6.99,11,V,""),
 ("Suino","Lidl","lidl","Macelleria","Trancio di coppa di suino","al kg",1,6.99,16,V,"Novità."),
 ("Suino","Lidl","lidl","Macelleria","Sottilissime di lonza di suino","250 g",0.250,1.99,16,V,"−21% con la carta Lidl Plus, prima 2,55. Il volantino stampa 7,96 al kg."),
 ("Suino","Ipercoop","ipercoop_extra","Gastronomia","Polpettone Buona Domenica – Amadori","700 g",0.700,7.43,14,V,"PREZZO SOCI (−40%). Senza tessera 9,91, cioè 14,16 al kg."),
 ("Suino","Bennet","bennet","Salumi","Pancetta dolce o affumicata a cubetti – Fratelli Beretta","300 g (4 × 75 g)",0.300,3.98,8,V,"−30%, prima 5,69."),
 ("Suino","Ipercoop","ipercoop","Salumi","Prosciutto cotto Alta Qualità – Beretta","240 g (2 × 120 g)",0.240,3.29,4,V,"Sottocosto −52%, prima 6,98."),
 ("Suino","Ipercoop","ipercoop","Salumi","Salame Negronetto – Negroni","220 g",0.220,3.48,4,V,"Sottocosto −38%, prima 5,69."),
 ("Suino","Bennet","bennet","Salumi","Prosciutto crudo o cotto di alta qualità – Citterio","240 g (3 × 80 g)",0.240,4.99,8,V,"−50% con la tessera Bennet Club, prima 9,99."),
 ("Suino","Ipercoop","ipercoop_extra","Gastronomia","Carne salada del Trentino per carpaccio","100 g",0.100,3.36,14,V,"PREZZO SOCI (−25%). Senza tessera 4,49, cioè 44,90 al kg."),
]

PRODOTTI.sort(key=lambda p: (list(UNITA).index(p[0]), p[7] / p[6]))
