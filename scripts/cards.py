# -*- coding: utf-8 -*-
"""Card metadata: icon SVG, category, search keywords, EN card blurb."""
ICONS={
 "merge-pdf": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"13\" y=\"4\" width=\"8\" height=\"16\" rx=\"2\"/><path d=\"M3 9h6m0 0L7 7m2 2-2 2M3 15h6m0 0-2-2m2 2-2 2\"/></svg>",
 "split-pdf": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"3\" y=\"4\" width=\"8\" height=\"16\" rx=\"2\"/><path d=\"M15 9h6m0 0-2-2m2 2-2 2M15 15h6m0 0-2-2m2 2-2 2\"/></svg>",
 "compress-pdf": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"5\" y=\"3\" width=\"14\" height=\"18\" rx=\"2\"/><path d=\"M12 7v3m0 0-2-2m2 2 2-2M12 17v-3m0 0-2 2m2-2 2 2\"/></svg>",
 "pdf-to-jpg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"4\" y=\"3\" width=\"16\" height=\"18\" rx=\"2\"/><circle cx=\"9.5\" cy=\"9.5\" r=\"1.6\"/><path d=\"m4 17 4.5-4.5 3 3L15 12l5 5\"/></svg>",
 "jpg-to-pdf": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"3\" y=\"3\" width=\"11\" height=\"11\" rx=\"2\"/><circle cx=\"6.8\" cy=\"6.8\" r=\"1.2\"/><path d=\"m3 11.5 3-3 3 3\"/><rect x=\"13\" y=\"13\" width=\"8\" height=\"8\" rx=\"1.5\"/></svg>",
 "compress-image": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"3\" y=\"5\" width=\"18\" height=\"14\" rx=\"2\"/><path d=\"M7 12h4M9.4 10.4 11 12l-1.6 1.6M17 12h-4M14.6 10.4 13 12l1.6 1.6\"/></svg>",
 "resize-image": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"7\" y=\"7\" width=\"10\" height=\"10\" rx=\"1.5\"/><path d=\"M3 3h4M3 3v4m0-4 4 4M21 21h-4m4 0v-4m0 4-4-4\"/></svg>",
 "convert-image": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M20.5 8A9 9 0 0 0 5 6.5L3.5 8M3.5 16a9 9 0 0 0 15.5 1.5l1.5-1.5\"/><path d=\"M3.5 3.5V8H8M20.5 20.5V16H16\"/></svg>",
 "heic-to-jpg": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"5\" y=\"2.5\" width=\"14\" height=\"19\" rx=\"2.5\"/><path d=\"M10 5.2h4\"/><path d=\"m8 15.5 2.6-2.6 2 2L15 12.5l1 1\"/><circle cx=\"14.6\" cy=\"9.4\" r=\"1\"/></svg>",
 "qr-code": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"3\" y=\"3\" width=\"7\" height=\"7\" rx=\"1\"/><rect x=\"14\" y=\"3\" width=\"7\" height=\"7\" rx=\"1\"/><rect x=\"3\" y=\"14\" width=\"7\" height=\"7\" rx=\"1\"/><path d=\"M14 14h3v3h-3zM21 14v.01M14 21v.01M18 18h3v3h-3z\"/></svg>",
 "password-generator": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><circle cx=\"7.5\" cy=\"15.5\" r=\"3.5\"/><path d=\"M10.2 12.8 21 2M15 8l3.2 3.2M12 11l2 2\"/></svg>",
 "word-counter": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M4 6h16M4 11h16M4 16h8\"/><path d=\"m15.5 17.5 2 2L21 16\"/></svg>",
 "signature": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"m14.5 4.5 5 5L8 21H3v-5z\"/><path d=\"m12.5 6.5 5 5\"/></svg>"
}
CATS={
 "merge-pdf": "pdf",
 "split-pdf": "pdf",
 "compress-pdf": "pdf",
 "pdf-to-jpg": "pdf",
 "jpg-to-pdf": "pdf",
 "compress-image": "image",
 "resize-image": "image",
 "convert-image": "image",
 "heic-to-jpg": "image",
 "qr-code": "util",
 "password-generator": "util",
 "word-counter": "util",
 "signature": "util"
}
KEYS={
 "merge-pdf": "merge combine join gabung satukan",
 "split-pdf": "split extract pages remove pisah ambil halaman",
 "compress-pdf": "compress shrink reduce size kecilkan kompres",
 "pdf-to-jpg": "pdf to jpg image png export convert",
 "jpg-to-pdf": "jpg to pdf image photo scan foto ubah",
 "compress-image": "compress image optimize kb photo kompres foto",
 "resize-image": "resize scale dimensions pixels ubah ukuran",
 "convert-image": "convert webp png jpg format ubah format",
 "heic-to-jpg": "heic heif iphone photo foto iphone convert jpg apple",
 "qr-code": "qr code link wifi barcode kode",
 "password-generator": "password secure random strong kata sandi",
 "word-counter": "word counter character count essay hitung kata",
 "signature": "signature sign draw tanda tangan ttd"
}
CARD_DESC_EN={
 "merge-pdf": "Put several PDFs into one file, in your order.",
 "split-pdf": "Pull out just the pages you need, or save every page separately.",
 "compress-pdf": "Shrink a PDF so it fits email and upload limits.",
 "pdf-to-jpg": "Save each PDF page as a JPG.",
 "jpg-to-pdf": "Put photos and scans into one PDF.",
 "compress-image": "Make photos much smaller without visible loss.",
 "resize-image": "Scale pictures to exact pixels or a percentage.",
 "convert-image": "Switch between JPG, PNG and WebP.",
 "heic-to-jpg": "Turn iPhone photos into JPGs that open anywhere.",
 "qr-code": "Turn any link or text into a scannable code.",
 "password-generator": "Random passwords made on your device.",
 "word-counter": "Words, characters and reading time, live.",
 "signature": "Draw a signature and save it as a transparent PNG."
}
