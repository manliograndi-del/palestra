/* Service worker della Spesa.

   Sta in questa cartella di proposito. Sopra, su /palestra/, ce n'è un altro:
   il suo scope copre anche noi e, senza rete, servirebbe l'index.html della
   Palestra al posto di questa pagina. Uno registrato più in basso vince sul
   suo scope, quindi questo file toglie di mezzo il problema e in più tiene la
   Spesa disponibile in negozio, dove il segnale è pessimo.

   Alza il numero a ogni rilascio, altrimenti resta in giro la copia vecchia. */
const PREFISSO = "spesa-";
const CACHE = PREFISSO + "v7";
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

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  /* Quello che non è di casa nostra non ci riguarda: i caratteri di Google
     se non arrivano fanno solo scendere ai caratteri di sistema. */
  if (new URL(e.request.url).origin !== self.location.origin) return;

  /* La pagina prima alla rete: i prezzi cambiano ogni settimana e servirla
     dalla cache vorrebbe dire mostrare offerte scadute. Senza rete si ricade
     sulla copia salvata, che è meglio di niente. */
  if (e.request.mode === "navigate" || e.request.destination === "document") {
    e.respondWith(
      fetch(e.request)
        .then((res) => {
          const copia = res.clone();
          caches.open(CACHE).then((c) => c.put(e.request, copia)).catch(() => {});
          return res;
        })
        .catch(() => caches.match(e.request).then((r) => r || caches.match("./index.html")))
    );
    return;
  }

  e.respondWith(caches.match(e.request).then((r) => r || fetch(e.request)));
});
