/* POST /api/e : Fileloka's only server-side code.
 *
 * It receives the anonymous counters sent by app.js (page opened, tool
 * finished, download, click on the money slot) and writes one row per event to
 * a Workers Analytics Engine dataset bound as STATS.
 *
 * What a row holds: event, tool or slot id, page path, page language, country
 * (two letters, from Cloudflare) and device class (m = phone, d = computer).
 * What it never holds: IP address, user agent, cookie, any id for the visitor,
 * anything about a file.
 *
 * It always answers 204 with an empty body. Bad input is dropped silently, so
 * there is nothing to probe and nothing reflected back.
 *
 * Without the STATS binding the function still answers 204 and stores nothing,
 * so deploying this before the binding exists is safe.
 */

const EVENTS = new Set(['pv', 'open', 'use', 'dl', 'out']);
const LANGS = new Set(['en', 'id']);
const ID_RE = /^[a-z0-9-]{0,40}$/;
const PATH_RE = /^\/[a-z0-9/-]{0,80}$/;
const BOT_RE = /bot|crawl|spider|slurp|headless|lighthouse|pagespeed|preview|monitor|scan|curl|wget|python|okhttp|axios|go-http|java\/|httpclient/i;
const MAX_BODY = 512;

const NO_CONTENT = () => new Response(null, {
  status: 204,
  headers: { 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' },
});

/** Turn a request into a clean row, or null when it should be ignored. Exported for tests. */
export async function parseEvent(request) {
  // Only our own pages may report. Browsers set Sec-Fetch-Site themselves; scripts on other sites can't fake it.
  const site = request.headers.get('Sec-Fetch-Site');
  if (site && site !== 'same-origin') return null;
  const origin = request.headers.get('Origin');
  if (origin && origin !== new URL(request.url).origin) return null;

  const ua = request.headers.get('User-Agent') || '';
  if (!ua || BOT_RE.test(ua)) return null;

  if (Number(request.headers.get('Content-Length') || 0) > MAX_BODY) return null;
  let d;
  try {
    const text = await request.text();
    if (text.length > MAX_BODY) return null;
    d = JSON.parse(text);
  } catch (_) {
    return null;
  }
  if (!d || typeof d !== 'object') return null;
  const { e, t = '', p, l } = d;
  if (!EVENTS.has(e) || !LANGS.has(l)) return null;
  if (typeof t !== 'string' || !ID_RE.test(t)) return null;
  if (typeof p !== 'string' || !PATH_RE.test(p)) return null;

  const country = (request.cf && request.cf.country) || 'XX';
  const device = /Mobi|Android|iPhone|iPad/i.test(ua) ? 'm' : 'd';
  return { e, t, p, l, country, device };
}

export async function onRequestPost({ request, env }) {
  const row = await parseEvent(request);
  if (row && env && env.STATS) {
    // Non-blocking by design; a failed write must never surface to the visitor.
    try {
      env.STATS.writeDataPoint({
        indexes: [row.e],
        blobs: [row.e, row.t, row.p, row.l, row.country, row.device],
        doubles: [1],
      });
    } catch (_) { /* dropped on purpose */ }
  }
  return NO_CONTENT();
}

// Anything that isn't a POST.
export function onRequest() {
  return new Response(null, { status: 405, headers: { Allow: 'POST', 'Cache-Control': 'no-store' } });
}
