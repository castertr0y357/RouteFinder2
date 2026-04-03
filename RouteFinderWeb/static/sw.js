self.addEventListener('install', (e) => {
    e.waitUntil(
      caches.open('routefinder-store').then((cache) => cache.addAll([
        '/',
        '/RouteFinderWeb/',
        '/static/icon.png'
      ])),
    );
  });
  
  self.addEventListener('fetch', (e) => {
    e.respondWith(
      caches.match(e.request).then((response) => response || fetch(e.request)),
    );
  });
