# 3 — R2 assets reorganized & globe textures added

**Date:** 2026-05-04

---

## What was done

- Identified missing globe textures (`earth-night.jpg`, `earth-topology.png`, `globe.gl.min.js`) from the original `ramo-web-V2` source on Google Drive — these were absent from the repo and previously pointing to a threejs.org CDN fallback.
- Uploaded the three globe assets to R2 under `assets/globe/`.
- Moved both large PDFs from the R2 bucket root into a `pdfs/` subfolder and deleted the old root-level objects, giving the bucket a clean folder hierarchy.
- Uploaded the third company profile PDF (`company-profile-G1-English.pdf`) which was in the source but had never been uploaded.
- Updated `V0/en/index.html` to point the globe texture URLs to R2 instead of threejs.org (committed to git, will trigger a GitHub Pages redeploy).

---

## Current R2 bucket structure

**Bucket:** `ramopharmin-assets`  
**Public base URL:** `https://pub-638fc8ca34b7400fa409ed5968293d2e.r2.dev`

```
ramopharmin-assets/
├── pdfs/
│   ├── company-profile-G2-English.pdf   (188 MB)
│   ├── company-profile-v1.pdf           (180 MB)
│   └── company-profile-G1-English.pdf   (~varies)
└── assets/
    └── globe/
        ├── earth-night.jpg              (698 KB — globe surface texture)
        ├── earth-topology.png           (bump/topology map)
        └── globe.gl.min.js              (globe.gl library)
```

---

## Key public URLs

| Asset | Public URL |
|-------|-----------|
| Globe surface texture | `https://pub-638fc8ca34b7400fa409ed5968293d2e.r2.dev/assets/globe/earth-night.jpg` |
| Globe topology/bump | `https://pub-638fc8ca34b7400fa409ed5968293d2e.r2.dev/assets/globe/earth-topology.png` |
| Globe GL library | `https://pub-638fc8ca34b7400fa409ed5968293d2e.r2.dev/assets/globe/globe.gl.min.js` |
| Company profile G2 (EN) | `https://pub-638fc8ca34b7400fa409ed5968293d2e.r2.dev/pdfs/company-profile-G2-English.pdf` |
| Company profile v1 | `https://pub-638fc8ca34b7400fa409ed5968293d2e.r2.dev/pdfs/company-profile-v1.pdf` |
| Company profile G1 (EN) | `https://pub-638fc8ca34b7400fa409ed5968293d2e.r2.dev/pdfs/company-profile-G1-English.pdf` |

---

## Assets already in git (not needed in R2)

These asset categories are already committed to the GitHub repo and served by GitHub Pages — no need to duplicate in R2:

- `V0/product-images/` — all product PNG images
- `V0/logos/` — `english-full-logo.png`, `english-full-logo-white.png`
- `V0/company-images/` — company photography
- `V0/company-profile/preview-jpg/` — page-01.jpg through page-19.jpg

---

## Uploading new files in the future

```bash
# From repo root (must be logged in: npx wrangler login)
npx wrangler r2 object put ramopharmin-assets/<folder/filename> \
  --file <local/path/to/file> \
  --content-type <mime/type> \
  --remote
```

Common content types:
- PDF: `application/pdf`
- JPEG: `image/jpeg`
- PNG: `image/png`
- JavaScript: `application/javascript`

---

## Next steps

- Register domain (recommended: `ramopharmin.com` via Cloudflare Registrar).
- After domain is registered, point `cdn.ramopharmin.com` to the R2 bucket via Cloudflare DNS — replace the long `pub-xxx.r2.dev` URLs with the clean subdomain.
- Update the PDF download button in `V0/company-profile/company-profile-G2-English.html` to link to the R2 URLs above.
