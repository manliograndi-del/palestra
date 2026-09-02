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

PDF     = {c: f for c, _, _, f in VOLANTINI}
PERIODO = {c: p for c, _, p, _ in VOLANTINI}

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
                         for c, i, p, f in VOLANTINI) if v['pagine']]

partenza = [dict(nome=n, parole=p, cat=c) for n, p, c in PARTENZA]

DATI = json.dumps(dict(offerte=offerte, pagine=pagine, volantini=volantini,
                       partenza=partenza, unita={k: v[0] for k, v in UNITA.items()},
                       letto='2 settembre 2026'),
                  ensure_ascii=False, separators=(',', ':'))

HTML = r'''<title>Offerte di Corso Siracusa</title>
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
    <input id="nuovo" type="text" placeholder="Che prodotto? pane, birra, yogurt…"
           autocomplete="off" aria-label="Nome del prodotto da aggiungere">
    <button type="submit">Aggiungi</button>
  </form>
</div>

<div id="risultato"></div>

<section class="spiega">
  <h2>Come leggerla</h2>
  <p>I <b>dodici prodotti di partenza</b> hanno i prezzi letti a mano, uno per uno, dalle pagine
  dei volantini. Il confronto è per unità e cambia col prodotto: la carne al chilo, il latte al
  litro, le uova all'uovo, la carta igienica al rotolo, il detersivo a lavaggio. Al chilo il
  detersivo darebbe un numero vero e inutile.</p>
  <p>Se <b>aggiungi un prodotto tuo</b>, quello i prezzi non ce li ha: ti dice in quali pagine
  dei volantini compare la parola, e il prezzo lo leggi tu aprendo il PDF a quella pagina. Se
  però scrivi una parola che questa pagina già conosce — «caffe», «bovino», «uovo» — si
  riaggancia da sola ai prezzi giusti.</p>
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
  <p><b>La lista dei prodotti resta su questo telefono.</b> Chi apre il link da un altro posto
  riparte dai dodici di partenza e se li cambia per conto suo, senza toccare i tuoi.</p>

  <h2 style="margin-top:18px">I volantini</h2>
  <ul class="vol" id="vol"></ul>
  <p style="margin-top:12px">Mercatò non c'è: il loro sito non pubblica il volantino in un
  formato che si riesca a scaricare.</p>
</section>

<footer>Volantini letti il 2 settembre 2026. I numeri di pagina sono quelli dei PDF.</footer>
</div>

<script>
const DATI = __DATI__;
const CHIAVE = 'spesa.lista.v1';

const norm = s => (s || '').toLowerCase()
  .normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/['\u2019]/g, ' ');
/* i detersivi stanno sotto i 20 centesimi a lavaggio: con due decimali
   diventerebbero tutti «0,14 €» e non si distinguerebbero piu */
const eur = n => (n < 1 ? n.toFixed(3) : n.toFixed(2)).replace('.', ',');

function leggiLista() {
  try {
    const g = localStorage.getItem(CHIAVE);
    if (g) { const v = JSON.parse(g); if (Array.isArray(v) && v.length) return v; }
  } catch (e) { /* memoria non disponibile: si riparte dai predefiniti */ }
  return DATI.partenza.map(p => ({ ...p }));
}
function salva() {
  try { localStorage.setItem(CHIAVE, JSON.stringify(lista)); }
  catch (e) { /* la pagina funziona lo stesso, solo non ricorda */ }
}

let lista = leggiLista();
let scelto = 0;
let tutteLePagine = false;

const offerteDi = v => v.cat ? DATI.offerte.filter(o => o.cat === v.cat) : [];

/* Se quello che scrive combacia con uno dei dodici di partenza (col nome o con
   una delle sue parole), gli attacca la stessa categoria: cosi chi riscrive
   «caffe» a mano ritrova i prezzi invece delle sole pagine. */
function costruisci(testo) {
  const t = norm(testo);
  const p = DATI.partenza.find(x =>
    norm(x.nome) === t || (x.parole || []).some(w => norm(w) === t));
  return p ? { nome: testo, parole: p.parole, cat: p.cat }
           : { nome: testo, parole: [testo], cat: null };
}
const pagineDi = v => {
  const t = (v.parole && v.parole.length ? v.parole : [v.nome]).map(norm);
  return DATI.pagine.filter(p => { const s = norm(p.parole); return t.some(x => s.includes(x)); });
};

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
  fr.innerHTML = '<input type="text" aria-label="Nuovo nome del prodotto"><button type="submit">Salva</button>';
  const inp = fr.querySelector('input');
  fr.onsubmit = ev => {
    ev.preventDefault();
    const t = inp.value.trim();
    if (!t) return;
    lista[scelto] = costruisci(t);
    salva(); disegna();
  };
  bRin.onclick = () => { fr.classList.add('on'); inp.value = v.nome; inp.focus(); inp.select(); };
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
  lista.push(costruisci(t));
  scelto = lista.length - 1;
  tutteLePagine = false;
  c.value = '';
  document.getElementById('form-agg').classList.remove('on');
  salva(); disegna();
};

document.getElementById('letto').textContent = 'letti il ' + DATI.letto;

disegna();
</script>'''

pagina = HTML.replace('__DATI__', DATI)
open('out/pagina.html', 'w', encoding='utf-8').write(pagina)

# Copia autonoma da mandare per posta o WhatsApp: la pagina pubblicata viene
# avvolta dal servizio in <!doctype>/<head>/<body>, il file grezzo no. Questa
# se li porta dietro e si apre a doppio clic, senza account e senza rete
# (i caratteri di Google non si caricano e si scende ai caratteri di sistema).
INTESTA = ('<!doctype html>\n<html lang="it">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
           '<style>body{margin:0}img{max-width:100%}</style>\n')
sola = INTESTA + pagina.replace('<title>', '<title>', 1) + '\n</body>\n</html>\n'
sola = sola.replace('</style>\n\n<div class="guscio">', '</style>\n</head>\n<body>\n<div class="guscio">', 1)
open('out/spesa-da-sola.html', 'w', encoding='utf-8').write(sola)
print('scritta —', len(HTML) + len(DATI), 'caratteri;', len(partenza), 'prodotti,',
      len(offerte), 'offerte,', len(pagine), 'pagine')
