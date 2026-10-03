/* Loads the static dataset at runtime.
   JSON import attributes (`with { type: 'json' }`) are still uneven across
   browsers, and a plain fetch of a static file works everywhere and maps
   directly onto how Vercel serves the directory. */

let cache = null;
let inflight = null;

const SOURCES = [
  { key: 'problems', url: '/data/problems.json' },
  { key: 'spine', url: '/data/spine.json' },
  { key: 'catalog', url: '/data/catalog.json' },
];

export async function loadData() {
  if (cache) return cache;
  if (!inflight) {
    /* The catalog is large and useful but not required to render, so a failure
       to fetch it degrades to "catalog unavailable" rather than taking the
       whole app down. The other two are load-bearing and must succeed. */
    const essential = SOURCES.filter((s) => s.key !== 'catalog').map((s) =>
      fetch(s.url, { cache: 'no-cache' }).then((r) => {
        if (!r.ok) throw new Error(`${s.key} request failed: ${r.status}`);
        return r.json();
      })
    );
    const catalog = fetch(SOURCES[2].url, { cache: 'no-cache' })
      .then((r) => (r.ok ? r.json() : null))
      .catch(() => null);

    inflight = Promise.all([Promise.all(essential), catalog])
      .then(([[problems, spine], catalogJson]) => {
        cache = { problems, spine, catalog: catalogJson };
        return cache;
      })
      .catch((err) => {
        inflight = null;
        throw err;
      });
  }
  return inflight;
}