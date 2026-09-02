# -*- coding: utf-8 -*-
"""Assembla le pagine scaricate in un PDF per volantino."""
import glob, os
from PIL import Image

NOMI = {
 'lidl':       'Lidl',              'eurospin':   'Eurospin',
 'md':         'MD',                'bennet':     'Bennet',
 'carriper20': 'Carrefour Iper',    'carriper04': 'Carrefour Iper',
 'carrmarket': 'Carrefour Market',
}
os.makedirs('out', exist_ok=True)
for chiave in NOMI:
    pagine = sorted(glob.glob(f'pg/{chiave}/*.jpg'))
    if not pagine:
        continue
    immagini = []
    for f in pagine:
        im = Image.open(f).convert('RGB')
        if im.width > 1400:                       # 1400 px basta per leggere i prezzi
            im = im.resize((1400, int(im.height * 1400 / im.width)), Image.LANCZOS)
        immagini.append(im)
    out = f'out/{chiave}.pdf'
    immagini[0].save(out, save_all=True, append_images=immagini[1:], resolution=150.0)
    print(f'{out}  {len(immagini)} pagine  {os.path.getsize(out)/1e6:.1f} MB')
