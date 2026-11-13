# -*- coding: utf-8 -*-
"""Copy for the four "who is behind this" pages: privacy, about, contact, terms.

Ad networks and affiliate programs check that these exist before they approve
a site, and visitors look for them before they trust one.

The text is built from the live settings in monetize.py, so the privacy page
can never claim something the site no longer does. Style rules are the same as
the rest of the site: plain words, "kamu" in Indonesian, no em dashes.

Paragraph strings are trusted HTML written here (they contain links); nothing
user-supplied ever reaches them.
"""
import monetize as M

UPDATED = {"en": "13 November 2026", "id": "13 November 2026"}
ORDER = ["privacy", "about", "contact", "terms"]
NAV = {
    "en": {"privacy": "Privacy", "about": "About", "contact": "Contact", "terms": "Terms"},
    "id": {"privacy": "Privasi", "about": "Tentang", "contact": "Kontak", "terms": "Ketentuan"},
}
CF_PRIVACY = "https://www.cloudflare.com/privacypolicy/"
GOOGLE_ADS_SETTINGS = "https://adssettings.google.com/"


def _mail(contact):
    return f'<a href="mailto:{contact}">{contact}</a>'


# ------------------------------------------------------------------ English
def _privacy_en(contact):
    s = [
        ("Your files", [
            "Every tool runs in your browser. The file you pick is read into your device's memory, processed there, "
            "and gone when you close the tab. It is never sent to us or to anyone else, so we couldn't look at it, "
            "keep it or hand it over even if someone asked.",
            "You can check this yourself. Open your browser's developer tools, watch the Network tab while a tool "
            "runs, and you'll see no request carrying your file. Or load a page, switch off your internet, and run "
            "the tool anyway.",
        ]),
    ]
    if M.ANALYTICS:
        s.append(("What we count", [
            "To know which tools are worth improving, the site counts a few events: a page was opened, a tool "
            "finished a job, a result was downloaded, a link in the support box was clicked. Each count carries the "
            "page path, the tool name, the page language, your country as reported by our host, and whether the "
            "device is a phone or a computer.",
            "It does not carry your IP address, a cookie, an ID that follows you around, a file name, a file size or "
            "anything from inside a file. Counts go to our own address (fileloka.id/api/e), not to an analytics "
            "company, and they can't be traced back to a person.",
            "If your browser sends a Do Not Track or Global Privacy Control signal, nothing is counted.",
        ]))
    else:
        s.append(("Analytics", ["There are none. The site doesn't count visits or tool runs."]))
    s.append(("Cookies and storage", [
        "Fileloka sets no cookies and saves nothing in your browser. That's also why the dark mode switch goes back "
        "to your system setting when you reload.",
    ]))
    s.append(("Hosting", [
        f'The site is served by Cloudflare. Like any web host, Cloudflare handles technical request data such as IP '
        f'addresses in order to deliver pages and block abuse. That handling falls under '
        f'<a href="{CF_PRIVACY}" rel="noopener">Cloudflare\'s privacy policy</a>.',
    ]))
    ads = ["There are no third-party ads on Fileloka today."]
    if M.has_support() or M.has_offers():
        ads.append("Some pages have one box that asks for voluntary support or, where it is labelled Sponsored, "
                   "points to a product we may earn a commission from. These are ordinary links. They load nothing "
                   "from another company until you click, and once you click you're on that company's site, under "
                   "its privacy policy.")
    if M.ADSENSE_CLIENT:
        ads.append(f'Fileloka is registered with Google AdSense, but no ad code runs on the site yet. If ads are '
                   f'switched on, Google and its partners may use cookies to show ads based on your visits to this '
                   f'and other sites, you\'ll be asked for consent where the law requires it, and you can turn off '
                   f'personalised ads in <a href="{GOOGLE_ADS_SETTINGS}" rel="noopener">Google\'s Ads Settings</a>. '
                   f'This page will say so before that happens.')
    s.append(("Ads and sponsors", ads))
    s.append(("Changes and questions", [
        f"If this page changes, the date below changes with it. Questions go to {_mail(contact)}.",
    ]))
    return dict(
        title="Privacy: What Fileloka Does and Doesn't Collect | Fileloka",
        meta="Your files are processed in your browser and never uploaded. No cookies, no accounts. "
             "Here is exactly what the site counts and what it doesn't.",
        h1="Privacy, in plain words",
        lead="Short version: your files never leave your device, and we don't know who you are.",
        sections=s)


def _about_en(contact):
    return dict(
        title="About Fileloka: File Tools That Run on Your Device | Fileloka",
        meta="Fileloka is a small set of free PDF and image tools that process files in your browser instead of "
             "on a server. Who runs it, why it exists and how it stays free.",
        h1="About Fileloka",
        lead="A small set of file tools built on one rule: the file stays on your device.",
        sections=[
            ("Why it exists", [
                "Most free PDF and image sites work the same way. You upload the file, their server processes it, "
                "and you trust them to delete it afterwards. That's a lot of trust to hand over for a payslip, an "
                "ID scan or a signed contract.",
                "Fileloka does the same jobs inside your browser. Nothing is uploaded, so the question of what "
                "happens to your file on someone's server never comes up.",
            ]),
            ("Who runs it", [
                f"Fileloka is built and maintained by {M.E(M.OWNER)}, an independent developer in Indonesia. "
                f"There is no company or investor behind it.",
            ]),
            ("How it stays free", [
                "Your device does the processing, so running the site costs little. Every tool works in full "
                "without an account, a watermark or a daily limit, and the tools that are free today stay free.",
            ]),
            ("Open source", [
                f'The code is public on <a href="{M.REPO}" rel="noopener">GitHub</a> under the MIT licence, so '
                f'anyone can check that it does what this page says.',
                "It stands on other people's open-source work: pdf-lib, PDF.js, JSZip, qrcodejs and libheif-js. "
                "Each one is bundled with the site at a fixed version and keeps its own licence.",
            ]),
            ("Get in touch", [
                f'Found a bug, or wish a tool existed? <a href="/contact/">The contact page</a> has the details.',
            ]),
        ])


def _contact_en(contact):
    return dict(
        title="Contact Fileloka | Fileloka",
        meta="How to reach Fileloka: email for questions, GitHub for bugs and feature requests, and where to "
             "send a security report.",
        h1="Contact",
        lead="One person runs this site and reads what you send.",
        sections=[
            ("Email", [
                f"For questions, a bug you ran into, or a tool you wish existed: {_mail(contact)}.",
            ]),
            ("Bugs and feature requests", [
                f'If you use GitHub, <a href="{M.REPO}/issues" rel="noopener">open an issue</a>. It helps to say '
                f'which tool, which browser, and what you expected to happen.',
            ]),
            ("Security reports", [
                f'Found a security problem? Please email before you publish it. The details are in '
                f'<a href="/.well-known/security.txt">security.txt</a>.',
            ]),
            ("Please don't send your files", [
                "We can't see what you process here, and we'd like to keep it that way. A description of the "
                "problem is nearly always enough.",
            ]),
        ])


def _terms_en(contact):
    return dict(
        title="Terms of Use | Fileloka",
        meta="Fileloka is free for personal and commercial use. The short list of conditions that come with it.",
        h1="Terms of use",
        lead="Fileloka is free to use. These are the few conditions that come with it.",
        sections=[
            ("Using the tools", [
                "You can use every tool for personal or commercial work, free of charge and without an account.",
            ]),
            ("Your files stay yours", [
                "Files are processed on your device and never sent to us. You're responsible for having the right "
                "to use the files you process, and for what you do with the results.",
            ]),
            ("Check the result", [
                "These tools change files. Compression lowers image quality, splitting removes pages, converting "
                "changes the format. Keep your original, and look at the output before you submit it somewhere "
                "that matters.",
            ]),
            ("No warranty", [
                "The site is provided as it is, with no warranty of any kind. As far as the law allows, we aren't "
                "liable for loss or damage that comes from using it, including a rejected upload or a missed "
                "deadline.",
            ]),
            ("Fair use", [
                "Don't use the site to break the law, and don't try to disrupt it or the people using it.",
            ]),
            ("Support and sponsored links", [
                "A box on some pages may link to a way to support the site or to another company's product. "
                "Sponsored links are labelled. Anything you buy from another company is between you and them.",
            ]),
            ("The code", [
                f'Fileloka\'s source code is available under the MIT licence on '
                f'<a href="{M.REPO}" rel="noopener">GitHub</a>.',
            ]),
            ("Changes", [
                f"These terms may change as the site does. The date below shows the current version. "
                f"Questions go to {_mail(contact)}.",
            ]),
        ])


# --------------------------------------------------------------- Indonesian
def _privacy_id(contact):
    s = [
        ("Soal filemu", [
            "Semua alat jalan di browser. File yang kamu pilih dibaca ke memori perangkatmu, diproses di situ, lalu "
            "hilang begitu tab ditutup. File itu tidak pernah dikirim ke kami atau ke siapa pun, jadi kami tidak "
            "bisa melihat, menyimpan, atau menyerahkannya walaupun diminta.",
            "Kamu bisa cek sendiri. Buka DevTools di browser, lihat tab Network waktu alatnya bekerja: tidak ada "
            "permintaan yang membawa filemu. Bisa juga buka halamannya, matikan internet, lalu jalankan alatnya.",
        ]),
    ]
    if M.ANALYTICS:
        s.append(("Yang kami hitung", [
            "Supaya tahu alat mana yang layak diperbaiki, situs ini menghitung beberapa kejadian: halaman dibuka, "
            "alat selesai memproses, hasil diunduh, tautan di kotak dukungan diklik. Tiap hitungan berisi alamat "
            "halaman, nama alat, bahasa halaman, negaramu menurut penyedia hosting kami, dan jenis perangkat (HP "
            "atau komputer).",
            "Yang tidak ikut: alamat IP, cookie, ID yang mengikutimu, nama file, ukuran file, dan isi file. "
            "Hitungannya dikirim ke alamat kami sendiri (fileloka.id/api/e), bukan ke perusahaan analytics, dan "
            "tidak bisa dihubungkan ke orang tertentu.",
            "Kalau browser-mu mengirim sinyal Do Not Track atau Global Privacy Control, tidak ada yang dihitung.",
        ]))
    else:
        s.append(("Analytics", ["Tidak ada. Situs ini tidak menghitung kunjungan atau pemakaian alat."]))
    s.append(("Cookie dan penyimpanan", [
        "Fileloka tidak memasang cookie dan tidak menyimpan apa pun di browser-mu. Itu juga sebabnya mode gelap "
        "kembali mengikuti setelan perangkat setiap halaman dimuat ulang.",
    ]))
    s.append(("Hosting", [
        f'Situs ini dilayani oleh Cloudflare. Seperti penyedia hosting lain, Cloudflare memproses data teknis '
        f'seperti alamat IP untuk mengirim halaman dan menahan penyalahgunaan. Pengolahan itu mengikuti '
        f'<a href="{CF_PRIVACY}" rel="noopener">kebijakan privasi Cloudflare</a>.',
    ]))
    ads = ["Saat ini tidak ada iklan pihak ketiga di Fileloka."]
    if M.has_support() or M.has_offers():
        ads.append("Di beberapa halaman ada satu kotak yang mengajak ikut mendukung situs ini atau, kalau berlabel "
                   "Sponsor, mengarah ke produk yang bisa memberi kami komisi. Isinya tautan biasa. Tidak ada yang "
                   "dimuat dari perusahaan lain sebelum kamu klik, dan setelah klik kamu berada di situs mereka "
                   "dengan kebijakan privasi mereka.")
    if M.ADSENSE_CLIENT:
        ads.append(f'Fileloka terdaftar di Google AdSense, tapi belum ada kode iklan yang berjalan di situs ini. '
                   f'Kalau iklan diaktifkan, Google dan mitranya bisa memakai cookie untuk menampilkan iklan '
                   f'berdasarkan kunjunganmu ke situs ini dan situs lain, kamu akan dimintai persetujuan kalau '
                   f'hukum mewajibkannya, dan iklan yang dipersonalisasi bisa dimatikan di '
                   f'<a href="{GOOGLE_ADS_SETTINGS}" rel="noopener">Setelan Iklan Google</a>. Halaman ini akan '
                   f'diperbarui sebelum itu terjadi.')
    s.append(("Iklan dan sponsor", ads))
    s.append(("Perubahan dan pertanyaan", [
        f"Kalau halaman ini berubah, tanggal di bawah ikut berubah. Ada pertanyaan? Kirim ke {_mail(contact)}.",
    ]))
    return dict(
        title="Privasi: Apa yang Dikumpulkan Fileloka dan Apa yang Tidak | Fileloka",
        meta="File diproses di browser dan tidak pernah di-upload. Tanpa cookie dan tanpa akun. "
             "Ini persisnya yang dihitung situs ini dan yang tidak.",
        h1="Soal privasi, apa adanya",
        lead="Singkatnya: filemu tidak pernah keluar dari perangkat, dan kami tidak tahu kamu siapa.",
        sections=s)


def _about_id(contact):
    return dict(
        title="Tentang Fileloka: Alat File yang Jalan di Perangkatmu | Fileloka",
        meta="Fileloka adalah kumpulan alat PDF dan foto gratis yang memproses file di browser, bukan di server. "
             "Siapa yang mengelola, kenapa dibuat, dan kenapa bisa gratis.",
        h1="Tentang Fileloka",
        lead="Kumpulan alat file dengan satu aturan: filenya tetap di perangkatmu.",
        sections=[
            ("Kenapa dibuat", [
                "Kebanyakan situs PDF dan foto gratis cara kerjanya sama. Kamu upload file, server mereka yang "
                "memproses, lalu kamu percaya saja filenya dihapus. Untuk slip gaji, scan KTP, atau kontrak yang "
                "sudah ditandatangani, itu kepercayaan yang besar.",
                "Fileloka mengerjakan hal yang sama di dalam browser-mu. Tidak ada yang di-upload, jadi urusan "
                "nasib file di server orang lain tidak pernah muncul.",
            ]),
            ("Siapa yang mengelola", [
                f"Fileloka dibuat dan dirawat oleh {M.E(M.OWNER)}, developer independen di Indonesia. "
                f"Tidak ada perusahaan atau investor di belakangnya.",
            ]),
            ("Kenapa bisa gratis", [
                "Yang memproses file itu perangkatmu, jadi biaya menjalankan situs ini kecil. Semua alat bisa "
                "dipakai penuh tanpa akun, watermark, atau batas harian, dan alat yang sekarang gratis akan "
                "tetap gratis.",
            ]),
            ("Kode terbuka", [
                f'Kodenya terbuka di <a href="{M.REPO}" rel="noopener">GitHub</a> dengan lisensi MIT, jadi siapa '
                f'pun bisa memeriksa bahwa situs ini memang bekerja seperti yang ditulis di sini.',
                "Fileloka berdiri di atas karya open source orang lain: pdf-lib, PDF.js, JSZip, qrcodejs, dan "
                "libheif-js. Semuanya disertakan langsung di situs ini dengan versi tetap dan lisensinya "
                "masing-masing.",
            ]),
            ("Hubungi kami", [
                'Ketemu bug, atau ada alat yang kamu harap tersedia? Caranya ada di '
                '<a href="/id/contact/">halaman kontak</a>.',
            ]),
        ])


def _contact_id(contact):
    return dict(
        title="Kontak Fileloka | Fileloka",
        meta="Cara menghubungi Fileloka: email untuk pertanyaan, GitHub untuk bug dan usulan fitur, serta alamat "
             "laporan keamanan.",
        h1="Kontak",
        lead="Situs ini dikelola satu orang, dan pesanmu dibaca.",
        sections=[
            ("Email", [
                f"Untuk pertanyaan, bug yang kamu temui, atau alat yang kamu harap tersedia: {_mail(contact)}.",
            ]),
            ("Bug dan usulan fitur", [
                f'Kalau kamu pakai GitHub, <a href="{M.REPO}/issues" rel="noopener">buat issue</a>. Sebutkan '
                f'alatnya, browser yang dipakai, dan hasil yang kamu harapkan.',
            ]),
            ("Laporan keamanan", [
                'Menemukan celah keamanan? Tolong kirim email dulu sebelum dipublikasikan. Detailnya ada di '
                '<a href="/.well-known/security.txt">security.txt</a>.',
            ]),
            ("Jangan kirim filemu", [
                "Kami tidak bisa melihat apa yang kamu proses di sini, dan sebaiknya tetap begitu. Cerita soal "
                "masalahnya hampir selalu sudah cukup.",
            ]),
        ])


def _terms_id(contact):
    return dict(
        title="Ketentuan Pemakaian | Fileloka",
        meta="Fileloka gratis untuk keperluan pribadi maupun usaha. Ini beberapa ketentuan yang menyertainya.",
        h1="Ketentuan pemakaian",
        lead="Fileloka gratis dipakai. Ini beberapa ketentuan yang menyertainya.",
        sections=[
            ("Memakai alatnya", [
                "Semua alat boleh dipakai untuk keperluan pribadi maupun usaha, gratis dan tanpa akun.",
            ]),
            ("Filemu tetap milikmu", [
                "File diproses di perangkatmu dan tidak pernah dikirim ke kami. Kamu yang bertanggung jawab bahwa "
                "kamu berhak memakai file yang diproses, dan atas pemakaian hasilnya.",
            ]),
            ("Periksa hasilnya", [
                "Alat-alat ini mengubah file. Kompres menurunkan kualitas gambar, pisah membuang halaman, konversi "
                "mengganti format. Simpan file aslinya, dan lihat dulu hasilnya sebelum dikirim ke tempat yang "
                "penting.",
            ]),
            ("Tanpa jaminan", [
                "Situs ini disediakan apa adanya, tanpa jaminan dalam bentuk apa pun. Sejauh diizinkan hukum, kami "
                "tidak bertanggung jawab atas kerugian akibat pemakaiannya, termasuk berkas yang ditolak atau "
                "tenggat yang terlewat.",
            ]),
            ("Pemakaian wajar", [
                "Jangan pakai situs ini untuk melanggar hukum, dan jangan mengganggu situs ini atau orang lain "
                "yang memakainya.",
            ]),
            ("Dukungan dan tautan sponsor", [
                "Kotak di beberapa halaman bisa mengarah ke cara mendukung situs ini atau ke produk perusahaan "
                "lain. Tautan sponsor selalu diberi label. Apa pun yang kamu beli dari perusahaan lain adalah "
                "urusanmu dengan mereka.",
            ]),
            ("Kodenya", [
                f'Kode sumber Fileloka tersedia dengan lisensi MIT di '
                f'<a href="{M.REPO}" rel="noopener">GitHub</a>.',
            ]),
            ("Perubahan", [
                f"Ketentuan ini bisa berubah mengikuti situsnya. Tanggal di bawah menunjukkan versi yang berlaku. "
                f"Ada pertanyaan? Kirim ke {_mail(contact)}.",
            ]),
        ])


_BUILD = {
    "en": {"privacy": _privacy_en, "about": _about_en, "contact": _contact_en, "terms": _terms_en},
    "id": {"privacy": _privacy_id, "about": _about_id, "contact": _contact_id, "terms": _terms_id},
}
UPDATED_LABEL = {"en": "Last updated", "id": "Terakhir diperbarui"}


def page(lang, slug, contact):
    return _BUILD[lang][slug](contact)
