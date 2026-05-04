/**
 * One-off / repeatable: wrap fragment HTML under V0 with FA magazine-style
 * chrome (fixed dark nav + white footer). Run from repo root:
 *   node V0/scripts/wrap-fa-chrome.mjs
 */
import { readFileSync, writeFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const V0 = join(__dirname, "..");

const CHROME_CSS = `
        html { background-color: #EFF2F3; }
        body { font-family: 'Vazirmatn', 'Tahoma', 'Arial', sans-serif; background: #EFF2F3; margin: 0; color: #0f172a; }

        #ramo-fa-header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 100;
            font-family: 'Vazirmatn', 'Tahoma', sans-serif;
            direction: rtl;
            background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            overflow: visible;
        }
        #ramo-fa-header > div {
            overflow: visible;
        }
        #ramo-fa-header img[src*="english-full-logo-white"] {
            transform: scale(1.1);
            transform-origin: center center;
        }
        #ramo-fa-header .fa-nav-link {
            color: rgba(255, 255, 255, 0.72);
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            transition: color 0.2s;
        }
        #ramo-fa-header .fa-nav-link:hover { color: #fff; }
        #ramo-fa-header .fa-nav-link.fa-nav-current {
            color: #5aaeb8;
            font-weight: 600;
        }
        #ramo-fa-header .fa-lang-btn {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 600;
            text-decoration: none;
            transition: background 0.2s;
        }
        #ramo-fa-header .fa-lang-active {
            background: rgba(23, 79, 87, 0.85);
            color: #fff;
            border: 1px solid rgba(90, 174, 184, 0.45);
        }
        #ramo-fa-header .fa-lang-inactive {
            background: rgba(255, 255, 255, 0.06);
            color: rgba(255, 255, 255, 0.72);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        #ramo-fa-header .fa-lang-inactive:hover {
            background: rgba(255, 255, 255, 0.12);
            color: #fff;
        }
        #ramo-fa-header .fa-mobile-btn {
            display: none;
            background: none;
            border: none;
            cursor: pointer;
            color: #fff;
            padding: 8px;
            border-radius: 10px;
        }
        #ramo-fa-header .fa-mobile-btn:hover { background: rgba(255, 255, 255, 0.08); }
        @media (max-width: 768px) {
            #ramo-fa-header .fa-nav-links { display: none !important; }
            #ramo-fa-header .fa-mobile-btn { display: block; }
        }
        #mag-mobile-panel {
            display: none;
            position: fixed;
            top: 64px;
            left: 0;
            right: 0;
            bottom: 0;
            background: #0f172a;
            z-index: 99;
            padding: 24px;
            flex-direction: column;
            gap: 16px;
        }
        #mag-mobile-panel.is-open { display: flex; }
        #mag-mobile-panel a {
            color: rgba(255, 255, 255, 0.9);
            text-decoration: none;
            font-size: 1.1rem;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }
        #ramo-fa-header .fa-nav-dd {
            position: relative;
            /* Large hit area under the label: submenu is out-of-flow, so this padding
               keeps :hover on the parent while moving toward the panel. */
            padding-bottom: 24px;
            margin-bottom: -24px;
        }
        #ramo-fa-header .fa-nav-submenu {
            display: none;
            position: absolute;
            top: calc(100% - 14px);
            right: 0;
            margin-top: 0;
            min-width: 220px;
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            padding: 8px 0;
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.35);
            z-index: 200;
        }
        /* Invisible wedge above the panel — still inside .fa-nav-submenu, so it counts
           as hovering the dropdown while crossing any remaining pixel gap. */
        #ramo-fa-header .fa-nav-submenu::before {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            bottom: 100%;
            height: 28px;
        }
        #ramo-fa-header .fa-nav-dd:hover .fa-nav-submenu,
        #ramo-fa-header .fa-nav-dd:focus-within .fa-nav-submenu {
            display: block;
        }
        #ramo-fa-header .fa-nav-submenu a {
            display: block;
            padding: 10px 18px;
            color: rgba(255, 255, 255, 0.88);
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
        }
        #ramo-fa-header .fa-nav-submenu a:hover {
            background: rgba(255, 255, 255, 0.08);
            color: #fff;
        }
        #ramo-fa-header .fa-nav-submenu a.fa-nav-current {
            color: #5aaeb8;
            background: rgba(90, 174, 184, 0.12);
        }
        main.ramo-page-main {
            background-color: #EFF2F3;
            min-height: calc(100vh - 64px);
        }
`;

function footerBlock(p) {
  return `<style>#ramo-news-footer a{color:#0f172a!important}#ramo-news-footer a:hover{color:#0d9488!important}</style>
<footer id="ramo-news-footer" class="border-t border-slate-300 bg-[#EFF2F3] pt-16 pb-8 mt-12" dir="rtl" style="border-top:1px solid #cbd5e1;">
    <div class="container mx-auto px-6">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 mb-12 border-b border-slate-200 pb-12">
            <div class="lg:col-span-5 text-right space-y-6">
                <div class="text-slate-900 font-bold text-xl">داروسازی راموفارمین</div>
                <p class="text-slate-600 leading-loose text-sm lg:text-base max-w-md text-right">
                    شرکت داروسازی راموفارمین به عنوان یکی از پیشگامان صنعت دارو در ایران، با بهره‌گیری از دانش روز، فناوری‌های نوین و استانداردهای بین‌المللی، در تولید و توزیع داروهای با کیفیت و موثر فعالیت می‌کند. ماموریت ما ارتقای سلامت و کیفیت زندگی جامعه است.
                </p>
                <div class="text-xs text-slate-400 flex flex-col gap-1">
                    <span>کد مستند: RM-12-2025</span>
                    <span>بازبینی: دسامبر 2025</span>
                </div>
            </div>
            <div class="lg:col-span-4 text-right">
                <h3 class="text-lg font-bold text-slate-900 mb-6 flex items-center justify-start gap-2">
                    <span class="w-1.5 h-6 bg-teal-500 rounded-full"></span>
                    منابع
                </h3>
                <ul class="space-y-3 text-sm text-slate-900">
                    <li><a href="#" class="hover:text-teal-600 transition-colors block hover:translate-x-1 transition-transform duration-300">نوآوری علمی</a></li>
                    <li><a href="#" class="hover:text-teal-600 transition-colors block hover:translate-x-1 transition-transform duration-300">پژوهش‌های اسپانسرشده</a></li>
                    <li><a href="#" class="hover:text-teal-600 transition-colors block hover:translate-x-1 transition-transform duration-300">اطلاعات پزشکی برای پزشکان</a></li>
                    <li><a href="#" class="hover:text-teal-600 transition-colors block hover:translate-x-1 transition-transform duration-300">برنامه‌های حمایت دارویی</a></li>
                    <li><a href="#" class="hover:text-teal-600 transition-colors block hover:translate-x-1 transition-transform duration-300">آزمایش‌های بالینی جهانی</a></li>
                    <li><a href="#" class="hover:text-teal-600 transition-colors block hover:translate-x-1 transition-transform duration-300">محصولات دارویی</a></li>
                    <li><a href="#" class="hover:text-teal-600 transition-colors block hover:translate-x-1 transition-transform duration-300">گزارش عارضه جانبی</a></li>
                </ul>
            </div>
            <div class="lg:col-span-3 text-right">
                <h3 class="text-lg font-bold text-slate-900 mb-6 flex items-center justify-start gap-2">
                    <span class="w-1.5 h-6 bg-teal-500 rounded-full"></span>
                    لینک‌های سریع
                </h3>
                <ul class="space-y-3 text-sm text-slate-900 mb-8">
                    <li><a href="${p.faHome}" class="hover:text-teal-600 transition-colors block hover:translate-x-1 transition-transform duration-300">خانه فارسی</a></li>
                    <li><a href="${p.contact}" class="hover:text-teal-600 transition-colors block hover:translate-x-1 transition-transform duration-300">ارتباط با ما</a></li>
                    <li><a href="${p.magazine}" class="hover:text-teal-600 transition-colors block hover:translate-x-1 transition-transform duration-300">مجله سلامت</a></li>
                    <li><a href="${p.en}" class="hover:text-teal-600 transition-colors block hover:translate-x-1 transition-transform duration-300">English site</a></li>
                    <li><a href="#" class="hover:text-teal-600 transition-colors block hover:translate-x-1 transition-transform duration-300">پایداری و محیط زیست</a></li>
                    <li><a href="#" class="hover:text-teal-600 transition-colors block hover:translate-x-1 transition-transform duration-300">سوالات متداول</a></li>
                </ul>
                <div class="flex justify-start gap-3">
                    <a href="#" class="w-10 h-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center text-slate-900 hover:bg-teal-50 hover:text-teal-600 hover:border-teal-200 transition-all shadow-sm hover:-translate-y-1" aria-label="LinkedIn">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/></svg>
                    </a>
                    <a href="#" class="w-10 h-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center text-slate-900 hover:bg-teal-50 hover:text-teal-600 hover:border-teal-200 transition-all shadow-sm hover:-translate-y-1" aria-label="Instagram">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/></svg>
                    </a>
                    <a href="#" class="w-10 h-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center text-slate-900 hover:bg-teal-50 hover:text-teal-600 hover:border-teal-200 transition-all shadow-sm hover:-translate-y-1" aria-label="Twitter">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z"/></svg>
                    </a>
                </div>
            </div>
        </div>
        <div class="flex flex-col-reverse md:flex-row items-center justify-between gap-6 text-xs text-slate-500">
            <div class="dir-ltr">© 2025 Ramopharmin. All rights reserved.</div>
            <div class="flex gap-6">
                <a href="#" class="hover:text-teal-600 transition-colors">حریم خصوصی</a>
                <a href="#" class="hover:text-teal-600 transition-colors">شرایط استفاده</a>
            </div>
        </div>
    </div>
</footer>
`;
}

function navBlock(p, current) {
  const cHome = current === "home" ? " fa-nav-current" : "";
  const cAboutHistory = current === "about" ? " fa-nav-current" : "";
  const cBoard = current === "about-board" ? " fa-nav-current" : "";
  const cManagers = current === "about-managers" ? " fa-nav-current" : "";
  const cProd = current === "products" ? " fa-nav-current" : "";
  const cMag = current === "magazine" ? " fa-nav-current" : "";
  const cNews = current === "news" ? " fa-nav-current" : "";
  return `<!-- HEADER (same chrome as health magazine) -->
<nav id="ramo-fa-header">
    <div style="max-width:1200px;margin:0 auto;padding:0 24px;height:64px;display:flex;align-items:center;justify-content:space-between;">
        <a href="${p.faHome}" style="text-decoration:none;display:flex;align-items:center;">
            <img src="${p.logo}" alt="Ramopharmin" style="height:64px;width:auto;display:block;">
        </a>
        <div class="fa-nav-links" style="display:flex;align-items:center;gap:28px;">
            <a href="${p.faHome}" class="fa-nav-link${cHome}">خانه</a>
            <div class="fa-nav-dd">
                <a href="${p.aboutBoard}" class="fa-nav-link${cAboutHistory}">درباره ما</a>
                <div class="fa-nav-submenu" role="menu">
                    <a href="${p.aboutBoard}" class="fa-nav-submenu-link${cBoard}" role="menuitem">هیئت مدیره</a>
                    <a href="${p.aboutManagers}" class="fa-nav-submenu-link${cManagers}" role="menuitem">مدیران ارشد</a>
                </div>
            </div>
            <a href="${p.productsHub}" class="fa-nav-link${cProd}">محصولات</a>
            <a href="${p.magazine}" class="fa-nav-link${cMag}">مجله سلامت</a>
            <a href="${p.news}" class="fa-nav-link${cNews}">اخبار</a>
        </div>
        <div style="display:flex;align-items:center;gap:10px;">
            <button type="button" class="fa-mobile-btn" id="mag-mobile-open" aria-label="باز کردن فهرست">
                <i data-lucide="menu" class="w-7 h-7"></i>
            </button>
            <a href="${p.en}" class="fa-lang-btn fa-lang-inactive">EN</a>
            <span class="fa-lang-btn fa-lang-active">FA</span>
        </div>
    </div>
</nav>
<div style="height:64px;"></div>

<div id="mag-mobile-panel" aria-hidden="true">
    <a href="${p.faHome}">خانه</a>
    <a href="${p.aboutBoard}">هیئت مدیره</a>
    <a href="${p.aboutManagers}">مدیران ارشد</a>
    <a href="${p.productsHub}">محصولات</a>
    <a href="${p.magazine}">مجله سلامت</a>
    <a href="${p.news}">اخبار</a>
    <a href="${p.en}">English</a>
</div>
`;
}

const TAIL = `<script>
document.addEventListener('DOMContentLoaded', function() {
    if (typeof lucide !== 'undefined') lucide.createIcons();
});
(function() {
    var btn = document.getElementById('mag-mobile-open');
    var panel = document.getElementById('mag-mobile-panel');
    if (!btn || !panel) return;
    var open = false;
    btn.addEventListener('click', function() {
        open = !open;
        panel.classList.toggle('is-open', open);
        panel.setAttribute('aria-hidden', open ? 'false' : 'true');
        btn.innerHTML = open ? '<i data-lucide="x" class="w-7 h-7"></i>' : '<i data-lucide="menu" class="w-7 h-7"></i>';
        if (typeof lucide !== 'undefined') lucide.createIcons();
    });
    panel.querySelectorAll('a').forEach(function(a) {
        a.addEventListener('click', function() {
            open = false;
            panel.classList.remove('is-open');
            panel.setAttribute('aria-hidden', 'true');
            btn.innerHTML = '<i data-lucide="menu" class="w-7 h-7"></i>';
            if (typeof lucide !== 'undefined') lucide.createIcons();
        });
    });
})();
</script>
</body>
</html>
`;

const pathsTher = {
  logo: "../logos/english-full-logo-white.png",
  faHome: "../fa/",
  aboutBoard: "../about-us/board-members.html",
  aboutManagers: "../about-us/managers.html",
  productsHub: "category-page.html",
  magazine: "../fa/magazine/",
  news: "../news-page/news-highlights.html",
  en: "../en/index.html",
  contact: "../contact-us/contact-us.html",
};

const pathsAbout = {
  logo: "../logos/english-full-logo-white.png",
  faHome: "../fa/",
  aboutBoard: "../about-us/board-members.html",
  aboutManagers: "../about-us/managers.html",
  productsHub: "../product-category-therapeutics/category-page.html",
  magazine: "../fa/magazine/",
  news: "../news-page/news-highlights.html",
  en: "../en/index.html",
  contact: "../contact-us/contact-us.html",
};

function wrapFragment(body, title, currentNav, pathObj) {
  const head = `<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title}</title>
    <meta name="description" content="داروسازی راموفارمین">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
      tailwind.config = { corePlugins: { preflight: false } }
    </script>
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>${CHROME_CSS}
    </style>
</head>
<body>
${navBlock(pathObj, currentNav)}
`;
  return (
    head +
    "<main class=\"ramo-page-main\">\n" +
    body.trim() +
    "\n</main>\n" +
    footerBlock(pathObj) +
    "\n" +
    TAIL
  );
}

function alreadyWrapped(s) {
  return /<!DOCTYPE html>/i.test(s) && /id="ramo-fa-header"/.test(s);
}

const jobs = [
  ...[
    "product-category-therapeutics/category-page.html",
    "product-category-therapeutics/anti-diabetes.html",
    "product-category-therapeutics/anti-migraine.html",
    "product-category-therapeutics/anti-parkinson.html",
    "product-category-therapeutics/antispasmodics-urinary.html",
    "product-category-therapeutics/cns-drugs.html",
    "product-category-therapeutics/cold-respiratory.html",
    "product-category-therapeutics/gastrointestinal.html",
  ].map((rel) => ({
    rel,
    title: rel.endsWith("category-page.html")
      ? "گروه‌های درمانی | راموفارمین"
      : "محصولات | راموفارمین",
    current: "products",
    paths: pathsTher,
  })),
  ...[
    ["about-us/board-members.html", "هیئت مدیره | راموفارمین", "about-board"],
    ["about-us/managers.html", "مدیران ارشد | راموفارمین", "about-managers"],
    ["about-us/history.html", "درباره ما | راموفارمین", "about"],
  ].map(([rel, title, navCurrent]) => ({
    rel,
    title,
    current: navCurrent,
    paths: pathsAbout,
  })),
];

for (const job of jobs) {
  const fp = join(V0, job.rel);
  let raw = readFileSync(fp, "utf8");
  if (alreadyWrapped(raw)) {
    console.log("skip (already wrapped):", job.rel);
    continue;
  }
  raw = wrapFragment(raw, job.title, job.current, job.paths);
  writeFileSync(fp, raw, "utf8");
  console.log("wrapped:", job.rel);
}
