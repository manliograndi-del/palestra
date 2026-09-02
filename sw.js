/* Service worker: tiene l'app disponibile anche senza rete — in palestra
   il segnale è pessimo. Mette in cache i file uno per uno: se uno manca,
   gli altri vengono salvati comunque.
   Il nome della cache porta il prefisso "palestra-": sull'origine github.io
   vive anche l'app Diario e le due si cancellerebbero la cache a vicenda.
   Alza il numero di versione a ogni rilascio. */
const PREFISSO = "palestra-";
const CACHE = PREFISSO + "v17";
const FILE = ["./", "./index.html", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => Promise.all(FILE.map((f) => c.add(f).catch(() => null))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((k) => Promise.all(k
        .filter((x) => x.indexOf(PREFISSO) === 0 && x !== CACHE)
        .map((x) => caches.delete(x))))
      .then(() => self.clients.claim())
  );
});

/* Mette da parte una copia buona della risposta. */
function conserva(richiesta, risposta) {
  const copia = risposta.clone();
  caches.open(CACHE).then((c) => c.put(richiesta, copia)).catch(() => {});
  return risposta;
}

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;

  /* Quello che non è di casa nostra non ci riguarda: da quando la Palestra
     parla con Google Drive, senza questa riga una chiamata a Google andata
     storta si sarebbe presa in cambio la pagina dell'app, e chi l'ha chiamata
     avrebbe letto HTML al posto della risposta. */
  if (new URL(e.request.url).origin !== self.location.origin) return;

  /* La pagina viene chiesta prima alla rete: è tutta l'app, e servirla dalla
     cache significava mostrare per giorni una versione vecchia, costringendo
     a ricaricare due volte. Senza rete si ricade sulla copia salvata. */
  if (e.request.mode === "navigate" || e.request.destination === "document") {
    e.respondWith(
      fetch(e.request)
        .then((res) => conserva(e.request, res))
        .catch(() => caches.match(e.request).then((r) => r || caches.match("./index.html")))
    );
    return;
  }

  /* Icone e manifest cambiano quasi mai: prima la cache, è più veloce. */
  e.respondWith(
    caches.match(e.request).then((r) => {
      if (r) return r;
      return fetch(e.request)
        .then((res) => conserva(e.request, res))
        .catch(() => caches.match("./index.html"));
    })
  );
});
