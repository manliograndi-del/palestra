# -*- coding: utf-8 -*-
"""Dice quali volantini vanno rinnovati e butta via quelli vecchi.

Regole chieste da Manlio il 2026-09-02:
  - il volantino nuovo si prende **il giorno prima** che scada il vecchio,
    così non c'è mai un giorno con i prezzi sbagliati;
  - il vecchio si cancella **due giorni dopo** che è scaduto, per non
    ritrovarsi una collezione di PDF.

I due giorni di tolleranza non sono un capriccio: servono a poter ancora
guardare l'offerta di ieri se qualcosa non torna con lo scontrino.

    python3 pulisci.py           dice solo cosa farebbe
    python3 pulisci.py --fai     cancella davvero
"""
import datetime, os, shutil, sys
from dati import VOLANTINI

FAI = '--fai' in sys.argv
oggi = datetime.date.today()

da_rinnovare, da_cancellare = [], []
for chiave, insegna, periodo, pdf, fino in VOLANTINI:
    giorni = (datetime.date.fromisoformat(fino) - oggi).days
    if giorni <= 1:
        da_rinnovare.append((chiave, insegna, fino, giorni))
    if giorni < -2:
        da_cancellare.append((chiave, insegna, fino, giorni))

print(f'oggi è {oggi}\n')
if da_rinnovare:
    print('DA RINNOVARE (scadono domani o sono già scaduti):')
    for c, i, f, g in da_rinnovare:
        print(f'  {i:16s} {c:16s} scade {f} ({g:+d} giorni)')
else:
    print('Nessun volantino da rinnovare: sono tutti buoni per almeno due giorni.')

print()
if da_cancellare:
    print('DA CANCELLARE (scaduti da più di due giorni):')
    for c, i, f, g in da_cancellare:
        print(f'  {i:16s} {c:16s} scaduto il {f} ({-g} giorni fa)')
        if FAI:
            for percorso in (f'pg/{c}', f'ocr/{c}'):
                if os.path.isdir(percorso):
                    shutil.rmtree(percorso); print(f'      via {percorso}')
            for percorso in (f'out/{c}.pdf', f'consegna/{pdf}'):
                if os.path.isfile(percorso):
                    os.remove(percorso); print(f'      via {percorso}')
    if not FAI:
        print('\n  (prova soltanto: rilancia con --fai per cancellare davvero)')
else:
    print('Niente da cancellare.')

print('\nQuando ne cancelli uno, togli la sua riga anche da VOLANTINI in dati.py')
print('e le righe dei suoi prezzi da PRODOTTI, se no la pagina lo nomina ancora.')
