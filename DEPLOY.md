# Deploy Ramopharmin static site (V0) to GitHub Pages

The public site files live in the [`V0/`](V0/) folder. GitHub Actions uploads that folder as the Pages artifact.

## One-time: GitHub repository

1. Create a new repository on GitHub and push this project (including `.github/workflows/deploy-pages.yml` and `V0/`).
2. In the repository: **Settings → Pages → Build and deployment**
   - Source: **GitHub Actions** (not “Deploy from a branch” for this workflow).

## First deploy

1. Push to `main` (or `master`; both are configured in the workflow).
2. Open **Actions** and confirm the “Deploy to GitHub Pages” workflow succeeds.
3. The site URL will be:
   - **Project site:** `https://<user-or-org>.github.io/<repo>/`
   - **User/org site:** only if the repo is named `<user>.github.io` (special case).

GitHub shows the exact Pages URL under **Settings → Pages** after the first successful deployment.

## Custom domain and HTTPS

This repo deploys with **GitHub Actions** (`upload-pages-artifact` from `V0/`). The live hostname is set in the repo’s **Pages** settings (or API), not via a `CNAME` file in the artifact (GitHub does not require that file for workflow-based Pages).

Always confirm current IP targets in [GitHub’s custom-domain documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).

### ramopharmin.net (GoDaddy → GitHub Pages)

**Primary hostname in GitHub:** `www.ramopharmin.net` (points at this project’s Pages site; paths are the same as on `github.io` but without `/project-ramo/`, e.g. `/fa/`, `/en/`).

In **GoDaddy → My Products → ramopharmin.net → DNS**:

1. **www** — add a **CNAME** record:
   - **Name / Host:** `www`
   - **Points to / Value:** `pouria-zarrin.github.io`
   - Remove or replace any existing `www` parking / forwarding that conflicts.

2. **Apex (optional)** — if you want `https://ramopharmin.net` (no `www`) to work as well, add GitHub’s **A** and **AAAA** records on **`@`** as listed in GitHub’s docs (four IPv4 and four IPv6 addresses). GitHub Pages will redirect apex ↔ `www` once both names resolve correctly.

3. Wait for DNS (often minutes, sometimes up to 24–48 hours). In GitHub: **Settings → Pages**, confirm the domain check passes, then turn on **Enforce HTTPS** when it becomes available.

If you change the hostname later, update the repo **Pages → Custom domain** to match DNS.

## Registering the domain

GitHub does not sell domains. Use any registrar (e.g. Cloudflare Registrar, Namecheap, Porkbun), then point DNS to GitHub as above.

## Local preview

From the repo root, serve `V0` with any static server, for example:

```bash
npx --yes serve V0
```

Open the printed URL and test `/`, `/en/`, `/fa/`, and `/fa/magazine/`.
