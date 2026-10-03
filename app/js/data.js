/* Loads the static dataset at runtime.
   JSON import attributes (`with { type: 'json' }`) are still uneven across
   browsers, and a plain fetch of a static file works everywhere and maps
   directly onto how Vercel serves the directory. */

let cache = null;
let inflight = null;

export async function loadData() {
  if (cache) return cache;
  if (!inflight) {
    inflight = fetch('/data/problems.json', { cache: 'no-cache' })
      .then((r) => {
        if (!r.ok) throw new Error(`Dataset request failed: ${r.status}`);
        return r.json();
      })
      .then((json) => {
        cache = json;
        return cache;
      })
      .catch((err) => {
        inflight = null;
        throw err;
      });
  }
  return inflight;
}