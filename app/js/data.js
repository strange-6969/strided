/* Loads the static dataset at runtime.
   JSON import attributes (`with { type: 'json' }`) are still uneven across
   browsers, and a plain fetch of a static file works everywhere and maps
   directly onto how Vercel serves the directory. */

let cache = null;
let inflight = null;

const SOURCES = [
  { key: 'problems', url: '/data/problems.json' },
  { key: 'spine', url: '/data/spine.json' },
];

export async function loadData() {
  if (cache) return cache;
  if (!inflight) {
    inflight = Promise.all(
      SOURCES.map((s) =>
        fetch(s.url, { cache: 'no-cache' }).then((r) => {
          if (!r.ok) throw new Error(`${s.key} request failed: ${r.status}`);
          return r.json();
        })
      )
    )
      .then(([problems, spine]) => {
        cache = { problems, spine };
        return cache;
      })
      .catch((err) => {
        inflight = null;
        throw err;
      });
  }
  return inflight;
}