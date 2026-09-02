# -*- coding: utf-8 -*-
"""Genera la pagina web da pubblicare.

Prodotti e prezzi vengono da dati.py, la lista di partenza da lista.py.
La pagina NON usa la memoria condivisa sul server: quella renderebbe
l'artifact apribile solo da dentro l'organizzazione Claude di Manlio, e la
moglie deve poterlo aprire da fuori. La lista quindi vive nel browser di chi
apre (localStorage), e ognuno può cambiarsela senza rompere quella dell'altro.
"""
import json, os, glob
from dati import PRODOTTI, VOLANTINI, D
from lista import PARTENZA

PDF     = {c: f for c, _, _, f in VOLANTINI}
PERIODO = {c: p for c, _, p, _ in VOLANTINI}

offerte = [dict(cat=cat, ins=ins, rep=rep, pro=pro, fmt=fmt, prezzo=pre,
                kg=round(pre / qta, 2), pag=pag, pdf=PDF[chiave],
                periodo=PERIODO[chiave], dubbio=(fon == D), note=note)
           for cat, ins, chiave, rep, pro, fmt, qta, pre, pag, fon, note in PRODOTTI]

idx = json.load(open('indice.json', encoding='utf-8'))
validi = {(os.path.basename(os.path.dirname(f)), int(os.path.basename(f)[:-4]))
          for f in glob.glob('pg/*/*.jpg')}
pagine = sorted((dict(ins=r['insegna'], periodo=r['validita'], pdf=PDF.get(r['chiave'], ''),
                      pag=r['pagina'], parole=r['parole'])
                 for r in idx if (r['chiave'], r['pagina']) in validi),
                key=lambda r: (r['ins'], r['periodo'], r['pag']))

volantini = [dict(ins=i, periodo=p, pdf=f, pagine=len([x for x in pagine if x['pdf'] == f]))
             for c, i, p, f in VOLANTINI]
volantini = [v for v in volantini if v['pagine']]

partenza = [dict(nome=n, parole=p, cat=c) for n, p, c in PARTENZA]

DATI = json.dumps(dict(offerte=offerte, pagine=pagine, volantini=volantini,
                       partenza=partenza), ensure_ascii=False, separators=(',', ':'))

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
.guscio{max-width:820px;margin:0 auto;padding:0 16px 64px}
button{font-family:var(--f-testo)}
:focus-visible{outline:2px solid var(--rosso);outline-offset:2px}

header{padding:26px 0 4px}
h1{font-family:var(--f-prezzo);font-weight:700;font-size:clamp(28px,7.5vw,42px);
  letter-spacing:-.01em;line-height:1;margin:0;text-transform:uppercase;text-wrap:balance}
h1 .zona{display:block;color:var(--rosso);font-size:.42em;letter-spacing:.14em;
  margin-bottom:9px;font-weight:600}
.sottotitolo{color:var(--tenue);margin:12px 0 0;font-size:15px;max-width:60ch}

.aggiungi{margin-top:20px;display:flex;gap:8px}
.aggiungi input{flex:1;min-width:0;background:var(--superficie);color:var(--inchiostro);
  border:1.5px solid var(--linea);border-radius:11px;padding:13px 14px;
  font-family:var(--f-testo);font-size:16px;box-shadow:var(--ombra)}
.aggiungi input:focus{outline:none;border-color:var(--rosso)}
.aggiungi input::placeholder{color:var(--tenue)}
.piu{flex:0 0 auto;background:var(--rosso);color:var(--su-rosso);border:0;
  border-radius:11px;padding:0 20px;font-size:17px;font-weight:600;cursor:pointer;
  min-height:48px;white-space:nowrap}
.piu[disabled]{opacity:.4;cursor:default}

.conteggio{display:flex;align-items:baseline;justify-content:space-between;gap:12px;
  margin:30px 0 4px;border-bottom:2px solid var(--inchiostro);padding-bottom:6px}
.conteggio h2{font-family:var(--f-prezzo);text-transform:uppercase;letter-spacing:.03em;
  font-size:19px;font-weight:600;margin:0}
.conteggio span{color:var(--tenue);font-size:13px;font-variant-numeric:tabular-nums}

.schede{display:grid;gap:0}
@media (min-width:660px){.schede{grid-template-columns:1fr 1fr;gap:0 26px}}

.scheda{border-bottom:1px solid var(--linea);padding:15px 0}
.testa{display:grid;grid-template-columns:1fr auto;gap:4px 12px;align-items:start;
  width:100%;background:none;border:0;padding:0;text-align:left;cursor:pointer;color:inherit}
.testa h3{margin:0;font-size:17.5px;font-weight:600;line-height:1.2}
.riassunto{grid-column:1;color:var(--tenue);font-size:13.5px;margin:4px 0 0}
.riassunto b{color:var(--inchiostro);font-weight:600}
.miglior{grid-column:2;grid-row:1/3;text-align:right;font-family:var(--f-prezzo);
  font-variant-numeric:tabular-nums;line-height:1;white-space:nowrap}
.miglior .n{display:block;font-size:23px;font-weight:700;color:var(--rosso)}
.miglior .u{display:block;font-family:var(--f-testo);font-size:10.5px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--tenue);margin-top:3px}
.freccia{grid-column:2;grid-row:1/3;align-self:center;color:var(--tenue);font-size:15px}

.dettaglio{padding:4px 0 2px}
.blocco{margin-top:12px}
.blocco h4{font-family:var(--f-prezzo);text-transform:uppercase;letter-spacing:.05em;
  font-size:12.5px;font-weight:600;color:var(--tenue);margin:0 0 6px}
.voce{display:grid;grid-template-columns:1fr auto;gap:2px 12px;padding:8px 0;
  border-top:1px solid var(--linea)}
.voce .n2{margin:0;font-size:15px;font-weight:600;line-height:1.25}
.voce .m2{margin:2px 0 0;color:var(--tenue);font-size:13px}
.voce .p2{text-align:right;font-family:var(--f-prezzo);font-variant-numeric:tabular-nums;
  font-size:19px;font-weight:600;color:var(--rosso);line-height:1.1;white-space:nowrap}
.voce .p2 small{display:block;font-family:var(--f-testo);font-size:11px;color:var(--tenue);
  font-weight:400;letter-spacing:.06em;text-transform:uppercase}
.voce .avv{grid-column:1/-1;margin:4px 0 0;font-size:12.5px;color:var(--ambra);
  background:var(--ambra-tenue);border-radius:5px;padding:4px 7px;display:inline-block}
.voce .meno{grid-column:1/-1;margin:5px 0 0;justify-self:start;font-size:11.5px;
  letter-spacing:.05em;text-transform:uppercase;font-weight:600;color:var(--verde);
  background:var(--verde-tenue);border-radius:5px;padding:3px 7px}
.voce .dove2{grid-column:1/-1;margin:4px 0 0;font-size:12.5px;color:var(--tenue)}
.pagina{display:flex;justify-content:space-between;gap:12px;padding:7px 0;
  border-top:1px solid var(--linea);font-size:13.5px}
.pagina .p-ins{font-weight:600}
.pagina .p-per{color:var(--tenue);font-size:12.5px}
.pagina .p-num{font-family:var(--f-prezzo);font-size:17px;font-weight:600;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.nulla{color:var(--tenue);font-size:13.5px;margin:6px 0 0}

.azioni{display:flex;gap:8px;margin-top:14px;flex-wrap:wrap}
.azioni button{background:var(--superficie2);color:var(--inchiostro);border:1.5px solid var(--linea);
  border-radius:9px;padding:9px 15px;font-size:14px;font-weight:600;cursor:pointer;min-height:42px}
.azioni .togli{color:var(--rosso)}
.rinomina{display:flex;gap:8px;margin-top:12px}
.rinomina input{flex:1;min-width:0;background:var(--superficie);color:var(--inchiostro);
  border:1.5px solid var(--rosso);border-radius:9px;padding:10px 12px;
  font-family:var(--f-testo);font-size:16px}
.rinomina input:focus{outline:none}
.rinomina button{background:var(--rosso);color:var(--su-rosso);border:0;border-radius:9px;
  padding:0 16px;font-size:15px;font-weight:600;cursor:pointer;min-height:44px}

.avvisi{margin-top:34px;background:var(--superficie2);border-radius:12px;padding:18px 18px 6px}
.avvisi h2{font-family:var(--f-prezzo);text-transform:uppercase;font-size:16px;
  letter-spacing:.04em;margin:0 0 10px}
.avvisi p{font-size:14px;margin:0 0 12px}
.avvisi .etichetta{color:var(--ambra);font-weight:600}
.elenco-vol{list-style:none;padding:0;margin:10px 0 0;display:grid;gap:1px;
  background:var(--linea);border:1px solid var(--linea);border-radius:10px;overflow:hidden}
.elenco-vol li{background:var(--superficie);padding:11px 13px;display:flex;
  justify-content:space-between;align-items:baseline;gap:12px;font-size:14px}
.elenco-vol .ins{font-weight:600}
.elenco-vol .per{color:var(--tenue);font-size:13px}
.elenco-vol .np{color:var(--tenue);font-size:12.5px;font-variant-numeric:tabular-nums;white-space:nowrap}
footer{margin-top:32px;padding-top:16px;border-top:1px solid var(--linea);
  color:var(--tenue);font-size:13px}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>

<div class="guscio">
<header>
  <h1><span class="zona">Torino · Corso Siracusa</span>La lista della spesa</h1>
  <p class="sottotitolo">I prodotti che tieni d'occhio, cercati dentro i volantini di Lidl,
  Eurospin, MD, Bennet, Ipercoop e Carrefour Iper. Tocca un prodotto per aprirlo. Puoi
  cambiarne il nome, toglierlo, o aggiungerne quanti vuoi qui sotto.</p>
  <form class="aggiungi" id="form-aggiungi">
    <input id="nuovo" type="text" placeholder="Aggiungi un prodotto: pane, birra, yogurt…"
           autocomplete="off" aria-label="Nome del prodotto da aggiungere">
    <button class="piu" type="submit" id="btn-piu" disabled>Aggiungi</button>
  </form>
</header>

<div class="conteggio"><h2>La tua lista</h2><span id="conta"></span></div>
<div class="schede" id="schede"></div>

<section class="avvisi">
  <h2>Come leggerla</h2>
  <p>Per <b>carne di bue, tonno e salmone</b> ho letto i prezzi a mano, uno per uno, dalla
  pagina del volantino: lì trovi il prezzo al chilo e sai già dove costa meno. Per tutto il
  resto la pagina ti dice soltanto <b>in quali pagine dei volantini compare quella parola</b>:
  il prezzo lo leggi tu aprendo il PDF a quella pagina. È come cercare in un indice, non in un
  listino.</p>
  <p>Le righe segnate <span class="etichetta">da controllare</span> vengono da riassunti trovati
  online e possono essere sbagliate: di errori così ne ho già trovati tre. Controllale sul PDF.</p>
  <p>Certi prezzi valgono <b>solo con la tessera</b> — soci Coop, Lidl Plus, Bennet Club.
  Dov'è così sta scritto nella riga.</p>
  <p>Le parole le ha lette il computer dalle immagini dei volantini: sulle scritte grandi e
  colorate spesso sbaglia, e i prezzi non li riconosce quasi mai. Se un prodotto dà zero
  pagine, può esserci lo stesso: prova un'altra parola.</p>
  <p><b>La lista è tua e resta su questo telefono.</b> Se la apri altrove, o se la apre tua
  moglie, si riparte dai dodici prodotti di partenza e ognuno se la cambia come vuole.</p>
  <h2 style="margin-top:18px">I volantini</h2>
  <ul class="elenco-vol" id="elenco-vol"></ul>
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
const eur = n => n.toFixed(2).replace('.', ',');

function leggiLista() {
  try {
    const g = localStorage.getItem(CHIAVE);
    if (g) {
      const v = JSON.parse(g);
      if (Array.isArray(v) && v.length) return v;
    }
  } catch (e) { /* niente memoria: si riparte dai predefiniti */ }
  return DATI.partenza.map(p => ({ ...p }));
}
function salvaLista() {
  try { localStorage.setItem(CHIAVE, JSON.stringify(lista)); }
  catch (e) { /* memoria piena o bloccata: la pagina funziona lo stesso, non ricorda */ }
}

let lista = leggiLista();
let aperto = null;

function offerteDi(v) {
  return v.cat ? DATI.offerte.filter(o => o.cat === v.cat) : [];
}
function pagineDi(v) {
  const termini = (v.parole && v.parole.length ? v.parole : [v.nome]).map(norm);
  return DATI.pagine.filter(p => {
    const t = norm(p.parole);
    return termini.some(x => t.includes(x));
  });
}

function schedaOfferta(o, primo) {
  const d = document.createElement('div');
  d.className = 'voce';
  d.innerHTML = `<div><p class="n2"></p><p class="m2"></p></div>
    <p class="p2"><span></span><small>al kg</small></p>`;
  d.querySelector('.n2').textContent = o.pro;
  d.querySelector('.m2').textContent = `${o.ins} · ${o.fmt} · ${eur(o.prezzo)} € la confezione`;
  d.querySelector('.p2 span').textContent = eur(o.kg) + ' €';
  if (primo) {
    const m = document.createElement('p');
    m.className = 'meno'; m.textContent = 'il meno caro';
    d.appendChild(m);
  }
  if (o.dubbio) {
    const a = document.createElement('p');
    a.className = 'avv'; a.textContent = 'da controllare sul volantino';
    d.appendChild(a);
  }
  if (o.note) {
    const n = document.createElement('p');
    n.className = 'dove2'; n.textContent = o.note;
    d.appendChild(n);
  }
  const w = document.createElement('p');
  w.className = 'dove2';
  w.textContent = o.pag ? `${o.pdf} — pagina ${o.pag}` : `${o.pdf} — pagina non individuata`;
  d.appendChild(w);
  return d;
}

function rigaPagina(p) {
  const d = document.createElement('div');
  d.className = 'pagina';
  d.innerHTML = `<span><span class="p-ins"></span><br><span class="p-per"></span></span>
                 <span class="p-num"></span>`;
  d.querySelector('.p-ins').textContent = p.ins;
  d.querySelector('.p-per').textContent = p.periodo;
  d.querySelector('.p-num').textContent = 'pag. ' + p.pag;
  return d;
}

function disegna() {
  const cont = document.getElementById('schede');
  cont.textContent = '';
  document.getElementById('conta').textContent =
    lista.length + (lista.length === 1 ? ' prodotto' : ' prodotti');

  lista.forEach((v, i) => {
    const off = offerteDi(v), pag = pagineDi(v);
    const apertaQui = aperto === i;

    const s = document.createElement('article');
    s.className = 'scheda';

    const testa = document.createElement('button');
    testa.className = 'testa';
    testa.type = 'button';
    testa.setAttribute('aria-expanded', String(apertaQui));
    testa.innerHTML = '<h3></h3><p class="riassunto"></p>';
    testa.querySelector('h3').textContent = v.nome;
    const ri = testa.querySelector('.riassunto');
    if (off.length) {
      ri.innerHTML = '<b></b> offerte lette a mano · <span></span> pagine nei volantini';
      ri.querySelector('b').textContent = off.length;
      ri.querySelector('span').textContent = pag.length;
    } else {
      ri.textContent = pag.length
        ? `${pag.length} pagine nei volantini lo nominano`
        : 'nessuna pagina lo nomina';
    }
    if (off.length) {
      const m = document.createElement('p');
      m.className = 'miglior';
      m.innerHTML = '<span class="n"></span><span class="u">al kg, il meno caro</span>';
      m.querySelector('.n').textContent = eur(off[0].kg) + ' €';
      testa.appendChild(m);
    } else {
      const f = document.createElement('span');
      f.className = 'freccia';
      f.textContent = apertaQui ? '▲' : '▼';
      testa.appendChild(f);
    }
    testa.onclick = () => { aperto = apertaQui ? null : i; disegna(); };
    s.appendChild(testa);

    if (apertaQui) {
      const det = document.createElement('div');
      det.className = 'dettaglio';

      if (off.length) {
        const b = document.createElement('div');
        b.className = 'blocco';
        b.innerHTML = '<h4>Prezzi letti dal volantino</h4>';
        off.forEach((o, k) => b.appendChild(schedaOfferta(o, k === 0)));
        det.appendChild(b);
      }

      const b2 = document.createElement('div');
      b2.className = 'blocco';
      b2.innerHTML = '<h4>Pagine da guardare</h4>';
      if (pag.length) {
        pag.slice(0, 14).forEach(p => b2.appendChild(rigaPagina(p)));
        if (pag.length > 14) {
          const p = document.createElement('p');
          p.className = 'nulla';
          p.textContent = `e altre ${pag.length - 14} pagine.`;
          b2.appendChild(p);
        }
      } else {
        const p = document.createElement('p');
        p.className = 'nulla';
        p.textContent = 'Il computer non ha letto questa parola in nessuna pagina. Prova a cambiare il nome del prodotto con una parola più comune.';
        b2.appendChild(p);
      }
      det.appendChild(b2);

      const az = document.createElement('div');
      az.className = 'azioni';
      const bRi = document.createElement('button');
      bRi.type = 'button'; bRi.textContent = 'Cambia prodotto';
      const bTo = document.createElement('button');
      bTo.type = 'button'; bTo.className = 'togli'; bTo.textContent = 'Togli dalla lista';
      bTo.onclick = () => {
        lista.splice(i, 1); aperto = null; salvaLista(); disegna();
      };
      az.append(bRi, bTo);
      det.appendChild(az);

      bRi.onclick = () => {
        az.remove();
        const f = document.createElement('form');
        f.className = 'rinomina';
        f.innerHTML = '<input type="text" aria-label="Nuovo nome del prodotto"><button type="submit">Salva</button>';
        const inp = f.querySelector('input');
        inp.value = v.nome;
        f.onsubmit = ev => {
          ev.preventDefault();
          const t = inp.value.trim();
          if (!t) return;
          lista[i] = { nome: t, parole: [t], cat: null };
          salvaLista(); disegna();
        };
        det.appendChild(f);
        inp.focus(); inp.select();
      };

      s.appendChild(det);
    }
    cont.appendChild(s);
  });
}

const vol = document.getElementById('elenco-vol');
DATI.volantini.forEach(v => {
  const li = document.createElement('li');
  li.innerHTML = `<span><span class="ins"></span> <span class="per"></span></span><span class="np"></span>`;
  li.querySelector('.ins').textContent = v.ins;
  li.querySelector('.per').textContent = v.periodo;
  li.querySelector('.np').textContent = v.pagine + ' pag.';
  vol.appendChild(li);
});

const nuovo = document.getElementById('nuovo');
const btnPiu = document.getElementById('btn-piu');
nuovo.addEventListener('input', () => { btnPiu.disabled = !nuovo.value.trim(); });
document.getElementById('form-aggiungi').onsubmit = ev => {
  ev.preventDefault();
  const t = nuovo.value.trim();
  if (!t) return;
  lista.push({ nome: t, parole: [t], cat: null });
  aperto = lista.length - 1;
  nuovo.value = ''; btnPiu.disabled = true;
  salvaLista(); disegna();
  document.querySelectorAll('.scheda')[aperto].scrollIntoView({ block: 'center' });
};

disegna();
</script>'''

open('out/pagina.html', 'w', encoding='utf-8').write(HTML.replace('__DATI__', DATI))
print('scritta out/pagina.html —', len(HTML) + len(DATI), 'caratteri;',
      len(partenza), 'prodotti di partenza,', len(offerte), 'offerte,', len(pagine), 'pagine')
