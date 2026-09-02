# -*- coding: utf-8 -*-
import json, os, glob
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

ARIAL  = 'Arial'
H_FILL = PatternFill('solid', fgColor='C00000')
H_FONT = Font(name=ARIAL, bold=True, color='FFFFFF', size=11)
TITLE  = Font(name=ARIAL, bold=True, size=14)
SUB    = Font(name=ARIAL, bold=True, size=12)
BODY   = Font(name=ARIAL, size=11)
NOTE   = Font(name=ARIAL, size=10, italic=True, color='666666')
THIN   = Border(bottom=Side('thin', color='DDDDDD'))
GIALLO = PatternFill('solid', fgColor='FFF2CC')

wb = Workbook()

# ---------------- Foglio 1: Come si usa ----------------
ws = wb.active; ws.title = 'Come si usa'
righe = [
 ("Offerte dei supermercati vicino a corso Siracusa, Torino", TITLE),
 ("Aggiornato al 2 settembre 2026", NOTE),
 ("", BODY),
 ("Cosa trovi in questo file", SUB),
 ("", BODY),
 ("Foglio «I tuoi prodotti» — carne di bue, tonno e salmone in offerta, con il prezzo al chilo", BODY),
 ("già calcolato per poterli confrontare. Sono ordinati dal più conveniente al più caro.", BODY),
 ("", BODY),
 ("Foglio «Indice pagine» — tutte le 242 pagine dei 7 volantini. Per ogni pagina ci sono le parole", BODY),
 ("che il computer è riuscito a leggerci dentro. Serve per cercare un prodotto qualsiasi: metti il", BODY),
 ("filtro sulla colonna «Parole trovate nella pagina», scrivi per esempio caffè, e ti dice insegna e", BODY),
 ("numero di pagina. Poi apri il PDF di quel volantino a quella pagina e leggi il prezzo.", BODY),
 ("", BODY),
 ("I volantini in PDF", SUB),
 ("", BODY),
 ("Insieme a questo file ci sono 7 PDF, uno per volantino. I numeri di pagina scritti qui sono", BODY),
 ("gli stessi del PDF.", BODY),
 ("", BODY),
 ("Due avvertenze", SUB),
 ("", BODY),
 ("1) I prezzi del foglio «I tuoi prodotti» li ho letti uno per uno dalle pagine del volantino.", BODY),
 ("   Le poche righe segnate in giallo vengono invece da riassunti trovati online e possono", BODY),
 ("   essere sbagliate: di errori così ne ho già trovati tre. Controllale sul PDF prima di fidarti.", BODY),
 ("", BODY),
 ("2) Le parole del foglio «Indice pagine» le ha lette il computer dalle immagini: sono spesso", BODY),
 ("   storpiate, e i prezzi non ci sono quasi mai. L'indice serve a trovare la pagina, non a", BODY),
 ("   sapere il prezzo. Il prezzo si legge sul PDF.", BODY),
 ("", BODY),
 ("Mercatò", SUB),
 ("", BODY),
 ("Mercatò non c'è: il loro sito non pubblica il volantino in un formato che si riesca a scaricare.", BODY),
 ("Gli altri cinque ci sono tutti. Di Carrefour ce ne sono due, Iper e Market.", BODY),
]
for i,(t,f) in enumerate(righe, start=1):
    ws.cell(row=i, column=1, value=t).font = f
ws.column_dimensions['A'].width = 100

# ---------------- Foglio 2: I tuoi prodotti ----------------
ws = wb.create_sheet('I tuoi prodotti')
COLS = ['Categoria','Insegna','Volantino valido','Reparto','Prodotto','Formato',
        'Quantità (kg)','Prezzo (€)','€ al kg','Pag. PDF','Fonte','Note']
V = 'letto dal volantino'
D = 'DA CONTROLLARE (riassunto online)'
DATI = [
 # categoria, insegna, validità, reparto, prodotto, formato, kg, prezzo, pagina, fonte, note
 ("Carne di bue","MD","25 ago – 6 set","Surgelati","10 hamburger di bovino – Le Specialità di Beppe","750 g",0.750,4.99,3,V,"Surgelato. Il volantino stampa 6,65 al kg."),
 ("Carne di bue","Eurospin","24 ago – 6 set","Macelleria","Macinato per ragù di bovino adulto","Confezione Famiglia, al kg",1,8.99,11,V,"È la confezione grande, il prezzo è già al chilo."),
 ("Carne di bue","Lidl","3 – 9 set","Macelleria","Macinato di bovino adulto Scottona","400 g",0.400,4.49,16,V,"Prima 5,99. Il volantino stampa 11,23 al kg."),
 ("Carne di bue","Carrefour Iper","20 ago – 3 set","Macelleria","Costata di bovino adulto – da 3 kg in su","al kg, almeno 3 kg",1,11.90,1,D,"Sconto a quantità: sotto i 3 kg costa 13,90 al kg."),
 ("Carne di bue","Bennet","27 ago – 9 set","Surgelati","4 hamburger di carne bovina con bacon – Montana","400 g",0.400,4.79,10,V,"Surgelato, −20%, prima 5,99."),
 ("Carne di bue","Eurospin","24 ago – 6 set","Macelleria","Maxi hamburger di scottona","200 g",0.200,2.49,11,V,"Il volantino stampa 12,45 al kg."),
 ("Carne di bue","Carrefour Market","dal 4 set","Macelleria","Fettine di bovino adulto – da 1 kg in su","al kg, almeno 1 kg",1,12.99,None,D,"Sconto a quantità."),
 ("Carne di bue","Lidl","3 – 9 set","Macelleria","Rollata di bovino allo speck","600 g",0.600,7.99,16,V,"Attenzione: 7,99 è il prezzo della confezione, non al chilo."),
 ("Carne di bue","Bennet","27 ago – 9 set","Macelleria","Fettine di bovino adulto","al kg",1,13.99,None,D,"Sottocosto Freschi."),
 ("Carne di bue","Eurospin","24 ago – 6 set","Macelleria","Fettine sottili di bovino adulto","al kg",1,17.99,11,V,""),
 ("Tonno","Bennet","27 ago – 9 set","Dispensa","Tonno all'olio di oliva – Flotta Azzurra","840 g (12 × 70 g)",0.840,7.48,12,V,"−30%, prima 10,69. Confezione grande."),
 ("Tonno","MD","25 ago – 6 set","Dispensa","Tonno all'olio d'oliva – Poseidon","840 g (12 × 70 g)",0.840,7.79,1,V,"Prima 9,49. Confezione grande."),
 ("Tonno","Carrefour Iper","dal 4 set","Dispensa","Tonno all'olio di oliva – Rio Mare","960 g (12 × 80 g)",0.960,10.45,4,V,"Sottocosto −47%, prima 19,73. Confezione grande."),
 ("Tonno","Eurospin","24 ago – 6 set","Dispensa","Filetti di tonno all'olio di oliva pinna gialla – Ondina","260 g",0.260,2.99,6,V,"Prima 4,29. Barattolo di vetro."),
 ("Tonno","Lidl","3 – 12 set","Sottocosto","Tonno in olio di oliva – Rio Mare","780 g (12 × 65 g)",0.780,9.99,1,V,"Sgocciolato fa 16,01 al kg. Sottocosto fino al 12 settembre."),
 ("Tonno","Carrefour Market","dal 4 set","Pescheria","Trancio di tonno pinne gialle decongelato","al kg",1,17.90,9,V,"Pesce fresco, −30%, prima 25,90. Solo dove c'è il banco."),
 ("Tonno","Bennet","27 ago – 9 set","Dispensa","Filetti di tonno – Rio Mare","250 g",0.250,4.99,12,V,"−40%, prima 8,32."),
 ("Tonno","Bennet","27 ago – 9 set","Dispensa","Tonno in olio – Consorcio","175 g",0.175,3.99,12,V,"−50%, ma solo con la tessera Bennet Club."),
 ("Salmone","Bennet","27 ago – 9 set","Pescheria","Filetto di salmone","al kg",1,17.69,None,D,"Sottocosto in copertina. Non valido nel Bennet di Alessandria."),
 ("Salmone","Lidl","3 – 9 set","Pesce","Filetto di salmone con pelle – Gastronomia di Mare","500 g",0.500,8.99,17,V,"Solo con carta Lidl Plus. Senza carta 10,49, cioè 20,98 al kg."),
 ("Salmone","MD","25 ago – 6 set","Freschi","Salmone affumicato","200 g",0.200,3.99,1,V,"Prima 5,49. Il volantino stampa 19,95 al kg."),
 ("Salmone","Carrefour Market","dal 4 set","Pescheria","Salmone affumicato Essential – Mowi","50 g",0.050,1.99,9,V,"−50%. Confezione piccolissima: al chilo è carissimo."),
 ("Salmone","Carrefour Market","dal 4 set","Pescheria","Saku di salmone Gimar (per sushi)","140 g",0.140,7.90,9,V,"−20%, prima 9,90."),
]
ORD = {'Carne di bue':0, 'Tonno':1, 'Salmone':2}
DATI.sort(key=lambda d: (ORD[d[0]], d[7]/d[6]))

for j,h in enumerate(COLS, start=1):
    c = ws.cell(row=1, column=j, value=h)
    c.font = H_FONT; c.fill = H_FILL
    c.alignment = Alignment(vertical='center', wrap_text=True)
for i,d in enumerate(DATI, start=2):
    cat,ins,val,rep,pro,fmt,qta,pre,pag,fon,note = d
    for j,v in enumerate([cat,ins,val,rep,pro,fmt,qta,pre,None,pag,fon,note], start=1):
        c = ws.cell(row=i, column=j, value=v)
        c.font = BODY; c.border = THIN
        c.alignment = Alignment(vertical='top', wrap_text=(j in (5,12)))
    ws.cell(row=i, column=9).value = f'=IFERROR(H{i}/G{i},"")'
    ws.cell(row=i, column=7).number_format = '0.000'
    ws.cell(row=i, column=8).number_format = '#,##0.00 "€"'
    c9 = ws.cell(row=i, column=9)
    c9.number_format = '#,##0.00 "€"'; c9.font = Font(name=ARIAL, size=11, bold=True)
    if fon == D:
        for j in range(1,13): ws.cell(row=i, column=j).fill = GIALLO
for col,w in zip('ABCDEFGHIJKL',[13,17,16,13,48,24,12,12,11,9,20,50]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = 'A2'
ws.auto_filter.ref = f'A1:L{len(DATI)+1}'
r = len(DATI)+3
ws.cell(row=r, column=1, value="La colonna «€ al kg» è calcolata: prezzo diviso quantità. Le righe gialle vengono da riassunti online e vanno controllate sul PDF.").font = NOTE

# ---------------- Foglio 3: Indice pagine ----------------
ws = wb.create_sheet('Indice pagine')
idx = json.load(open('indice.json', encoding='utf-8'))
validi = {(os.path.basename(os.path.dirname(f)), int(os.path.basename(f)[:-4])) for f in glob.glob('pg/*/*.jpg')}
idx = [r for r in idx if (r['chiave'], r['pagina']) in validi]
idx.sort(key=lambda r: (r['insegna'], r['validita'], r['pagina']))
for j,h in enumerate(['Insegna','Volantino valido','File PDF','Pagina','Parole trovate nella pagina'], start=1):
    c = ws.cell(row=1, column=j, value=h); c.font = H_FONT; c.fill = H_FILL
for i,r in enumerate(idx, start=2):
    for j,v in enumerate([r['insegna'], r['validita'], r['chiave']+'.pdf', r['pagina'], r['parole']], start=1):
        c = ws.cell(row=i, column=j, value=v); c.font = BODY
        c.alignment = Alignment(vertical='top', wrap_text=(j==5))
for col,w in zip('ABCDE',[18,34,18,9,120]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = 'A2'
ws.auto_filter.ref = f'A1:E{len(idx)+1}'

wb.save('out/offerte-supermercati-torino.xlsx')
print('prodotti:', len(DATI), '| pagine indicizzate:', len(idx))
