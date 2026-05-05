import fs from "node:fs";
import path from "node:path";
import { ContentRecord } from "./types.js";

interface RenderContext {
  record: ContentRecord;
  canonicalUrl: string;
  tocItemsHtml: string;
  referencesHtml: string;
}

const replaceTokens = (template: string, tokens: Record<string, string>): string => {
  let out = template;
  for (const [key, value] of Object.entries(tokens)) {
    out = out.replaceAll(`{{${key}}}`, value);
  }
  return out;
};

export const renderFromTemplate = (repoRoot: string, kind: "article" | "news", ctx: RenderContext): string => {
  const file = path.join(repoRoot, "templates", `${kind}-template.html`);
  const template = fs.readFileSync(file, "utf8");
  const { record } = ctx;
  const isFa = record.language === "fa";
  return replaceTokens(template, {
    lang: record.language,
    dir: isFa ? "rtl" : "ltr",
    title: record.title,
    description: record.summary,
    keywords: `${record.type},ramopharmin`,
    author_name: "Ramopharmin Editorial",
    canonical_url: ctx.canonicalUrl,
    home_url: isFa ? "../fa/index.html" : "../en/index.html",
    site_label: isFa ? "مجله سلامت راموفارمین" : "Ramopharmin Journal",
    nav_home: isFa ? "خانه" : "Home",
    nav_about: isFa ? "درباره ما" : "About",
    nav_products: isFa ? "محصولات" : "Products",
    nav_magazine: isFa ? "مجله سلامت" : "Magazine",
    about_url: "../about-us/history.html",
    products_url: "../product-category-therapeutics/category-page.html",
    magazine_url: "../fa/magazine/",
    download_pdf_label: isFa ? "دانلود PDF" : "Print / PDF",
    toc_title: isFa ? "فهرست مطالب" : "Contents",
    toc_items_html: ctx.tocItemsHtml,
    kicker: record.type === "news" ? (isFa ? "اخبار" : "News") : (isFa ? "مقاله سلامت" : "Health article"),
    abstract: record.summary,
    author_label: isFa ? "نویسنده" : "Author",
    updated_label: isFa ? "آخرین بروزرسانی" : "Updated",
    updated_at: new Date(record.createdAtIso).toISOString().slice(0, 10),
    reading_time_label: isFa ? "زمان مطالعه" : "Reading time",
    reading_time: isFa ? "5 دقیقه" : "5 min",
    hero_image_url: record.imageUrl,
    hero_image_alt: record.imageAlt,
    hero_image_caption: record.imageCaption,
    article_body_html: record.bodyHtml,
    references_title: isFa ? "منابع" : "References",
    references_html: ctx.referencesHtml,
    about_author_title: isFa ? "درباره نویسنده" : "About author",
    about_author_text: isFa ? "محتوا پس از دریافت از مشتری با حداقل ویرایش منتشر شده است." : "Content is client-provided and minimally edited for consistency.",
    date_modified: record.createdAtIso
  });
};
