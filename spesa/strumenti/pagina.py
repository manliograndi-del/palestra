# -*- coding: utf-8 -*-
"""Genera la pagina web da pubblicare. Stessi dati dell'Excel (dati.py)."""
import json, os, glob
from dati import PRODOTTI, VOLANTINI, D

PDF     = {c: f for c, _, _, f in VOLANTINI}
PERIODO = {c: p for c, _, p, _ in VOLANTINI}
INSEGNA = {c: i for c, i, _, _ in VOLANTINI}

offerte = []
for cat, ins, chiave, rep, pro, fmt, qta, pre, pag, fon, note in PRODOTTI:
    offerte.append(dict(cat=cat, ins=ins, rep=rep, pro=pro, fmt=fmt,
                        prezzo=pre, kg=round(pre/qta, 2), pag=pag,
                        pdf=PDF[chiave], periodo=PERIODO[chiave],
                        dubbio=(fon == D), note=note))

idx = json.load(open('indice.json', encoding='utf-8'))
validi = {(os.path.basename(os.path.dirname(f)), int(os.path.basename(f)[:-4]))
          for f in glob.glob('pg/*/*.jpg')}
pagine = [dict(ins=r['insegna'], periodo=r['validita'], pdf=PDF.get(r['chiave'], ''),
               pag=r['pagina'], parole=r['parole'])
          for r in idx if (r['chiave'], r['pagina']) in validi]
pagine.sort(key=lambda r: (r['ins'], r['periodo'], r['pag']))

volantini = []
for chiave, ins, per, f in VOLANTINI:
    n = len([p for p in pagine if p['pdf'] == f])
    if n: volantini.append(dict(ins=ins, periodo=per, pdf=f, pagine=n))

DATI = json.dumps(dict(offerte=offerte, pagine=pagine, volantini=volantini),
                  ensure_ascii=False, separators=(',', ':'))

HTML = r'''<title>Offerte di Corso Siracusa</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Asap:ital,wght@0,400;0,500;0,600;1,400&family=Oswald:wght@500;600;700&display=swap">
<style>
:root{
  --carta:#FBF9F6; --superficie:#FFFFFF; --superficie2:#F4F0E9;
  --inchiostro:#221F1A; --tenue:#7A7167; --linea:#E4DED4;
  --rosso:#C8102E; --su-rosso:#FFFFFF;
  --verde:#2E6B4F; --verde-tenue:#E7F0EA;
  --ambra:#8A5A12; --ambra-tenue:#FBF0DC;
  --ombra:0 1px 2px rgba(34,31,26,.06);
  --f-testo:'Asap',ui-sans-serif,system-ui,'Segoe UI',sans-serif;
  --f-prezzo:'Oswald','Arial Narrow',ui-sans-serif,sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --carta:#15130F; --superficie:#1F1C18; --superficie2:#272320;
  --inchiostro:#F2EEE7; --tenue:#A79C8F; --linea:#332E27;
  --rosso:#FF6B7E; --su-rosso:#1F1C18;
  --verde:#7FC7A2; --verde-tenue:#1B2A22;
  --ambra:#E0AC5C; --ambra-tenue:#2C2317;
  --ombra:0 1px 2px rgba(0,0,0,.4);
}}
:root[data-theme="dark"]{
  --carta:#15130F; --superficie:#1F1C18; --superficie2:#272320;
  --inchiostro:#F2EEE7; --tenue:#A79C8F; --linea:#332E27;
  --rosso:#FF6B7E; --su-rosso:#1F1C18;
  --verde:#7FC7A2; --verde-tenue:#1B2A22;
  --ambra:#E0AC5C; --ambra-tenue:#2C2317;
  --ombra:0 1px 2px rgba(0,0,0,.4);
}
*{box-sizing:border-box}
body{background:var(--carta);color:var(--inchiostro);font-family:var(--f-testo);
  font-size:16px;line-height:1.45;-webkit-text-size-adjust:100%}
.guscio{max-width:760px;margin:0 auto;padding:0 16px 64px}

header{padding:28px 0 18px}
h1{font-family:var(--f-prezzo);font-weight:700;font-size:clamp(30px,8vw,44px);
  letter-spacing:-.01em;line-height:1;margin:0;text-wrap:balance;text-transform:uppercase}
h1 .zona{display:block;color:var(--rosso);font-size:.42em;letter-spacing:.14em;
  margin-bottom:9px;font-weight:600}
.sottotitolo{color:var(--tenue);margin:10px 0 0;font-size:15px}

.cerca{position:sticky;top:0;z-index:9;background:var(--carta);
  padding:12px 0 10px;margin-top:14px;border-bottom:1px solid var(--linea)}
.campo{display:flex;align-items:center;gap:10px;background:var(--superficie);
  border:1.5px solid var(--linea);border-radius:11px;padding:11px 13px;box-shadow:var(--ombra)}
.campo:focus-within{border-color:var(--rosso)}
.campo svg{flex:0 0 18px;color:var(--tenue)}
.campo input{flex:1;min-width:0;border:0;background:none;color:var(--inchiostro);
  font-family:var(--f-testo);font-size:16px;outline:none}
.campo input::placeholder{color:var(--tenue)}
.pulisci{border:0;background:none;color:var(--tenue);cursor:pointer;font-size:20px;
  line-height:1;padding:0 2px;display:none}
.pulisci.on{display:block}

.filtri{display:flex;gap:7px;flex-wrap:wrap;margin-top:10px}
.filtro{font-family:var(--f-testo);font-size:13.5px;font-weight:500;
  border:1.5px solid var(--linea);background:var(--superficie);color:var(--inchiostro);
  border-radius:99px;padding:6px 13px;cursor:pointer}
.filtro[aria-pressed="true"]{background:var(--rosso);border-color:var(--rosso);color:var(--su-rosso)}
.filtro:focus-visible,.campo input:focus-visible{outline:2px solid var(--rosso);outline-offset:2px}

section{margin-top:30px}
.titolo-sez{display:flex;align-items:baseline;justify-content:space-between;gap:12px;
  border-bottom:2px solid var(--inchiostro);padding-bottom:6px;margin-bottom:2px}
.titolo-sez h2{font-family:var(--f-prezzo);text-transform:uppercase;letter-spacing:.02em;
  font-size:20px;font-weight:600;margin:0}
.titolo-sez .conta{color:var(--tenue);font-size:13px;font-variant-numeric:tabular-nums}

.riga{display:grid;grid-template-columns:1fr auto;gap:6px 14px;align-items:start;
  padding:14px 0;border-bottom:1px solid var(--linea)}
.nome{font-weight:600;font-size:16.5px;line-height:1.25;margin:0}
.meta{color:var(--tenue);font-size:13.5px;margin:4px 0 0}
.meta b{color:var(--inchiostro);font-weight:600}
.prezzo{text-align:right;font-family:var(--f-prezzo);font-variant-numeric:tabular-nums;
  line-height:1;white-space:nowrap}
.prezzo .n{display:block;font-size:26px;font-weight:700;color:var(--rosso)}
.prezzo .u{display:block;font-family:var(--f-testo);font-size:11px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--tenue);margin-top:3px}
.prezzo .conf{display:block;font-family:var(--f-testo);font-size:12.5px;color:var(--tenue);margin-top:5px}
.tag{grid-column:1/-1;display:flex;gap:6px;flex-wrap:wrap;margin-top:2px}
.pill{font-size:11.5px;letter-spacing:.05em;text-transform:uppercase;font-weight:600;
  border-radius:5px;padding:3px 7px}
.pill.best{background:var(--verde-tenue);color:var(--verde)}
.pill.warn{background:var(--ambra-tenue);color:var(--ambra)}
.nota{grid-column:1/-1;font-size:13.5px;color:var(--tenue);margin:3px 0 0}
.dove{grid-column:1/-1;font-size:13px;color:var(--tenue);margin:5px 0 0;
  padding-left:10px;border-left:2px solid var(--linea)}

.pagine .riga{grid-template-columns:1fr auto}
.pagine .num{font-family:var(--f-prezzo);font-size:22px;font-weight:600;
  font-variant-numeric:tabular-nums;color:var(--inchiostro)}
.pagine .num small{display:block;font-family:var(--f-testo);font-size:10.5px;
  letter-spacing:.08em;text-transform:uppercase;color:var(--tenue);font-weight:400}
.parole{font-size:13px;color:var(--tenue);margin:5px 0 0;overflow-wrap:anywhere}
.parole mark{background:var(--rosso);color:var(--su-rosso);border-radius:3px;padding:0 2px}

.vuoto{padding:26px 0;color:var(--tenue);font-size:15px}
.piu{display:block;width:100%;margin-top:14px;font-family:var(--f-testo);font-size:14px;
  font-weight:600;background:var(--superficie2);color:var(--inchiostro);
  border:1.5px solid var(--linea);border-radius:9px;padding:11px;cursor:pointer}
.piu:focus-visible{outline:2px solid var(--rosso);outline-offset:2px}

.avvisi{margin-top:36px;background:var(--superficie2);border-radius:12px;padding:18px 18px 6px}
.avvisi h2{font-family:var(--f-prezzo);text-transform:uppercase;font-size:16px;
  letter-spacing:.04em;margin:0 0 10px}
.avvisi p{font-size:14px;margin:0 0 12px;color:var(--inchiostro)}
.avvisi p .etichetta{color:var(--ambra);font-weight:600}

.elenco-vol{list-style:none;padding:0;margin:10px 0 0;display:grid;gap:1px;
  background:var(--linea);border:1px solid var(--linea);border-radius:10px;overflow:hidden}
.elenco-vol li{background:var(--superficie);padding:11px 13px;display:flex;
  justify-content:space-between;align-items:baseline;gap:12px;font-size:14px}
.elenco-vol .ins{font-weight:600}
.elenco-vol .per{color:var(--tenue);font-size:13px}
.elenco-vol .np{color:var(--tenue);font-size:12.5px;font-variant-numeric:tabular-nums;white-space:nowrap}

footer{margin-top:34px;padding-top:16px;border-top:1px solid var(--linea);
  color:var(--tenue);font-size:13px}
@media (min-width:620px){ .riga{grid-template-columns:1fr auto} .prezzo .n{font-size:30px} }
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>

<div class="guscio">
<header>
  <h1><span class="zona">Torino · Corso Siracusa</span>Offerte della settimana</h1>
  <p class="sottotitolo">Carne di bue, tonno e salmone nei volantini di Lidl, Eurospin, MD,
  Bennet, Ipercoop e Carrefour Iper. Ordinati per <b>prezzo al chilo</b>, che è l'unico modo
  onesto di confrontare confezioni di taglia diversa. Letti a mano dai volantini il 2 settembre 2026.</p>
</header>

<div class="cerca">
  <label class="campo">
    <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
      <circle cx="9" cy="9" r="6"/><path d="M13.5 13.5 18 18"/></svg>
    <input id="q" type="search" placeholder="Cerca: tonno, caffè, detersivo…"
           autocomplete="off" aria-label="Cerca fra le offerte e nelle pagine dei volantini">
    <button class="pulisci" id="pulisci" type="button" aria-label="Cancella la ricerca">×</button>
  </label>
  <div class="filtri" id="filtri" role="group" aria-label="Filtra per categoria"></div>
</div>

<div id="risultati"></div>

<section class="avvisi">
  <h2>Prima di fidarti</h2>
  <p>I prezzi qui sopra li ho letti uno per uno dalla pagina del volantino. Le righe segnate
  <span class="etichetta">da controllare</span> no: vengono da riassunti trovati online, e di errori
  così ne ho già trovati tre — una rollata data a 7,99 al chilo che in realtà era 7,99 la confezione
  da 600 grammi, un salmone dato per 150 grammi che era da 500, un macinato dato a 6,99 che sul
  volantino faceva 8,99. Quelle tre righe controllale sul PDF.</p>
  <p>Certi prezzi valgono <b>solo con la tessera</b>: soci Coop all'Ipercoop, Lidl Plus, Bennet Club.
  Dov'è così sta scritto nella riga.</p>
  <p>Le parole che compaiono cercando dentro le pagine le ha lette il computer dalle immagini:
  sono spesso storpiate, e i prezzi non li riconosce quasi mai. Servono a dirti <b>quale pagina
  aprire</b>, non quanto costa.</p>
  <h2 style="margin-top:18px">I volantini</h2>
  <ul class="elenco-vol" id="elenco-vol"></ul>
  <p style="margin-top:12px">Mercatò non c'è: il loro sito non pubblica il volantino in un formato
  che si riesca a scaricare.</p>
</section>

<footer>Fatto per Manlio. I numeri di pagina sono quelli dei PDF dei volantini.</footer>
</div>

<script>
const DATI = __DATI__;
const norm = s => (s||'').toLowerCase()
  .normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/['\u2019]/g,' ');

let categoria = 'Tutto';
let query = '';
let tuttePagine = false;

const CATEGORIE = ['Tutto','Carne di bue','Tonno','Salmone'];
const filtri = document.getElementById('filtri');
CATEGORIE.forEach(c => {
  const b = document.createElement('button');
  b.className = 'filtro'; b.type = 'button'; b.textContent = c;
  b.setAttribute('aria-pressed', String(c === categoria));
  b.onclick = () => {
    categoria = c;
    [...filtri.children].forEach(x => x.setAttribute('aria-pressed', String(x.textContent === c)));
    disegna();
  };
  filtri.appendChild(b);
});

const vol = document.getElementById('elenco-vol');
DATI.volantini.forEach(v => {
  const li = document.createElement('li');
  li.innerHTML = `<span><span class="ins"></span> <span class="per"></span></span>
                  <span class="np"></span>`;
  li.querySelector('.ins').textContent = v.ins;
  li.querySelector('.per').textContent = v.periodo;
  li.querySelector('.np').textContent = v.pagine + ' pag.';
  vol.appendChild(li);
});

const eur = n => n.toFixed(2).replace('.', ',');

function evidenzia(testo, q) {
  const frag = document.createDocumentFragment();
  if (!q) { frag.appendChild(document.createTextNode(testo)); return frag; }
  const n = norm(testo), nq = norm(q);
  let i = 0, p;
  while ((p = n.indexOf(nq, i)) !== -1) {
    frag.appendChild(document.createTextNode(testo.slice(i, p)));
    const m = document.createElement('mark');
    m.textContent = testo.slice(p, p + nq.length);
    frag.appendChild(m);
    i = p + nq.length;
  }
  frag.appendChild(document.createTextNode(testo.slice(i)));
  return frag;
}

function rigaOfferta(o, migliore) {
  const d = document.createElement('article');
  d.className = 'riga';
  d.innerHTML = `<div><p class="nome"></p><p class="meta"></p></div>
    <div class="prezzo"><span class="n"></span><span class="u">al kg</span><span class="conf"></span></div>
    <div class="tag"></div><p class="nota"></p><p class="dove"></p>`;
  d.querySelector('.nome').appendChild(evidenzia(o.pro, query));
  const meta = d.querySelector('.meta');
  meta.innerHTML = '<b></b> · <span></span> · <span></span>';
  meta.querySelector('b').textContent = o.ins;
  meta.querySelectorAll('span')[0].textContent = o.rep;
  meta.querySelectorAll('span')[1].textContent = o.fmt;
  d.querySelector('.n').textContent = eur(o.kg) + ' €';
  d.querySelector('.conf').textContent = eur(o.prezzo) + ' € la confezione';
  const tag = d.querySelector('.tag');
  if (migliore) tag.insertAdjacentHTML('beforeend', '<span class="pill best">il più conveniente</span>');
  if (o.dubbio) tag.insertAdjacentHTML('beforeend', '<span class="pill warn">da controllare</span>');
  const nota = d.querySelector('.nota');
  if (o.note) nota.textContent = o.note; else nota.remove();
  d.querySelector('.dove').textContent = o.pag
    ? `${o.pdf} — pagina ${o.pag}`
    : `${o.pdf} — pagina non individuata`;
  return d;
}

function disegna() {
  const out = document.getElementById('risultati');
  out.textContent = '';
  const q = norm(query);

  let off = DATI.offerte.filter(o => categoria === 'Tutto' || o.cat === categoria);
  if (q) off = off.filter(o => norm(o.pro + ' ' + o.ins + ' ' + o.rep + ' ' + o.fmt + ' ' + o.note).includes(q));

  const cats = CATEGORIE.slice(1).filter(c => off.some(o => o.cat === c));
  cats.forEach(c => {
    const gruppo = off.filter(o => o.cat === c);
    const sec = document.createElement('section');
    const h = document.createElement('div');
    h.className = 'titolo-sez';
    h.innerHTML = '<h2></h2><span class="conta"></span>';
    h.querySelector('h2').textContent = c;
    h.querySelector('.conta').textContent =
      `da ${eur(gruppo[0].kg)} € a ${eur(gruppo[gruppo.length-1].kg)} € al kg`;
    sec.appendChild(h);
    gruppo.forEach((o, i) => sec.appendChild(rigaOfferta(o, i === 0 && !q)));
    out.appendChild(sec);
  });

  if (!off.length) {
    const v = document.createElement('p');
    v.className = 'vuoto';
    v.textContent = 'Nessuna offerta fra quelle che ho letto a mano. Guarda qui sotto: forse è in una pagina del volantino.';
    out.appendChild(v);
  }

  if (q.length >= 3) {
    const trovate = DATI.pagine.filter(p =>
      norm(p.parole).includes(q));
    const sec = document.createElement('section');
    sec.className = 'pagine';
    const h = document.createElement('div');
    h.className = 'titolo-sez';
    h.innerHTML = '<h2>Nelle pagine dei volantini</h2><span class="conta"></span>';
    h.querySelector('.conta').textContent =
      trovate.length ? `${trovate.length} pagine su ${DATI.pagine.length}` : `niente su ${DATI.pagine.length} pagine`;
    sec.appendChild(h);
    const mostra = tuttePagine ? trovate : trovate.slice(0, 8);
    mostra.forEach(p => {
      const d = document.createElement('article');
      d.className = 'riga';
      d.innerHTML = `<div><p class="nome"></p><p class="meta"></p><p class="parole"></p></div>
        <div class="num"><span></span><small>pagina</small></div>`;
      d.querySelector('.nome').textContent = p.ins;
      d.querySelector('.meta').textContent = p.periodo;
      d.querySelector('.num span').textContent = p.pag;
      const par = p.parole.split(' ').filter(w => norm(w).includes(q)).slice(0, 12).join(' · ');
      d.querySelector('.parole').appendChild(evidenzia(par, query));
      sec.appendChild(d);
    });
    if (!trovate.length) {
      const v = document.createElement('p');
      v.className = 'vuoto';
      v.textContent = 'Il computer non ha letto questa parola in nessuna pagina. Può darsi che ci sia lo stesso: sulle scritte grandi e colorate spesso sbaglia. Prova una parola più comune.';
      sec.appendChild(v);
    }
    if (trovate.length > mostra.length) {
      const b = document.createElement('button');
      b.className = 'piu'; b.type = 'button';
      b.textContent = `Mostra le altre ${trovate.length - mostra.length} pagine`;
      b.onclick = () => { tuttePagine = true; disegna(); };
      sec.appendChild(b);
    }
    out.appendChild(sec);
  }
}

const input = document.getElementById('q');
const pulisci = document.getElementById('pulisci');
input.addEventListener('input', () => {
  query = input.value.trim();
  tuttePagine = false;
  pulisci.classList.toggle('on', query.length > 0);
  disegna();
});
pulisci.onclick = () => {
  input.value = ''; query = ''; tuttePagine = false;
  pulisci.classList.remove('on'); disegna(); input.focus();
};
disegna();
</script>'''

open('out/pagina.html', 'w', encoding='utf-8').write(HTML.replace('__DATI__', DATI))
print('scritta out/pagina.html —', len(HTML) + len(DATI), 'caratteri;',
      len(offerte), 'offerte,', len(pagine), 'pagine indicizzate')
