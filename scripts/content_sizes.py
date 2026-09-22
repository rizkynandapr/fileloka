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
        return ("Mudah — tetap berwarna & tajam" if lang == "id" else "Easy — stays in colour and sharp")
    if budget >= 55_000:
        return ("Bisa — kualitas baik" if lang == "id" else "Yes — good quality")
    if budget >= 28_000:
        return ("Bisa — centang hitam putih" if lang == "id" else "Yes — tick black & white")
    if budget >= 15_000:
        return ("Mepet — hitam putih, detail rendah" if lang == "id" else "Tight — B&W, lower detail")
    return ("Sulit — sebaiknya pisah jadi beberapa file" if lang == "id" else "Hard — split into several files")

def text_verdict(size, lang):
    if size >= 300_000:
        return ("Biasanya sudah muat, teks tetap utuh" if lang == "id" else "Usually fits already, text intact")
    if size >= 150_000:
        return ("Umumnya muat; kalau tidak, halaman dijadikan gambar" if lang == "id" else "Usually fits; otherwise pages become images")
    return ("Tergantung font — sering harus jadi gambar" if lang == "id" else "Depends on fonts — often needs image pages")

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
 "100kb": "Batas 100 KB biasanya muncul di formulir yang meminta satu dokumen pendek — misalnya scan KTP, kartu keluarga, atau surat pernyataan satu halaman. Ini target yang ketat: satu halaman scan masih nyaman, tapi dokumen banyak halaman hampir pasti perlu opsi hitam putih.",
 "200kb": "200 KB adalah salah satu batas paling umum di portal pendaftaran online untuk scan dokumen satu sampai dua halaman: ijazah, transkrip, SKCK, atau surat keterangan. Satu-dua halaman scan HP biasanya bisa masuk dengan warna tetap jelas.",
 "300kb": "300 KB memberi ruang sedikit lebih lega untuk dokumen dua sampai tiga halaman — misalnya transkrip bolak-balik atau sertifikat beserta lampirannya — tanpa harus menurunkan kualitas terlalu jauh.",
 "500kb": "Batas 500 KB sering dipakai portal lamaran kerja, beasiswa, dan pendaftaran seleksi untuk berkas beberapa halaman. Scan tiga sampai lima halaman umumnya masuk dengan kualitas baik; PDF dari Word biasanya bahkan tidak perlu diubah jadi gambar.",
 "1mb":   "1 MB adalah batas yang umum di portal lamaran kerja, e-learning, dan aplikasi instansi. Untuk kebanyakan dokumen, mode yang menjaga teks tetap bisa diseleksi sudah cukup — teks, tautan, dan tanda tangan digital tetap utuh.",
 "2mb":   "2 MB cukup longgar: cocok untuk lampiran email kantor, laporan dengan grafik, atau portofolio berisi foto. Hampir semua PDF bisa masuk tanpa kehilangan teks yang bisa diseleksi — yang dikecilkan hanya foto di dalamnya.",
}
USE_EN = {
 "100kb": "A 100 KB limit usually comes from forms that want one short document — an ID scan, a one-page declaration, a proof of address. It's a strict target: one scanned page is comfortable, but multi-page documents almost always need the black & white option.",
 "200kb": "200 KB is one of the most common limits on application and registration portals for a one- or two-page scan: diplomas, transcripts, certificates, reference letters. A couple of phone-scanned pages usually fit while staying in clear colour.",
 "300kb": "300 KB gives a little more room for two- or three-page documents — a double-sided transcript, or a certificate with its attachment — without pushing quality too low.",
 "500kb": "500 KB is a typical limit on job, scholarship and visa portals for multi-page uploads. Three to five scanned pages usually fit at good quality, and PDFs exported from Word often don't need converting to images at all.",
 "1mb":   "1 MB is a common cap on job portals, learning platforms and government forms. For most documents the text-preserving method is enough — text, links and signatures stay intact and selectable.",
 "2mb":   "2 MB is generous: office email attachments, reports with charts, portfolios with photos. Nearly any PDF fits without losing selectable text — only the photos inside get smaller.",
}

def faq_id(key, label):
    base = [
     (f"Bagaimana cara kompres PDF jadi {label} di HP?",
      f"Buka halaman ini di Chrome atau Safari, ketuk area pilih file, ambil PDF dari penyimpanan atau WhatsApp. Target {label} sudah terpilih — tinggal ketuk tombol Kompres, lalu unduh. Tidak perlu install aplikasi."),
     (f"Kenapa hasilnya sedikit di bawah {label}, bukan pas {label}?",
      f"Sengaja. Sebagian portal menghitung 1 KB = 1000 byte, sebagian 1024 byte. Fileloka menargetkan di bawah {label} versi 1000 byte, jadi file lolos di kedua cara hitung. Kualitas yang dipilih tetap yang tertinggi yang masih muat."),
     ("Apakah teks di PDF masih bisa diseleksi?",
      "Selama bisa, ya. Fileloka lebih dulu mencoba mengecilkan foto dan scan di dalam PDF saja — teks tetap utuh. Hanya jika itu belum cukup, halaman diubah menjadi gambar, dan hasilnya memberi tahu kamu dengan jelas mana yang terjadi."),
     ("Aman untuk KTP, ijazah, atau dokumen pribadi?",
      "Aman, karena file tidak pernah di-upload. Kompresi dilakukan oleh browser di perangkatmu sendiri; tidak ada server yang menyimpan atau bisa membocorkan dokumenmu. Coba saja: setelah halaman terbuka, nyalakan mode pesawat — alatnya tetap bekerja."),
    ]
    extra = {
     "100kb": ("PDF saya 5 halaman, bisa sampai 100 KB?",
               "Bisa dicoba dengan mencentang Hitam putih — anggarannya kira-kira 18 KB per halaman, cukup untuk teks yang masih terbaca tapi detail kecil akan berkurang. Kalau hasilnya kurang jelas, lebih baik pisah PDF lalu kirim per bagian."),
     "200kb": ("Scan ijazah saya berwarna, apakah tetap berwarna di 200 KB?",
               "Untuk satu sampai dua halaman, umumnya ya. Warna baru perlu dikorbankan kalau halamannya banyak; kalau itu terjadi, hasil akan tertulis ‘Paling mendekati’ dan kamu bisa mencoba opsi hitam putih."),
     "300kb": ("Lebih baik pilih 200 KB atau 300 KB?",
               "Selalu pilih batas yang diminta portal. Makin longgar batasnya, makin tinggi kualitas yang bisa dipertahankan — jadi kalau boleh 300 KB, jangan kompres sampai 200 KB."),
     "500kb": ("CV dan lampiran saya digabung dulu atau dikompres dulu?",
               "Gabung dulu dengan alat Gabung PDF, baru kompres ke 500 KB. Mengompres file yang sudah digabung memberi hasil lebih kecil dan kualitas lebih rata daripada mengompres satu per satu."),
     "1mb":   ("PDF saya cuma 1,3 MB, kenapa tidak diubah jadi gambar?",
               "Karena tidak perlu. Untuk selisih kecil, mengecilkan foto di dalamnya sudah cukup — teks, tautan, dan kualitas cetak tetap terjaga. Halaman baru diubah jadi gambar jika memang tidak ada cara lain."),
     "2mb":   ("Laporan saya 15 MB, bisa jadi 2 MB?",
               "Biasanya bisa, terutama jika besarnya berasal dari foto. Untuk file sebesar itu, prosesnya butuh beberapa detik sampai semenit di HP — laptop akan lebih cepat."),
    }[key]
    return base[:2] + [extra] + base[2:]

def faq_en(key, label):
    base = [
     (f"How do I compress a PDF to {label} on my phone?",
      f"Open this page in Chrome or Safari, tap the file area and pick the PDF from your files. The {label} target is already selected — tap Compress, then download. No app to install."),
     (f"Why is the result a bit under {label} rather than exactly {label}?",
      f"On purpose. Some portals count 1 KB as 1000 bytes, others as 1024. Fileloka aims under the 1000-byte version of {label}, so the file passes either way — at the highest quality that still fits."),
     ("Will the text in my PDF stay selectable?",
      "Whenever possible, yes. Fileloka first shrinks only the photos and scans inside the PDF, leaving text intact. Pages are converted to images only if that isn't enough — and the result tells you clearly which one happened."),
     ("Is it safe for passports, IDs and contracts?",
      "Yes, because the file is never uploaded. Your own browser does the compression; there's no server that could store or leak the document. Try it: load the page, switch on airplane mode, and it still works."),
    ]
    extra = {
     "100kb": ("My PDF has 5 pages — can it reach 100 KB?",
               "Try it with Black & white ticked: that's roughly 18 KB per page, enough for legible text but fine detail will soften. If the result isn't clear enough, split the PDF and send it in parts."),
     "200kb": ("Will my colour scan stay in colour at 200 KB?",
               "For one or two pages, usually yes. Colour only has to go when there are many pages; if that happens the result says ‘Closest possible’ and you can try black & white."),
     "300kb": ("Should I pick 200 KB or 300 KB?",
               "Always pick the limit the portal asks for. A looser limit means higher quality is kept — if 300 KB is allowed, don't squeeze to 200 KB."),
     "500kb": ("Should I merge my CV and attachments first, or compress first?",
               "Merge first with the Merge PDF tool, then compress to 500 KB. Compressing the combined file gives a smaller result with more even quality than compressing each part separately."),
     "1mb":   ("My PDF is only 1.3 MB — why weren't pages turned into images?",
               "Because it wasn't needed. For a small gap, shrinking the photos inside is enough — text, links and print quality are preserved. Pages become images only when there's no other way."),
     "2mb":   ("Can a 15 MB report get down to 2 MB?",
               "Usually, especially when the size comes from photos. A file that large takes a few seconds to a minute on a phone — laptops are faster."),
    }[key]
    return base[:2] + [extra] + base[2:]

def page(lang, key, nbytes, label):
    if lang == "id":
        return dict(
            title=f"Kompres PDF {label} Online Gratis — Otomatis, Tanpa Upload | Fileloka",
            meta=f"Kompres PDF jadi di bawah {label} secara otomatis: pilih target, Fileloka mencari kualitas terbaik yang masih muat. Gratis, tanpa daftar, file tidak di-upload.",
            h1=f"Kompres PDF ke {label}",
            lead=f"Pilih file, dan Fileloka mencarikan kualitas tertinggi yang masih muat di bawah {label} — tanpa coba-coba slider. Teks dipertahankan selama memungkinkan, dan semuanya diproses di perangkatmu sendiri.",
            kicker=[f"Target {label} otomatis", "Teks tetap bisa diseleksi bila memungkinkan", "Tanpa upload"],
            use_h=f"Kapan butuh PDF di bawah {label}?",
            use=USE_ID[key],
            table_h=f"Seberapa realistis {label}?",
            table_note="Perkiraan untuk halaman A4. Hasil nyata tergantung isi dokumen — ukuran akhir selalu ditampilkan sebelum kamu mengunduh.",
            th=("Jenis dokumen", f"Ke {label}"),
            rows=feasibility_rows(nbytes, "id"),
            steps=[f"Pilih atau jatuhkan PDF — target {label} sudah terpilih.",
                   "Klik Kompres. Fileloka mencoba mode penjaga teks dulu, lalu mencari kualitas gambar terbaik yang muat.",
                   "Cek ukuran sebelum/sesudah dan tanda ‘Di bawah " + label + "’, lalu unduh."],
            faqs=faq_id(key, label),
            name=f"Kompres PDF {label}",
        )
    return dict(
        title=f"Compress PDF to {label} Online Free — Auto-Fit, No Upload | Fileloka",
        meta=f"Compress a PDF to under {label} automatically: choose the target and Fileloka finds the best quality that still fits. Free, no sign-up, files never uploaded.",
        h1=f"Compress PDF to {label}",
        lead=f"Pick a file and Fileloka finds the highest quality that still fits under {label} — no guessing with sliders. Text is kept selectable whenever possible, and everything runs on your own device.",
        kicker=[f"Auto-fit to {label}", "Keeps text when possible", "No upload"],
        use_h=f"When do you need a PDF under {label}?",
        use=USE_EN[key],
        table_h=f"How realistic is {label}?",
        table_note="Estimates for A4 pages. Real results depend on the content — the final size is always shown before you download.",
        th=("Document", f"To {label}"),
        rows=feasibility_rows(nbytes, "en"),
        steps=[f"Choose or drop a PDF — the {label} target is preselected.",
               "Click Compress. Fileloka tries the text-preserving method first, then searches for the best image quality that fits.",
               "Check the before/after size and the ‘Under " + label + "’ badge, then download."],
        faqs=faq_en(key, label),
        name=f"Compress PDF to {label}",
    )
