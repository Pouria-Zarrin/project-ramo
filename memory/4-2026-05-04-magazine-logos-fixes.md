# 4 — Magazine page rebuilt & logo fixes

**Date:** 2026-05-04

---

## What was done

### Health magazine page — complete rebuild

- Source blocks in `ramo-web-V2/salamt/` were merged into a single combined page at `V0/fa/magazine/index.html`, replacing the old fragmented version.
- Blocks merged (in order):
  1. `0-white-header-with-holding.html` — sticky site header with holding info bar, nav, language toggle
  2. `01-magazine-header.html` — page title, search bar, topic chips
  3. `02-feature-article.html` — featured dark-background article block
  4. `02-feature-spotlight-azaram.html` — Azaram product spotlight with image gallery and key takeaways
  5. `03-latest-articles.html` — 6-card article grid
  6. `04-featured-topics.html` — 6 topic cards (AZ, IM, TX, PH, PT, LV)
  7. `05-editorial-standards.html` — 4-card editorial principles section
  8. `8.1-white-version-footer.html` — light footer with brand description, links, socials
- All CSS from the 8 blocks was consolidated into one `<style>` block in `<head>`; duplicate CDN script/link tags were removed.
- Header adaptations:
  - Language toggle buttons replaced with actual links (`../../en/` and `../`) — removed `alert()` placeholders
  - Nav links updated to relative paths pointing to our static site structure
  - "مجله سلامت" nav item highlighted as active page

### Shared header/footer files updated

- `V0/fa/0-white-header-with-holding.html` — updated with white logo from repo and functional language toggle links
- `V0/fa/8.1-white-version-footer.html` — synced from latest salamt source

### Logo handling

- Both logo files uploaded to R2 under `logos/`:
  - `logos/english-full-logo.png` — full color, for home pages
  - `logos/english-full-logo-white.png` — white version, for subpages
- Initial implementation used R2 URLs (`pub-xxx.r2.dev/logos/...`) which **failed to load** in the browser (R2 public URL had network/SSL issues from certain environments).
- **Fix:** switched all logo `src` attributes to relative paths pointing to `V0/logos/` (already committed in git, served reliably by GitHub Pages):
  - `en/index.html` → `../logos/english-full-logo.png`
  - `fa/index.html` → `../logos/english-full-logo.png`
  - `fa/magazine/index.html` → `../../logos/english-full-logo-white.png` (header + footer)
- R2 CORS rules were also configured (`GET`/`HEAD` from `*`) in case R2 is used for other assets in the browser.

---

## R2 bucket — final structure

**Bucket:** `ramopharmin-assets`
**Public URL:** `https://pub-638fc8ca34b7400fa409ed5968293d2e.r2.dev`
**CORS:** enabled (GET/HEAD from any origin)

```
ramopharmin-assets/
├── pdfs/
│   ├── company-profile-G2-English.pdf   (188 MB)
│   ├── company-profile-v1.pdf           (180 MB)
│   └── company-profile-G1-English.pdf
├── assets/
│   └── globe/
│       ├── earth-night.jpg
│       ├── earth-topology.png
│       └── globe.gl.min.js
└── logos/
    ├── english-full-logo.png
    └── english-full-logo-white.png
```

> **Note:** Logos on R2 are a backup copy. The live site uses the repo-served versions via relative paths. Use R2 logo URLs only if moving to an external CMS or CDN-only deployment.

---

## Live URLs

| Page | URL |
|------|-----|
| Root (redirects to EN) | https://pouria-zarrin.github.io/project-ramo/ |
| English home | https://pouria-zarrin.github.io/project-ramo/en/ |
| Farsi home | https://pouria-zarrin.github.io/project-ramo/fa/ |
| **Health magazine** | **https://pouria-zarrin.github.io/project-ramo/fa/magazine/** |

---

## Current site structure (V0/)

```
V0/
├── index.html                  ← redirects to en/
├── en/index.html               ← English corporate home (full color logo)
├── fa/index.html               ← Farsi corporate home (full color logo)
├── fa/magazine/index.html      ← Health magazine (white logo, new combined page)
├── logos/
│   ├── english-full-logo.png
│   └── english-full-logo-white.png
├── product-images/
├── company-images/
├── company-profile/
├── product-category-therapeutics/
├── about-us/
├── news/
└── contact-us/
```

---

## Logo convention (established)

| Context | Logo file | Where |
|---------|-----------|-------|
| Home pages (dark/colored headers) | `english-full-logo.png` | `en/`, `fa/` |
| Subpages (light `#EFF2F3` headers) | `english-full-logo-white.png` | `fa/magazine/`, future subpages |

---

## Pending / next steps

- Register domain (`ramopharmin.com` via Cloudflare Registrar) and point to GitHub Pages.
- Apply the same white-header + footer pattern to other subpages (`about-us/`, `news/`, `product-category-therapeutics/`, etc.).
- Replace placeholder `href="#"` links in the magazine page with real article URLs as content is published.
- Link the PDF download buttons in `company-profile-G2-English.html` to the R2 PDF URLs.
- Add a `cdn.ramopharmin.com` subdomain pointing to the R2 bucket once domain is registered.
