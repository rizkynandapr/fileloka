# -*- coding: utf-8 -*-
"""Everything that earns money on Fileloka is configured in this one file.

Edit the values below, then rebuild:  python3 scripts/generate_tool_pages.py

Nothing here loads code from another company. The slot is plain HTML with
plain links, so the site's CSP (script-src 'self') stays exactly as it is.
See MONETIZATION.md for the order to switch things on.
"""
import html
import re

E = html.escape

# --------------------------------------------------------------- 1. support
# A pay-what-you-want link. Leave both empty and the support box is not drawn.
# "id" falls back to "en" when empty. A local wallet page (Saweria, Trakteer)
# converts better for Indonesian visitors than a USD checkout.
SUPPORT_URL = {
    "en": "",   # e.g. "https://rizkynandapr.gumroad.com/l/support-fileloka"
    "id": "",   # e.g. "https://saweria.co/yourname"
}

# ----------------------------------------------------- 2. sponsored offers
# One offer per tool page, shown instead of the support box on that page.
# Key = tool id ("password-generator", "compress-pdf", ...) or "home".
# Only add programs you have actually joined; the link must be https.
#
# OFFERS = {
#     "password-generator": {
#         "slug": "pwmanager",          # a-z, 0-9, dash. Shows up in the stats as the click target.
#         "url": "https://partner.example/?ref=YOUR_ID",
#         "en": ("Headline", "One or two plain sentences on why it fits this tool.", "Button label"),
#         "id": ("Judul", "Satu atau dua kalimat kenapa cocok dengan alat ini.", "Label tombol"),
#     },
# }
OFFERS = {}

# ------------------------------------------------------- 3. Google AdSense
# Your publisher id ("ca-pub-" + 16 digits). When set, every page gets the
# ownership meta tag and /ads.txt is written, which is all AdSense needs to
# review the site. It does NOT load ad code: serving ads needs a different
# CSP and a consent banner, so that is a separate, deliberate step
# (MONETIZATION.md, step 5).
ADSENSE_CLIENT = ""

# ------------------------------------------------------------- 4. counting
# First-party, cookieless counters (page opened, tool finished, slot clicked)
# sent to /api/e on this same domain. Set to False and no page sends anything;
# the privacy page rewrites itself to match.
ANALYTICS = True

# ------------------------------------------------------------ 5. who runs it
# Shown on /about/. Ad networks and affiliate programs look for a named owner.
OWNER = "Rizky Nanda Praditia"
REPO = "https://github.com/rizkynandapr/fileloka"

# =============================================================== rendering
ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
         'stroke-linejoin="round" aria-hidden="true"><path d="M4 12h13m-5-5 5 5-5 5"/></svg>')

TXT = {
    "en": dict(
        support=("Support", "Keep Fileloka free",
                 "Your device does the processing, so running this site costs little: a domain and some time. "
                 "If a tool here saved you a headache, you can chip in. Pay what you want.",
                 "Chip in"),
        support_meta="Opens in a new tab. Your files stay here.",
        sponsored="Sponsored",
        disclosure="We may earn a commission if you sign up through this link. Opens in a new tab.",
    ),
    "id": dict(
        support=("Dukung", "Bantu Fileloka tetap gratis",
                 "Yang memproses file itu perangkatmu, jadi biaya situs ini kecil: domain dan waktu. "
                 "Kalau alat di sini pernah menolongmu, kamu bisa ikut patungan. Nominalnya bebas.",
                 "Ikut patungan"),
        support_meta="Dibuka di tab baru. Filemu tetap di sini.",
        sponsored="Sponsor",
        disclosure="Kami bisa dapat komisi kalau kamu mendaftar lewat tautan ini. Dibuka di tab baru.",
    ),
}

_SLUG = re.compile(r"^[a-z0-9-]{1,24}$")
_PUB = re.compile(r"^ca-pub-\d{16}$")


def _https(url, what):
    if not url.startswith("https://") or any(c in url for c in '"<> \n\t'):
        raise SystemExit(f"monetize.py: {what} must be a clean https:// link, got {url!r}")
    return url


def validate():
    """Fail the build loudly instead of shipping a broken or unsafe link."""
    for lang, url in SUPPORT_URL.items():
        if url:
            _https(url, f"SUPPORT_URL[{lang}]")
    for key, o in OFFERS.items():
        if not _SLUG.match(o.get("slug", "")):
            raise SystemExit(f"monetize.py: OFFERS[{key}] needs a slug of a-z, 0-9 and dashes")
        _https(o.get("url", ""), f"OFFERS[{key}]['url']")
        for lang in ("en", "id"):
            if len(o.get(lang, ())) != 3:
                raise SystemExit(f"monetize.py: OFFERS[{key}]['{lang}'] must be (headline, text, button)")
    if ADSENSE_CLIENT and not _PUB.match(ADSENSE_CLIENT):
        raise SystemExit("monetize.py: ADSENSE_CLIENT must look like ca-pub-0000000000000000")


def support_url(lang):
    return SUPPORT_URL.get(lang) or SUPPORT_URL.get("en") or ""


def has_support():
    return bool(support_url("en") or support_url("id"))


def has_offers():
    return bool(OFFERS)


def _card(kind, tag, title, text, cta, url, slug, meta, rel):
    return (f'<aside class="slot hud" data-kind="{kind}" aria-label="{E(tag)}">\n'
            f'    <div class="slot-main">\n'
            f'      <p class="slot-tag"><b>{E(tag)}</b></p>\n'
            f'      <p class="slot-title">{E(title)}</p>\n'
            f'      <p class="slot-text">{E(text)}</p>\n'
            f'    </div>\n'
            f'    <div class="slot-side">\n'
            f'      <a class="btn btn-primary" href="{E(url)}" target="_blank" rel="{rel}" data-slot="{slug}">{E(cta)} {ARROW}</a>\n'
            f'      <p class="slot-meta">{E(meta)}</p>\n'
            f'    </div>\n'
            f'  </aside>')


def slot(lang, key):
    """The one money slot on a page: a sponsored offer if this page has one,
    otherwise the support box, otherwise nothing at all (no empty frame)."""
    t = TXT[lang]
    o = OFFERS.get(key)
    if o:
        title, text, cta = o[lang]
        return _card("offer", t["sponsored"], title, text, cta, o["url"], o["slug"],
                     t["disclosure"], "sponsored noopener noreferrer")
    url = support_url(lang)
    if url:
        tag, title, text, cta = t["support"]
        return _card("support", tag, title, text, cta, url, "support", t["support_meta"], "noopener")
    return ""


def head_extra():
    """Extra <head> markup. Only the AdSense ownership tag, and only when configured."""
    if ADSENSE_CLIENT:
        return f'\n<meta name="google-adsense-account" content="{ADSENSE_CLIENT}">'
    return ""


def ads_txt():
    """Contents of /ads.txt, or None when there is no ad network to declare."""
    if not ADSENSE_CLIENT:
        return None
    return f"google.com, {ADSENSE_CLIENT[3:]}, DIRECT, f08c47fec0942fa0\n"
