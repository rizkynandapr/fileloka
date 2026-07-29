# Third-party libraries

These files are vendored (unmodified) from their official releases and remain
under their own licenses. The MIT License in the repository root covers
Fileloka's own source only, not these dependencies.

| File                | Library    | Version   | License       |
|---------------------|------------|-----------|---------------|
| pdf-lib.min.js      | pdf-lib    | 1.17.1    | MIT           |
| pdf.min.js          | pdf.js     | 3.11.174  | Apache-2.0    |
| pdf.worker.min.js   | pdf.js     | 3.11.174  | Apache-2.0    |
| jszip.min.js        | JSZip      | 3.10.1    | MIT / GPLv3   |
| qrcode.min.js       | qrcodejs   | 1.0.0     | MIT           |
| libheif.js          | libheif-js | 1.18.2    | **LGPL-3.0**  |

SHA-256 checksums for these files are recorded in ../SECURITY.md.

`libheif.js` is licensed under the LGPL-3.0; its full licence text is included
here as `LICENSE-libheif-LGPL-3.0.txt`. It is shipped **unmodified** and loaded
dynamically as a separate file, so it can be replaced independently — the
arrangement the LGPL is designed for. Fileloka's own MIT licence does not
extend to it.
