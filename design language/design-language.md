# Ramopharmin Design Language

## 1) Design language overview

Ramopharmin website uses a pharma-corporate visual system with:

- **Trust-first tone**: deep navy and teal palette, high-contrast text, restrained decoration.
- **Clean information hierarchy**: bold section titles, readable body text, generous spacing.
- **Bilingual support**: Persian-first RTL pages (`fa`) plus English pages (`en`).
- **Static HTML composition**: reusable header/footer blocks and page templates replicated across sections.

Typography and UI stack in current pages:

- **Primary Persian font**: `Vazirmatn`
- **Utility framework**: `Tailwind CSS` (CDN setup in many pages/components)
- **Icon systems**: `Lucide` and `Font Awesome` depending on template/page

---

## 2) Website relative map

Top-level website root is `V0/`.

### Core sections

- `V0/index.html` — language chooser / root landing
- `V0/fa/` — Persian primary experience (home + shared chrome fragments)
- `V0/en/` — English home and sections
- `V0/about-us/` — history, board members, managers
- `V0/product-category-therapeutics/` — product/category pages
- `V0/news-page/` — news listing/highlights pages
- `V0/news/` — article-level news pages and templates
- `V0/articles/` — long-form and news/feature/scientific templates
- `V0/contact-us/` — contact page(s)
- `V0/fa/magazine/` — health magazine listing pages
- `V0/company-news/` — alternate/company-news header/footer/news cards
- `V0/assets/`, `V0/logos/`, `V0/company-images/`, `V0/product-images/` — static assets
- `V0/scripts/` — generation/wrapping scripts for shared structures

### Shared chrome fragments (important)

- `V0/fa/0-header.html`
- `V0/fa/0-white-header.html`
- `V0/fa/0-header-with-holding.html`
- `V0/fa/0-white-header-with-holding.html`
- `V0/fa/8-footer.html`
- `V0/fa/8.1-white-version-footer.html`
- `V0/company-news/header.html`
- `V0/company-news/footer.html`

### Article/news templates

- `V0/articles/news-article-template.html`
- `V0/articles/feature-article-template.html`
- `V0/articles/scientific-article-template.html`
- `V0/news/news-article-template.html`

---

## 3) Color system (current implementation)

The palette is already present in multiple pages/components. Core tokens and frequent usage:

### Primary brand colors

- `#0f172a` — deep navy (header backgrounds, strong text)
- `#174f57` / `#195057` — brand teal-blue (buttons, accents, headings)
- `#5aaeb8` — light teal accent (active/hover/underline emphasis)

### Supporting neutrals

- `#EFF2F3` — light gray page background
- `#ffffff` — cards/surfaces on light layout
- `#e2e8f0` / `#cbd5e1` — borders/dividers
- `#334155`, `#475569`, `#64748b`, `#94a3b8` — body/meta text scale

### Accent/utility colors in current pages

- `#0d9488`, `#2dd4bf` — hover/interactive teal accents
- `#fbbf24` — emphasized "news" highlight in dark header variant

### Recommended token naming for consistency

- `--ramo-bg-dark: #0f172a`
- `--ramo-primary: #174f57`
- `--ramo-primary-alt: #195057`
- `--ramo-accent: #5aaeb8`
- `--ramo-bg-light: #EFF2F3`
- `--ramo-text-title: #0f172a`
- `--ramo-text-body: #334155`
- `--ramo-border: #cbd5e1`

---

## 4) Header and footer language

### Header behavior

Current common header patterns include:

- **Top ticker strip** on dark theme variants
- **RTL navigation** with dropdowns:
  - Home
  - About (History as parent)
  - Board Members / Managers as submenu
  - Products
  - Health Magazine
  - News
  - Contact
- **Language toggle** (`FA` / `EN`)
- **Desktop + mobile menu parity** (mobile accordions/submenus)

Design characteristics:

- Dark shell (`#0f172a`) with white/soft-white typography
- Teal hover/active underlines and bullets
- Rounded dropdown containers with soft transparency/blur on dark variants

### Footer behavior

Two major footer styles currently coexist:

1. **Dark gradient footer** (`8-footer.html`)
   - Radial/mesh background
   - White and slate text
   - Teal hover accents
2. **Light footer** (`8.1-white-version-footer.html` and magazine/article pages)
   - `#EFF2F3` background
   - Dark text with teal hover accents

Common footer content structure:

- Brand/about paragraph
- Resource links
- Quick links
- Social links/icons
- Bottom legal row (copyright/privacy/terms)

---

## 5) Templates for news and articles

### News template pattern

Primary files:

- `V0/articles/news-article-template.html`
- `V0/news/news-article-template.html`

Structure pattern:

- Sticky/fixed top nav
- 3-column article layout (desktop):
  - right: table of contents / metadata
  - center: article body
  - left: author/related/company card
- Mobile slide-out menu
- Footer block at page bottom
- JSON-LD Article metadata in-page

### Article template pattern

Primary files:

- `V0/articles/feature-article-template.html`
- `V0/articles/scientific-article-template.html`

Recommended usage split:

- **News template**: announcements, press coverage, corporate updates
- **Feature template**: public education, narrative editorial, broad audience pieces
- **Scientific template**: evidence-heavy medical/scientific content with stronger references structure

### Content block standards (recommended)

Each article/news page should include:

- Kicker/category label
- H1 title
- Short lead paragraph
- Author/source + update date + reading time
- Feature image + caption
- Sectioned H2/H3 body
- Optional TOC and share actions
- References section for medical/scientific claims
- Structured metadata (`schema.org/Article`)

---

## 6) Consistency checklist (implementation)

- Use shared header/footer fragments instead of one-off nav/footer rewrites.
- Keep about-menu routing aligned: main About -> `about-us/history.html`; submenu -> board/managers.
- Keep `www.ramopharmin.net` as canonical domain in structured data and any hardcoded absolute URLs.
- Prefer the defined color tokens instead of introducing new close variants.
- Maintain RTL spacing/typography rhythm in Persian pages and preserve EN parity where applicable.
