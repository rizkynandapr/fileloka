# ToolDock — Security Model & Runbook

Baca ini sebelum launch. Bagian 1–2 menjelaskan apa yang sudah dikerjakan di kode; bagian 3 adalah hal yang **hanya kamu** yang bisa lakukan (akun & domain) — dan itu justru risiko terbesar yang tersisa.

---

## 1. Threat model — jujur, bukan jargon

**Yang tidak bisa bocor, by design.** Tidak ada server aplikasi, database, akun user, session, atau endpoint upload. File user diproses di memori browser mereka sendiri dan tidak pernah dikirim. Skenario breach klasik ("database berisi jutaan file/user bocor") tidak mungkin terjadi karena datanya tidak pernah ada di sisi kita. Ini bisa diverifikasi siapa pun: DevTools → Network (tidak ada request berisi file), atau matikan internet setelah halaman termuat — tool tetap jalan.

**Sisa permukaan serangan, diurutkan dari yang paling realistis:**

| # | Vektor | Dampak | Status |
|---|--------|--------|--------|
| 1 | **Account takeover** — GitHub / Vercel / registrar domain dibajak, situs diganti versi jahat | Kritis: attacker bisa serve JS yang mencuri file user | Mitigasi di §3 — tanggung jawab operasional |
| 2 | **Supply chain** — library pihak ketiga disusupi | Sama kritisnya | **Dieliminasi**: semua library di-vendor lokal, tidak ada script origin eksternal (§2.1) |
| 3 | **XSS** — nama file jahat (`<img onerror=…>.pdf`) dieksekusi | Pencurian file dalam sesi | Escape di semua titik insersi + CSP tanpa inline script sebagai lapis kedua (§2.2) |
| 4 | **Clickjacking / framing / MIME sniffing** | Rendah | Diblokir via headers (§2.3) |
| 5 | **Privasi pasif** — Google Fonts melihat IP pengunjung | Privasi, bukan breach | Satu-satunya request pihak ketiga tersisa; opsi eliminasi di §4 |
| 6 | **Device user sendiri** (malware, browser lawas) | Di luar kendali situs mana pun | Out of scope — tidak ada situs yang bisa menjamin ini |

Kalimat jujur untuk dipakai di halaman publik: *"File kamu tidak pernah meninggalkan device-mu — dan itu bisa kamu buktikan sendiri."* Jangan pernah menulis "100% tidak bisa dihack" — klaim itu tidak bisa dibuktikan untuk sistem apa pun dan menurunkan kredibilitas.

---

## 2. Kontrol yang sudah diimplementasikan di build ini

### 2.1 Supply chain: zero third-party script
Semua library di-download dari registry resmi (npm) pada versi pinned, di-vendor ke `/lib/`, dan di-load dari origin sendiri. Halaman **tidak pernah mengeksekusi JavaScript dari domain pihak ketiga** — kompromi CDN eksternal tidak lagi relevan.

Provenance record (SHA-256 — simpan; cocokkan lagi kapan pun curiga):

```
0f9a5cad07941f0826586c94e089d89b918c46e5c17cf2d5a3c6f666e3bc694f  lib/pdf-lib.min.js      (pdf-lib@1.17.1, npm)
5b5799e6f8c680663207ac5b42ee14eed2a406fa7af48f50c154f0c0b1566946  lib/pdf.min.js          (pdfjs-dist@3.11.174, npm)
feabdf309770ed24bba31a5467836cdc8cf639c705af27d52b585b041bb8527b  lib/pdf.worker.min.js   (pdfjs-dist@3.11.174, npm)
acc7e41455a80765b5fd9c7ee1b8078a6d160bbbca455aeae854de65c947d59e  lib/jszip.min.js        (jszip@3.10.1, npm)
c541ef06327885a8415bca8df6071e14189b4855336def4f36db54bde8484f36  lib/qrcode.min.js       (davidshimjs/qrcodejs@master, GitHub)
```

Verifikasi kapan saja: `sha256sum lib/*.js` dan bandingkan dengan tabel di atas.

### 2.2 XSS: dua lapis
1. **Escape di sumber** — semua string yang bisa dikontrol user (terutama nama file) melewati `esc()` sebelum masuk `innerHTML`, atau di-set via `textContent` (toast, progress label). Sudah diaudit per titik insersi.
2. **CSP sebagai jaring pengaman** — `script-src 'self'` **tanpa** `'unsafe-inline'`: seandainya pun satu escape terlewat, inline script hasil injeksi tidak akan dieksekusi browser. Ini alasan utama kode dipecah dari single-file menjadi `app.js` eksternal.

Catatan trade-off yang disengaja: `style-src` masih memuat `'unsafe-inline'` karena markup memakai atribut `style="…"`. Injeksi CSS berisiko jauh lebih rendah daripada injeksi script dan ini praktik yang diterima industri; menghapusnya berarti memindah semua inline style ke class — nice-to-have, bukan blocker.

### 2.3 Headers (di `vercel.json`, aktif otomatis saat deploy)
- **CSP**: `default-src 'none'` (deny-by-default), script hanya `'self'`, worker `'self' blob:`, gambar `'self' data: blob:`, koneksi hanya `'self'`, `frame-ancestors 'none'`, `object-src 'none'`, `form-action 'none'`, `base-uri 'self'`, `upgrade-insecure-requests`.
- **HSTS** `max-age=63072000; includeSubDomains; preload` — browser menolak koneksi non-HTTPS. Setelah stabil, daftarkan ke hstspreload.org.
- `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` (kamera/mic/lokasi/payment dimatikan), `COOP: same-origin`, `CORP: same-origin`.
- Cache: `/lib/*` immutable 1 tahun (file pinned); HTML/CSS/JS utama selalu revalidate (patch keamanan langsung sampai ke user, tidak tersangkut cache).
- `/.well-known/security.txt` (RFC 9116) — ganti emailnya.

Yang **sengaja tidak dipakai**: COEP/`require-corp` (tidak butuh SharedArrayBuffer, gampang merusak font loading); `X-XSS-Protection` (deprecated, digantikan CSP).

### 2.4 Aplikasi
- Password generator: `crypto.getRandomValues` + rejection sampling (tanpa modulo bias) + jaminan tiap charset terwakili — teruji 300 sampel.
- File terenkripsi/korup ditolak dengan pesan jelas, tidak setengah diproses.
- Re-encode JPG/WebP otomatis membuang metadata EXIF (lokasi GPS, perangkat) — bonus privasi, disebut di UI.
- Nol storage: tanpa cookie, `localStorage`, tracker, analytics. Tidak ada consent banner karena memang tidak ada yang dikumpulkan.

---

## 3. Runbook operasional — risiko #1 ada di sini

Untuk situs statis yang sudah dikeraskan, jalur pembobolan yang realistis bukan "menghack website"-nya, tapi **membajak akunmu** lalu men-deploy versi jahat. Kerjakan semua ini (±20 menit sekali seumur hidup):

- [ ] **GitHub**: 2FA hardware key/TOTP (bukan SMS) · branch `main` di-protect (require PR) · jangan simpan token di plaintext.
- [ ] **Vercel**: 2FA · hapus member/integrasi tak terpakai · deploy hanya dari repo resmi.
- [ ] **Registrar domain**: 2FA · **registrar lock** aktif · **DNSSEC** aktif · auto-renew nyala (domain expired = takeover termudah).
- [ ] **Email pemulihan** semua akun di atas: 2FA juga (email adalah master key).
- [ ] `security.txt` + email kontak di halaman privacy → ganti dari placeholder ke alamat asli.

**Kebijakan update dependensi**: library pinned tidak akan berubah diam-diam. Saat mau upgrade: download versi baru dari npm → catat SHA-256 baru di tabel §2.1 → jalankan `test.js` → deploy. Jangan pernah copy-paste file .js dari sumber tak resmi.

**Monitoring ringan (gratis, 10 menit)**:
- UptimeRobot/cron eksternal: cek situs hidup + `curl -s https://domainmu/app.js | sha256sum` sebulan sekali, cocokkan dengan hash deploy terakhir — deteksi dini bila situs diganti.
- Aktifkan notifikasi login/deploy di GitHub & Vercel.

**Jika terjadi kompromi**: putuskan integrasi & rotasi semua kredensial → `vercel rollback` ke deployment terakhir yang sah → audit riwayat commit/deploy → baru umumkan. Karena tidak ada data user tersimpan, insiden terburuk adalah *defacement/malicious JS berjangka pendek*, bukan kebocoran data historis.

---

## 4. Opsional berikutnya (naikkan lagi satu tingkat)

1. **Self-host Google Fonts** (menghapus request pihak ketiga terakhir + patuh preseden GDPR Jerman soal Google Fonts):
   unduh ketiga font (Gabarito, Public Sans, IBM Plex Mono) sebagai `woff2` via google-webfonts-helper → taruh di `/fonts/` + satu `fonts.css` `@font-face` → ganti `<link>` Google Fonts → di CSP, kecilkan `style-src` ke `'self' 'unsafe-inline'` dan `font-src` ke `'self'`. Setelah ini, **satu-satunya koneksi keluar situs = nol**.
2. Hapus semua atribut `style="…"` → class, lalu buang `'unsafe-inline'` dari `style-src`.
3. Subresource pinning di sisi user berlebihan untuk same-origin (attacker yang bisa ubah `/lib` bisa ubah HTML-nya juga) — fokus tetap di §3.
4. Saat menambah **AdSense** nanti: itu berarti mengizinkan script Google (longgarkan CSP sesuai domain resmi Google) — trade-off sadar antara monetisasi vs "zero third-party". Dokumentasikan di halaman privacy saat itu terjadi.

---

## 5. Menjalankan

**Lokal (untuk testing) — jangan double-click file** (pdf.js Worker diblokir di `file://` oleh Chrome):
```bash
cd tooldock
python3 -m http.server 8000        # atau: npx serve .
# buka http://localhost:8000
```

**Production:**
```bash
cd tooldock && vercel --prod       # atau drag-drop folder di vercel.com/new
```
HTTPS + sertifikat otomatis dari Vercel; semua header §2.3 aktif dari `vercel.json` tanpa konfigurasi tambahan. Setelah deploy, cek nilai di securityheaders.com (target: A/A+) dan observatory.mozilla.org.
