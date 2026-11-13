# Monetisasi Fileloka: yang sudah terpasang dan cara menyalakannya

Semua setelan ada di satu file: `scripts/monetize.py`. Ubah nilainya, jalankan
`python3 scripts/generate_tool_pages.py`, commit, push. Tidak ada yang lain.

## Yang sudah terpasang

| Bagian | Isi | Status setelah deploy |
|---|---|---|
| Slot uang | Satu kotak per halaman: tawaran sponsor kalau halaman itu punya, kalau tidak kotak dukungan. Tautan HTML biasa, CSP tidak berubah | **Mati** sampai `SUPPORT_URL` atau `OFFERS` diisi |
| Ajakan setelah hasil | Satu baris di bawah tombol Unduh ("Terbantu? Ikut patungan"), muncul tepat setelah alat selesai | Ikut slot dukungan |
| Penghitung anonim | `/api/e` (Pages Function) mencatat halaman dibuka, alat selesai, unduh, klik slot. Tanpa cookie, tanpa IP | **Jalan tapi tidak menyimpan** sampai binding `STATS` dibuat |
| Halaman kepercayaan | `/privacy/`, `/about/`, `/contact/`, `/terms/` + versi `/id/`. Syarat praktis AdSense dan program affiliate | Aktif |
| Verifikasi AdSense | Meta tag kepemilikan + `/ads.txt` | **Mati** sampai `ADSENSE_CLIENT` diisi |

## Urutan menyalakan

Kerjakan dari atas. Langkah 1 sampai 3 total sekitar 20 menit.

### 1. Sambungkan penghitung (5 menit)

Cloudflare dashboard → Workers & Pages → project Fileloka → Settings → Bindings → Add → **Analytics Engine**.

- Variable name: `STATS`
- Dataset: `fileloka_events`

Simpan untuk Production, lalu redeploy. Dataset dibuat otomatis saat data pertama masuk.
Gratis sampai 100.000 data point per hari; trafik sekarang jauh di bawah itu.

Baca angkanya:

```bash
export CF_ACCOUNT_ID=...   # sidebar kanan dashboard
export CF_API_TOKEN=...    # API token dengan izin "Account Analytics: Read"
python3 scripts/stats.py 7
```

Angka yang paling penting: `use` dibagi `pv` per halaman alat. Halaman yang sering dibuka tapi jarang
selesai berarti alatnya bermasalah. Halaman yang selesai terus berarti layak dibuatkan variasi baru.

### 2. Isi tautan dukungan (10 menit)

Buat satu produk pay-what-you-want di Gumroad (payout bank sudah tersambung), lalu:

```python
SUPPORT_URL = {
    "en": "https://rizkynandapr.gumroad.com/l/NAMA-PRODUK",
    "id": "",   # opsional: halaman Saweria/Trakteer, lebih cocok untuk pengunjung Indonesia
}
```

Rebuild dan push. Kotak dukungan muncul di semua halaman, dan baris ajakan muncul setelah tiap hasil.

### 3. Google Search Console (5 menit, tanpa kode)

Tambahkan `fileloka.id` sebagai Domain property, verifikasi lewat DNS TXT, kirim
`https://fileloka.id/sitemap.xml`. Ini satu-satunya tempat yang menunjukkan kata kunci apa yang
membawa orang ke situs, dan itu yang menentukan alat apa yang dibangun berikutnya.

### 4. Tawaran sponsor (affiliate)

Setelah diterima di sebuah program, tambahkan satu entri per halaman alat:

```python
OFFERS = {
    "password-generator": {
        "slug": "pwmanager",
        "url": "https://partner.example/?ref=ID_KAMU",
        "en": ("Headline", "Satu dua kalimat kenapa cocok.", "Label tombol"),
        "id": ("Judul", "Satu dua kalimat kenapa cocok.", "Label tombol"),
    },
}
```

Label "Sponsored" dan kalimat pengungkapan komisi ditambahkan otomatis, dan tautannya diberi
`rel="sponsored"`. Build gagal kalau tautan bukan `https://`. Pasangan yang masuk akal: password manager
di Password generator, penyimpanan cloud atau tanda tangan elektronik di halaman PDF.

### 5. AdSense

Daftar di AdSense, lalu isi `ADSENSE_CLIENT = "ca-pub-................"` dan rebuild. Itu memasang
meta tag kepemilikan dan `/ads.txt`, cukup untuk proses review. **Belum ada iklan yang tayang.**

Menayangkan iklan adalah keputusan terpisah karena harganya nyata:

- Google hanya mendukung CSP berbasis nonce (`script-src 'nonce-…' 'strict-dynamic' https: …`), bukan
  daftar domain. CSP `default-src 'none'; script-src 'self'` yang sekarang harus dilepas di halaman beriklan.
- Nonce harus baru di tiap request, jadi setiap halaman HTML harus lewat Pages Function. Request statis
  yang sekarang gratis tanpa batas berubah jadi invocation (kuota gratis 100.000 per hari).
- Iklan yang dipersonalisasi untuk pengunjung EEA, Inggris, dan Swiss wajib lewat CMP bersertifikat
  Google (banner persetujuan). Tanpa itu hanya iklan non-personal yang boleh tayang. Data Juli
  menunjukkan banyak trafik dari Belanda, jadi ini berlaku.
- Kalimat "tidak ada kode pihak ketiga" di halaman utama dan SECURITY.md tidak lagi benar.

Saran: tunda sampai angka di langkah 1 menunjukkan trafik manusia yang cukup (lihat hitungan di bawah).

## Hitungan jujur

Pakai asumsi RPM iklan $1 sampai $4 per 1.000 tampilan halaman (angka yang sama dengan README §5):

| Tampilan halaman per bulan | Perkiraan iklan per bulan |
|---|---|
| 3.000 | $3 sampai $12 |
| 30.000 | $30 sampai $120 |
| 300.000 | $300 sampai $1.200 |

Artinya lapisan ini membuat Fileloka **bisa** menghasilkan, tapi yang menentukan jumlahnya adalah
trafik. Tuas trafik yang sudah terbukti di repo ini adalah halaman per kata kunci (contoh:
`/compress-pdf-to-200kb/`). Menambah halaman seperti itu lebih bernilai daripada menambah slot.

Catatan: angka "unique visitors" di dashboard Cloudflare ikut menghitung bot. Penghitung di langkah 1
hanya jalan di browser sungguhan dan membuang user agent bot, jadi angka itu yang dipakai untuk memutuskan.

## Pengaman (opsional, 2 menit)

Siapa pun bisa mengirim POST palsu ke `/api/e` untuk menggelembungkan angka atau menghabiskan kuota
Function harian. Dampaknya hanya ke statistik: halaman statis tetap dilayani karena `_routes.json`
membatasi Function ke `/api/*`. Untuk menutupnya, buat satu rate limiting rule (paket gratis dapat
satu): path sama dengan `/api/e`, 30 request per menit per IP, aksi Block.

## Mematikan

`ANALYTICS = False` di `monetize.py` lalu rebuild: tidak ada halaman yang mengirim apa pun, dan
halaman privasi menulis ulang dirinya sendiri. Mengosongkan `SUPPORT_URL` dan `OFFERS` menghilangkan slot.
