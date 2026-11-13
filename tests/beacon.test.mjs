// Tests for functions/api/e.js, the counter endpoint. Run: node beacon.test.mjs
import { readFileSync } from 'node:fs';

// Cloudflare builds functions/ as ES modules. Loading the source through a data: URL lets
// Node run it the same way without a package.json that Pages would also have to read.
const src = readFileSync(new URL('../functions/api/e.js', import.meta.url), 'utf8');
const { parseEvent, onRequestPost, onRequest } = await import('data:text/javascript;base64,' + Buffer.from(src).toString('base64'));

let pass = 0, fail = 0;
const ok = (name, cond) => { if (cond) { pass++; console.log('  PASS  ' + name); } else { fail++; console.log('  FAIL  ' + name); } };

const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36';
const PHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148';
const good = { e: 'use', t: 'compress-pdf', p: '/compress-pdf-to-200kb/', l: 'en' };

function req(body, headers = {}, method = 'POST') {
  const h = { 'User-Agent': UA, 'Sec-Fetch-Site': 'same-origin', 'Content-Type': 'text/plain;charset=UTF-8', ...headers };
  for (const k of Object.keys(h)) if (h[k] === null) delete h[k];
  const init = { method, headers: h };
  if (method === 'POST') init.body = typeof body === 'string' ? body : JSON.stringify(body);
  return new Request('https://fileloka.id/api/e', init);
}

const row = await parseEvent(req(good));
ok('valid event is accepted', row && row.e === 'use' && row.t === 'compress-pdf' && row.p === '/compress-pdf-to-200kb/');
ok('device class: computer', row && row.device === 'd');
ok('device class: phone', (await parseEvent(req(good, { 'User-Agent': PHONE }))).device === 'm');
ok('country falls back to XX without Cloudflare', row && row.country === 'XX');
ok('row holds nothing but the six agreed fields', row && Object.keys(row).sort().join() === 'country,device,e,l,p,t');
ok('empty tool id is fine (home page view)', !!(await parseEvent(req({ e: 'pv', t: '', p: '/', l: 'id' }))));

ok('cross-site request is dropped', (await parseEvent(req(good, { 'Sec-Fetch-Site': 'cross-site' }))) === null);
ok('foreign Origin is dropped', (await parseEvent(req(good, { Origin: 'https://evil.example' }))) === null);
ok('own Origin is accepted', !!(await parseEvent(req(good, { Origin: 'https://fileloka.id' }))));
ok('bot user agent is dropped', (await parseEvent(req(good, { 'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1)' }))) === null);
ok('curl is dropped', (await parseEvent(req(good, { 'User-Agent': 'curl/8.5.0' }))) === null);
ok('missing user agent is dropped', (await parseEvent(req(good, { 'User-Agent': null }))) === null);
ok('unknown event is dropped', (await parseEvent(req({ ...good, e: 'login' }))) === null);
ok('unknown language is dropped', (await parseEvent(req({ ...good, l: 'xx' }))) === null);
ok('path with a query string is dropped', (await parseEvent(req({ ...good, p: '/merge-pdf/?email=a@b.c' }))) === null);
ok('path with markup is dropped', (await parseEvent(req({ ...good, p: '/<script>' }))) === null);
ok('file-name-like tool id is dropped', (await parseEvent(req({ ...good, t: 'Payslip March.pdf' }))) === null);
ok('non-string fields are dropped', (await parseEvent(req({ ...good, t: { a: 1 } }))) === null);
ok('oversized body is dropped', (await parseEvent(req(JSON.stringify({ ...good, x: 'a'.repeat(600) })))) === null);
ok('broken JSON is dropped', (await parseEvent(req('{not json'))) === null);
ok('JSON null is dropped', (await parseEvent(req('null'))) === null);

// The handler: always 204, empty body, writes exactly once for a good event.
const writes = [];
const env = { STATS: { writeDataPoint: (d) => writes.push(d) } };
let res = await onRequestPost({ request: req(good), env });
ok('good event answers 204 with no body', res.status === 204 && (await res.text()) === '');
ok('good event writes one data point', writes.length === 1);
ok('data point is indexed by event and counts 1', writes[0].indexes[0] === 'use' && writes[0].doubles[0] === 1);
ok('data point blobs are [event, tool, path, lang, country, device]',
  writes[0].blobs.join('|') === 'use|compress-pdf|/compress-pdf-to-200kb/|en|XX|d');
res = await onRequestPost({ request: req({ ...good, e: 'nope' }), env });
ok('bad event still answers 204 (nothing to probe)', res.status === 204 && writes.length === 1);
res = await onRequestPost({ request: req(good), env: {} });
ok('missing STATS binding is harmless', res.status === 204);
res = await onRequestPost({ request: req(good), env: { STATS: { writeDataPoint() { throw new Error('boom'); } } } });
ok('a failing write never reaches the visitor', res.status === 204);
ok('responses are never cached', res.headers.get('Cache-Control') === 'no-store');
ok('GET is refused with 405', onRequest().status === 405);

console.log('\n=================================');
console.log(` RESULT: ${pass} passed, ${fail} failed`);
console.log('=================================');
process.exit(fail ? 1 : 0);
