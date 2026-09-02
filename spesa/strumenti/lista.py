# -*- coding: utf-8 -*-
"""I 12 prodotti di partenza della pagina.

Ognuno ha un nome (quello che si legge) e le parole con cui cercarlo: l'OCR
scrive «bovino» dove il volantino dice carne di bue, e «capsule» dove dice
caffè, quindi un nome solo non basta. Quando Manlio ne aggiunge uno dalla
pagina, la parola cercata è quella che ha scritto lui.

Il terzo campo è la categoria delle offerte lette a mano dal volantino. Dal
2026-09-02 ce l'hanno tutti e dodici: Manlio ha chiesto i prezzi anche per le
categorie che avevo messo io, e le ho lette pagina per pagina come le prime tre.
Serve il legame esplicito perché la ricerca per testo sbagliava: «olio» pescava
i tonni all'olio d'oliva e sembravano offerte sull'olio.

Un prodotto aggiunto a mano dalla pagina non ha categoria e mostra solo le
pagine dei volantini — a meno che quello che scrive non combaci con il nome o
con una delle parole di uno di questi dodici, e allora la pagina glielo lega da
sola.
"""
PARTENZA = [
 ("Carne di bue",   ["bovino", "bovina", "scottona", "macinato", "manzo", "hamburger"], "Carne di bue"),
 ("Tonno",          ["tonno"], "Tonno"),
 ("Salmone",        ["salmone"], "Salmone"),
 ("Caffè",          ["caffè", "caffe", "capsule", "cialde", "moka"], "Caffè"),
 ("Latte",          ["latte"], "Latte"),
 ("Pasta",          ["pasta", "spaghetti", "penne", "fusilli"], "Pasta"),
 ("Olio d'oliva",   ["olio", "extravergine", "oliva"], "Olio d'oliva"),
 ("Pollo",          ["pollo", "petto", "cosce"], "Pollo"),
 ("Formaggio",      ["formaggio", "parmigiano", "grana", "mozzarella", "gorgonzola"], "Formaggio"),
 ("Uova",           ["uova", "uovo"], "Uova"),
 ("Carta igienica", ["igienica", "rotoloni", "carta"], "Carta igienica"),
 ("Detersivo",      ["detersivo", "lavatrice", "lavastoviglie", "ammorbidente"], "Detersivo"),
]
