#!/bin/bash
# Scarica le pagine dei volantini da anteprimavolantino.it.
# Le pagine hanno nomi prevedibili: volantino-<insegna>-<AAAA-MM-GG>-p-<NN>.jpg
# Le date e la larghezza del numero (2 o 5 cifre) cambiano a ogni volantino:
# vanno lette dalla pagina dell'articolo prima di lanciare questo.
set -u
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120"
B=https://www.anteprimavolantino.it/public/uploads
: > urls.txt
gen(){ nome=$1; base=$2; cifre=$3; mkdir -p "pg/$nome"
  for n in $(seq 1 60); do
    out="pg/$nome/$(printf '%03d' "$n").jpg"; [ -s "$out" ] && continue
    printf '%s %s%0*d.jpg\n' "$out" "$base" "$cifre" "$n" >> urls.txt
  done; }

# --- aggiornare queste righe a ogni volantino nuovo ---
gen lidl       "$B/2026/08/volantino-lidl-2026-09-03-p-" 2
gen eurospin   "$B/2026/08/volantino-eurospin-2026-08-24-p-" 2
gen md         "$B/2026/08/volantino-md-2026-08-25-p-" 2
gen bennet     "$B/2026/08/volantino-bennet-2026-08-27-p-" 5
gen carriper04 "$B/2026/09/volantino-carrefour-iper-2026-09-04-p-" 5
gen carrmarket "$B/2026/09/volantino-carrefour-market-2026-09-04-p-" 5

# -f fa fallire curl sui 404, cosi le pagine oltre la fine non restano come file vuoti
xargs -a urls.txt -P 12 -n 2 sh -c 'curl -sSf -o "$0" --max-time 35 -A "'"$UA"'" "$1" || rm -f "$0"'
for d in pg/*/; do echo "$(basename "$d"): $(ls "$d" | wc -l) pagine"; done
