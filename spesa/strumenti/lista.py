# -*- coding: utf-8 -*-
"""I 12 prodotti di partenza della pagina.

Ognuno ha un nome (quello che si legge) e le parole con cui cercarlo: l'OCR
scrive «bovino» dove il volantino dice carne di bue, e «capsule» dove dice
caffè, quindi un nome solo non basta. Quando Manlio ne aggiunge uno dalla
pagina, la parola cercata è quella che ha scritto lui.

Il terzo campo è la categoria delle offerte lette a mano dal volantino. Ce l'hanno
solo i tre prodotti che ho letto pagina per pagina; per tutti gli altri la pagina
mostra soltanto in quali pagine dei volantini compare la parola, che è tutto
quello che so davvero. Senza questo legame «olio» pescava anche i tonni
all'olio d'oliva e sembravano offerte sull'olio.
"""
PARTENZA = [
 ("Carne di bue",   ["bovino", "bovina", "scottona", "macinato", "manzo", "hamburger"], "Carne di bue"),
 ("Tonno",          ["tonno"], "Tonno"),
 ("Salmone",        ["salmone"], "Salmone"),
 ("Caffè",          ["caffè", "caffe", "capsule", "cialde", "moka"], None),
 ("Latte",          ["latte"], None),
 ("Pasta",          ["pasta", "spaghetti", "penne", "fusilli"], None),
 ("Olio d'oliva",   ["olio", "extravergine", "oliva"], None),
 ("Pollo",          ["pollo", "petto", "cosce"], None),
 ("Formaggio",      ["formaggio", "parmigiano", "grana", "mozzarella", "gorgonzola"], None),
 ("Uova",           ["uova", "uovo"], None),
 ("Carta igienica", ["igienica", "rotoloni", "carta"], None),
 ("Detersivo",      ["detersivo", "lavatrice", "lavastoviglie", "ammorbidente"], None),
]
