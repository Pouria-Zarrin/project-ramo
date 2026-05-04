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

1. In your DNS (registrar or Cloudflare), add records per [GitHub’s custom-domain documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site). The docs list the current **A**, **AAAA**, and **CNAME** values (they can change; always use GitHub’s page as source of truth).
2. In `V0/`, add a file named `CNAME` whose **only line** is your hostname, e.g. `www.example.com` (no `https://`, no path). You can start from [`V0/CNAME.example`](V0/CNAME.example).
3. Push the `CNAME` file, wait for DNS propagation, then in **Settings → Pages** enable **Enforce HTTPS** once the certificate is issued.

## Registering the domain

GitHub does not sell domains. Use any registrar (e.g. Cloudflare Registrar, Namecheap, Porkbun), then point DNS to GitHub as above.

## Local preview

From the repo root, serve `V0` with any static server, for example:

```bash
npx --yes serve V0
```

Open the printed URL and test `/`, `/en/`, `/fa/`, and `/fa/magazine/`.
