import fs from "node:fs";
import path from "node:path";
import * as cheerio from "cheerio";
import { ContentRecord } from "./types.js";

const read = (file: string): string => fs.readFileSync(file, "utf8");
const write = (file: string, content: string): void => fs.writeFileSync(file, content, "utf8");

const slugToHref = (record: ContentRecord): string =>
  record.type === "news" ? `../news/${record.slug}.html` : `../articles/${record.slug}.html`;

const buildFaArticleCard = (record: ContentRecord): string => `
<article class="article-card glass-panel rounded-2xl overflow-hidden hover:bg-white/5 transition-all duration-300 hover:-translate-y-2 group/card">
  <a href="../articles/${record.slug}.html" class="block no-underline text-inherit focus:outline-none focus-visible:ring-2 focus-visible:ring-[#5aaeb8] rounded-2xl">
    <div class="h-48 overflow-hidden relative"><div class="absolute inset-0 bg-gradient-to-t from-slate-900/80 to-transparent z-10 opacity-60"></div><img src="${record.imageUrl}" class="w-full h-full object-cover transition-transform duration-500 group-hover/card:scale-110" alt=""><div class="absolute bottom-3 right-3 z-20"><span class="px-3 py-1 bg-brand/90 backdrop-blur text-xs rounded-full font-bold text-white">جدید</span></div></div>
    <div class="p-6 text-right"><h3 class="text-xl font-bold text-white mb-3 leading-snug">${record.title}</h3><p class="text-sm text-slate-400 mb-4 line-clamp-3 leading-relaxed">${record.summary}</p><span class="inline-flex items-center gap-2 text-brand-light font-bold text-sm group-hover/card:text-white">بیشتر بخوانید<i data-lucide="arrow-left" class="w-4 h-4"></i></span></div>
  </a>
</article>`;

const buildEnArticleCard = (record: ContentRecord): string => `
<article class="article-card glass-panel rounded-2xl overflow-hidden hover:bg-white/5 transition-all duration-300 hover:-translate-y-2 group/card">
  <a href="../articles/${record.slug}.html" class="block no-underline text-inherit focus:outline-none focus-visible:ring-2 focus-visible:ring-[#5aaeb8] rounded-2xl">
    <div class="h-48 overflow-hidden relative"><div class="absolute inset-0 bg-gradient-to-t from-slate-900/80 to-transparent z-10 opacity-60"></div><img src="${record.imageUrl}" class="w-full h-full object-cover transition-transform duration-500 group-hover/card:scale-110" alt=""><div class="absolute bottom-3 left-3 z-20"><span class="px-3 py-1 bg-brand/90 backdrop-blur text-xs rounded-full font-bold text-white">New</span></div></div>
    <div class="p-6 text-left"><h3 class="text-xl font-bold text-white mb-3 leading-snug">${record.title}</h3><p class="text-sm text-slate-400 mb-4 line-clamp-3 leading-relaxed">${record.summary}</p><span class="inline-flex items-center gap-2 text-brand-light font-bold text-sm group-hover/card:text-white">Read more<i data-lucide="arrow-right" class="w-4 h-4"></i></span></div>
  </a>
</article>`;

const buildFaNewsCard = (record: ContentRecord): string => `
<article class="news-card glass-panel rounded-2xl p-6 relative group flex flex-col h-[320px]"><div class="card-accent-line bg-teal-500"></div><div class="flex justify-between items-start mb-4" dir="rtl"><div class="flex items-center gap-2 text-xs text-slate-400"><i data-lucide="calendar" class="w-3 h-3"></i><time>${new Date(record.createdAtIso).toLocaleDateString("fa-IR")}</time></div><span class="px-3 py-1 rounded-full text-xs font-bold bg-teal-500/20 text-teal-300 border border-teal-500/30">جدید</span></div><div class="text-right flex-grow flex flex-col" dir="rtl"><h3 class="text-xl font-bold text-white mb-3 leading-snug group-hover:text-teal-300 transition-colors">${record.title}</h3><p class="text-sm text-slate-400 leading-relaxed line-clamp-3 mb-4">${record.summary}</p><div class="mt-auto pt-4 border-t border-white/5 flex justify-between items-center"><i data-lucide="file-text" class="w-5 h-5 text-slate-600 group-hover:text-teal-400 transition-colors"></i><a href="../news/${record.slug}.html" class="text-sm font-bold text-teal-400 hover:text-white transition-colors flex items-center gap-1 no-underline">مشاهده خبر<i data-lucide="arrow-left" class="w-4 h-4"></i></a></div></div></article>`;

const prependAndCap = ($: cheerio.CheerioAPI, selector: string, html: string, cap = 5): void => {
  const container = $(selector);
  if (!container.length) return;
  container.prepend(html);
  const items = container.children();
  if (items.length > cap) {
    items.slice(cap).remove();
  }
};

const updateTickerArray = (filePath: string, text: string): void => {
  const source = read(filePath);
  const arrayMatch = source.match(/var newsItems = \[(.*?)\];/s);
  if (!arrayMatch) return;
  const itemMatches = [...arrayMatch[1].matchAll(/"([^"]*)"/g)].map((m) => m[1]);
  const unique = [text, ...itemMatches.filter((item) => item !== text)].slice(0, 5);
  const replacement = `var newsItems = [\n${unique.map((item) => `                "${item}"`).join(",\n")}\n            ];`;
  write(filePath, source.replace(/var newsItems = \[(.*?)\];/s, replacement));
};

const prependIndexItem = (indexPath: string, html: string): void => {
  const $ = cheerio.load(read(indexPath));
  const list = $(".mag-article-list").first();
  if (!list.length) return;
  list.prepend(html);
  write(indexPath, $.html());
};

const prependToIndexes = (indexes: string[], html: string): void => {
  for (const file of indexes) prependIndexItem(file, html);
};

export const updateFeeds = (repoRoot: string, record: ContentRecord): void => {
  const faHome = path.join(repoRoot, "V0/fa/index.html");
  const faHome$ = cheerio.load(read(faHome));

  if (record.type === "health_magazine_article") {
    prependAndCap(faHome$, "#art-slider", buildFaArticleCard(record), 5);
    write(faHome, faHome$.html());
    prependToIndexes(
      [
        path.join(repoRoot, "V0/fa/magazine/index.html"),
        path.join(repoRoot, "V0/fa/magazine/index-2.html")
      ],
      `<li><a class="mag-article-title" href="articles/${record.slug}.html">${record.title}</a><p class="mag-article-meta">تحریریه راموفارمین</p><p class="mag-article-excerpt">${record.summary}</p></li>`
    );
    if (record.language === "en") {
      const enHome = path.join(repoRoot, "V0/en/index.html");
      const en$ = cheerio.load(read(enHome));
      prependAndCap(en$, "#en-art-slider", buildEnArticleCard(record), 5);
      write(enHome, en$.html());
    }
  } else {
    prependAndCap(faHome$, "#news-slider", buildFaNewsCard(record), 5);
    write(faHome, faHome$.html());
    prependToIndexes(
      [
        path.join(repoRoot, "V0/news-page/news-highlights.html"),
        path.join(repoRoot, "V0/news-page/news-highlights-2.html")
      ],
      `<li class="news-index-item" data-search="${record.title} ${record.summary}"><a class="mag-article-title" href="../news/${record.slug}.html">${record.title}</a><p class="mag-article-meta">خبر جدید</p><p class="mag-article-excerpt">${record.summary}</p></li>`
    );
    const tickerText = `${record.title} — ${record.summary}`;
    updateTickerArray(path.join(repoRoot, "V0/fa/0-header.html"), tickerText);
    updateTickerArray(path.join(repoRoot, "V0/fa/0-header-with-holding.html"), tickerText);
  }
};

export const buildTocHtml = (record: ContentRecord): string => {
  const label = record.language === "fa" ? "متن کامل" : "Full text";
  return `<li><a href="#content-main" class="text-gray-600 hover:text-ramo-blue block py-1 border-r-2 border-transparent hover:border-ramo-accent pr-2">${label}</a></li>`;
};

export const buildReferencesHtml = (record: ContentRecord): string =>
  `<ol class="list-decimal list-inside text-xs text-gray-500 space-y-2"><li>${record.language === "fa" ? "متن دریافتی از مشتری، ویرایش حداقلی تحریری." : "Client-submitted copy with minimal editorial cleanup."}</li></ol>`;
