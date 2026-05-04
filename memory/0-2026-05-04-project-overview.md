# 0 — Project overview & progress log
**Date:** 2026-05-04  
**Project:** Ramopharmin static website

---

## What this project is

A fully static (plain HTML + inline CSS) corporate website for **Ramopharmin**, an Iranian pharmaceutical company. No build tool, no framework — every page is a self-contained HTML file that links to CDN-hosted libraries (Tailwind CSS, Lucide icons, Three.js, Vazirmatn font).

The site is bilingual:
- **English** — corporate home page with a 3-D globe export-network visualisation, product categories, mission statement, news, and articles.
- **Farsi / فارسی (RTL)** — same sections as individual fragment files; served through a hub index.
- **Health magazine (مجله سلامت)** — a standalone Farsi magazine landing page (`salamt-redesigned`).

---

## Repository layout (after cleanup — 2026-05-04)

```
project-ramo/
├── .github/
│   └── workflows/
│       └── deploy-pages.yml   ← GitHub Actions: publishes V0/ to GitHub Pages on push
├── .gitignore                 ← Ignores node_modules, .DS_Store, logs
├── DEPLOY.md                  ← Step-by-step deploy + DNS notes
├── memory/
│   └── 0-2026-05-04-project-overview.md  ← this file
└── V0/                        ← PUBLISH ROOT (125 files, GitHub Pages serves this)
    ├── index.html             ← Language / site chooser (EN / FA / Magazine)
    ├── en/
    │   └── index.html         ← English corporate home (V3 combined page)
    ├── fa/
    │   ├── index.html         ← Farsi hub linking all section fragments
    │   ├── magazine/
    │   │   └── index.html     ← Salamt health magazine (RTL)
    │   └── [section fragments — 0-header.html … 8-footer.html]
    ├── about-us/
    ├── articles/
    ├── company-images/
    ├── company-news/
    ├── company-profile/
    ├── contact-us/
    ├── logos/
    ├── news/
    ├── news-page/
    ├── product-category-therapeutics/
    └── product-images/
```

---

## Completed work

| # | Task | Status |
|---|------|--------|
| 1 | Audit all files and folders | ✅ Done |
| 2 | Rename ` company-images` (leading-space bug) → `company-images` | ✅ Done |
| 3 | Fix broken image paths in `company-profile-G2-English.html` | ✅ Done |
| 4 | Create `V0/` publish tree: root chooser, `/en/`, `/fa/`, `/fa/magazine/` | ✅ Done |
| 5 | Wire Three.js globe textures to threejs.org CDN (were missing locally) | ✅ Done |
| 6 | Add `.gitignore` | ✅ Done |
| 7 | Add GitHub Actions workflow `deploy-pages.yml` | ✅ Done |
| 8 | Write `DEPLOY.md` (DNS + HTTPS instructions) | ✅ Done |
| 9 | Delete all legacy / duplicate source files from repo root | ✅ Done |

---

## Next steps

| # | Task | Status |
|---|------|--------|
| 10 | `git init` + push to new GitHub repository | ⏳ Pending |
| 11 | Register a domain name | ⏳ Pending |
| 12 | Set GitHub Pages → Source: GitHub Actions in repo settings | ⏳ Pending |
| 13 | Add `V0/CNAME` with chosen domain; push | ⏳ Pending |
| 14 | Set DNS records at registrar; enable HTTPS in Pages settings | ⏳ Pending |

---

## Key technical notes

- **All CSS is inline** (no external `.css` files); no build step needed.
- **CDN dependencies** (loaded at runtime): Tailwind CSS, Lucide, Three.js, Vazirmatn font, Font Awesome.
- **Globe textures** now point to stable `threejs.org/examples/textures/planets/` URLs.
- `node_modules/` and `export-pdf.js` (Puppeteer PDF helper) have been removed from the deployable tree — they were dev-only.
- `memory/` and `DEPLOY.md` are at repo root (not inside `V0/`) so they are never served publicly.
