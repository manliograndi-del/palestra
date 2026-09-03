#!/bin/bash
# OCR di tutte le pagine scaricate. Serve: apt-get install -y tesseract-ocr tesseract-ocr-ita
# In sequenza di proposito: con xargs -P su questa macchina si pianta e non produce niente.
set -u
ls pg/*/*.jpg | while read -r f; do
  n=$(echo "$f" | cut -d/ -f2); b=$(basename "$f" .jpg); mkdir -p "ocr/$n"
  [ -s "ocr/$n/$b.txt" ] || tesseract "$f" "ocr/$n/$b" -l ita --psm 11 >/dev/null 2>&1
done
for d in ocr/*/; do echo "$(basename "$d"): $(find "$d" -name '*.txt' | wc -l)"; done
