# -*- coding: utf-8 -*-
"""La lista di partenza, cioè quella con cui nasce la pagina la prima volta.

Dal 2026-09-02 la lista **vive dentro la pagina pubblicata** e la modificano
sia Manlio sia sua moglie: questa serve solo a far nascere la prima versione.
Dopo, comanda quella pubblicata, e questo file non la tocca più.

È la lista che Manlio mi ha incollato quel giorno, meno la carta igienica che
aveva tolto, più il suino che aveva aggiunto.

Ogni voce ha un nome (quello sul bottone), le parole con cui cercarla nei
volantini, e la categoria dei prezzi letti a mano in dati.py. L'OCR scrive
«bovino» dove il volantino dice carne di bue: con un nome solo non si trova.

In dati.py restano i prezzi anche di caffè, latte, pasta, detersivo e carta
igienica, che lui ha tolto: se uno dei due li rimette, i prezzi ci sono già.
"""
PARTENZA = [
 ("Carne di bue",   ["bovino", "bovina", "scottona", "macinato", "manzo", "hamburger"], "Carne di bue"),
 ("Tonno",          ["tonno"],                                                          "Tonno"),
 ("Salmone",        ["salmone"],                                                        "Salmone"),
 ("Suino",          ["suino", "maiale", "salsiccia", "lonza", "coppa", "pancetta"],      "Suino"),
 ("Pollo",          ["pollo", "petto", "cosce"],                                        "Pollo"),
 ("Formaggio",      ["formaggio", "parmigiano", "grana", "mozzarella", "gorgonzola"],   "Formaggio"),
 ("Uova",           ["uova", "uovo"],                                                   "Uova"),
 ("Olio d'oliva",   ["olio", "extravergine", "oliva"],                                  "Olio d'oliva"),
 # aggiunti da Manlio il 2026-09-04, con l'iniziale maiuscola come ha chiesto
 ("Biscotti",       ["biscotti", "biscotto", "frollini", "gocciole", "pavesini", "wafer"], "Biscotti"),
 ("Yogurt",         ["yogurt", "yoghurt", "kefir", "vasetti"],                            "Yogurt"),
 ("Marmellata",     ["marmellata", "confettura", "confetture", "fiordifrutta"],           "Marmellata"),
 ("Cioccolato",     ["cioccolato", "cioccolata", "tavoletta", "nutella", "cacao"],        "Cioccolato"),
]
