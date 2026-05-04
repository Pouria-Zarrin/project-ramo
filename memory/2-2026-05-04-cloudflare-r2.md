# 2 — Cloudflare R2 setup
**Date:** 2026-05-04

---

## What was done

- Authenticated Wrangler CLI with Cloudflare account (Pouria-Zarrin) via OAuth
- Created R2 bucket: **ramopharmin-assets**
- Enabled public access (dev URL)
- Uploaded both oversized PDFs that could not be stored in git

---

## Bucket details

| Item | Value |
|------|-------|
| Bucket name | `ramopharmin-assets` |
| Public base URL | `https://pub-638fc8ca34b7400fa409ed5968293d2e.r2.dev` |
| Storage class | Standard |
| Free tier | 10 GB storage, 1M ops/month, zero egress |

---

## Uploaded files

| File | Public URL |
|------|-----------|
| `company-profile-G2-English.pdf` (188 MB) | `https://pub-638fc8ca34b7400fa409ed5968293d2e.r2.dev/company-profile-G2-English.pdf` |
| `company-profile-v1.pdf` (180 MB) | `https://pub-638fc8ca34b7400fa409ed5968293d2e.r2.dev/company-profile-v1.pdf` |

---

## Uploading new files in future

```bash
# From repo root (must be logged in: npx wrangler login)
npx wrangler r2 object put ramopharmin-assets/<filename> \
  --file <local/path/to/file> \
  --content-type <mime/type> \
  --remote
```

Common content types:
- PDF: `application/pdf`
- JPEG: `image/jpeg`
- PNG: `image/png`
- WebP: `image/webp`

---

## Next steps

- When domain is registered, add a custom `cdn.ramopharmin.com` subdomain pointing to the R2 bucket (via Cloudflare DNS — zero extra cost)
- Link PDF download buttons in `company-profile-G2-English.html` to the R2 URLs above
