#!/usr/bin/env python3
"""Costruisce scuole.html dal CSV dell'anagrafe delle scuole statali.

Il CSV del ministero pesa tredici megabyte e ripete migliaia di volte gli
stessi comuni, gli stessi istituti, gli stessi indirizzi web. Qui le colonne
che si ripetono diventano dizionari e ogni scuola resta una riga di indici:
la pagina finale scende sotto i cinque megabyte e continua a stare in un file
solo, senza chiamate alla rete.

    python3 strumenti/scuole-impacchetta.py SCUANAGRAFESTAT....csv

Scrive scuole.html nella radice del repository.
"""

import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
MODELLO = os.path.join(QUI, "scuole-modello.html")
USCITA = os.path.join(os.path.dirname(QUI), "scuole.html")


def ripulisci(v):
    """Il ministero scrive "Non Disponibile" al posto del vuoto."""
    v = v.strip()
    return "" if v.lower() == "non disponibile" else v


def b36(n):
    if n == 0:
        return "0"
    cifre = "0123456789abcdefghijklmnopqrstuvwxyz"
    s = ""
    while n:
        s = cifre[n % 36] + s
        n //= 36
    return s


class Dizionario:
    """Tiene una sola copia di ogni valore e ne restituisce la posizione."""

    def __init__(self):
        self.voci = []
        self.dove = {}

    def indice(self, v):
        if v not in self.dove:
            self.dove[v] = len(self.voci)
            self.voci.append(v)
        return self.dove[v]


def impacchetta(percorso_csv):
    with open(percorso_csv, encoding="utf-8-sig", newline="") as f:
        righe = list(csv.DictReader(f))
    if not righe:
        raise SystemExit("Il CSV e' vuoto.")

    prov = Dizionario()
    com = Dizionario()
    ist = Dizionario()
    tip = Dizionario()
    car = Dizionario()
    web = Dizionario()
    scuole = []

    for x in righe:
        ip = prov.indice("\t".join([x["PROVINCIA"], x["REGIONE"], x["AREAGEOGRAFICA"]]))
        ic = com.indice("\t".join([x["CODICECOMUNESCUOLA"], x["DESCRIZIONECOMUNE"], b36(ip)]))
        ii = ist.indice("\t".join([
            x["CODICEISTITUTORIFERIMENTO"],
            ripulisci(x["DENOMINAZIONEISTITUTORIFERIMENTO"]),
        ]))
        it = tip.indice(x["DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA"])
        ia = car.indice(x["DESCRIZIONECARATTERISTICASCUOLA"])
        iw = web.indice(ripulisci(x["SITOWEBSCUOLA"]))

        # Quasi tutte le scuole hanno la posta nella forma
        # CODICEISTITUTO@istruzione.it: quando e' cosi' non la scriviamo, la
        # pagina la ricostruisce. Il trattino distingue "assente davvero" da
        # "ricavabile dal codice".
        posta = ripulisci(x["INDIRIZZOEMAILSCUOLA"])
        atteso = x["CODICEISTITUTORIFERIMENTO"].lower() + "@istruzione.it"
        if not posta:
            posta = "-"
        elif posta.lower() == atteso:
            posta = ""

        bandiere = ("1" if x["INDICAZIONESEDEDIRETTIVO"] == "SI" else "0") \
                 + ("1" if x["SEDESCOLASTICA"] == "SI" else "0")

        scuole.append("\t".join([
            x["CODICESCUOLA"],
            ripulisci(x["DENOMINAZIONESCUOLA"]),
            ripulisci(x["INDIRIZZOSCUOLA"]),
            ripulisci(x["CAPSCUOLA"]),
            b36(ic), b36(ii), b36(it), b36(ia), b36(iw),
            bandiere,
            posta,
            ripulisci(x["INDIRIZZOPECSCUOLA"]),
            ripulisci(x["INDICAZIONESEDEOMNICOMPRENSIVO"]),
        ]).rstrip("\t"))

    blocchi = [
        ("ANNO", righe[0]["ANNOSCOLASTICO"]),
        ("PROV", "\n".join(prov.voci)),
        ("COM", "\n".join(com.voci)),
        ("IST", "\n".join(ist.voci)),
        ("TIP", "\n".join(tip.voci)),
        ("CAR", "\n".join(car.voci)),
        ("WEB", "\n".join(web.voci)),
        ("SCU", "\n".join(scuole)),
    ]
    # I dati finiscono dentro template literal: l'unico carattere da
    # proteggere e' la barra rovesciata (nel CSV ce ne sono cinque).
    dati = "\n".join(
        "const D_%s = `%s`;" % (nome, testo.replace("\\", "\\\\"))
        for nome, testo in blocchi
    )

    with open(MODELLO, encoding="utf-8") as f:
        modello = f.read()
    if "/*DATI*/" not in modello:
        raise SystemExit("Nel modello manca il segnaposto /*DATI*/.")
    with open(USCITA, "w", encoding="utf-8") as f:
        f.write(modello.replace("/*DATI*/", dati))

    print("scuole.html scritto: %d scuole, %d comuni, %d istituti, %.1f MB"
          % (len(scuole), len(com.voci), len(ist.voci),
             os.path.getsize(USCITA) / 1048576.0))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: scuole-impacchetta.py <anagrafe.csv>")
    impacchetta(sys.argv[1])
