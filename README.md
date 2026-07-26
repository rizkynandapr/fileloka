# Fileloka — free file tools that never see your files

![tests](https://github.com/rizkynandapr/fileloka/actions/workflows/test.yml/badge.svg)

A single-file, production-ready website in the iLovePDF category, with one structural difference that doubles as its security model and its marketing angle: **every tool runs 100% client-side.** Files are never uploaded — there is no backend at all.

**Deliverables:** `index.html` (the entire site), `vercel.json` (security headers), this README.

---

## 1. Why these tools (research basis)

Decision inputs, gathered before building (July 2026):

- The category leader iLovePDF serves roughly 215–230M visits/month and sits around the global top-110 websites (Similarweb/Semrush estimates), with ~7-minute average sessions. Traffic is ~45% Google organic + ~44% direct — meaning people *remember and return to* these tools.
- Its top markets are India, **Indonesia (#2)**, Brazil, US, Colombia — utility tools are a genuinely universal, worldwide need, strongest in mobile-first emerging markets.
- The universally demanded core across iLovePDF/Smallpdf/PDF24/Adobe's free tools is stable: **merge, split, compress, PDF↔image**, plus image compress/resize/convert.
- iLovePDF is bootstrapped and profitable: freemium subscriptions provide 80–90% of revenue, the rest from a single small ad banner — proof the model works without VC money.
- Every major competitor's FAQ leads with the same user anxiety: "is my file safe? when is it deleted from your servers?" They answer with encryption promises. **Fileloka answers by removing the server.** That is the wedge.

Sources: Similarweb, Semrush, Ahrefs-style trackers for ilovepdf.com; iLovePDF case studies (marketingcrafted.com, lettersbydavey.com); competitor tool pages (Smallpdf, Adobe, PDF24, FreeConvert).

### The 12 launch tools
| # | Tool | Demand rationale |
|---|------|------------------|
| 1 | Merge PDF | #1 PDF task worldwide |
| 2 | Split PDF | Core PDF task |
| 3 | Compress PDF | Highest search intent ("fit email limit") |
| 4 | PDF → JPG | Core converter |
| 5 | Images → PDF | Scans/receipts → document; huge on mobile |
| 6 | Compress image | Universal (forms, WhatsApp, web) |
| 7 | Resize image | Universal |
| 8 | Convert image (JPG/PNG/WebP) | Universal |
| 9 | QR code maker | Evergreen utility, high search volume |
| 10 | Password generator | Evergreen utility |
| 11 | Word counter | Students/writers, evergreen |
| 12 | Signature maker | Pairs naturally with the PDF workflow |

Deliberately **excluded from v1** (need a server or heavy WASM): PDF↔Word/Excel, OCR, HEIC input, PDF unlock. They're on the roadmap (§7) as the premium/differentiation layer.

---

## 2. Architecture

- **Five static files** — `index.html`, `styles.css`, `app.js`, `/lib/*` (vendored libraries), `vercel.json`. Still zero build step; deploys anywhere static files are served.
- Heavy libraries are **self-hosted in `/lib/` (pinned versions, SHA-256 recorded in SECURITY.md) and lazy-loaded only when a tool needs them** — the page never executes third-party-origin JavaScript. First paint still ships ~0 KB of libraries:
  - `pdf-lib@1.17.1` — merge/split/build PDFs
  - `pdf.js@3.11.174` — render PDF pages (compress-strong, PDF→JPG)
  - `jszip@3.10.1` — multi-file downloads
  - `qrcodejs@1.0.0` — QR codes
  - Image tools use the native Canvas API — no library.
- **Signature UX features:** drop a file *anywhere* on the page and Fileloka suggests matching tools; hash routing (`#/merge-pdf`) makes every tool linkable; dark mode; `/` to search; keyboard + reduced-motion + focus-visible accessibility.
- No `localStorage`/`sessionStorage`, no cookies, no analytics, no external requests besides cdnjs + Google Fonts.

**Design system (intentionally not the default AI look):** porcelain `#F3F5F4` / ink `#12151A` / cobalt `#2440E8` / manila `#F0E4C3`; type = Gabarito (display) + Public Sans (body — literally designed for government documents) + IBM Plex Mono (numbers). The signature element is the **manila-folder tab on every tool card**, which carries the category label.

---

## 3. Security review (done before "listing")

**Threat model advantage:** with no upload endpoint there is no server-side attack surface for user files — nothing to breach, subpoena, or leak. Verifiable by users via DevTools → Network, or by going offline after page load.

Checklist status:

| Item | Status |
|---|---|
| Files processed locally only; zero upload endpoints | ✅ by architecture |
| XSS: all user-controlled strings (filenames, inputs) escaped via `esc()` before DOM insertion | ✅ |
| CSP `default-src 'none'`; `script-src 'self'` with **no** `unsafe-inline` and **no** external script origins; `object-src/frame-ancestors/form-action 'none'` | ✅ `vercel.json` |
| Clickjacking (`X-Frame-Options: DENY`), MIME sniffing (`nosniff`), referrer policy, permissions policy | ✅ `vercel.json` |
| Dependencies vendored locally at exact pinned versions — no third-party CDN in the execution path | ✅ (hashes in SECURITY.md) |
| Unbiased CSPRNG for passwords (`crypto.getRandomValues` + rejection sampling; guaranteed charset coverage) | ✅ tested |
| Encrypted/corrupt PDFs rejected with a clear message, never half-processed | ✅ tested |
| EXIF metadata stripped on JPG/WebP re-encode (privacy bonus, stated in UI) | ✅ |
| Object URLs revoked after download; canvases zeroed after use (memory hygiene) | ✅ |
| No storage APIs, no cookies, no trackers | ✅ |
| Honest privacy note + contact placeholder in-page | ✅ (replace the email before launch) |

**Before launch (see SECURITY.md for the full runbook):**
1. Replace `hello@fileloka.example` with a real address (page footer + `.well-known/security.txt`).
2. Lock down the *accounts* (GitHub/Vercel/registrar 2FA, registrar lock, DNSSEC) — for a hardened static site, account takeover is the #1 residual risk.
3. Optional next level: self-host the three Google Fonts → zero third-party requests of any kind (steps in SECURITY.md §4).
4. When you add AdSense later, you will consciously loosen the CSP for Google's domains — the current CSP correctly blocks ads until you do.

---

## 4. Test report

**Automated (27/27 passed)** — `test.js` runs the *verbatim* production functions against the same pdf-lib/jszip versions the CDN serves:

- Merge: 2+3 pages → valid 5-page PDF with `%PDF-` header
- Split: range parsing (`1-2, 5` → correct indices; reversed ranges normalized; duplicates de-duplicated; out-of-range/garbage/empty rejected with friendly errors); extracted PDFs valid; per-page → valid ZIP of 5 valid PDFs
- Compress (balanced): 10-page re-save stays valid, all pages kept
- Images→PDF: PNG embeds into a valid PDF
- Corrupt-file guard: friendly error, no crash
- Passwords: exact length at 8/16/64; across 300 samples every selected charset always present and look-alikes never appear; 16-char entropy ≈ 101 bits
- Word counter: words/sentences/paragraphs/unique/empty-input all correct
- Byte formatting correct

**Manual browser checklist (run once after deploy — needs a real browser for canvas/pdf.js rendering):**
- [ ] Chrome + Firefox + Safari (iOS): each tool end-to-end with a real file
- [ ] Compress-strong & PDF→JPG on a 50+ page scan (progress bar, memory)
- [ ] Drop-anywhere → chooser → tool receives files
- [ ] Dark mode, mobile layout (≤ 390px), keyboard-only navigation
- [ ] Offline test: load page, disconnect, run an image tool (libraries for PDF tools must be loaded once first)

---

## 5. Monetization plan (realistic, staged)

**Honest math:** display-ad RPM for utility sites is roughly **$1–4** (higher in US/EU traffic, lower in ID/IN). Revenue = traffic × RPM, so the site earns meaningfully only after SEO traffic compounds. iLovePDF's own model (freemium + one small banner) is the proven endgame.

- **Stage 1 — now:** two clearly-labeled ad slots are already in the layout (search `AD SLOT` in `index.html`). Apply for **Google AdSense** once you have a custom domain + the privacy note (already in-page) + some traffic. Keep exactly one visible ad per view — it's part of the brand ("one ad keeps every tool free").
- **Stage 2 — affiliate (higher RPM than display):** the audience is privacy-minded → VPN, password managers, and cloud-storage affiliate programs fit natively (e.g., a tasteful card under the password generator). 
- **Stage 3 — Pro tier ($2–4/mo):** batch processing, larger-file workflows, OCR and PDF↔Word (these genuinely need compute, so people accept paying), no ads. Payment via Stripe/Paddle or, for the Indonesian market, Midtrans/Xendit.
- **Stage 4 — API/embed** (iLovePDF's backlink flywheel): a free embeddable widget that links back = SEO engine.

**Traffic strategy (the actual moat):** one indexable page per tool (see roadmap), task-phrased blog posts ("cara kompres PDF jadi 200 KB"), bilingual EN+ID content — Indonesia is the category's #2 market and you're a native speaker; that's an unfair advantage.

---

## 6. Deploy (2 minutes)

```bash
# Option A — Vercel CLI
cd fileloka && vercel --prod
# Option B — drag-and-drop the folder at vercel.com/new
# Option C — Netlify/Cloudflare Pages: same files; port the headers from vercel.json
```
Then: custom domain → replace contact email → add SRI hashes → submit sitemap to Google Search Console.

## 7. Roadmap
1. ~~**SEO split**~~ — **shipped**: every tool now has its own indexable page (`/merge-pdf/`, `/split-pdf/`, …) with unique title, intro, FAQ + FAQPage/SoftwareApplication schema, plus `sitemap.xml` and `robots.txt`. Regenerate after copy edits with `python scripts/generate_tool_pages.py`.
2. PWA (manifest + service worker) → true offline + "install app" on mobile.
3. HEIC input (iPhone photos — very high search volume) via `heic2any`/WASM.
4. OCR (Tesseract WASM), PDF↔Word server-side → the Pro tier.
5. i18n: Bahasa Indonesia first (`/id/`), then ES/PT (Brazil/Colombia are top-5 markets).

---
*Built July 2026. Stack: HTML/CSS/JS, pdf-lib, pdf.js, jszip, qrcodejs — all client-side.*

---

## License

MIT © 2026 Rizky Nanda Praditia — see [LICENSE](LICENSE). Bundled libraries in `/lib` keep their own licenses (see [lib/README.md](lib/README.md)).
