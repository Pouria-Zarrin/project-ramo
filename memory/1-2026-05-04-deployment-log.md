# 1 — Deployment log
**Date:** 2026-05-04  
**Session:** GitHub repository creation + GitHub Pages deployment

---

## What was done in this session

### 1. Git initialisation
- Ran `git init` in `/Users/pouriazarrin/project-ramo`.
- Made initial commit of 129 files (all `V0/` content, `.github/`, `.gitignore`, `DEPLOY.md`, `memory/`).
- Renamed default branch from `master` → `main`.

### 2. GitHub repository
- Created public repo via GitHub CLI (`gh`): **[github.com/Pouria-Zarrin/project-ramo](https://github.com/Pouria-Zarrin/project-ramo)**
- GitHub account in use: **Pouria-Zarrin** (already authenticated via `gh auth`, keyring token with `repo` + `workflow` scopes).

### 3. Oversized file problem — resolved
Two company-profile PDFs exceeded GitHub's 100 MB hard limit:

| File | Size |
|------|------|
| `V0/company-profile/company-profile-G2-English.pdf` | 188 MB |
| `V0/company-profile/company-profile-v1.pdf` | 180 MB |

**Fix applied:**
- Used `git-filter-repo` to surgically remove both files from all commits (rewriting history).
- Added both paths to `.gitignore` so they can never be committed again.
- Force-pushed the clean history to GitHub.
- Files still exist on local disk only.

### 4. GitHub Pages enabled
- Enabled Pages via GitHub API: source set to **GitHub Actions** (not branch-based).
- Workflow file: `.github/workflows/deploy-pages.yml` — publishes `V0/` on every push to `main`.
- Pages URL confirmed: **[https://pouria-zarrin.github.io/project-ramo/](https://pouria-zarrin.github.io/project-ramo/)**

### 5. First successful deploy
- Deploy workflow completed in **28 seconds**, all steps green.
- Node.js 24 opt-in env var added to workflow to suppress upcoming deprecation warnings.

---

## Live URLs

| Page | URL |
|------|-----|
| Root (language chooser) | https://pouria-zarrin.github.io/project-ramo/ |
| English corporate home | https://pouria-zarrin.github.io/project-ramo/en/ |
| Farsi hub | https://pouria-zarrin.github.io/project-ramo/fa/ |
| Health magazine (مجله سلامت) | https://pouria-zarrin.github.io/project-ramo/fa/magazine/ |

---

## Current git state

| Item | Detail |
|------|--------|
| Remote | `https://github.com/Pouria-Zarrin/project-ramo.git` |
| Branch | `main` |
| Commits | 4 (initial → PDF removal → trigger commit → Node 24 fix) |
| Working tree | Clean (no uncommitted changes) |

---

## Next steps

| # | Task |
|---|------|
| 1 | Register a domain name (recommended: Cloudflare Registrar — check `ramopharmin.com` / `ramopharmin.org`) |
| 2 | Create `V0/CNAME` with the chosen hostname (e.g. `www.ramopharmin.com`) and push |
| 3 | Set DNS A/AAAA and CNAME records at registrar per [GitHub's custom domain docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site) |
| 4 | Enable **Enforce HTTPS** in repo Settings → Pages once certificate is issued |
| 5 | Optionally host the two large PDFs on Google Drive / Dropbox and link from the company profile page |
