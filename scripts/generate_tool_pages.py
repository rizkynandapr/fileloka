#!/usr/bin/env python3
"""Generate static per-tool landing pages for Fileloka.

Each tool gets a real URL (/merge-pdf/, /split-pdf/, ...) with unique
title, description, intro, steps, FAQ and JSON-LD - the pages Google can
rank individually. Shared chrome (topbar/footer/ad-slot) is extracted from
index.html at build time so design stays in sync.

Run from the repo root:  python scripts/generate_tool_pages.py
Commit the generated folders. Deploy stays a plain static upload.
"""
import re, json, os, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content_id import P_ID, NAMES, CARD_DESC_ID, UI, HOME_ID

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://fileloka.id"   # <- replaced once the real domain exists

P = {
 "merge-pdf": dict(
   title="Merge PDF Files Online Free — No Upload | Fileloka",
   h1="Merge PDF files into one document",
   lead="Combine two or more PDFs into a single file, in exactly the order you choose. Unlike other merge tools, your documents are never uploaded — everything happens inside your browser, so contracts, invoices and reports stay on your device.",
   meta="Combine multiple PDF files into one, free and without uploading. Reorder pages, merge locally in your browser — files never leave your device.",
   steps=["Choose or drop two or more PDF files — anywhere on the page works.",
          "Drag the arrows to put them in the right order; page counts are shown for each file.",
          "Click Merge and download one combined PDF instantly."],
   faqs=[("Is there a limit to how many PDFs I can merge?",
          "No fixed limit. The practical ceiling is your device's memory — merging dozens of normal documents is fine on any modern phone or laptop."),
         ("Will the quality of my PDFs change?",
          "No. Pages are copied into the new file exactly as they are — text stays selectable, images keep their original resolution, and links keep working."),
         ("Can I merge password-protected PDFs?",
          "Not yet. Encrypted files are detected and clearly marked in the list so they're skipped rather than half-processed. Remove the password first, then merge."),
         ("Why is this safer than other merge tools?",
          "Most merge sites upload your files to a server, process them there, and promise to delete them later. Here there is no server step at all — you can watch the Network tab in your browser's dev tools and see that nothing is sent.")],
   related=["split-pdf","compress-pdf","jpg-to-pdf"]),
 "split-pdf": dict(
   title="Split PDF & Extract Pages Online Free — No Upload | Fileloka",
   h1="Split a PDF — extract exactly the pages you need",
   lead="Pull specific pages or page ranges out of a PDF (like 1-3, 7), or save every page as its own file. Processing runs entirely on your device, which makes this one of the few PDF extractors that never sees your document.",
   meta="Extract pages from a PDF or split every page into separate files — free, private, no upload. Enter ranges like 1-3, 7 and download instantly.",
   steps=["Choose or drop the PDF you want to split.",
          "Pick a mode: extract a page range (e.g. 1-3, 7) or save every page as its own PDF.",
          "Download the extracted pages, or a ZIP when there are many files."],
   faqs=[("How do I extract just a few pages from a PDF?",
          "Choose 'Extract pages', type the pages you want — formats like 5, 2-4 or 1-3, 7, 12 all work — and download a new PDF containing only those pages, in order."),
         ("Can I split a PDF into separate files for every page?",
          "Yes. Pick 'Every page as its own PDF' and you'll get a ZIP with one numbered PDF per page — useful for splitting scanned batches or shared handouts."),
         ("Does splitting reduce quality or remove text?",
          "No. Pages are copied, not re-rendered: text remains selectable and searchable, and images keep full resolution."),
         ("Is my document uploaded while splitting?",
          "Never. The file is read into your browser's memory, split there, and discarded when you close the tab. You can even disconnect from the internet after the page loads and the tool keeps working.")],
   related=["merge-pdf","pdf-to-jpg","compress-pdf"]),
 "compress-pdf": dict(
   title="Compress PDF Online Free — Shrink Size, No Upload | Fileloka",
   h1="Compress a PDF to fit email and upload limits",
   lead="Shrink a PDF right in your browser. Balanced mode re-packs the file and keeps text selectable; Strong mode redraws pages as compressed images for the smallest possible size — you see before/after sizes before downloading.",
   meta="Reduce PDF file size for free without uploading. Two modes: keep selectable text, or maximum compression. See the size saving before you download.",
   steps=["Choose or drop the PDF you need to shrink.",
          "Pick Balanced (keeps text) or Strong (smallest file), and tune image quality if you like.",
          "Compare the before/after size and download the compressed PDF."],
   faqs=[("How small will my PDF get?",
          "It depends on what's inside. Scanned or image-heavy PDFs often shrink 50–90% in Strong mode. Already-efficient, text-only PDFs may barely change — the tool tells you honestly instead of inflating numbers."),
         ("What's the difference between Balanced and Strong?",
          "Balanced rewrites the file structure and keeps text selectable and searchable. Strong re-renders each page as a compressed JPEG — much smaller, but text can no longer be selected. Use Balanced for documents you'll edit or search, Strong for archiving and sending."),
         ("Will my PDF still be readable after compression?",
          "Yes — you control the quality slider in Strong mode, and the default keeps documents comfortably readable on screen and in print."),
         ("Is it safe to compress confidential PDFs here?",
          "Yes. Compression happens on your device; the file is never transmitted. That's a structural guarantee, not a policy promise — there is no server that could store or leak it.")],
   related=["merge-pdf","split-pdf","compress-image"]),
 "pdf-to-jpg": dict(
   title="PDF to JPG Converter Online Free — No Upload | Fileloka",
   h1="Convert PDF pages to JPG images",
   lead="Turn every page of a PDF into a high-quality JPG — for slides, sharing on chat apps, or embedding in documents. Choose quality and detail level, preview thumbnails, and download one image or a ZIP of all pages.",
   meta="Convert PDF to JPG images free, without uploading. Choose quality and resolution, preview pages, download single images or a ZIP.",
   steps=["Choose or drop a PDF file.",
          "Set JPG quality and detail (screen, print or maximum).",
          "Convert, preview the thumbnails, and download images individually or as a ZIP."],
   faqs=[("What resolution will the JPG images be?",
          "You choose: Good (screen) renders around 1.5×, Sharp (print) 2×, and Maximum 3× the page's base size. Higher detail means larger files, so pick what the images are for."),
         ("Can I convert just one page to JPG?",
          "Convert the document, then download only the page you need from the results list — each page is a separate numbered image."),
         ("Why do some PDFs take longer to convert?",
          "Each page is genuinely rendered by your own device (the same engine Firefox uses to display PDFs). Long or graphics-heavy documents simply take more work — a progress bar keeps you posted."),
         ("Are my PDF's contents uploaded during conversion?",
          "No. Rendering happens locally via pdf.js in your browser. Nothing is sent anywhere — verifiable in your browser's Network tab.")],
   related=["jpg-to-pdf","compress-image","split-pdf"]),
 "jpg-to-pdf": dict(
   title="JPG to PDF Converter Online Free — Images to PDF, No Upload | Fileloka",
   h1="Turn images into a clean PDF document",
   lead="Pack photos, scans and screenshots (JPG, PNG or WebP) into one tidy PDF. Reorder pages, choose between matching the image size or standard A4, add margins — all without your pictures ever leaving your device.",
   meta="Convert JPG, PNG or WebP images to PDF free, without uploading. Reorder pages, pick A4 or original size, add margins, download instantly.",
   steps=["Choose or drop your images — as many as you like, mixed formats are fine.",
          "Arrange the order and pick a page size: match each image, A4 portrait, or A4 landscape.",
          "Click Make PDF and download the finished document."],
   faqs=[("Can I combine photos from my phone into one PDF?",
          "Yes — that's the main use. Select or drop all the photos, reorder them, and export a single PDF that's easy to email or archive. iPhone HEIC photos aren't supported yet; convert them to JPG first."),
         ("Which page size should I choose?",
          "'Match image' keeps every photo at its natural proportions — best for screenshots. A4 fits each image neatly onto a standard page — best for printing or official submissions."),
         ("Will my images be compressed?",
          "JPG images are embedded as-is with no quality loss. PNG and WebP are embedded losslessly too — the PDF simply wraps them."),
         ("Is this converter really private?",
          "Yes. The PDF is assembled in your browser's memory using pdf-lib. Your photos are never transmitted, stored, or seen by anyone.")],
   related=["pdf-to-jpg","compress-image","merge-pdf"]),
 "compress-image": dict(
   title="Compress Images Online Free — JPG, PNG, WebP, No Upload | Fileloka",
   h1="Compress images without losing what matters",
   lead="Cut photo file sizes hard — for web forms, email attachments and faster websites — while keeping them sharp. Batch-compress JPG, PNG and WebP, optionally cap the width, and see the exact savings per file.",
   meta="Compress JPG, PNG and WebP images for free without uploading. Batch processing, quality control, max-width resize, EXIF removed automatically.",
   steps=["Choose or drop one or many images.",
          "Set quality, output format (JPG, WebP, or keep original) and an optional max width.",
          "Compress and download each file or everything as a ZIP, with before/after sizes shown."],
   faqs=[("How much smaller will my photos get?",
          "Typical phone photos shrink 60–90% at the default quality with no visible difference on screen. The results list shows the exact before/after size for every file."),
         ("What happens to the hidden data in my photos?",
          "Re-encoding to JPG or WebP automatically strips EXIF metadata — GPS location, camera model, timestamps — which is a genuine privacy win when sharing photos publicly."),
         ("Why didn't my PNG get smaller?",
          "PNG is lossless, so the quality slider doesn't apply. Use the max-width option to shrink its dimensions, or convert it to JPG/WebP for dramatic savings."),
         ("Are my photos uploaded for compression?",
          "No — compression runs on your device using your browser's own image engine. Nothing is transmitted, which also makes it fast: there's no upload wait at all.")],
   related=["resize-image","convert-image","jpg-to-pdf"]),
 "resize-image": dict(
   title="Resize Images Online Free — Exact Pixels or Percent, No Upload | Fileloka",
   h1="Resize images to exact pixels or a percentage",
   lead="Scale pictures to precise dimensions for profile photos, marketplaces, forms and documents. Keep proportions automatically or set exact width × height — in batch, privately, on your own device.",
   meta="Resize JPG, PNG and WebP images free without uploading. Exact pixel dimensions or percentage scaling, batch support, proportions kept automatically.",
   steps=["Choose or drop the images you want to resize.",
          "Enter a width and/or height in pixels — or switch to percent mode.",
          "Resize and download; new dimensions are added to each filename."],
   faqs=[("How do I resize without stretching my image?",
          "Leave 'Keep proportions' on. Enter just a width (or height) and the other side is calculated automatically; enter both and the image is fitted inside without distortion."),
         ("Can I make an image larger?",
          "Yes, both pixel and percent modes can upscale. Browsers use high-quality smoothing, but enlarging beyond ~2× will always look soft — that's physics, not the tool."),
         ("Does resizing reduce image quality?",
          "Downscaling keeps images crisp. JPG output is saved at 92% quality — visually indistinguishable for photos. PNG stays lossless."),
         ("Are my pictures uploaded to a server?",
          "No. Resizing uses your browser's canvas engine locally. Your images never leave your device.")],
   related=["compress-image","convert-image","jpg-to-pdf"]),
 "convert-image": dict(
   title="Convert Images Online Free — JPG, PNG, WebP, No Upload | Fileloka",
   h1="Convert images between JPG, PNG and WebP",
   lead="Switch formats in one click: WebP screenshots to JPG for compatibility, JPG to PNG for editing, anything to WebP for smaller web images. Batch conversion, quality control, and zero uploads.",
   meta="Convert images between JPG, PNG and WebP free, without uploading. Batch conversion with quality control — fast, private, in your browser.",
   steps=["Choose or drop the images to convert — mixed input formats are fine.",
          "Pick the target format and, for JPG/WebP, the quality level.",
          "Convert and download the results individually or as a ZIP."],
   faqs=[("Which format should I choose?",
          "JPG for photos and maximum compatibility, PNG for screenshots, logos and anything needing transparency, WebP for the smallest files on the modern web. When unsure, JPG is the safe default."),
         ("What happens to transparency when converting to JPG?",
          "JPG can't store transparency, so transparent areas are placed on a clean white background — stated up front instead of surprising you with black boxes."),
         ("Why can't I select WebP output?",
          "A few browsers (mainly older Safari) can't encode WebP. When that's the case the option is hidden and you'll see a note — JPG and PNG work everywhere."),
         ("Is the conversion done on a server?",
          "No — your browser's own canvas engine re-encodes the image locally. Files are never transmitted, which is also why conversion is instant.")],
   related=["compress-image","resize-image","pdf-to-jpg"]),
 "qr-code": dict(
   title="Free QR Code Generator — PNG Download, No Sign-up | Fileloka",
   h1="Make a QR code for any link or text",
   lead="Type a link, Wi-Fi note or any text and get a crisp, scannable QR code in seconds — sized for screens, print or posters. No account, no watermark, and the code is generated on your device.",
   meta="Generate QR codes free — no sign-up, no watermark. Download as PNG in screen, print or poster sizes. Created locally in your browser.",
   steps=["Type or paste the link or text.",
          "Pick a size: 256 px for screens, 512 px for print, 1024 px for posters.",
          "Generate and download the PNG."],
   faqs=[("Do these QR codes expire?",
          "Never. This generates a plain, static QR code containing exactly your text or URL — there's no shortener or middleman service that could shut down or start charging."),
         ("Can I use the QR codes commercially?",
          "Yes — on packaging, menus, flyers, anywhere. The generated image is yours, with no watermark and no attribution required."),
         ("How much text fits in a QR code?",
          "Comfortably a URL or a few hundred characters. If you paste something too long the tool says so — shorter content also scans faster from further away."),
         ("Is what I type sent to a server?",
          "No. The code is drawn locally in your browser, which matters if you're encoding private links, Wi-Fi details or contact info.")],
   related=["password-generator","word-counter","signature"]),
 "password-generator": dict(
   title="Strong Random Password Generator — Free, On-Device | Fileloka",
   h1="Generate strong random passwords",
   lead="Create genuinely random passwords using your browser's cryptographic engine — with length, character sets and look-alike filtering under your control, and an honest entropy meter instead of vague 'strength' colors.",
   meta="Free strong password generator running entirely on your device. Cryptographically random, adjustable length and characters, entropy shown in bits.",
   steps=["Set the length (16+ recommended) and which character sets to include.",
          "Optionally avoid look-alike characters (l, 1, O, 0) for passwords you'll type by hand.",
          "Copy the password — a new one is generated every time you change anything."],
   faqs=[("Is this generator actually secure?",
          "Yes. It uses crypto.getRandomValues — the same cryptographic randomness source password managers use — with unbiased sampling, and guarantees every selected character set appears. The code is open source, so this is verifiable."),
         ("What do the entropy bits mean?",
          "Entropy measures how hard a password is to brute-force. Roughly: 45 bits is weak, 70 is fair, 100+ is excellent. A 16-character password from all character sets lands around 100 bits — strong for anything."),
         ("Is my password sent or stored anywhere?",
          "No. It's generated in your browser's memory and exists only on your screen and clipboard. Nothing is transmitted or saved — refresh the page and it's gone."),
         ("Should I avoid look-alike characters?",
          "Turn that option on for passwords you'll read and type manually (Wi-Fi, TVs). For passwords stored in a manager, leave it off for a slightly larger character pool.")],
   related=["qr-code","word-counter","signature"]),
 "word-counter": dict(
   title="Word Counter — Words, Characters & Reading Time | Fileloka",
   h1="Count words, characters and reading time",
   lead="Paste or type text and get live counts: words, characters (with and without spaces), sentences, paragraphs, unique words, plus estimated reading and speaking time — handy for essays, ads, and speeches.",
   meta="Free live word counter: words, characters, sentences, paragraphs, unique words, reading and speaking time. Your text never leaves your browser.",
   steps=["Paste or type your text into the box.",
          "Counts update live as you edit — no button to press.",
          "Use reading time (~220 wpm) and speaking time (~130 wpm) to fit limits."],
   faqs=[("How is reading time calculated?",
          "Reading time assumes about 220 words per minute (average adult silent reading); speaking time assumes about 130 wpm, a comfortable presentation pace. Both are estimates to plan against, not stopwatch guarantees."),
         ("Does it work for character-limited platforms?",
          "Yes — the character counts (with and without spaces) update live, so you can trim a bio, ad, or meta description to an exact limit as you type."),
         ("What counts as a sentence or paragraph?",
          "Sentences are split on ., ! and ? endings; paragraphs on blank lines. Text without ending punctuation still counts as one sentence rather than zero."),
         ("Is my text saved or sent anywhere?",
          "No. Counting happens in your browser as you type; nothing is transmitted or stored. Paste confidential drafts freely.")],
   related=["password-generator","qr-code","signature"]),
 "signature": dict(
   title="Draw Your Signature Online Free — Transparent PNG | Fileloka",
   h1="Draw a signature and save it as a PNG",
   lead="Sign with your mouse, finger or stylus and download a clean signature image — transparent PNG for dropping onto documents, or white background for forms. Smooth strokes, undo, ink colors, nothing uploaded.",
   meta="Create a handwritten signature online free — draw with mouse or touch, download as transparent PNG. Runs on your device; nothing is uploaded.",
   steps=["Draw your signature on the pad — mouse, finger or stylus all work.",
          "Adjust pen color and thickness; use Undo to fix a stroke.",
          "Download as PNG — transparent by default, or tick white background."],
   faqs=[("How do I put this signature on a PDF or document?",
          "Download the transparent PNG, then insert it as an image in Word, Google Docs, or your PDF editor and place it on the signature line. The transparent background makes it sit naturally on any page."),
         ("Is a drawn signature legally valid?",
          "In many situations and countries, yes — most e-signature laws accept an image of your signature for everyday documents. For high-stakes contracts, check what the receiving party requires; this tool creates the image, not a certified e-signature."),
         ("Why does my signature look smooth here?",
          "Strokes are rendered with curve smoothing and high-DPI scaling, so the exported PNG is crisp even when drawn with a fingertip on a phone."),
         ("Is my signature uploaded or stored?",
          "No — it exists only in your browser while you draw and in the PNG you download. Close the tab and it's gone, which is exactly what you want for something as personal as a signature.")],
   related=["jpg-to-pdf","merge-pdf","word-counter"]),
}


CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>'
SEARCH_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.8-3.8"/></svg>'
TODAY = "2026-07-26"
LANGS = {"en": dict(prefix="", lang="en", locale="en_US"),
         "id": dict(prefix="id/", lang="id", locale="id_ID")}
CONTENT = {"en": P, "id": P_ID}

def urls_for(tid):
    en = f"{DOMAIN}/" + (tid + "/" if tid else "")
    idu = f"{DOMAIN}/id/" + (tid + "/" if tid else "")
    return en, idu

def hreflang_links(tid):
    en, idu = urls_for(tid)
    return (f'<link rel="alternate" hreflang="en" href="{en}">\n'
            f'<link rel="alternate" hreflang="id" href="{idu}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{en}">')

def lang_link(target, label):
    return f'<a class="lang-link" href="{target}" aria-label="Switch language">{label}</a>'

def topbar_for(base, lang, twin):
    tb = re.sub(r'<a class="lang-link"[^>]*>[^<]*</a>\s*', "", base)
    if lang == "id":
        tb = tb.replace("0 files uploaded — ever", UI["id"]["pill"])
    m = re.search(r'<button[^>]*id="themeBtn"', tb)
    return tb[:m.start()] + lang_link(twin, UI[lang]["lang_link"]) + tb[m.start():]

def footer_for(base, lang):
    if lang == "en":
        return base
    f = base.replace('<a href="/">All tools</a>', '<a href="/id/">Beranda</a>')
    f = f.replace('<a href="/#faq">FAQ</a>', '<a href="/id/#faq">FAQ</a>')
    f = f.replace('<a href="/#privacy">Privacy</a>', '<a href="/id/#privacy">Privasi</a>')
    return f

def render_tool(lang, tid, chrome):
    cfg, d = LANGS[lang], CONTENT[lang][tid]
    url = f"{DOMAIN}/{cfg['prefix']}{tid}/"
    en_url, id_url = urls_for(tid)
    twin = id_url if lang == "en" else en_url
    ui = UI[lang]
    faq_html = "\n".join(
        f"<details>\n  <summary>{html.escape(q)}</summary>\n  <p>{html.escape(a)}</p>\n</details>"
        for q, a in d["faqs"])
    steps_html = "\n".join(f"<li>{html.escape(s)}</li>" for s in d["steps"])
    rel_html = "\n".join(
        f'<a class="rel-link" href="/{cfg["prefix"]}{r}/">{html.escape(NAMES[r][lang])}</a>'
        for r in d["related"])
    ld = {"@context":"https://schema.org","@graph":[
        {"@type":"SoftwareApplication","name":NAMES[tid][lang]+" — Fileloka",
         "url":url,"inLanguage":cfg["lang"],
         "applicationCategory":"UtilitiesApplication","operatingSystem":"Any",
         "description":d["meta"],
         "offers":{"@type":"Offer","price":"0","priceCurrency":"USD"}},
        {"@type":"FAQPage","inLanguage":cfg["lang"],"mainEntity":[
            {"@type":"Question","name":q,
             "acceptedAnswer":{"@type":"Answer","text":a}} for q,a in d["faqs"]]}]}
    page = f"""<!doctype html>
<html lang="{cfg['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(d["title"])}</title>
<meta name="description" content="{html.escape(d["meta"])}">
<link rel="canonical" href="{url}">
{hreflang_links(tid)}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Fileloka">
<meta property="og:locale" content="{cfg['locale']}">
<meta property="og:title" content="{html.escape(d["title"])}">
<meta property="og:description" content="{html.escape(d["meta"])}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
{chrome['theme']}
{chrome['favicon']}
{chrome['fonts']}
<link rel="stylesheet" href="/styles.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body data-tool="{tid}">
{topbar_for(chrome['topbar'], lang, twin)}
<main class="wrap">
  <div class="tool-hero">
    <a class="back" href="{'/' if lang=='en' else '/id/'}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 12H7m5 5-5-5 5-5"/></svg>{ui['back']}</a>
    <h1>{html.escape(d["h1"])}</h1>
    <p class="lead">{html.escape(d["lead"])}</p>
  </div>
  <section class="view is-active" id="view-tool">
    <div id="toolMount"></div>
  </section>
  {chrome['ad']}
  <section class="section">
    <h2>{ui['how']}</h2>
    <ol class="howto">
{steps_html}
    </ol>
  </section>
  <section class="section faq">
    <h2>{ui['faq']}</h2>
{faq_html}
  </section>
  <section class="section">
    <h2>{ui['rel']}</h2>
    <div class="rel-links">
{rel_html}
    </div>
  </section>
</main>
{footer_for(chrome['footer'], lang)}
<div class="toasts" id="toasts" aria-live="polite"></div>
<script src="/app.js" defer></script>
</body>
</html>
"""
    out = os.path.join(ROOT, cfg["prefix"] + tid)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page)

def build_id_home(chrome, cards):
    H = HOME_ID
    proof = "\n".join(f"<li>{CHECK}{html.escape(p)}</li>" for p in H["proof"])
    tabs = "\n".join(
        f'<button class="tab" role="tab" aria-selected="{"true" if i==0 else "false"}" data-cat="{c}">{t}</button>'
        for i,(c,t) in enumerate(H["tabs"]))
    card_html = []
    for tid, c in cards.items():
        c2 = c.replace(f'href="/{tid}/"', f'href="/id/{tid}/"')
        c2 = re.sub(r"<h3>[^<]*</h3>", f"<h3>{html.escape(NAMES[tid]['id'])}</h3>", c2)
        c2 = re.sub(r"</h3><p>[^<]*</p>", f"</h3><p>{html.escape(CARD_DESC_ID[tid])}</p>", c2)
        c2 = c2.replace(">Open tool <", ">Buka alat <")
        card_html.append(c2)
    faq_html = "\n".join(
        f"<details>\n  <summary>{html.escape(q)}</summary>\n  <p>{html.escape(a)}</p>\n</details>"
        for q, a in H["faqs"])
    why = "\n".join(f"<p>{html.escape(p)}</p>" for p in H["why"])
    priv0 = html.escape(H["privacy"][0])
    priv1 = html.escape(H["privacy"][1]).replace(
        "rizkynandapr@gmail.com",
        '<a href="mailto:rizkynandapr@gmail.com">rizkynandapr@gmail.com</a>')
    flinks = " ".join(f'<a href="{u}">{t}</a>' for t, u in H["footer_links"])
    footer = re.sub(r"<nav>.*?</nav>", f"<nav>{flinks}</nav>", chrome["footer"], flags=re.S)
    en_url, id_url = urls_for(None)
    ld = {"@context":"https://schema.org","@type":"WebApplication","name":"Fileloka",
          "url":id_url,"inLanguage":"id","applicationCategory":"UtilitiesApplication",
          "operatingSystem":"Any","description":H["meta"],
          "offers":{"@type":"Offer","price":"0","priceCurrency":"USD"}}
    page = f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(H["title"])}</title>
<meta name="description" content="{html.escape(H["meta"])}">
<link rel="canonical" href="{id_url}">
{hreflang_links(None)}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Fileloka">
<meta property="og:locale" content="id_ID">
<meta property="og:title" content="{html.escape(H["title"])}">
<meta property="og:description" content="{html.escape(H["meta"])}">
<meta property="og:url" content="{id_url}">
<meta name="twitter:card" content="summary">
{chrome['theme']}
{chrome['favicon']}
{chrome['fonts']}
<link rel="stylesheet" href="/styles.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body data-tool="none">
{topbar_for(chrome['topbar'], 'id', '/')}
<main>
<section class="view is-active">
  <div class="wrap">
    <div class="hero">
      <h1 class="rise">{H["h1"]}</h1>
      <p class="lede rise" style="animation-delay:.06s">{H["lede"]}</p>
      <ul class="proof rise" style="animation-delay:.12s">
{proof}
      </ul>
    </div>
    <div class="finder">
      <div class="search">
        {SEARCH_SVG}
        <input type="search" id="searchInput" placeholder="{html.escape(H["search_ph"])}" aria-label="Cari alat">
        <kbd>/</kbd>
      </div>
      <div>
        <div class="tabs" role="tablist" aria-label="Kategori alat">
{tabs}
        </div>
        <div class="tabs-rule"></div>
      </div>
    </div>
    <div class="grid" id="toolGrid">
{"".join(card_html)}
    </div>
    <p class="grid-empty" id="gridEmpty">{html.escape(H["grid_empty"])}</p>
  </div>
</section>
<div class="wrap">
  {chrome['ad']}
  <section class="section">
    <h2>{html.escape(H["why_h"])}</h2>
{why}
  </section>
  <section class="section faq" id="faq">
    <h2>{html.escape(H["faq_h"])}</h2>
{faq_html}
  </section>
  <section class="section" id="privacy">
    <h2>{html.escape(H["privacy_h"])}</h2>
    <p>{priv0}</p>
    <p>{priv1}</p>
  </section>
</div>
</main>
{footer}
<div class="toasts" id="toasts" aria-live="polite"></div>
<script src="/app.js" defer></script>
</body>
</html>
"""
    os.makedirs(os.path.join(ROOT, "id"), exist_ok=True)
    open(os.path.join(ROOT, "id", "index.html"), "w", encoding="utf-8").write(page)

def patch_root_index():
    p = os.path.join(ROOT, "index.html")
    s = open(p, encoding="utf-8").read()
    if 'hreflang' not in s:
        anchor = '<meta property="og:url" content="https://fileloka.id/">'
        s = s.replace(anchor, anchor + "\n" + hreflang_links(None), 1)
    if 'lang-link' not in s:
        m = re.search(r'<button[^>]*id="themeBtn"', s)
        s = s[:m.start()] + lang_link("/id/", "ID") + s[m.start():]
    open(p, "w", encoding="utf-8").write(s)

def patch_css():
    p = os.path.join(ROOT, "styles.css")
    s = open(p, encoding="utf-8").read()
    if ".lang-link" not in s:
        s += ("\n.lang-link{display:inline-flex;align-items:center;padding:6px 11px;margin-right:10px;"
              "border:1.5px solid var(--line);border-radius:999px;font-weight:700;font-size:.72rem;"
              "letter-spacing:.06em;color:var(--muted);text-decoration:none}\n"
              ".lang-link:hover{color:var(--accent);border-color:var(--accent)}\n")
        open(p, "w", encoding="utf-8").write(s)

def main():
    idx = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    topbar = re.search(r'<header class="topbar">.*?</header>', idx, re.S).group(0)
    topbar = topbar.replace('href="#" id="brandHome"', 'href="/"')
    footer = re.search(r"<footer>.*?</footer>", idx, re.S).group(0)
    footer = footer.replace('<a href="#" data-nav="home">Tools</a>', '<a href="/">All tools</a>')
    footer = footer.replace('<a href="#faq">FAQ</a>', '<a href="/#faq">FAQ</a>')
    footer = footer.replace('<a href="#privacy">Privacy</a>', '<a href="/#privacy">Privacy</a>')
    ad = re.search(r'<aside class="ad-slot".*?</aside>', idx, re.S).group(0)
    fonts = "\n".join(re.findall(r'<link rel="preconnect"[^>]*>|<link href="https://fonts[^>]*>', idx))
    favicon = re.search(r'<link rel="icon"[^>]*>', idx).group(0)
    theme_m = re.search(r'<meta name="theme-color"[^>]*>', idx)
    chrome = dict(topbar=topbar, footer=footer, ad=ad, fonts=fonts, favicon=favicon,
                  theme=theme_m.group(0) if theme_m else "")
    cards = {}
    for tid in P:
        m = re.search(r'<a class="card" href="/' + tid + r'/".*?</a>', idx, re.S)
        cards[tid] = m.group(0)
    for lang in ("en", "id"):
        for tid in P:
            render_tool(lang, tid, chrome)
    build_id_home(chrome, cards)
    patch_root_index()
    patch_css()
    urls = [f"{DOMAIN}/", f"{DOMAIN}/id/"]
    urls += [f"{DOMAIN}/{t}/" for t in P] + [f"{DOMAIN}/id/{t}/" for t in P]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm += ["  <url>", f"    <loc>{u}</loc>", f"    <lastmod>{TODAY}</lastmod>", "  </url>"]
    sm.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w").write("\n".join(sm) + "\n")
    open(os.path.join(ROOT, "robots.txt"), "w").write(
        f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    print("built", 2 * len(P), "tool pages +", "/id/ home |", len(urls), "URLs in sitemap")

if __name__ == "__main__":
    sys.exit(main())
