# -*- coding: utf-8 -*-
"""Costruisce indice.json: per ogni pagina, le parole leggibili trovate dall'OCR.

L'OCR sulle pagine dei volantini restituisce molta spazzatura (sono immagini
disegnate, non testo). Il filtro qui sotto tiene solo le parole che hanno la
forma di una parola italiana; i prezzi non passano quasi mai, perche sono
numeri grandi e stilizzati che tesseract non riconosce. Per questo l'indice
serve a trovare LA PAGINA, e il prezzo si legge poi sul PDF.
"""
import glob, os, re, json

# aggiornare le date a ogni volantino nuovo
META = {
 'lidl':          ('Lidl',             'dal 3 al 9 settembre 2026 (sottocosto fino al 12)'),
 'eurospin':      ('Eurospin',         'dal 24 agosto al 6 settembre 2026'),
 'md':            ('MD',               'dal 25 agosto al 6 settembre 2026'),
 'bennet':        ('Bennet',           'dal 27 agosto al 9 settembre 2026'),
 'ipercoop':      ('Ipercoop',         'Sottocosto, dal 31 agosto al 9 settembre 2026'),
 'ipercoop_extra':('Ipercoop',         'Extra offerte, dal 27 agosto al 9 settembre 2026'),
 'carriper20':    ('Carrefour Iper',   'dal 20 agosto al 3 settembre 2026'),
 'carriper04':    ('Carrefour Iper',   'dal 4 settembre 2026'),
}
VOC = set('aeiouàèéìòù')

def plausibile(w):
    w = w.strip(" .,;:|_-–—•*()[]{}\"'”“’«»/\\!?")
    if not 4 <= len(w) <= 22:
        return None
    lw = w.lower()
    if not all(c.isalpha() or c in "'-" for c in lw):
        return None
    v = sum(1 for c in lw if c in VOC)
    if not 0.22 <= v / len(lw) <= 0.75:      # senza vocali, o tutte vocali: e rumore
        return None
    if re.search(r'(.)\1\1', lw):            # tre lettere uguali di fila: e rumore
        return None
    return lw

righe = []
for chiave, (insegna, validita) in sorted(META.items()):
    for f in sorted(glob.glob(f'ocr/{chiave}/*.txt')):
        parole = []
        for w in re.split(r'\s+', open(f, encoding='utf-8', errors='ignore').read()):
            p = plausibile(w)
            if p and p not in parole:
                parole.append(p)
        righe.append(dict(chiave=chiave, insegna=insegna, validita=validita,
                          pagina=int(os.path.basename(f)[:-4]),
                          parole=' '.join(sorted(parole))))
json.dump(righe, open('indice.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('pagine indicizzate:', len(righe))
