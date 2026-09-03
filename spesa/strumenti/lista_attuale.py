# -*- coding: utf-8 -*-
"""Tira fuori la lista dalla pagina pubblicata e la scrive in lista-attuale.json.

Da lanciare PRIMA di pagina.py a ogni aggiornamento dei volantini, altrimenti
si ripubblica la lista di lista.py e si cancella quella che Manlio e sua moglie
si sono fatti.

    (leggere l'artifact con lo strumento Artifact, action "read", salvarlo)
    python3 lista_attuale.py pagina-viva.html
    python3 pagina.py
"""
import json, re, sys

sorgente = sys.argv[1] if len(sys.argv) > 1 else 'pagina-viva.html'
testo = open(sorgente, encoding='utf-8').read()

m = re.search(r'^const LISTA_PUBBLICATA = (.*);$', testo, re.M)
if not m:
    sys.exit('Non trovo la lista nella pagina. Fermati: rigenerare adesso la cancella.')

grezzo = m.group(1)
# nel documento pubblicato «</» e scritto «<\/» per non chiudere lo <script>
lista = json.loads(grezzo.replace('<\\/', '</'))
if not isinstance(lista, list) or not lista:
    sys.exit('La lista trovata è vuota o malformata. Fermati.')

json.dump(lista, open('lista-attuale.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(f'{len(lista)} prodotti ripresi:', ', '.join(v.get('nome', '?') for v in lista))
