# -*- coding: utf-8 -*-
"""Genera la pagina web da pubblicare.

Prodotti e prezzi da dati.py, lista di partenza da lista.py.

Due scelte volute, chieste da Manlio il 2026-09-02 dopo aver provato la
prima versione:

1. TEMA CHIARO FISSO. Niente blocco `prefers-color-scheme: dark`: il suo
   telefono è in modalità notte e la pagina gli si apriva nera («così non
   si può vedere»). Sfondo bianco dichiarato esplicitamente, così tiene
   anche se chi ospita la pagina è scuro.
2. BOTTONI IN CIMA. I prodotti sono bottoni in testa alla pagina; toccarne
   uno riempie la lista qui sotto, già ordinata dal meno caro. Prima erano
   schede da aprire e chiudere una per una, e per arrivare al tonno
   toccava scorrere.

La lista vive in localStorage, non sul server: vedi NOTE.md.
"""
import json, os, glob
from dati import PRODOTTI, VOLANTINI, UNITA, D
from lista import PARTENZA

PDF     = {c: f for c, _, _, f, _ in VOLANTINI}
PERIODO = {c: p for c, _, p, _, _ in VOLANTINI}

offerte = [dict(cat=cat, ins=ins, rep=rep, pro=pro, fmt=fmt, prezzo=pre,
                unitario=round(pre / qta, 3), pag=pag, pdf=PDF[chiave],
                periodo=PERIODO[chiave], dubbio=(fon == D), note=note)
           for cat, ins, chiave, rep, pro, fmt, qta, pre, pag, fon, note in PRODOTTI]

idx = json.load(open('indice.json', encoding='utf-8'))
validi = {(os.path.basename(os.path.dirname(f)), int(os.path.basename(f)[:-4]))
          for f in glob.glob('pg/*/*.jpg')}
pagine = sorted((dict(ins=r['insegna'], periodo=r['validita'], pdf=PDF.get(r['chiave'], ''),
                      pag=r['pagina'], parole=r['parole'])
                 for r in idx if (r['chiave'], r['pagina']) in validi),
                key=lambda r: (r['ins'], r['periodo'], r['pag']))

volantini = [v for v in (dict(ins=i, periodo=p, pdf=f,
                              pagine=len([x for x in pagine if x['pdf'] == f]))
                         for c, i, p, f, _ in VOLANTINI) if v['pagine']]

partenza = [dict(nome=n, parole=p, cat=c) for n, p, c in PARTENZA]

# LA LISTA CHE COMANDA E QUELLA CHE HANNO LORO.
# Manlio e la moglie aggiungono e tolgono prodotti dalla pagina pubblicata. Se
# l'aggiornamento settimanale dei volantini ripartisse da PARTENZA, gliela
# cancellerebbe tutta a ogni giro. Quindi: prima di rigenerare, si legge la
# lista dalla pagina viva (lista_attuale.py la tira fuori e la scrive qui) e si
# riparte da quella. PARTENZA serve solo se il file non c'e, cioe la prima volta.
lista_viva = 'lista-attuale.json'
if os.path.exists(lista_viva):
    salvata = json.load(open(lista_viva, encoding='utf-8'))
    if isinstance(salvata, list) and salvata:
        partenza = salvata
        print(f'lista ripresa dalla pagina viva: {len(partenza)} prodotti')

DATI = json.dumps(dict(offerte=offerte, pagine=pagine, volantini=volantini,
                       partenza=partenza, unita={k: v[0] for k, v in UNITA.items()},
                       letto='4 settembre 2026'),
                  ensure_ascii=False, separators=(',', ':'))
LISTA0 = json.dumps(partenza, ensure_ascii=False, separators=(',', ':'))

HTML = r'''<title>Spesa</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Asap:wght@400;500;600;700&family=Oswald:wght@500;600;700&display=swap">
<style>
/* Tema chiaro unico e dichiarato: nessun blocco scuro, perché la pagina
   si apriva nera sul telefono di Manlio in modalità notte. */
:root{
  --carta:#FFFFFF;
  --pannello:#F6F5F2;
  --inchiostro:#1B1B1A;
  --tenue:#6E6C66;
  --linea:#E5E3DD;
  --linea-forte:#CFCCC4;
  --rosso:#D40D2B;
  --su-rosso:#FFFFFF;
  --verde:#1E7A4B;
  --verde-tenue:#E6F3EC;
  --ambra:#8A5A08;
  --ambra-tenue:#FCF2DE;
  --f-testo:'Asap',ui-sans-serif,system-ui,'Segoe UI',sans-serif;
  --f-prezzo:'Oswald','Arial Narrow',ui-sans-serif,sans-serif;
  color-scheme:light;
}
*{box-sizing:border-box}
html{background:var(--carta)}
body{background:var(--carta);color:var(--inchiostro);font-family:var(--f-testo);
  font-size:16px;line-height:1.45;-webkit-text-size-adjust:100%}
button{font-family:var(--f-testo);color:inherit}
:focus-visible{outline:3px solid var(--rosso);outline-offset:2px}
.guscio{max-width:800px;margin:0 auto;padding:0 15px 60px}

/* ---- testa ---- */
header{padding:20px 0 2px}
h1{font-family:var(--f-prezzo);font-weight:700;font-size:26px;letter-spacing:.01em;
  line-height:1.05;margin:0;text-transform:uppercase}
h1 span{display:block;color:var(--rosso);font-size:12px;letter-spacing:.16em;margin-bottom:6px}
.sottotitolo{color:var(--tenue);margin:8px 0 0;font-size:14px;max-width:62ch}

/* ---- barra dei prodotti ---- */
.barra{position:sticky;top:0;z-index:20;background:var(--carta);
  padding:12px 0 12px;border-bottom:2px solid var(--inchiostro);margin-top:14px}
.tasti{display:flex;flex-wrap:wrap;gap:8px}
.tasto{background:var(--carta);border:1.5px solid var(--linea-forte);border-radius:99px;
  padding:10px 15px;font-size:15px;font-weight:600;cursor:pointer;line-height:1.1;
  min-height:44px;white-space:nowrap}
.tasto[aria-pressed="true"]{background:var(--rosso);border-color:var(--rosso);color:var(--su-rosso)}
.tasto.agg{border-style:dashed;color:var(--tenue);font-weight:500}

/* ---- aggiunta ---- */
.form-agg{display:none;gap:8px;margin-top:10px}
.form-agg.on{display:flex}
.form-agg input{flex:1;min-width:0;background:var(--carta);color:var(--inchiostro);
  border:1.5px solid var(--rosso);border-radius:10px;padding:12px 13px;
  font-family:var(--f-testo);font-size:16px}
.form-agg input:focus{outline:none}
.form-agg button{background:var(--rosso);color:var(--su-rosso);border:0;border-radius:10px;
  padding:0 18px;font-size:15px;font-weight:600;cursor:pointer;min-height:46px}

/* ---- intestazione del risultato ---- */
.capo{display:flex;align-items:baseline;justify-content:space-between;gap:10px;
  flex-wrap:wrap;margin:20px 0 2px}
.capo h2{font-family:var(--f-prezzo);text-transform:uppercase;letter-spacing:.02em;
  font-size:22px;font-weight:600;margin:0}
.capo .quanti{color:var(--tenue);font-size:13px;font-variant-numeric:tabular-nums}
.sinonimi{margin:6px 0 0;font-size:13.5px;color:var(--tenue);display:flex;
  flex-wrap:wrap;gap:6px;align-items:baseline}
.sinonimi em{font-style:normal;background:var(--pannello);border:1px solid var(--linea);
  border-radius:99px;padding:2px 9px;font-size:13px;color:var(--inchiostro)}
.gestisci{display:flex;gap:9px;margin:12px 0 0;flex-wrap:wrap}
.gestisci button{background:var(--carta);border:1.5px solid var(--linea-forte);border-radius:9px;
  padding:10px 16px;font-size:14.5px;font-weight:600;cursor:pointer;min-height:44px}
.gestisci .togli{border-color:var(--rosso);color:var(--rosso)}
.form-rin{display:none;gap:8px;margin-top:10px}
.form-rin.on{display:flex}
.form-rin input{flex:1;min-width:0;border:1.5px solid var(--rosso);border-radius:10px;
  padding:12px 13px;font-family:var(--f-testo);font-size:16px;background:var(--carta);
  color:var(--inchiostro)}
.form-rin input:focus{outline:none}
.form-rin button{background:var(--rosso);color:var(--su-rosso);border:0;border-radius:10px;
  padding:0 18px;font-size:15px;font-weight:600;cursor:pointer;min-height:46px}

/* ---- elenco prezzi ---- */
.fascia{font-family:var(--f-prezzo);text-transform:uppercase;letter-spacing:.06em;
  font-size:12.5px;font-weight:600;color:var(--tenue);margin:22px 0 0}
.prezzo-riga{display:grid;grid-template-columns:1fr auto;gap:3px 14px;
  padding:13px 0;border-top:1px solid var(--linea)}
.prezzo-riga:first-of-type{border-top:1.5px solid var(--inchiostro)}
.prezzo-riga .nome{margin:0;font-size:16.5px;font-weight:600;line-height:1.25}
.prezzo-riga .sotto{margin:3px 0 0;color:var(--tenue);font-size:13.5px}
.prezzo-riga .sotto b{color:var(--inchiostro);font-weight:600}
.prezzo-riga .val{grid-row:1/3;text-align:right;font-family:var(--f-prezzo);
  font-variant-numeric:tabular-nums;line-height:1;white-space:nowrap}
.prezzo-riga .val .n{display:block;font-size:27px;font-weight:700;color:var(--rosso)}
.prezzo-riga .val .u{display:block;font-family:var(--f-testo);font-size:10.5px;
  letter-spacing:.08em;text-transform:uppercase;color:var(--tenue);margin-top:4px}
.prezzo-riga .coda{grid-column:1/-1;margin:7px 0 0;display:flex;flex-wrap:wrap;gap:6px;
  align-items:center}
.bollo{font-size:11.5px;letter-spacing:.05em;text-transform:uppercase;font-weight:700;
  border-radius:5px;padding:3px 8px}
.bollo.meno{background:var(--verde-tenue);color:var(--verde)}
.bollo.dubbio{background:var(--ambra-tenue);color:var(--ambra)}
.prezzo-riga .nota{grid-column:1/-1;margin:6px 0 0;font-size:13.5px;color:var(--tenue)}
.prezzo-riga .dove{grid-column:1/-1;margin:6px 0 0;font-size:13px;color:var(--tenue);
  border-left:3px solid var(--linea);padding-left:9px}

/* ---- elenco pagine ---- */
.pag-riga{display:flex;justify-content:space-between;align-items:baseline;gap:12px;
  padding:11px 0;border-top:1px solid var(--linea);font-size:14.5px}
.pag-riga:first-of-type{border-top:1.5px solid var(--inchiostro)}
.pag-riga .ins{font-weight:600}
.pag-riga .per{display:block;color:var(--tenue);font-size:12.5px;font-weight:400}
.pag-riga .np{font-family:var(--f-prezzo);font-size:19px;font-weight:600;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.altre{width:100%;margin-top:12px;background:var(--pannello);border:1.5px solid var(--linea);
  border-radius:10px;padding:12px;font-size:14.5px;font-weight:600;cursor:pointer;min-height:46px}
.vuoto{color:var(--tenue);font-size:14.5px;margin:14px 0 0;background:var(--pannello);
  border-radius:10px;padding:14px}

/* ---- coda ---- */
.manda{margin-top:30px;border:2px solid var(--inchiostro);border-radius:12px;padding:16px}
.manda h2{font-family:var(--f-prezzo);text-transform:uppercase;font-size:15px;
  letter-spacing:.04em;margin:0 0 8px}
.manda p{font-size:14px;margin:0 0 12px;color:var(--tenue)}
.manda button{background:var(--inchiostro);color:var(--carta);border:0;border-radius:10px;
  padding:13px 18px;font-size:15px;font-weight:600;cursor:pointer;min-height:48px;width:100%}
.manda textarea{display:none;width:100%;margin-top:12px;min-height:150px;resize:vertical;
  font-family:ui-monospace,'SF Mono',Menlo,monospace;font-size:13px;line-height:1.5;
  background:var(--pannello);color:var(--inchiostro);border:1.5px solid var(--linea);
  border-radius:10px;padding:11px}
.manda textarea.on{display:block}
.manda .esito{font-size:13.5px;margin:10px 0 0;color:var(--verde);font-weight:600;min-height:1.2em}
.spiega{margin-top:34px;background:var(--pannello);border-radius:12px;padding:16px 16px 4px}
.spiega h2{font-family:var(--f-prezzo);text-transform:uppercase;font-size:15px;
  letter-spacing:.04em;margin:0 0 10px}
.spiega p{font-size:14px;margin:0 0 12px}
.spiega .ev{color:var(--ambra);font-weight:700}
.vol{list-style:none;padding:0;margin:10px 0 0;display:grid;gap:1px;background:var(--linea);
  border:1px solid var(--linea);border-radius:10px;overflow:hidden}
.vol li{background:var(--carta);padding:11px 13px;display:flex;justify-content:space-between;
  align-items:baseline;gap:12px;font-size:14px}
.vol .i{font-weight:600}
.vol .p{color:var(--tenue);font-size:13px}
.vol .n{color:var(--tenue);font-size:12.5px;font-variant-numeric:tabular-nums;white-space:nowrap}
footer{margin-top:28px;padding-top:14px;border-top:1px solid var(--linea);
  color:var(--tenue);font-size:13px}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>

<div class="guscio">
<header>
  <h1><span>Torino · Corso Siracusa</span>La lista della spesa</h1>
  <p class="sottotitolo">Tocca un prodotto: qui sotto compaiono le offerte, dalla più
  conveniente in giù. Volantini di Lidl, Eurospin, MD, Bennet, Ipercoop e Carrefour Iper.</p>
</header>

<div class="barra">
  <div class="tasti" id="tasti" role="group" aria-label="Scegli il prodotto"></div>
  <form class="form-agg" id="form-agg">
    <input id="nuovo" type="text" placeholder="Nome del prodotto, o più nomi separati da virgola"
           autocomplete="off" aria-label="Nomi del prodotto da aggiungere, separati da virgola">
    <button type="submit">Aggiungi</button>
  </form>
  <p class="stato" id="stato-lista" role="status"></p>
</div>

<div id="risultato"></div>

<section class="manda" id="riquadro-manda">
  <h2>Mandami la tua lista</h2>
  <p id="perche-manda">Se la lista è condivisa non serve: la leggo da solo dalla pagina.
  Serve solo su una copia che gira per conto suo, come il file salvato sul telefono.</p>
  <button type="button" id="btn-copia">Copia la mia lista</button>
  <p class="esito" id="esito" role="status"></p>
  <textarea id="testo-lista" readonly aria-label="La tua lista, da copiare"></textarea>
</section>

<section class="spiega">
  <h2>Come leggerla</h2>
  <p>I <b>dodici prodotti di partenza</b> hanno i prezzi letti a mano, uno per uno, dalle pagine
  dei volantini. Il confronto è per unità e cambia col prodotto: la carne al chilo, il latte al
  litro, le uova all'uovo, la carta igienica al rotolo, il detersivo a lavaggio. Al chilo il
  detersivo darebbe un numero vero e inutile.</p>
  <p>Se <b>aggiungi un prodotto nuovo</b>, quello i prezzi non ce li ha ancora: ti dice in quali pagine
  dei volantini compare la parola, e il prezzo lo leggi tu aprendo il PDF a quella pagina. Se
  però scrivi una parola che questa pagina già conosce — «caffe», «bovino», «uovo» — si
  riaggancia da sola ai prezzi giusti.</p>
  <p><b>La stessa cosa si chiama in modi diversi</b>, e il volantino ne usa uno solo: quello che
  tu chiami detersivo lì è scritto «lavatrice», la carne di bue è «bovino» o «scottona». Perciò
  puoi mettere <b>più nomi separati da virgola</b> — per esempio
  <i>yogurt, yogurth, vasetti</i> — e la pagina ti trova tutte le pagine dove compare
  <b>almeno uno</b> di quei nomi. Il primo è quello che leggi sul bottone, gli altri lavorano
  sotto e te li fa vedere sotto il titolo. Vale anche su «Cambia nome»: si apre già con tutti i
  nomi che sta usando, e li correggi.</p>
  <p>Le righe segnate <span class="ev">da controllare</span> vengono da riassunti trovati
  online e possono essere sbagliate: di errori così ne ho già trovati tre.</p>
  <p>Certi prezzi valgono <b>solo con la tessera</b> — soci Coop, Lidl Plus, Bennet Club — e
  qualche riga confronta cose diverse fra loro: il caffè in capsule al chilo costa sempre molto
  più del macinato, e l'ammorbidente non è detersivo. Sta scritto nella riga.</p>
  <p>Le parole le ha lette il computer dalle immagini: sulle scritte grandi spesso sbaglia. Se
  un prodotto dà zero pagine può esserci lo stesso, prova a chiamarlo in un altro modo.</p>

  <h2 style="margin-top:18px">Quando arrivano le offerte nuove</h2>
  <p>I prezzi qui sopra sono dei volantini <b id="letto"></b>. Quando escono quelli nuovi
  <b>la pagina si aggiorna da sola</b>: chi l'ha aperta col link ricarica e vede i prezzi nuovi,
  senza premere niente e senza che nessuno debba rimandare niente. Vale per chiunque abbia il
  link, da qualsiasi telefono.</p>
  <p>L'unica copia che <b>non</b> si aggiorna è il file salvato sul telefono: quello resta fermo
  al giorno in cui è stato fatto. Se ti interessa avere sempre i prezzi giusti, usa il link.</p>
  <p><b>La lista dei prodotti è una sola, condivisa.</b> Chi apre il link vede la stessa, e se
  la cambia la cambia per tutti: aggiungere e togliere prodotti lo può fare chiunque abbia il
  link. Quando qualcuno la tocca, gli altri schermi si aggiornano da soli. In cima alla pagina
  c'è scritto se la copia che stai guardando è condivisa o no.</p>
  <p>Un prodotto aggiunto adesso mostra <b>subito le pagine</b> dove compare, ma i
  <b>prezzi arrivano dopo</b>: quelli vanno letti dalle pagine dei volantini a occhio, non c'è
  modo di ricavarli da soli. Quando li ho letti compaiono anche quelli, senza che dobbiate
  rifare niente.</p>

  <h2 style="margin-top:18px">I volantini</h2>
  <ul class="vol" id="vol"></ul>
  <p style="margin-top:12px">Mercatò non c'è: il loro sito non pubblica il volantino in un
  formato che si riesca a scaricare.</p>
</section>

<footer>Volantini letti il 2 settembre 2026. I numeri di pagina sono quelli dei PDF.</footer>
</div>

<script>
const DATI = __DATI__;

/* La lista non e piu solo mia: vive DENTRO questa pagina pubblicata, cosi la
   vedono e la cambiano tutti quelli che hanno il link. Quando qualcuno la
   tocca, la pagina si ripubblica con la lista nuova dentro e ogni schermo
   aperto si ricarica su quella. Vedi NOTE.md per il perche di questa strada
   invece della memoria sul server. */
const LISTA_PUBBLICATA = __LISTA__;
const TEMPLATE = __TEMPLATE__;

/* Vero solo nella copia pubblicata su Claude, dove la lista e davvero
   condivisa e comanda quella dentro la pagina. Sul sito e falso: li dentro non
   c'e niente che possa aggiornare la lista incorporata, quindi comanda quella
   che l'utente si e fatto nel suo browser, altrimenti le sue modifiche
   sparirebbero a ogni ricaricamento. */
const CONDIVISA = __CONDIVISA__;
const CHIAVE = 'spesa.lista.v1';

/* Rimette insieme il documento intero con dentro una lista nuova. L'ordine
   conta: prima la lista, poi il template. Al contrario, il template appena
   infilato porterebbe dentro un altro __LISTA__ e verrebbe riempito quello
   sbagliato. Le barre si spezzano in <\/ perche il tag di chiusura dello
   script, scritto per esteso dentro una stringa, chiuderebbe lo script per
   davvero: il browser lo cerca nel testo, non gli importa che sia in una
   stringa o in un commento. */
function documento(nuova) {
  const l = JSON.stringify(nuova).split('</').join('<\\/');
  const t = JSON.stringify(TEMPLATE).split('</').join('<\\/');
  /* Il modello va SEMPRE per ultimo: appena infilato porta dentro una copia di
     tutti gli altri segnaposto, e da quel momento replace() troverebbe quelli
     invece dei veri. Chi si ripubblica e sempre la copia condivisa. */
  return TEMPLATE
    .replace('__LISTA__', () => l)
    .replace('__CONDIVISA__', () => 'true')
    .replace('__TEMPLATE__', () => t);
}

const norm = s => (s || '').toLowerCase()
  .normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/['\u2019]/g, ' ');
/* i detersivi stanno sotto i 20 centesimi a lavaggio: con due decimali
   diventerebbero tutti «0,14 €» e non si distinguerebbero piu */
const eur = n => (n < 1 ? n.toFixed(3) : n.toFixed(2)).replace('.', ',');

/* Dove la lista e condivisa comanda quella dentro la pagina: e quella che
   vedono tutti, e viene aggiornata ripubblicando. Dove non lo e (il sito, il
   file) comanda quella che l'utente si e fatto: nessuno aggiornera mai quella
   incorporata, che li vale solo come punto di partenza. */
function leggiLista() {
  const dentro = Array.isArray(LISTA_PUBBLICATA) && LISTA_PUBBLICATA.length
    ? LISTA_PUBBLICATA.map(riaggancia) : null;
  if (CONDIVISA && dentro) return dentro;
  try {
    const g = localStorage.getItem(CHIAVE);
    if (g) { const v = JSON.parse(g); if (Array.isArray(v) && v.length) return v.map(riaggancia); }
  } catch (e) { /* memoria non disponibile: si riparte da quella incorporata */ }
  return dentro || DATI.partenza.map(p => ({ ...p }));
}

/* Una lista salvata da una versione vecchia della pagina puo avere prodotti
   senza categoria — quando i prezzi letti a mano coprivano solo carne, tonno e
   salmone. Qui si riattaccano ai prezzi che nel frattempo sono arrivati, senza
   toccare i nomi che l'utente si e scelto. Chi ha aggiunto un prodotto suo che
   non corrisponde a niente resta com'e. */
function riaggancia(v) {
  if (!v || !v.nome) return v;
  if (v.cat) return v;
  const nomi = [v.nome].concat(v.parole || []).map(norm);
  const seme = DATI.partenza.find(x =>
    nomi.includes(norm(x.nome)) || (x.parole || []).some(w => nomi.includes(norm(w))));
  if (!seme) return v;
  const parole = (v.parole || []).slice();
  seme.parole.forEach(p => { if (!parole.some(x => norm(x) === norm(p))) parole.push(p); });
  return { nome: v.nome, parole, cat: seme.cat };
}
function salvaLocale() {
  try { localStorage.setItem(CHIAVE, JSON.stringify(lista)); }
  catch (e) { /* la pagina funziona lo stesso, solo non ricorda */ }
}

let ART = null;          // la capacita di ripubblicare, se questa vista ce l'ha
let soloMio = true;      // finche non sappiamo il contrario, la lista e solo qui
let attesa = null;       // per non ripubblicare a ogni singolo tocco

function stato(testo, brutto) {
  const e = document.getElementById('stato-lista');
  if (!e) return;
  e.textContent = testo;
  e.className = 'stato' + (brutto ? ' brutto' : '');
}

/* Si ripubblica dopo un attimo, non a ogni tocco: chi ne toglie tre di fila
   fa una pubblicazione sola invece di tre, e gli altri schermi si ricaricano
   una volta sola. */
function salva() {
  salvaLocale();
  if (!ART || soloMio || !TEMPLATE) return;
  stato('Sto salvando per tutti…');
  clearTimeout(attesa);
  attesa = setTimeout(async () => {
    try {
      await ART.publish(documento(lista));
      stato('Salvata. La vedono tutti quelli che hanno il link.');
    } catch (err) {
      const c = err && err.code;
      if (c === 'conflict') {
        /* qualcun altro ha salvato nel frattempo: ogni schermo si ricarica
           sulla sua versione, quindi qui non si insiste */
        stato('Nel frattempo l\'ha cambiata qualcun altro: fra un attimo vedi la sua.');
      } else if (c === 'not_writer' || c === 'not_granted') {
        soloMio = true;
        stato('Puoi solo guardare la lista di chi te l\'ha mandata: le tue modifiche restano su questo telefono.', true);
      } else {
        stato('Non sono riuscito a salvarla per tutti. Resta su questo telefono.', true);
      }
    }
  }, 1200);
}


let lista = leggiLista();
let scelto = 0;
let tutteLePagine = false;

const offerteDi = v => v.cat ? DATI.offerte.filter(o => o.cat === v.cat) : [];

/* Le pagine dei volantini dove compare almeno uno dei nomi del prodotto.
   Se non ha nomi alternativi si cerca il nome stesso. */
const pagineDi = v => {
  const termini = (v.parole && v.parole.length ? v.parole : [v.nome]).map(norm);
  return DATI.pagine.filter(p => {
    const dentro = norm(p.parole);
    return termini.some(t => dentro.includes(t));
  });
};

/* tutti i nomi di un prodotto: quello sul bottone piu gli altri con cui cercarlo */
function nomiDi(v) {
  const out = [v.nome];
  (v.parole || []).forEach(p => { if (norm(p) !== norm(v.nome)) out.push(p); });
  return out;
}

/* Un prodotto si puo chiamare in piu modi, e il volantino ne usa uno solo:
   «detersivo» o «lavatrice», «carne di bue» o «bovino». Qui si scrivono tutti,
   separati da virgola, e la pagina cerca le pagine dove compare ALMENO UNO.
   Il primo nome e quello che si legge sul bottone, gli altri lavorano sotto.
   Se uno dei nomi e gia noto (uno dei dodici di partenza, o una delle sue
   parole), si porta dietro anche i prezzi letti a mano e le sue parole. */
function costruisci(testo) {
  const termini = testo.split(/[,;]+/).map(x => x.trim()).filter(Boolean);
  if (!termini.length) return null;
  let seme = null;
  for (const t of termini) {
    const n = norm(t);
    seme = DATI.partenza.find(x => norm(x.nome) === n || (x.parole || []).some(w => norm(w) === n));
    if (seme) break;
  }
  const parole = [];
  for (const p of termini.concat(seme ? seme.parole : [])) {
    if (!parole.some(x => norm(x) === norm(p))) parole.push(p);
  }
  return { nome: termini[0], parole, cat: seme ? seme.cat : null };
}

/* ---------- barra dei prodotti ---------- */
function disegnaTasti() {
  const box = document.getElementById('tasti');
  box.textContent = '';
  lista.forEach((v, i) => {
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'tasto'; b.textContent = v.nome;
    b.setAttribute('aria-pressed', String(i === scelto));
    b.onclick = () => {
      scelto = i; tutteLePagine = false;
      document.getElementById('form-agg').classList.remove('on');
      disegna();
    };
    box.appendChild(b);
  });
  const piu = document.createElement('button');
  piu.type = 'button'; piu.className = 'tasto agg'; piu.textContent = '+ aggiungi';
  piu.onclick = () => {
    const f = document.getElementById('form-agg');
    f.classList.add('on');
    document.getElementById('nuovo').focus();
  };
  box.appendChild(piu);
}

/* ---------- righe ---------- */
function rigaPrezzo(o, primo) {
  const d = document.createElement('article');
  d.className = 'prezzo-riga';
  d.innerHTML = `<div><p class="nome"></p><p class="sotto"></p></div>
    <p class="val"><span class="n"></span><span class="u"></span></p>
    <div class="coda"></div>`;
  d.querySelector('.nome').textContent = o.pro;
  const s = d.querySelector('.sotto');
  s.innerHTML = '<b></b> · <span></span> · <span></span>';
  s.querySelector('b').textContent = o.ins;
  s.querySelectorAll('span')[0].textContent = o.fmt;
  s.querySelectorAll('span')[1].textContent = eur(o.prezzo) + ' € la confezione';
  d.querySelector('.val .n').textContent = eur(o.unitario) + ' €';
  d.querySelector('.val .u').textContent = DATI.unita[o.cat] || 'al kg';
  const coda = d.querySelector('.coda');
  if (primo) coda.insertAdjacentHTML('beforeend', '<span class="bollo meno">il meno caro</span>');
  if (o.dubbio) coda.insertAdjacentHTML('beforeend', '<span class="bollo dubbio">da controllare</span>');
  if (!coda.children.length) coda.remove();
  if (o.note) {
    const n = document.createElement('p'); n.className = 'nota'; n.textContent = o.note;
    d.appendChild(n);
  }
  const w = document.createElement('p');
  w.className = 'dove';
  w.textContent = o.pag ? `${o.pdf} — pagina ${o.pag}` : `${o.pdf} — pagina non individuata`;
  d.appendChild(w);
  return d;
}

function rigaPagina(p) {
  const d = document.createElement('div');
  d.className = 'pag-riga';
  d.innerHTML = `<span><span class="ins"></span><span class="per"></span></span><span class="np"></span>`;
  d.querySelector('.ins').textContent = p.ins;
  d.querySelector('.per').textContent = p.periodo;
  d.querySelector('.np').textContent = 'pag. ' + p.pag;
  return d;
}

/* ---------- pagina ---------- */
function disegna() {
  disegnaTasti();
  const out = document.getElementById('risultato');
  out.textContent = '';
  if (!lista.length) {
    out.innerHTML = '<p class="vuoto">La lista è vuota. Tocca «+ aggiungi» per rimetterci qualcosa.</p>';
    return;
  }
  if (scelto >= lista.length) scelto = lista.length - 1;

  const v = lista[scelto];
  const off = offerteDi(v), pag = pagineDi(v);

  const capo = document.createElement('div');
  capo.className = 'capo';
  capo.innerHTML = '<h2></h2><span class="quanti"></span>';
  capo.querySelector('h2').textContent = v.nome;
  capo.querySelector('.quanti').textContent = off.length
    ? `${off.length} ${off.length === 1 ? 'offerta letta' : 'offerte lette'} dal volantino · ${pag.length} pagine da guardare`
    : `${pag.length} ${pag.length === 1 ? 'pagina lo nomina' : 'pagine lo nominano'}`;
  out.appendChild(capo);

  const altri = nomiDi(v).slice(1);
  if (altri.length) {
    const p = document.createElement('p');
    p.className = 'sinonimi';
    p.innerHTML = '<span></span> ';
    p.querySelector('span').textContent = 'cerca anche:';
    altri.forEach(a => {
      const c = document.createElement('em');
      c.textContent = a;
      p.appendChild(c);
    });
    out.appendChild(p);
  }

  const g = document.createElement('div');
  g.className = 'gestisci';
  const bRin = document.createElement('button');
  bRin.type = 'button'; bRin.textContent = 'Cambia nome';
  const bTog = document.createElement('button');
  bTog.type = 'button'; bTog.className = 'togli';
  bTog.textContent = 'Togli «' + v.nome + '» dalla lista';
  bTog.onclick = () => {
    lista.splice(scelto, 1);
    if (scelto > 0) scelto--;
    salva(); disegna();
  };
  g.append(bRin, bTog);
  out.appendChild(g);

  const fr = document.createElement('form');
  fr.className = 'form-rin';
  fr.innerHTML = '<input type="text" aria-label="Nomi del prodotto, separati da virgola"><button type="submit">Salva</button>';
  const inp = fr.querySelector('input');
  fr.onsubmit = ev => {
    ev.preventDefault();
    const t = inp.value.trim();
    if (!t) return;
    const v2 = costruisci(t);
    if (!v2) return;
    lista[scelto] = v2;
    salva(); disegna();
  };
  bRin.onclick = () => {
    fr.classList.add('on');
    inp.value = nomiDi(v).join(', ');
    inp.focus(); inp.select();
  };
  out.appendChild(fr);

  if (off.length) {
    const f = document.createElement('p');
    f.className = 'fascia'; f.textContent = 'Prezzi letti dal volantino';
    out.appendChild(f);
    off.forEach((o, i) => out.appendChild(rigaPrezzo(o, i === 0)));
  }

  const f2 = document.createElement('p');
  f2.className = 'fascia';
  f2.textContent = off.length ? 'Altre pagine che lo nominano' : 'Pagine da guardare';
  out.appendChild(f2);

  if (pag.length) {
    const quante = tutteLePagine ? pag.length : 10;
    pag.slice(0, quante).forEach(p => out.appendChild(rigaPagina(p)));
    if (pag.length > quante) {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'altre';
      b.textContent = `Mostra le altre ${pag.length - quante} pagine`;
      b.onclick = () => { tutteLePagine = true; disegna(); };
      out.appendChild(b);
    }
  } else {
    const p = document.createElement('p');
    p.className = 'vuoto';
    p.textContent = 'Il computer non ha letto questa parola in nessuna pagina. Può esserci lo stesso: prova a chiamare il prodotto in un altro modo, con una parola più comune.';
    out.appendChild(p);
  }
}

/* ---------- volantini in fondo ---------- */
const ul = document.getElementById('vol');
DATI.volantini.forEach(v => {
  const li = document.createElement('li');
  li.innerHTML = `<span><span class="i"></span> <span class="p"></span></span><span class="n"></span>`;
  li.querySelector('.i').textContent = v.ins;
  li.querySelector('.p').textContent = v.periodo;
  li.querySelector('.n').textContent = v.pagine + ' pag.';
  ul.appendChild(li);
});

document.getElementById('form-agg').onsubmit = ev => {
  ev.preventDefault();
  const c = document.getElementById('nuovo');
  const t = c.value.trim();
  if (!t) return;
  const v2 = costruisci(t);
  if (!v2) return;
  lista.push(v2);
  scelto = lista.length - 1;
  tutteLePagine = false;
  c.value = '';
  document.getElementById('form-agg').classList.remove('on');
  salva(); disegna();
};

/* La lista vive solo qui dentro (localStorage) e non torna indietro a chi ha fatto
   la pagina. Questo bottone la impacchetta in testo da incollare in chat. La
   textarea non e un ripiego per il telefono: negli artifact la scrittura negli
   appunti puo essere negata senza dire niente, e allora il testo dev'essere li
   pronto da selezionare a mano. */
function listaInTesto() {
  const righe = lista.map(v => {
    const altri = nomiDi(v).slice(1);
    return '- ' + v.nome + (altri.length ? '  (anche: ' + altri.join(', ') + ')' : '');
  });
  return 'LA MIA LISTA DELLA SPESA — ' + lista.length +
         (lista.length === 1 ? ' prodotto' : ' prodotti') + '\n' + righe.join('\n');
}

const btnCopia = document.getElementById('btn-copia');
const areaLista = document.getElementById('testo-lista');
const esito = document.getElementById('esito');
btnCopia.onclick = async () => {
  const testo = listaInTesto();
  areaLista.value = testo;
  areaLista.classList.add('on');
  try {
    await navigator.clipboard.writeText(testo);
    esito.textContent = 'Copiata. Adesso incollala nella chat.';
  } catch (e) {
    esito.textContent = 'Non sono riuscito a copiarla da solo: tienila premuta qui sotto, «Seleziona tutto», copia.';
    areaLista.focus();
    areaLista.select();
  }
};

document.getElementById('letto').textContent = 'letti il ' + DATI.letto;

/* Il riquadro per rimandarmi la lista a mano ha senso solo dove la lista non e
   condivisa: se lo e, la leggo dalla pagina pubblicata senza chiedere niente. */
function aggiornaRiquadroManda() {
  const r = document.getElementById('riquadro-manda');
  const p = document.getElementById('perche-manda');
  if (!r) return;
  r.style.display = soloMio ? '' : 'none';
  if (p && soloMio) {
    p.textContent = 'Questa copia non è collegata alle altre: quello che cambi qui non arriva a me. '
      + 'Tocca il bottone e incolla nella chat, ci sono anche i nomi alternativi.';
  }
}

disegna();

/* Va in fondo, DOPO che «lista» e stata creata e la pagina disegnata una prima
   volta. Messo prima, chiamava disegna() quando «lista» non esisteva ancora e
   moriva li: i bottoni comparivano lo stesso (li disegnava la chiamata in
   fondo) ma sotto non usciva niente. La capacita, dove c'e, arriva comunque
   dopo il primo giro di questo script: la pagina deve funzionare gia prima e
   accendersi quando arriva. */
(async () => {
  try {
    ART = window.claude && claude.use ? await claude.use('artifact') : null;
  } catch (e) { ART = null; }
  if (ART) {
    soloMio = false;
    stato('Lista condivisa: quello che cambi lo vede anche chi ha il link.');
    lista = leggiLista();
  } else {
    stato('Questa copia è solo tua: le modifiche restano su questo telefono.');
  }
  aggiornaRiquadroManda();
  disegna();
})();
</script>'''

# ---------------------------------------------------------------------------
# Il documento contiene una copia di se stesso, cosi puo ripubblicarsi con una
# lista nuova dentro senza perdere la capacita di rifarlo la volta dopo.
#
#   CORPO    = la pagina come la vuole il servizio (senza <html>/<head>: li
#              mette lui), con dentro i due segnaposto
#   COMPLETO = lo stesso, ma documento intero: e questo che la pagina
#              ripubblica di sua iniziativa, e quindi e questo che si porta
#              dietro come modello
#
# I segnaposto restano NON risolti dentro COMPLETO: e proprio quello che
# permette alla generazione dopo di riempirli di nuovo. Prima la lista e poi il
# modello, altrimenti il modello appena infilato porta dentro un altro
# __LISTA__ e si riempie quello sbagliato.
# ---------------------------------------------------------------------------
def racchiudi(testo):
    """JSON da mettere dentro un <script>: </script> va spezzato o chiude il tag."""
    return json.dumps(testo, ensure_ascii=False).replace('</', '<\\/')

CORPO = HTML.replace('__DATI__', DATI)

INTESTA = ('<!doctype html>\n<html lang="it">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
           '<style>body{margin:0}img{max-width:100%}</style>\n')
COMPLETO = (INTESTA + CORPO + '\n</body>\n</html>\n').replace(
    '</style>\n\n<div class="guscio">', '</style>\n</head>\n<body>\n<div class="guscio">', 1)

def riempi(modello):
    """Riempie SOLO la prima occorrenza di ogni segnaposto.

    I due segnaposto compaiono due volte ciascuno: una e quella vera, in cima
    allo script, l'altra e la stringa dentro documento() che serve a
    sostituirla la volta dopo. Riempiendole tutte e due si rompe documento() e
    il file cresce di 200 KB inutili. La prima e sempre quella vera, perche le
    due costanti sono dichiarate sopra la funzione; in JavaScript replace() con
    una stringa si ferma alla prima da solo, quindi le due parti si comportano
    allo stesso modo."""
    # il modello per ultimo: vedi documento() nello script, stessa trappola
    return (modello
            .replace('__LISTA__', LISTA0, 1)
            .replace('__CONDIVISA__', 'true', 1)
            .replace('__TEMPLATE__', racchiudi(COMPLETO), 1))

open('out/pagina.html', 'w', encoding='utf-8').write(riempi(CORPO))

# Copia che si apre a doppio clic, senza account e senza rete. Non puo
# ripubblicare (non c'e nessun window.claude), quindi niente modello e niente
# lista condivisa: li la lista e di chi apre e resta nel suo browser.
open('out/spesa-da-sola.html', 'w', encoding='utf-8').write(
    COMPLETO.replace('__LISTA__', LISTA0, 1)
            .replace('__TEMPLATE__', '""', 1)
            .replace('__CONDIVISA__', 'false', 1))

# ---------------------------------------------------------------------------
# La versione per il sito vero (GitHub Pages). Li dentro non esiste
# window.claude, quindi la pagina non potra mai ripubblicarsi: il modello e
# peso morto e lo si toglie (230 KB in meno). Ha invece il manifest e il suo
# service worker, per potersi installare sul telefono e funzionare in negozio
# senza segnale.
# ---------------------------------------------------------------------------
TESTA_SITO = ('<link rel="manifest" href="./manifest.webmanifest">\n'
              '<meta name="theme-color" content="#FFFFFF">\n'
              '<meta name="apple-mobile-web-app-title" content="Spesa">\n')
CODA_SITO = '''<script>
/* Un service worker suo, in questa cartella. Serve a due cose: tenere la
   pagina disponibile senza rete (in negozio il segnale e pessimo) e togliere
   di mezzo quello della Palestra, che ha lo scope sopra e senza rete
   servirebbe l'app della palestra al posto di questa. */
if ('serviceWorker' in navigator) {
  addEventListener('load', () => navigator.serviceWorker.register('./sw.js').catch(() => {}));
}
</script>
'''
sito = (COMPLETO
        .replace('<meta name="viewport" content="width=device-width, initial-scale=1">\n',
                 '<meta name="viewport" content="width=device-width, initial-scale=1">\n' + TESTA_SITO, 1)
        .replace('\n</body>\n</html>\n', '\n' + CODA_SITO + '</body>\n</html>\n', 1)
        .replace('__LISTA__', LISTA0, 1)
        .replace('__TEMPLATE__', '""', 1)
        .replace('__CONDIVISA__', 'false', 1))
open('out/sito.html', 'w', encoding='utf-8').write(sito)
print('sito:', len(sito) // 1024, 'KB (senza la copia di se stessa)')


# ---------------------------------------------------------------------------
# CONTROLLO OBBLIGATORIO, non un lusso.
#
# Il 2026-09-03 un commento conteneva il tag di chiusura dello script scritto
# per esteso. Il browser lo cerca nel testo e non gli importa che sia dentro un
# commento: ha chiuso lo script a meta e tutte e tre le pagine sono uscite
# morte, quella gia in mano a Manlio compresa. Da fuori sembravano a posto —
# intestazione, riquadri, tutto — solo senza prodotti.
#
# Qui si spezza ogni file dove il browser lo spezzerebbe e si controlla che
# ogni pezzo sia JavaScript valido e che quello grosso contenga davvero la
# funzione che disegna la pagina. Se non torna, il file NON si consegna.
# ---------------------------------------------------------------------------
def controlla(percorso):
    import re, subprocess, tempfile
    testo = open(percorso, encoding='utf-8').read()
    pezzi = re.findall(r'<script>(.*?)</script>', testo, re.S)
    if not pezzi:
        raise SystemExit(f'{percorso}: nessuno script trovato')
    for n, pezzo in enumerate(pezzi):
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as t:
            t.write(pezzo); tmp = t.name
        esito = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
        os.unlink(tmp)
        if esito.returncode != 0:
            riga = esito.stderr.strip().split(chr(10))
            raise SystemExit(f'{percorso}: il pezzo {n} non e JavaScript valido\n  '
                             + chr(10).join('  ' + r for r in riga[:4]))
    if 'function disegna' not in pezzi[0]:
        raise SystemExit(f'{percorso}: lo script principale e stato tagliato prima di '
                         'disegna(). Quasi certamente c\'e un tag di chiusura scritto '
                         'per esteso in un commento o in una stringa.')
    print(f'  {os.path.basename(percorso):24s} {len(pezzi)} script, tutti validi')

print('controllo che le pagine non siano spezzate:')
for f in ('out/pagina.html', 'out/sito.html', 'out/spesa-da-sola.html'):
    controlla(f)

print('scritta —', len(riempi(CORPO)) // 1024, 'KB;', len(partenza), 'prodotti in lista,',
      len(offerte), 'prezzi,', len(pagine), 'pagine indicizzate')
