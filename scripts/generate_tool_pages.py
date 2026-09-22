#!/usr/bin/env python3
"""Build every static page of Fileloka from one set of templates.

Outputs (all committed; deploy stays a plain static upload):
  /index.html, /id/index.html                 home pages (EN / ID)
  /<tool>/, /id/<tool>/                       13 tools × 2 languages
  /compress-pdf-to-<size>/, /id/kompres-pdf-<size>/   target-size landings
  /404.html, /sitemap.xml, /robots.txt

Run from the repo root:  python3 scripts/generate_tool_pages.py
"""
import hashlib, html, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content_en import P
from content_id import P_ID, NAMES, CARD_DESC_ID, UI, HOME_ID
from content_sizes import SIZES, slug as size_slug, page as size_page
from cards import ICONS, CATS, KEYS, CARD_DESC_EN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://fileloka.id"
TODAY = "2026-09-23"
CONTACT = "rizkynandapr@gmail.com"
ORDER = ["compress-pdf", "merge-pdf", "split-pdf", "pdf-to-jpg", "jpg-to-pdf", "heic-to-jpg",
         "compress-image", "resize-image", "convert-image", "qr-code", "password-generator",
         "word-counter", "signature"]
CONTENT = {"en": P, "id": P_ID}
PREFIX = {"en": "", "id": "id/"}
LOCALE = {"en": "en_US", "id": "id_ID"}
E = html.escape

def asset_ver(name):
    with open(os.path.join(ROOT, name), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:10]
V_CSS, V_JS = asset_ver("styles.css"), asset_ver("app.js")

ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12h13m-5-5 5 5-5 5"/></svg>'
CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>'
SEARCH_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.8-3.8"/></svg>'
UP_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 16V4m0 0 4 4m-4-4-4 4"/><path d="M3 15v3a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-3"/></svg>'
BACK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 12H7m5 5-5-5 5-5"/></svg>'
BRAND_MARK = ('<svg class="brand-mark" viewBox="0 0 32 32" aria-hidden="true">'
              '<rect x="1" y="1" width="30" height="30" rx="8" fill="var(--ink)"/>'
              '<path d="M9.5 7.5h7.2l5.3 5.3v11.7H9.5z" fill="none" stroke="var(--bg)" stroke-width="1.9" stroke-linejoin="round"/>'
              '<path d="M16.5 7.5v5.5H22" fill="none" stroke="var(--bg)" stroke-width="1.9" stroke-linejoin="round"/>'
              '<circle cx="24.2" cy="24.2" r="4.2" fill="#C4EE2F" stroke="var(--ink)" stroke-width="1.6"/></svg>')

TXT = {
 "en": dict(pill="Local · 0 uploads", home="Home", tools="Tools", faq="FAQ", privacy="Privacy",
            theme="Switch color theme", lang_label="Bahasa Indonesia", sizes_h="Compress to an exact size",
            sizes_lead="Upload forms reject anything over their limit. Pick the number they ask for and Fileloka fits your PDF under it.",
            foot="© 2026 Fileloka. Every tool runs on your device.", crumbs="Breadcrumb",
            chooser=("Got it.", "What do you want to do with these files?", "Cancel"),
            overlay="Let go and we'll suggest a tool", ad=("Advertisement", "This one ad pays for the hosting."),
            all_sizes="Other targets", tool_404="Page not found"),
 "id": dict(pill="Lokal · 0 upload", home="Beranda", tools="Alat", faq="FAQ", privacy="Privasi",
            theme="Ganti tema warna", lang_label="English", sizes_h="Kompres ke ukuran pasti",
            sizes_lead="Formulir online menolak file yang lewat batas. Pilih angka yang diminta, Fileloka yang mengepaskan PDF-mu di bawahnya.",
            foot="© 2026 Fileloka. Semua alat jalan di perangkatmu.", crumbs="Navigasi",
            chooser=("Oke.", "File ini mau diapakan?", "Batal"),
            overlay="Lepaskan, nanti kami sarankan alatnya", ad=("Iklan", "Satu iklan ini yang membayar biaya hosting."),
            all_sizes="Target lain", tool_404="Halaman tidak ditemukan"),
}

# ------------------------------------------------------------------ chrome
def head(lang, title, meta, url, alts, ld, extra=""):
    alt_html = "\n".join(f'<link rel="alternate" hreflang="{h}" href="{u}">' for h, u in alts)
    lds = ld if isinstance(ld, list) else [ld]
    ld_html = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(meta)}">
<link rel="canonical" href="{url}">
{alt_html}
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#EDF0F3" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#07090D" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Fileloka">
<meta property="og:locale" content="{LOCALE[lang]}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(meta)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMAIN}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/fonts/geist.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/styles.css?v={V_CSS}">
{ld_html}{extra}
</head>"""

def topbar(lang, twin):
    t = TXT[lang]
    home = "/" if lang == "en" else "/id/"
    other = "ID" if lang == "en" else "EN"
    other_lang = "id" if lang == "en" else "en"
    return f"""<header class="topbar">
  <div class="wrap topbar-in">
    <a class="brand" href="{home}" aria-label="Fileloka, {t['home']}">{BRAND_MARK}<span class="brand-name">File<em>loka</em></span></a>
    <div class="topbar-actions">
      <span class="privacy-pill" title="{E('All tools run locally in your browser' if lang=='en' else 'Semua alat berjalan lokal di browser-mu')}"><span class="dot"></span>{t['pill']}</span>
      <a class="lang-link" href="{twin}" hreflang="{other_lang}" lang="{other_lang}" aria-label="{t['lang_label']}">{other}</a>
      <button class="icon-btn" id="themeBtn" type="button" aria-label="{t['theme']}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path id="themeIcon" d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z"/></svg></button>
    </div>
  </div>
</header>"""

def footer(lang):
    t, pre = TXT[lang], PREFIX[lang]
    tools = "".join(f'<li><a href="/{pre}{tid}/">{E(NAMES[tid][lang])}</a></li>' for tid in ORDER)
    sizes = "".join(f'<li><a href="/{size_slug(lang,k)}/">{E(("Kompres PDF " if lang=="id" else "Compress PDF to ")+lab)}</a></li>' for k, _, lab in SIZES)
    home = "/" if lang == "en" else "/id/"
    other = ("/id/", "Bahasa Indonesia") if lang == "en" else ("/", "English")
    return f"""<footer>
  <div class="wrap">
    <ul class="foot-tools">{tools}{sizes}</ul>
    <div class="foot-in">
      <div>{t['foot']}</div>
      <nav>
        <a href="{home}">{t['home']}</a>
        <a href="{home}#faq">{t['faq']}</a>
        <a href="{home}#privacy">{t['privacy']}</a>
        <a href="{other[0]}" hreflang="{'id' if lang=='en' else 'en'}">{other[1]}</a>
        <a href="https://github.com/rizkynandapr/tooldock" rel="noopener">GitHub</a>
      </nav>
    </div>
  </div>
</footer>
<div class="toasts" id="toasts" aria-live="polite"></div>
<script src="/app.js?v={V_JS}" defer></script>
</body>
</html>
"""

def ad(lang):
    a, b = TXT[lang]["ad"]
    return f'<aside class="ad-slot" aria-label="{a}"><span>{a}</span><small>{b}</small></aside>'

def faq_block(faqs):
    return "\n".join(f"<details>\n  <summary>{E(q)}</summary>\n  <p>{E(a)}</p>\n</details>" for q, a in faqs)

def faq_ld(lang, faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": lang,
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

def crumbs_html(lang, items):
    lis = []
    for i, (n, u) in enumerate(items):
        path = u.replace(DOMAIN, "")
        lis.append(f'<li><a href="{path}">{E(n)}</a></li>' if i < len(items) - 1 else f'<li aria-current="page">{E(n)}</li>')
    return f'<ol class="crumbs" aria-label="{TXT[lang]["crumbs"]}">{"".join(lis)}</ol>'

def app_ld(lang, name, url, desc):
    return {"@context": "https://schema.org", "@type": "WebApplication", "name": name, "url": url,
            "inLanguage": lang, "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any (web browser)",
            "browserRequirements": "Requires JavaScript", "isAccessibleForFree": True, "description": desc,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            "publisher": {"@type": "Organization", "name": "Fileloka", "url": DOMAIN + "/"}}

def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def size_links(lang, current=None):
    out = []
    for k, _, lab in SIZES:
        cur = ' aria-current="page"' if k == current else ""
        out.append(f'<a class="rel-link size" href="/{size_slug(lang,k)}/"{cur}>{lab}</a>')
    return '<div class="rel-links">' + "".join(out) + "</div>"

# ------------------------------------------------------------------ tool pages
def render_tool(lang, tid):
    d, t, ui, pre = CONTENT[lang][tid], TXT[lang], UI[lang], PREFIX[lang]
    url = f"{DOMAIN}/{pre}{tid}/"
    en_url, id_url = f"{DOMAIN}/{tid}/", f"{DOMAIN}/id/{tid}/"
    twin = id_url if lang == "en" else en_url
    home_url = f"{DOMAIN}/" + pre
    crumbs = [(t["home"], home_url), (NAMES[tid][lang], url)]
    rel_html = "\n".join(f'<a class="rel-link" href="/{pre}{r}/">{E(NAMES[r][lang])}</a>' for r in d["related"])
    sizes = ""
    if tid == "compress-pdf":
        sizes = f"""
  <section class="section">
    <h2>{t['sizes_h']}</h2>
    <p class="note" style="margin:-8px 0 16px">{t['sizes_lead']}</p>
    {size_links(lang)}
  </section>"""
    steps = "\n".join(f"<li>{E(s)}</li>" for s in d["steps"])
    ld = [app_ld(lang, NAMES[tid][lang] + " | Fileloka", url, d["meta"]), faq_ld(lang, d["faqs"]), crumbs_ld(crumbs)]
    page = head(lang, d["title"], d["meta"], url, [("en", en_url), ("id", id_url), ("x-default", en_url)], ld)
    page += f"""
<body data-tool="{tid}">
{topbar(lang, twin)}
<main class="wrap">
  <div class="tool-hero">
    {crumbs_html(lang, crumbs)}
    <h1>{E(d["h1"])}</h1>
    <p class="lead">{E(d["lead"])}</p>
  </div>
  <section class="view is-active" id="view-tool">
    <div id="toolMount"></div>
  </section>{sizes}
  <section class="section">
    <h2>{ui['how']}</h2>
    <ol class="howto">
{steps}
    </ol>
  </section>
  {ad(lang)}
  <section class="section faq">
    <h2>{ui['faq']}</h2>
{faq_block(d["faqs"])}
  </section>
  <section class="section">
    <h2>{ui['rel']}</h2>
    <div class="rel-links">
{rel_html}
    </div>
  </section>
</main>
"""
    page += footer(lang)
    write(f"{pre}{tid}/index.html", page)
    return url

# ------------------------------------------------------------------ size landings
def render_size(lang, key, nbytes, label):
    d, t, ui, pre = size_page(lang, key, nbytes, label), TXT[lang], UI[lang], PREFIX[lang]
    url = f"{DOMAIN}/{size_slug(lang,key)}/"
    en_url, id_url = f"{DOMAIN}/{size_slug('en',key)}/", f"{DOMAIN}/{size_slug('id',key)}/"
    twin = id_url if lang == "en" else en_url
    crumbs = [(t["home"], f"{DOMAIN}/{pre}"), (NAMES["compress-pdf"][lang], f"{DOMAIN}/{pre}compress-pdf/"), (label, url)]
    steps = "\n".join(f"<li>{E(s)}</li>" for s in d["steps"])
    rows = "\n".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td></tr>" for a, b in d["rows"])
    kicker = "".join(f"<li>{E(k)}</li>" for k in d["kicker"])
    rel = ["merge-pdf", "split-pdf", "jpg-to-pdf"]
    rel_html = "\n".join(f'<a class="rel-link" href="/{pre}{r}/">{E(NAMES[r][lang])}</a>' for r in rel)
    ld = [app_ld(lang, d["name"] + " | Fileloka", url, d["meta"]), faq_ld(lang, d["faqs"]), crumbs_ld(crumbs)]
    page = head(lang, d["title"], d["meta"], url, [("en", en_url), ("id", id_url), ("x-default", en_url)], ld)
    page += f"""
<body data-tool="compress-pdf" data-target="{nbytes}">
{topbar(lang, twin)}
<main class="wrap">
  <div class="tool-hero">
    {crumbs_html(lang, crumbs)}
    <h1>{E(d["h1"])}</h1>
    <p class="lead">{E(d["lead"])}</p>
    <ul class="kicker">{kicker}</ul>
  </div>
  <section class="view is-active" id="view-tool">
    <div id="toolMount"></div>
  </section>
  <section class="section">
    <h2>{t['all_sizes']}</h2>
    {size_links(lang, key)}
  </section>
  <section class="section prose">
    <h2>{E(d["use_h"])}</h2>
    <p>{E(d["use"])}</p>
    <h3>{E(d["table_h"])}</h3>
    <div class="table-wrap"><table class="spec">
      <thead><tr><th scope="col">{E(d["th"][0])}</th><th scope="col">{E(d["th"][1])}</th></tr></thead>
      <tbody>
{rows}
      </tbody>
    </table></div>
    <p class="note">{E(d["table_note"])}</p>
  </section>
  <section class="section">
    <h2>{ui['how']}</h2>
    <ol class="howto">
{steps}
    </ol>
  </section>
  {ad(lang)}
  <section class="section faq">
    <h2>{ui['faq']}</h2>
{faq_block(d["faqs"])}
  </section>
  <section class="section">
    <h2>{ui['rel']}</h2>
    <div class="rel-links">
<a class="rel-link" href="/{pre}compress-pdf/">{E(NAMES['compress-pdf'][lang])}</a>
{rel_html}
    </div>
  </section>
</main>
"""
    page += footer(lang)
    write(f"{size_slug(lang,key)}/index.html", page)
    return url

# ------------------------------------------------------------------ home
HOME_EN = dict(
 title="Fileloka: Free PDF and Image Tools That Don't Upload Your Files",
 meta="Compress, merge and split PDFs, convert and resize images, make QR codes and more. Free and without sign-up. Every tool runs in your browser, so your files stay on your device.",
 eyebrow=("Local-first", "file tools"),
 h1='File tools that <span class="hl">never see your files.</span>',
 lede='Compress, merge, split and convert PDFs and images for free. Everything happens in your browser, <strong>so your files never leave your device</strong> and you don\'t need an account.',
 proof=["0 files uploaded", "No sign-up", "Works on phones"],
 dock=("Drop dock", "ready", "Drop PDFs or images here", "or tap to pick, and we'll suggest a tool"),
 dock_rows=[("Uploads", "0"), ("Account", "none"), ("Watermark", "none")],
 search_ph="Find a tool, e.g. compress or merge",
 tabs=[("all", "All"), ("pdf", "PDF"), ("image", "Image"), ("util", "Everyday")],
 grid_label="Tools", grid_empty="Nothing matches that. Try PDF, image or QR.",
 feat_chips=["100 KB", "200 KB", "500 KB", "1 MB"],
 why_h="How it's different",
 why=[("Your files stay with you", "Most tool sites upload your file, process it on their server and promise to delete it later. Fileloka skips the upload. Your browser does the work, so there's nothing on our side to store or leak."),
      ("Quick, even on bad Wi-Fi", "There's nothing to upload and nothing to download back, so a typical PDF is done in a few seconds. Slow hotel Wi-Fi doesn't matter because it isn't involved."),
      ("Free, and it stays free", "Without servers crunching files, running Fileloka costs very little. That's why every tool is fully usable, without watermarks or a daily limit.")],
 faq_h="Fair questions",
 faqs=[("Are my files really private?", "Yes, and you can check. Open your browser's developer tools (F12, then the Network tab) while you use a tool and you'll see no file being sent. You can also load a page, switch off your internet, and the tools keep working."),
       ("Is there a file size limit?", "Not one we set. Your device's memory is the limit, and most phones and laptops handle files up to around 100 MB without trouble. Big scans take longer on older devices because they're doing the work."),
       ("Can I compress a PDF to an exact size like 200 KB?", "Yes. Open Compress PDF, choose Target size and pick 100 KB, 200 KB, 500 KB or 1 MB, or type your own number. Fileloka finds the best quality that fits under it."),
       ("Why is it free?", "Your device does the processing, so hosting costs very little. One clearly labelled ad spot is enough to cover it, and every tool works fully without a watermark."),
       ("Can I use it for work or for clients?", "Yes. Since files never leave your device, it's a better fit for contracts, IDs and invoices than sites that keep copies on their servers.")],
 privacy_h="Privacy, in plain words",
 privacy=f"Your files are processed in your browser and never reach us. There are no accounts, cookies or analytics on this site. If we show ads in the future, the ad provider may set its own cookies, but that never touches your files. Questions: <a href=\"mailto:{CONTACT}\">{CONTACT}</a>.",
)
HOME_ID2 = dict(
 title=HOME_ID["title"], meta=HOME_ID["meta"],
 eyebrow=("Lokal", "alat file"),
 h1='Alat file yang <span class="hl">tidak pernah melihat filemu.</span>',
 lede='Kompres, gabung, pisah, dan ubah PDF serta foto, gratis. Semua diproses di browser, <strong>jadi filemu tidak pernah keluar dari perangkat</strong> dan kamu tidak perlu bikin akun.',
 proof=["0 file di-upload", "Tanpa daftar", "Bisa di HP"],
 dock=("Dok file", "siap", "Seret PDF atau foto ke sini", "atau ketuk untuk memilih, nanti kami sarankan alatnya"),
 dock_rows=[("Upload", "0"), ("Akun", "tidak perlu"), ("Watermark", "tidak ada")],
 search_ph=HOME_ID["search_ph"], tabs=[("all", "Semua"), ("pdf", "PDF"), ("image", "Gambar"), ("util", "Harian")],
 grid_label="Alat", grid_empty=HOME_ID["grid_empty"],
 feat_chips=["100 KB", "200 KB", "500 KB", "1 MB"],
 why_h=HOME_ID["why_h"],
 why=[("Filemu tetap di tanganmu", "Kebanyakan situs sejenis meng-upload file ke server lalu janji menghapusnya nanti. Fileloka tidak meng-upload apa pun. Browser-mu yang bekerja, jadi di pihak kami tidak ada file yang bisa tersimpan atau bocor."),
      ("Tetap cepat walau sinyal jelek", "Tidak ada yang perlu di-upload lalu diunduh lagi, jadi PDF biasa selesai dalam beberapa detik. Wi-Fi lemot tidak berpengaruh karena memang tidak dipakai."),
      ("Gratis, dan akan tetap gratis", "Karena tidak ada server yang memproses file, biaya menjalankan Fileloka kecil sekali. Makanya semua alat bisa dipakai penuh, tanpa watermark dan tanpa batas harian.")],
 faq_h=HOME_ID["faq_h"],
 faqs=HOME_ID["faqs"][:2] + [("Bisa kompres PDF ke ukuran tertentu, misalnya 200 KB?", "Bisa. Buka Kompres PDF, pilih Target ukuran, lalu klik 100 KB, 200 KB, 500 KB, atau 1 MB. Bisa juga ketik angka sendiri. Fileloka mencarikan kualitas terbaik yang masih muat di bawahnya.")] + HOME_ID["faqs"][2:],
 privacy_h=HOME_ID["privacy_h"],
 privacy=f"Filemu diproses di browser dan tidak pernah sampai ke kami. Situs ini tidak memakai akun, cookie, atau analytics. Kalau nanti ada iklan, penyedia iklannya mungkin memasang cookie sendiri, tapi itu tidak pernah menyentuh filemu. Ada pertanyaan? <a href=\"mailto:{CONTACT}\">{CONTACT}</a>.",
)
WHY_ICONS = [
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l7 3v5c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/><path d="m9.5 11.5 2 2 3.5-3.5"/></svg>',
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M13 2 4 14h6l-1 8 9-12h-6z"/></svg>',
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v10M14.5 9.5c0-1.1-1.1-2-2.5-2s-2.5.9-2.5 2 1 1.6 2.5 2 2.5.9 2.5 2-1.1 2-2.5 2-2.5-.9-2.5-2"/></svg>',
]
CAT_LABEL = {"en": {"pdf": "PDF", "image": "Image", "util": "Util"}, "id": {"pdf": "PDF", "image": "Gambar", "util": "Harian"}}

def card(lang, tid, H):
    pre = PREFIX[lang]
    name = NAMES[tid][lang]
    desc = CARD_DESC_EN[tid] if lang == "en" else CARD_DESC_ID[tid]
    go = UI[lang]["open_tool"]
    feat = tid == "compress-pdf"
    fm = ('<span class="fm" aria-hidden="true"><span><em>' + ("before" if lang=="en" else "awal") + '</em><b><i style="width:100%"></i></b><s>2.4 MB</s></span>'
          '<span><em>' + ("after" if lang=="en" else "hasil") + '</em><b><i class="on" style="width:8%"></i></b><s>196 KB</s></span></span>') if feat else ""
    chips = ('<span class="chips">' + "".join(f"<span>{c}</span>" for c in H["feat_chips"]) + "</span>") if feat else ""
    keys = KEYS[tid] + (" 100kb 200kb 500kb 1mb target size ukuran" if feat else "")
    return (f'<a class="card{" feat" if feat else ""}" href="/{pre}{tid}/" data-cat="{CATS[tid]}" data-tab="{CAT_LABEL[lang][CATS[tid]]}" data-k="{E(keys)}">\n'
            f'  <span class="ic">{ICONS[tid]}</span>{fm}\n'
            f'  <h3>{E(name)}</h3><p>{E(desc)}</p>{chips}\n'
            f'  <span class="go">{go} {ARROW}</span>\n</a>')

def render_home(lang):
    H = HOME_EN if lang == "en" else HOME_ID2
    t, pre = TXT[lang], PREFIX[lang]
    url = f"{DOMAIN}/{pre}"
    twin = f"{DOMAIN}/id/" if lang == "en" else f"{DOMAIN}/"
    proof = "".join(f"<li>{CHECK}{E(p)}</li>" for p in H["proof"])
    tabs = "".join(f'<button class="tab" type="button" role="tab" aria-selected="{"true" if i==0 else "false"}" data-cat="{c}">{E(n)}</button>' for i, (c, n) in enumerate(H["tabs"]))
    cards = "\n".join(card(lang, tid, H) for tid in ORDER)
    why = "".join(f"<article><h3>{WHY_ICONS[i]}{E(h)}</h3><p>{E(p)}</p></article>" for i, (h, p) in enumerate(H["why"]))
    rows = "".join(f"<li><span>{E(a)}</span><b>{E(b)}</b></li>" for a, b in H["dock_rows"])
    site_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "Fileloka", "url": url, "inLanguage": lang}
    ld = [app_ld(lang, "Fileloka", url, H["meta"]), site_ld, faq_ld(lang, H["faqs"])]
    ch = t["chooser"]
    page = head(lang, H["title"], H["meta"], url, [("en", f"{DOMAIN}/"), ("id", f"{DOMAIN}/id/"), ("x-default", f"{DOMAIN}/")], ld)
    page += f"""
<body>
<div class="overlay" id="dropOverlay" aria-hidden="true"><div class="ov-card">{E(t['overlay'])}</div></div>
<div class="chooser" id="chooser" role="dialog" aria-modal="true" aria-labelledby="chTitle">
  <div class="ch-card">
    <h3 id="chTitle">{E(ch[0])}</h3>
    <p id="chSub">{E(ch[1])}</p>
    <div class="ch-list" id="chList"></div>
    <button class="btn btn-ghost btn-sm ch-cancel" id="chCancel" type="button">{E(ch[2])}</button>
  </div>
</div>
{topbar(lang, twin)}
<main>
<section class="view is-active" id="view-home">
  <div class="wrap">
    <div class="hero">
      <div>
        <p class="eyebrow rise"><b>{E(H['eyebrow'][0])}</b>{E(H['eyebrow'][1])}</p>
        <h1 class="rise" style="animation-delay:.04s">{H['h1']}</h1>
        <p class="lede rise" style="animation-delay:.08s">{H['lede']}</p>
        <ul class="proof rise" style="animation-delay:.12s">{proof}</ul>
      </div>
      <div class="dock hud rise" style="animation-delay:.1s">
        <div class="dock-head"><span>{E(H['dock'][0])}</span><i>{E(H['dock'][1])}</i></div>
        <div class="dz" id="heroDz" tabindex="0" role="button" aria-label="{E(H['dock'][2])}">
          <span class="dz-ic">{UP_SVG}</span><strong>{E(H['dock'][2])}</strong><small>{E(H['dock'][3])}</small><input type="file">
        </div>
        <ul class="dock-rows">{rows}</ul>
      </div>
    </div>

    <div class="finder">
      <div class="search">
        {SEARCH_SVG}
        <input type="search" id="searchInput" placeholder="{E(H['search_ph'])}" aria-label="{E(H['search_ph'])}">
        <kbd>/</kbd>
      </div>
      <div class="tabs" role="tablist" aria-label="{E(H['grid_label'])}">{tabs}</div>
    </div>
    <h2 class="section-label">{E(H['grid_label'])} · {len(ORDER)}</h2>
    <div class="grid" id="toolGrid">
{cards}
    </div>
    <p class="grid-empty" id="gridEmpty">{E(H['grid_empty'])}</p>

    <section class="section">
      <h2>{t['sizes_h']}</h2>
      <p class="note" style="margin:-8px 0 16px">{t['sizes_lead']}</p>
      {size_links(lang)}
    </section>

    {ad(lang)}

    <section class="section" id="why">
      <h2>{E(H['why_h'])}</h2>
      <div class="why">{why}</div>
    </section>

    <section class="section faq" id="faq">
      <h2>{E(H['faq_h'])}</h2>
{faq_block(H['faqs'])}
    </section>

    <section class="section" id="privacy">
      <h2>{E(H['privacy_h'])}</h2>
      <p class="fineprint">{H['privacy']}</p>
    </section>
  </div>
</section>

<section class="view" id="view-tool">
  <div class="wrap">
    <button class="back" id="backBtn" type="button">{BACK_SVG}{UI[lang]['back']}</button>
    <div id="toolMount"></div>
  </div>
</section>
</main>
"""
    page += footer(lang)
    write(f"{pre}index.html", page)
    return url

def render_404():
    t = TXT["en"]
    page = head("en", "Page not found | Fileloka", "This page doesn't exist. Browse Fileloka's free, private PDF and image tools.",
                f"{DOMAIN}/404", [], [], extra='\n<meta name="robots" content="noindex">')
    links = "".join(f'<a class="rel-link" href="/{tid}/">{E(NAMES[tid]["en"])}</a>' for tid in ORDER[:6])
    page += f"""
<body>
{topbar('en', '/id/')}
<main class="wrap">
  <div class="tool-hero" style="padding:72px 0 20px">
    <p class="eyebrow"><b>404</b>{t['tool_404']}</p>
    <h1>We couldn't find that page.</h1>
    <p class="lead">The link might be old or have a typo. The tools are all still here. <a href="/id/" hreflang="id">Versi Bahasa Indonesia</a></p>
  </div>
  <div class="rel-links">{links}<a class="rel-link" href="/">All tools →</a></div>
</main>
"""
    page += footer("en")
    write("404.html", page)

def main():
    urls = []
    for lang in ("en", "id"):
        urls.append(render_home(lang))
        for tid in ORDER:
            urls.append(render_tool(lang, tid))
        for k, b, lab in SIZES:
            urls.append(render_size(lang, k, b, lab))
    render_404()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for u in urls:
        path = u.replace(DOMAIN, "")
        en_path = path[3:] if path.startswith("/id/") else path
        if en_path.startswith("/kompres-pdf-"):
            en_path = "/compress-pdf-to-" + en_path[len("/kompres-pdf-"):]
        id_path = path if path.startswith("/id/") else ("/id" + path if not path.startswith("/compress-pdf-to-") else "/id/kompres-pdf-" + path[len("/compress-pdf-to-"):])
        sm += ["  <url>", f"    <loc>{u}</loc>", f"    <lastmod>{TODAY}</lastmod>",
               f'    <xhtml:link rel="alternate" hreflang="en" href="{DOMAIN}{en_path}"/>',
               f'    <xhtml:link rel="alternate" hreflang="id" href="{DOMAIN}{id_path}"/>',
               f'    <xhtml:link rel="alternate" hreflang="x-default" href="{DOMAIN}{en_path}"/>',
               "  </url>"]
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm) + "\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    print(f"built {len(urls)} indexable pages + 404 | css v{V_CSS} js v{V_JS}")

if __name__ == "__main__":
    sys.exit(main())
