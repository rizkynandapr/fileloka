# -*- coding: utf-8 -*-
"""Target-size landing pages: "kompres pdf 200kb", "compress pdf to 200kb" ...

Each page pre-selects the Target-size mode of the Compress PDF tool
(body data-target=bytes) and carries its own, size-specific guidance:
a realistic feasibility table computed from a per-page byte budget,
use cases, and FAQs. Sizes are decimal (200 KB = 200,000 bytes) so the
result fits portals that count 1 KB as 1000 *or* 1024 bytes.
"""

SIZES = [
    # key, bytes, label
    ("100kb", 100_000, "100 KB"),
    ("200kb", 200_000, "200 KB"),
    ("300kb", 300_000, "300 KB"),
    ("500kb", 500_000, "500 KB"),
    ("1mb",   1_000_000, "1 MB"),
    ("2mb",   2_000_000, "2 MB"),
]

def slug(lang, key):
    return ("id/kompres-pdf-" + key) if lang == "id" else ("compress-pdf-to-" + key)

# ---- feasibility heuristics (bytes per page) ------------------------------
# Measured ballparks for A4 pages rendered by the Target engine:
#   colour phone scan, readable ............ ~60–120 KB/page
#   black & white scan, readable ........... ~25–50 KB/page
#   minimum still legible (B&W, low detail)  ~14–20 KB/page
#   text PDF exported from Word ............ fonts ~40–120 KB once + ~3–10 KB/page
def scan_verdict(budget, lang):
    if budget >= 110_000:
        return ("Mudah, tetap berwarna dan tajam" if lang == "id" else "Easy, stays sharp and in colour")
    if budget >= 55_000:
        return ("Bisa, kualitasnya masih bagus" if lang == "id" else "Fine, still good quality")
    if budget >= 28_000:
        return ("Bisa, centang opsi hitam putih" if lang == "id" else "Doable with black & white ticked")
    if budget >= 15_000:
        return ("Mepet. Hitam putih, detail berkurang" if lang == "id" else "Tight. Black & white, less detail")
    return ("Susah. Lebih baik pisah jadi beberapa file" if lang == "id" else "Hard. Better to split it into several files")

def text_verdict(size, lang):
    if size >= 300_000:
        return ("Biasanya sudah muat, teks tetap utuh" if lang == "id" else "Usually fits already, text intact")
    if size >= 150_000:
        return ("Umumnya muat. Kalau tidak, halaman dijadikan gambar" if lang == "id" else "Usually fits. If not, pages become images")
    return ("Tergantung font. Sering harus dijadikan gambar" if lang == "id" else "Depends on the fonts. Often needs image pages")

def feasibility_rows(size, lang):
    L = (lambda i, e: i) if lang == "id" else (lambda i, e: e)
    rows = []
    for pages, label in [(1, L("Scan 1 halaman (foto HP)", "1-page scan (phone photo)")),
                         (3, L("Scan 3 halaman", "3-page scan")),
                         (10, L("Scan 10 halaman", "10-page scan"))]:
        budget = (size - 1600) / pages - 700
        rows.append((label, scan_verdict(budget, lang)))
    rows.append((L("PDF teks 10 halaman (dari Word)", "10-page text PDF (from Word)"), text_verdict(size, lang)))
    return rows

# ---- per-size copy ---------------------------------------------------------
USE_ID = {
 "100kb": "Batas 100 KB biasanya muncul di formulir yang cuma minta satu dokumen pendek, misalnya scan KTP, kartu keluarga, atau surat pernyataan satu halaman. Targetnya ketat. Satu halaman scan masih santai, tapi dokumen beberapa halaman hampir pasti butuh opsi hitam putih.",
 "200kb": "200 KB termasuk batas yang paling sering dipakai portal pendaftaran untuk scan satu atau dua halaman: ijazah, transkrip, SKCK, surat keterangan. Satu-dua halaman hasil foto HP biasanya masih bisa masuk dan warnanya tetap jelas.",
 "300kb": "300 KB memberi sedikit ruang lebih untuk dokumen dua atau tiga halaman, seperti transkrip bolak-balik atau sertifikat plus lampirannya, tanpa harus menurunkan kualitas terlalu jauh.",
 "500kb": "Portal lamaran kerja, beasiswa, dan seleksi sering membatasi berkas di 500 KB. Scan tiga sampai lima halaman umumnya masih masuk dengan kualitas bagus, dan PDF dari Word biasanya bahkan tidak perlu diubah jadi gambar.",
 "1mb":   "1 MB adalah batas yang umum di portal lamaran kerja, e-learning, dan aplikasi instansi. Untuk kebanyakan dokumen, mode yang menjaga teks sudah cukup, jadi teks, link, dan tanda tangan digitalnya tetap utuh.",
 "2mb":   "2 MB tergolong longgar. Cukup untuk lampiran email kantor, laporan penuh grafik, atau portofolio berisi foto. Hampir semua PDF bisa masuk tanpa teksnya berubah jadi gambar, karena yang dikecilkan cuma foto di dalamnya.",
}
USE_EN = {
 "100kb": "A 100 KB limit usually shows up on forms that want one short document: an ID scan, a one page declaration, a proof of address. It's strict. One scanned page is comfortable, but anything with several pages will almost certainly need the black & white option.",
 "200kb": "200 KB is one of the most common limits on application portals for a one or two page scan, like a diploma, a transcript or a reference letter. A couple of pages photographed with a phone usually fit and stay in clear colour.",
 "300kb": "300 KB leaves a bit more room for two or three pages, say a double sided transcript or a certificate with its attachment, without pushing the quality down too far.",
 "500kb": "Job, scholarship and visa portals often cap uploads at 500 KB. Three to five scanned pages usually fit at good quality, and a PDF exported from Word often doesn't need to become images at all.",
 "1mb":   "1 MB is a common cap on job portals, learning platforms and government forms. For most documents the text preserving mode is enough, so text, links and digital signatures stay as they are.",
 "2mb":   "2 MB is roomy. It covers office email attachments, reports full of charts and portfolios with photos. Nearly any PDF fits without its text turning into images, because only the photos inside get smaller.",
}

def faq_id(key, label):
    base = [
     (f"Bagaimana cara kompres PDF jadi {label} di HP?",
      f"Buka halaman ini di Chrome atau Safari, ketuk area pilih file, lalu ambil PDF dari penyimpanan atau folder WhatsApp. Target {label} sudah terpilih, jadi tinggal ketuk Kompres dan unduh hasilnya. Tidak perlu install aplikasi."),
     (f"Kenapa hasilnya sedikit di bawah {label}, bukan pas {label}?",
      f"Memang sengaja. Ada portal yang menghitung 1 KB = 1000 byte, ada juga yang 1024 byte. Fileloka mengincar di bawah {label} versi 1000 byte, jadi filenya lolos di dua-duanya. Kualitas yang dipakai tetap yang paling tinggi yang masih muat."),
     ("Teks di PDF masih bisa diseleksi?",
      "Selama memungkinkan, ya. Fileloka mencoba mengecilkan foto dan scan di dalam PDF dulu, dan teksnya dibiarkan. Halaman baru diubah jadi gambar kalau cara itu belum cukup, dan hasilnya akan memberi tahu kamu mana yang terjadi."),
     ("Aman untuk KTP, ijazah, atau dokumen pribadi?",
      "Aman, karena filenya tidak di-upload. Kompresinya dikerjakan browser di perangkatmu sendiri dan tidak ada server yang menerima dokumenmu. Coba saja: setelah halaman terbuka, nyalakan mode pesawat. Alatnya tetap jalan."),
    ]
    extra = {
     "100kb": ("PDF saya 5 halaman, bisa sampai 100 KB?",
               "Bisa dicoba dengan mencentang Hitam putih. Jatahnya sekitar 18 KB per halaman, cukup untuk teks yang masih terbaca, tapi detail kecil akan berkurang. Kalau hasilnya kurang jelas, lebih baik pisah PDF-nya lalu kirim per bagian."),
     "200kb": ("Scan ijazah saya berwarna. Masih berwarna kalau jadi 200 KB?",
               "Untuk satu atau dua halaman, biasanya masih. Warna baru perlu dikorbankan kalau halamannya banyak. Kalau itu terjadi, hasilnya akan bertanda Paling mendekati dan kamu bisa coba opsi hitam putih."),
     "300kb": ("Lebih baik pilih 200 KB atau 300 KB?",
               "Pilih sesuai batas yang diminta portal. Makin longgar batasnya, makin bagus kualitas yang bisa dipertahankan. Jadi kalau boleh 300 KB, tidak usah ditekan sampai 200 KB."),
     "500kb": ("CV dan lampiran sebaiknya digabung dulu atau dikompres dulu?",
               "Gabung dulu pakai alat Gabung PDF, baru kompres ke 500 KB. Mengompres file yang sudah digabung hasilnya lebih kecil dan kualitasnya lebih rata dibanding mengompres satu per satu."),
     "1mb":   ("PDF saya cuma 1,3 MB. Kenapa halamannya tidak diubah jadi gambar?",
               "Karena tidak perlu. Selisihnya kecil, jadi mengecilkan foto di dalamnya sudah cukup, dan teks, link, serta kualitas cetaknya tetap terjaga. Halaman baru diubah jadi gambar kalau memang tidak ada cara lain."),
     "2mb":   ("Laporan saya 15 MB. Bisa jadi 2 MB?",
               "Biasanya bisa, apalagi kalau ukurannya besar karena foto. File sebesar itu butuh beberapa detik sampai semenit di HP. Di laptop lebih cepat."),
    }[key]
    return base[:2] + [extra] + base[2:]

def faq_en(key, label):
    base = [
     (f"How do I compress a PDF to {label} on my phone?",
      f"Open this page in Chrome or Safari, tap the file area and pick the PDF from your files. The {label} target is already selected, so just tap Compress and download the result. There's no app to install."),
     (f"Why is the result a little under {label} instead of exactly {label}?",
      f"That's on purpose. Some portals count 1 KB as 1000 bytes and others as 1024. Fileloka aims under the 1000 byte version of {label}, so the file passes either way, at the highest quality that still fits."),
     ("Will the text in my PDF stay selectable?",
      "When it can, yes. Fileloka first shrinks only the photos and scans inside the PDF and leaves the text alone. Pages are turned into images only if that isn't enough, and the result tells you which one happened."),
     ("Is it safe for passports, IDs and contracts?",
      "Yes, because the file isn't uploaded. Your own browser does the compressing and no server ever receives the document. Try it: load the page, turn on airplane mode, and the tool still works."),
    ]
    extra = {
     "100kb": ("My PDF has 5 pages. Can it get to 100 KB?",
               "Try it with Black & white ticked. That works out to about 18 KB a page, which is enough for readable text, though small details get softer. If it isn't clear enough, split the PDF and send it in parts."),
     "200kb": ("Will my colour scan still be in colour at 200 KB?",
               "For one or two pages, usually yes. Colour only has to go when there are a lot of pages. If that happens, the result is marked Closest possible and you can try black & white."),
     "300kb": ("Should I pick 200 KB or 300 KB?",
               "Pick whatever the portal asks for. A looser limit means more quality is kept, so if 300 KB is allowed there's no reason to squeeze down to 200 KB."),
     "500kb": ("Should I merge my CV and attachments first, or compress first?",
               "Merge first with Merge PDF, then compress to 500 KB. Compressing the combined file gives a smaller result and more even quality than compressing each part on its own."),
     "1mb":   ("My PDF is only 1.3 MB. Why weren't the pages turned into images?",
               "Because it wasn't needed. With a small gap, shrinking the photos inside is enough, and the text, links and print quality stay intact. Pages only become images when there's no other way."),
     "2mb":   ("Can a 15 MB report get down to 2 MB?",
               "Usually, especially when the size comes from photos. A file that big takes anywhere from a few seconds to a minute on a phone. Laptops are quicker."),
    }[key]
    return base[:2] + [extra] + base[2:]

def page(lang, key, nbytes, label):
    if lang == "id":
        return dict(
            title=f"Kompres PDF {label} Online Gratis, Otomatis | Fileloka",
            meta=f"Kompres PDF jadi di bawah {label} secara otomatis. Pilih targetnya, Fileloka carikan kualitas terbaik yang masih muat. Gratis, tanpa daftar, dan filenya tidak di-upload.",
            h1=f"Kompres PDF ke {label}",
            lead=f"Pilih file, lalu Fileloka mencarikan kualitas paling tinggi yang masih muat di bawah {label}. Kamu tidak perlu coba-coba geser slider. Teksnya dipertahankan kalau memungkinkan, dan semuanya diproses di perangkatmu sendiri.",
            kicker=[f"Target {label} sudah terpilih", "File tidak di-upload"],
            use_h=f"Kapan butuh PDF di bawah {label}?",
            use=USE_ID[key],
            table_h=f"Seberapa realistis {label}?",
            table_note="Ini perkiraan untuk halaman A4. Hasil sebenarnya tergantung isi dokumen, dan ukuran akhirnya selalu kelihatan sebelum kamu mengunduh.",
            th=("Jenis dokumen", f"Ke {label}"),
            rows=feasibility_rows(nbytes, "id"),
            steps=[f"Pilih PDF atau seret ke halaman ini. Target {label} sudah terpilih.",
                   "Klik Kompres. Fileloka mencoba mempertahankan teks dulu, lalu mencari kualitas gambar terbaik yang masih muat.",
                   f"Cek ukuran sebelum dan sesudah serta tanda Di bawah {label}, lalu unduh."],
            faqs=faq_id(key, label),
            name=f"Kompres PDF {label}",
        )
    return dict(
        title=f"Compress PDF to {label} Online Free, Auto Fit | Fileloka",
        meta=f"Compress a PDF to under {label} automatically. Choose the target and Fileloka finds the best quality that still fits. Free, no sign-up, and the file is never uploaded.",
        h1=f"Compress PDF to {label}",
        lead=f"Pick a file and Fileloka finds the highest quality that still fits under {label}, so you don't have to guess with a slider. It keeps the text selectable when it can, and everything runs on your own device.",
        kicker=[f"{label} target preselected", "Your file stays on your device"],
        use_h=f"When do you need a PDF under {label}?",
        use=USE_EN[key],
        table_h=f"How realistic is {label}?",
        table_note="These are estimates for A4 pages. Real results depend on what's in the document, and you always see the final size before downloading.",
        th=("Document", f"To {label}"),
        rows=feasibility_rows(nbytes, "en"),
        steps=[f"Pick a PDF or drop it on the page. The {label} target is already selected.",
               "Click Compress. Fileloka tries to keep the text first, then looks for the best image quality that fits.",
               f"Check the before and after sizes and the Under {label} badge, then download."],
        faqs=faq_en(key, label),
        name=f"Compress PDF to {label}",
    )
