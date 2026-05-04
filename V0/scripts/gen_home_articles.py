#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build FA + EN magazine article HTML from scientific-article-template shell."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "articles" / "scientific-article-template.html"
text = TEMPLATE.read_text(encoding="utf-8")
start = text.index('<article class="lg:col-span-6')
end = text.index("</article>", start) + len("</article>")
prefix = text[:start]
suffix = text[end:]


def toc_fa(items):
    return "\n                        ".join(
        f'<li><a href="#{hid}" class="text-gray-600 hover:text-ramo-blue block py-1 border-r-2 border-transparent hover:border-ramo-accent pr-2">{label}</a></li>'
        for hid, label in items
    )


def toc_en(items):
    return "\n                        ".join(
        f'<li><a href="#{hid}" class="text-gray-600 hover:text-ramo-blue block py-1 border-l-2 border-transparent hover:border-ramo-accent pl-2">{label}</a></li>'
        for hid, label in items
    )


def replace_sidebar_toc(out, toc_html, title_sidebar="فهرست مطالب"):
    marker = f'<h3 class="font-bold text-gray-900 mb-3 text-sm border-b pb-2">{title_sidebar}</h3>'
    i = out.index(marker)
    ul_start = out.index('<ul class="space-y-2 text-sm toc-scrollbar', i)
    ul_end = out.index("</ul>", ul_start) + len("</ul>")
    ul_tag = '<ul class="space-y-2 text-sm toc-scrollbar max-h-[60vh] overflow-y-auto pl-2">'
    return out[:ul_start] + ul_tag + "\n                        " + toc_html + "\n                    </ul>" + out[ul_end:]


def replace_sidebar_abstract(out, title, abstract, summary_href):
    old = """<h4 class="text-xs font-bold text-ramo-blue uppercase mb-2">عنوان مقاله</h4>
                    <h5 class="text-sm font-extrabold text-text-header leading-tight mb-3">
                        آنفلوآنزا؛ پیشگیری با واکسیناسیون، درمان و راهنمای جامع
                    </h5>
                    <div class="text-xs text-gray-600 leading-relaxed mb-3">
                        <p class="text-justify">
                            این مقاله راهنمای جامعی برای عموم درباره انتقال، پیشگیری، واکسن‌ها و درمان آنفلوآنزا فراهم می‌کند تا خوانندگان تصمیم‌های عملی و آگاهانه بگیرند.
                        </p>
                    </div>
                    <a href="#sec-summary" class="text-xs bg-ramo-blue text-white px-3 py-2 rounded inline-block hover:bg-ramo-dark transition-colors">مشاهده جمع‌بندی</a>"""
    new = f"""<h4 class="text-xs font-bold text-ramo-blue uppercase mb-2">عنوان مقاله</h4>
                    <h5 class="text-sm font-extrabold text-text-header leading-tight mb-3">
                        {title}
                    </h5>
                    <div class="text-xs text-gray-600 leading-relaxed mb-3">
                        <p class="text-justify">{abstract}</p>
                    </div>
                    <a href="#{summary_href}" class="text-xs bg-ramo-blue text-white px-3 py-2 rounded inline-block hover:bg-ramo-dark transition-colors">مشاهده جمع‌بندی</a>"""
    if old not in out:
        old_en = old.replace("عنوان مقاله", "Article").replace("مشاهده جمع‌بندی", "Summary")
        new_en = new.replace("عنوان مقاله", "Article").replace("مشاهده جمع‌بندی", "Summary")
        if old_en in out:
            return out.replace(old_en, new_en)
        return out
    return out.replace(old, new)


def build_article_inner(header_block, figure_html, body_html, refs_html, json_ld):
    return f"""{header_block}
            <div class="mb-6 hidden sm:flex items-center gap-3">
                <div class="flex gap-2">
                    <a href="#" class="text-xs bg-white border border-gray-200 px-3 py-2 rounded inline-flex items-center gap-2"> <i class="fa-brands fa-linkedin"></i> اشتراک در LinkedIn</a>
                    <a href="#" class="text-xs bg-white border border-gray-200 px-3 py-2 rounded inline-flex items-center gap-2"> <i class="fa-solid fa-link"></i> کپی لینک</a>
                </div>
                <div class="flex-1 text-right text-xs text-gray-500">دانلود نسخه PDF: <a href="#" onclick="window.print(); return false;" class="text-ramo-blue hover:underline" aria-label="چاپ یا ذخیره به‌عنوان PDF">دانلود</a></div>
            </div>
            {figure_html}
            <div class="a-article">
            {body_html}
            </div>
            {refs_html}
            <script type="application/ld+json">
            {json_ld}
            </script>"""


def build_article_inner_en(header_block, figure_html, body_html, refs_html, json_ld):
    return f"""{header_block}
            <div class="mb-6 hidden sm:flex items-center gap-3 flex-row">
                <div class="flex gap-2">
                    <a href="#" class="text-xs bg-white border border-gray-200 px-3 py-2 rounded inline-flex items-center gap-2"> <i class="fa-brands fa-linkedin"></i> Share</a>
                    <a href="#" class="text-xs bg-white border border-gray-200 px-3 py-2 rounded inline-flex items-center gap-2"> <i class="fa-solid fa-link"></i> Copy link</a>
                </div>
                <div class="flex-1 text-left text-xs text-gray-500">PDF: <a href="#" onclick="window.print(); return false;" class="text-ramo-blue hover:underline">Print / save</a></div>
            </div>
            {figure_html}
            <div class="a-article text-left">
            {body_html}
            </div>
            {refs_html}
            <script type="application/ld+json">
            {json_ld}
            </script>"""


def fa_header(title, abstract):
    return f"""<header class="mb-6">
                <div class="text-xs font-bold text-clinical-teal mb-2">مقاله علمی</div>
                <h1 class="text-2xl md:text-3xl font-extrabold text-text-header leading-tight mb-3">{title}</h1>
                <p class="text-sm text-gray-600 mb-3">{abstract}</p>
                <div class="flex flex-wrap gap-4 text-xs text-gray-400">
                    <span>نویسنده: واحد تحریریه راموفارمین</span>
                    <span class="dot">•</span>
                    <span>آخرین بروزرسانی: ۸ آبان ۱۴۰۴</span>
                    <span class="dot">•</span>
                    <span>زمان مطالعه: ۱۲ دقیقه</span>
                </div>
            </header>"""


def en_header(title, abstract):
    return f"""<header class="mb-6">
                <div class="text-xs font-bold text-clinical-teal mb-2">Scientific article</div>
                <h1 class="text-2xl md:text-3xl font-extrabold text-text-header leading-tight mb-3">{title}</h1>
                <p class="text-sm text-gray-600 mb-3">{abstract}</p>
                <div class="flex flex-wrap gap-4 text-xs text-gray-400">
                    <span>Author: Ramopharmin Editorial</span>
                    <span class="dot">•</span>
                    <span>Updated: May 2026</span>
                    <span class="dot">•</span>
                    <span>Reading time: 12 min</span>
                </div>
            </header>"""


REFS_FA = """<section id="refs" class="pt-6 border-t border-gray-200">
                <h2 class="text-lg font-bold text-gray-900 mb-4">منابع</h2>
                <ol class="list-decimal list-inside text-xs text-gray-500 space-y-2" dir="ltr">
                    <li>UpToDate — Immunosuppressive therapy (clinical overviews).</li>
                    <li>BNF / national formulary monographs.</li>
                    <li>FDA prescribing information (azathioprine, carbamazepine).</li>
                </ol>
            </section>"""

REFS_EN = """<section id="refs" class="pt-6 border-t border-gray-200">
                <h2 class="text-lg font-bold text-gray-900 mb-4">References</h2>
                <ol class="list-decimal list-inside text-xs text-gray-500 space-y-2">
                    <li>UpToDate — Immunosuppressive therapy overviews.</li>
                    <li>BNF / national formulary monographs.</li>
                    <li>FDA prescribing information.</li>
                </ol>
            </section>"""

SPECS = [
    # ─────────────────────────────────────────────────────────────────────────
    # 1. Azathioprine vs other immunosuppressants
    # ─────────────────────────────────────────────────────────────────────────
    {
        "slug": "azathioprine-comparison",
        "title_fa": "آزاتیوپرین در مقایسه با سایر مهارکننده‌های ایمنی",
        "title_en": "Azathioprine compared with other immunosuppressants",
        "abstract_fa": "مروری بر تفاوت‌های اثربخشی، ایمنی، پایش آزمایشگاهی و هزینه بین آزاتیوپرین و سایر مهارکننده‌های رایج برای تصمیم‌گیری بالینی آگاهانه‌تر.",
        "abstract_en": "A concise comparison of efficacy, safety, laboratory monitoring, and cost between azathioprine and other common immunosuppressants to support informed clinical decisions.",
        "summary_id": "sec-summary",
        "toc_fa": [
            ("sec-intro", "مرور"),
            ("sec-aza", "نقش آزاتیوپرین"),
            ("sec-mmf", "میکوفنولات موفتیل"),
            ("sec-mtx", "متوترکسات و سایرین"),
            ("sec-monitor", "پایش و انتخاب"),
            ("sec-summary", "جمع‌بندی"),
        ],
        "toc_en": [
            ("sec-intro", "Overview"),
            ("sec-aza", "Azathioprine"),
            ("sec-mmf", "Mycophenolate"),
            ("sec-mtx", "Methotrexate & others"),
            ("sec-monitor", "Monitoring & selection"),
            ("sec-summary", "Summary"),
        ],
        "body_fa": """<h2 id="sec-intro" class="text-xl font-bold text-text-header mb-3">مرور</h2>
            <p class="mb-4 text-justify text-gray-700">مهارکننده‌های ایمنی امروزه ستون فقرات درمان بسیاری از بیماری‌های خودایمنی مانند لوپوس، آرتریت روماتوئید، واسکولیت‌ها، و بیماری‌های التهابی روده، و همچنین پیوند عضو هستند. این داروها با کاهش هدفمند پاسخ ایمنی از آسیب بافتی ناشی از التهاب مزمن جلوگیری می‌کنند. در عین حال، سرکوب ایمنی با افزایش خطر عفونت‌های فرصت‌طلب، برخی بدخیمی‌ها، و عوارض اعضا همراه است؛ بنابراین انتخاب دقیق دارو و تنظیم دوز مناسب اهمیت بالایی دارند.</p>
            <p class="mb-4 text-justify text-gray-700">داروهای اصلی این گروه عبارتند از: آزاتیوپرین (AZA)، میکوفنولات موفتیل (MMF)، متوترکسات (MTX)، مهارکننده‌های کلسی‌نئورین (سیکلوسپورین، تاکرولیموس)، و طیف روزافزونی از داروهای بیولوژیک. هر کدام مکانیسم اثر، پروفایل عوارض، و نشانه‌های مصرف متفاوتی دارند. انتخاب درست نیازمند ارزیابی جامع بیمار از جهت تشخیص، شدت بیماری، عملکرد کلیه و کبد، سن، جنس، برنامه باروری، پروفایل عفونت، و هزینه است.</p>
            <h2 id="sec-aza" class="text-xl font-bold text-text-header mb-3">نقش آزاتیوپرین</h2>
            <p class="mb-4 text-justify text-gray-700">آزاتیوپرین یک پیش‌دارو (prodrug) است که پس از جذب خوراکی به ۶-مرکاپتوپورین (6-MP) تبدیل می‌شود. 6-MP سپس از طریق مسیرهای آنزیماتیک رقیب به متابولیت‌های فعال تیوگوانین نوکلئوتید (6-TGN) تبدیل می‌شود. این متابولیت‌ها با قرار گرفتن در DNA در حال سنتز و مهار آنزیم‌های کلیدی مسیر پورین، از تکثیر لنفوسیت‌های T و B جلوگیری می‌کنند. AZA از دهه ۱۹۶۰ میلادی کاربرد بالینی دارد و یکی از پرسابقه‌ترین و مقرون‌به‌صرفه‌ترین مهارکننده‌های ایمنی در جهان است.</p>
            <p class="mb-4 text-justify text-gray-700">موارد مصرف AZA شامل لوپوس اریتماتوز سیستمیک (مرحله نگهدارنده)، آرتریت روماتوئید، واسکولیت‌ها، بیماری التهابی روده (کرون و کولیت اولسراتیو)، نفروپاتی IgA، میاستنی گراویس، و پیوند اعضا می‌شود. دوز معمول ۱ تا ۳ میلی‌گرم به ازای هر کیلوگرم وزن بدن در روز است و باید به تدریج و با نظارت پزشک افزایش یابد.</p>
            <p class="mb-4 text-justify text-gray-700">پیش از شروع درمان، تعیین فعالیت آنزیم TPMT (تیوپورین متیل‌ترانسفراز) یا ژنوتایپینگ TPMT/NUDT15 توصیه می‌شود. کمبود این آنزیم‌ها باعث تجمع متابولیت‌های سمی و سرکوب شدید مغز استخوان (لکوپنی، آنمی، ترومبوسیتوپنی) می‌شود. مهم‌ترین و خطرناک‌ترین تداخل دارویی AZA با آلوپورینول است؛ آلوپورینول مسیر کاتابولیک AZA را از طریق مهار گزانتین اکسیداز مسدود می‌کند و سطح متابولیت‌های سمی را چند برابر افزایش می‌دهد. این ترکیب بدون کاهش دوز AZA به ۲۵٪ اولیه می‌تواند به سرکوب مغز استخوان و مرگ منجر شود. پایش منظم شامل شمارش کامل خون (CBC) و آنزیم‌های کبدی است.</p>
            <h2 id="sec-mmf" class="text-xl font-bold text-text-header mb-3">میکوفنولات موفتیل</h2>
            <p class="mb-4 text-justify text-gray-700">میکوفنولات موفتیل (MMF) پیش‌داروی اسید میکوفنولیک است. اسید میکوفنولیک آنزیم IMPDH (اینوزین مونوفسفات دهیدروژناز) را به‌صورت برگشت‌پذیر مهار می‌کند. این آنزیم گام کلیدی در مسیر سنتز de novo گوانوزین نوکلئوتیدهاست. از آنجا که لنفوسیت‌های T و B بیشتر از سایر سلول‌ها به این مسیر وابسته‌اند (و مسیر بازیافت در آنها ناکافی است)، MMF نسبتاً انتخابی‌تر از AZA برای سلول‌های ایمنی عمل می‌کند و سمیت مغز استخوان کمتری دارد.</p>
            <p class="mb-4 text-justify text-gray-700">MMF در نفریت لوپوس (هم مرحله القا با دوز بالاتر هم نگهدارنده)، پیوند کلیه، کبد، قلب، و برخی بیماری‌های خودایمنی سیستمیک کاربرد وسیعی دارد. دوز معمول ۱.۵ تا ۳ گرم در روز در دو وعده تقسیم‌شده است. شایع‌ترین عوارض گوارشی هستند: تهوع، اسهال، و کرامپ شکمی که گاه مانع رسیدن به دوز هدف می‌شوند. تغییر به فرم سدیم میکوفنولات (پوشش انتریک) اغلب تحمل گوارشی را بهبود می‌بخشد. نکته مهم: MMF تراتوژنیک است و باید حداقل شش هفته پیش از اقدام به بارداری قطع شود.</p>
            <h2 id="sec-mtx" class="text-xl font-bold text-text-header mb-3">متوترکسات و سایرین</h2>
            <p class="mb-4 text-justify text-gray-700">متوترکسات (MTX) در دوزهای پایین هفتگی (۷.۵ تا ۲۵ میلی‌گرم در هفته) به‌عنوان آنتاگونیست فولات عمل می‌کند و با مهار آنزیم دی‌هیدروفولات ردوکتاز، از سنتز تیمیدین و پورین‌ها جلوگیری می‌کند. علاوه بر اثر ضد تکثیری، MTX از طریق تجمع آدنوزین درون‌سلولی اثرات ضدالتهابی مستقلی اعمال می‌کند. MTX داروی پایه در آرتریت روماتوئید، پسوریازیس، آرتریت پسوریاتیک، واسکولیت‌ها، و برخی اسپوندیلوآرتریت‌هاست. تکمیل با اسید فولیک ۱ تا ۵ میلی‌گرم روزانه (در روزهای غیر MTX) عوارض مخاطی و کبدی را به‌طور قابل توجهی کاهش می‌دهد.</p>
            <p class="mb-4 text-justify text-gray-700">مهارکننده‌های کلسی‌نئورین (سیکلوسپورین، تاکرولیموس) با مهار مسیر کلسینئورین–NFAT، تولید اینترلوکین-۲ توسط T-cell را مسدود می‌کنند و پایه اصلی پروتکل‌های ضد رد در پیوند اعضا هستند. پایش سطح خونی دارو، فشار خون، و کراتینین ضروری است. بیولوژیک‌ها (مهارکننده‌های TNF مانند اینفلیکسیماب و آدالیموماب، anti-IL-6 مانند توسیلیزوماب، anti-CD20 مانند ریتوکسیماب، و مهارکننده‌های هم‌تحریکی مانند آباتاسپت) در بیماران مقاوم به درمان سنتی اثربخشی بالایی دارند اما نیاز به غربالگری قبل از شروع برای سل نهفته، هپاتیت B و C دارند و هزینه بسیار بالاتری دارند.</p>
            <h2 id="sec-monitor" class="text-xl font-bold text-text-header mb-3">پایش و انتخاب</h2>
            <p class="mb-4 text-justify text-gray-700">تمام داروهای مهارکننده ایمنی نیازمند پیگیری منظم آزمایشگاهی و بالینی هستند. برای اکثر داروها، شمارش کامل خون (CBC) هر ۴ هفته تا تثبیت دوز و سپس هر ۸ تا ۱۲ هفته یک بار توصیه می‌شود. آزمایش‌های عملکرد کبد (AST، ALT، بیلی‌روبین) و کلیه (کراتینین، BUN) نیز باید دوره‌ای تکرار شوند. هر نشانه‌ای از عفونت (تب، لرز، سرفه غیرمعمول، تغییر در ادرار، زخم‌های پوستی یا دهانی) باید فوراً به تیم درمان گزارش شود.</p>
            <p class="mb-4 text-justify text-gray-700">انتخاب بین داروها باید بر اساس تشخیص دقیق، شدت و فعالیت بیماری، بیماری‌های همراه (نارسایی کلیه یا کبد می‌تواند گزینه‌ها را محدود کند)، وضعیت باروری، هزینه و دسترسی، و اولویت‌های فردی بیمار صورت گیرد. هیچ دارویی برای همه بیماران مناسب نیست. مشاوره با پزشک متخصص (روماتولوژیست، نفرولوژیست، متخصص پیوند) الزامی است. این متن صرفاً جنبه آموزشی دارد و جایگزین ویزیت تخصصی نیست.</p>
            <h2 id="sec-summary" class="text-xl font-bold text-text-header mb-3">جمع‌بندی</h2>
            <p class="mb-6 text-justify text-gray-700">آزاتیوپرین همچنان گزینه‌ای معتبر، پرسابقه، و مقرون‌به‌صرفه در طیف وسیعی از بیماری‌های خودایمنی و پیوند است. میکوفنولات موفتیل مزایای خاصی در نفریت لوپوس و پیوند کلیه دارد. متوترکسات پایه درمان آرتریت روماتوئید و بیماری‌های التهابی مفصلی است. مهارکننده‌های کلسی‌نئورین در پیوند اعضا نقشی کلیدی دارند. بیولوژیک‌ها برای بیماری مقاوم به درمان سنتی حفظ می‌شوند. بهترین نتیجه با انتخاب فردی‌شده، پایش منظم، و ارتباط مستمر با تیم درمان حاصل می‌شود.</p>""",
        "body_en": """<h2 id="sec-intro" class="text-xl font-bold text-text-header mb-3">Overview</h2>
            <p class="mb-4 text-justify text-gray-700">Immunosuppressive agents are the cornerstone of treatment for many autoimmune diseases—including lupus, rheumatoid arthritis, vasculitides, and inflammatory bowel disease—as well as solid-organ transplantation. By selectively dampening immune responses, these drugs prevent tissue damage driven by chronic inflammation or allo-immune rejection. At the same time, immune suppression carries risks of opportunistic infections, certain malignancies, and organ toxicities, making precise drug selection and dose titration essential.</p>
            <p class="mb-4 text-justify text-gray-700">The principal agents include azathioprine (AZA), mycophenolate mofetil (MMF), methotrexate (MTX), calcineurin inhibitors (cyclosporine, tacrolimus), and a growing armamentarium of biologics. Each has a distinct mechanism, safety profile, monitoring requirements, and set of indications. Choosing the right agent requires an integrated assessment of diagnosis, disease severity, renal and hepatic function, age, sex, reproductive plans, infection risk, cost, and patient preference.</p>
            <h2 id="sec-aza" class="text-xl font-bold text-text-header mb-3">Azathioprine</h2>
            <p class="mb-4 text-justify text-gray-700">Azathioprine is a prodrug converted after oral absorption to 6-mercaptopurine (6-MP). Competing enzymatic pathways further metabolise 6-MP to the active thioguanine nucleotides (6-TGN), which are incorporated into replicating DNA and inhibit key purine-synthesis enzymes, thereby blocking T- and B-lymphocyte proliferation. In clinical use since the 1960s, AZA has one of the longest track records of any immunosuppressant and remains widely available at low cost.</p>
            <p class="mb-4 text-justify text-gray-700">Key indications include systemic lupus erythematosus (maintenance), rheumatoid arthritis, vasculitides, inflammatory bowel disease (Crohn's and ulcerative colitis), IgA nephropathy, myasthenia gravis, and solid-organ transplantation. Typical dosing is 1–3 mg/kg/day, titrated gradually under medical supervision.</p>
            <p class="mb-4 text-justify text-gray-700">Before initiation, TPMT enzyme activity or TPMT/NUDT15 genotyping is strongly recommended. Deficiency of these enzymes leads to toxic 6-TGN accumulation and severe, potentially life-threatening myelosuppression (leukopenia, anaemia, thrombocytopenia). The most critical drug interaction is with allopurinol: allopurinol inhibits xanthine oxidase, blocking the catabolism of AZA metabolites and dramatically raising toxic metabolite levels. Using this combination without reducing the AZA dose to approximately 25% of the original can be fatal. Regular CBC and liver function tests are mandatory monitoring parameters throughout therapy.</p>
            <h2 id="sec-mmf" class="text-xl font-bold text-text-header mb-3">Mycophenolate</h2>
            <p class="mb-4 text-justify text-gray-700">Mycophenolate mofetil (MMF) is the prodrug of mycophenolic acid, a potent and reversible inhibitor of inosine monophosphate dehydrogenase (IMPDH). IMPDH catalyses the rate-limiting step in the de novo guanosine nucleotide synthesis pathway. Because T and B lymphocytes rely predominantly on this pathway (lacking sufficient salvage pathway capacity), MMF exerts greater selectivity toward immune cells than AZA and is associated with less myelosuppression in most patients.</p>
            <p class="mb-4 text-justify text-gray-700">MMF is widely used in lupus nephritis (both induction at higher doses and maintenance at lower doses), kidney, liver, and heart transplantation, and selected systemic autoimmune conditions. The typical dose is 1.5–3 g/day in two divided doses. Gastrointestinal side effects—nausea, diarrhoea, and abdominal cramping—are the most common dose-limiting problem; switching to enteric-coated sodium mycophenolate often improves tolerability. An important safety consideration: MMF is teratogenic and must be discontinued at least six weeks before a planned pregnancy.</p>
            <h2 id="sec-mtx" class="text-xl font-bold text-text-header mb-3">Methotrexate &amp; others</h2>
            <p class="mb-4 text-justify text-gray-700">At low weekly doses (7.5–25 mg/week), methotrexate acts as a folate antagonist by inhibiting dihydrofolate reductase, impairing thymidine and purine synthesis. Beyond its antiproliferative action, MTX exerts independent anti-inflammatory effects through intracellular adenosine accumulation. It is the anchor drug for rheumatoid arthritis and is also used in psoriasis, psoriatic arthritis, vasculitides, and spondyloarthropathies. Supplementing with folic acid 1–5 mg/day (on non-MTX days) substantially reduces mucosal, haematological, and hepatic adverse effects without compromising efficacy.</p>
            <p class="mb-4 text-justify text-gray-700">Calcineurin inhibitors (cyclosporine, tacrolimus) block T-cell activation through the calcineurin–NFAT pathway, suppressing IL-2 production, and form the backbone of most solid-organ transplant immunosuppression protocols. Drug-level monitoring, blood pressure assessment, and serial creatinine measurement are essential. Biologics—TNF inhibitors (infliximab, adalimumab), anti-IL-6 agents (tocilizumab), anti-CD20 (rituximab), and costimulation blockers (abatacept)—are highly effective in refractory autoimmune disease, but require pre-treatment screening for latent tuberculosis and hepatitis B/C, and carry considerably higher cost.</p>
            <h2 id="sec-monitor" class="text-xl font-bold text-text-header mb-3">Monitoring &amp; selection</h2>
            <p class="mb-4 text-justify text-gray-700">All immunosuppressive agents require structured, ongoing laboratory and clinical follow-up. For most drugs, a complete blood count every 4 weeks until dose stabilisation and then every 8–12 weeks is recommended, together with periodic liver and renal function panels. Any sign of infection—fever, rigors, unusual cough, changes in urine, cutaneous or oral lesions—should be reported to the care team without delay, as immunosuppressed patients may deteriorate rapidly.</p>
            <p class="mb-4 text-justify text-gray-700">Selecting among these agents must integrate diagnosis, disease activity, comorbidities (renal or hepatic impairment can restrict options), reproductive status, cost, accessibility, and patient values and preferences. No single drug suits all patients. Specialist consultation—rheumatologist, nephrologist, or transplant physician—is mandatory before initiating immunosuppression. This article is educational only and does not replace individualised medical assessment.</p>
            <h2 id="sec-summary" class="text-xl font-bold text-text-header mb-3">Summary</h2>
            <p class="mb-6 text-justify text-gray-700">Azathioprine remains a valid, cost-effective, and well-established option across a broad range of autoimmune conditions and transplantation protocols. MMF offers advantages in lupus nephritis and renal transplant; MTX anchors treatment of RA and inflammatory joint disease; calcineurin inhibitors are pivotal in organ transplant; and biologics are reserved for refractory disease. The best outcomes arise from individualised drug selection, systematic monitoring, and sustained collaboration between the patient and the treatment team.</p>""",
        "img": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1600&q=80",
        "img_alt_fa": "آزمایشگاه پزشکی",
        "img_alt_en": "Medical laboratory",
        "cap_fa": "پایش آزمایشگاهی منظم در درمان‌های مهارکننده ایمنی از اهمیت حیاتی برخوردار است.",
        "cap_en": "Regular laboratory monitoring is central to safe immunosuppressive therapy.",
        "refs_fa": """<section id="refs" class="pt-6 border-t border-gray-200">
                <h2 class="text-lg font-bold text-gray-900 mb-4">منابع</h2>
                <ol class="list-decimal list-inside text-xs text-gray-500 space-y-2" dir="ltr">
                    <li>Ponticelli C, Moroni G. Azathioprine in lupus nephritis. <em>Lupus.</em> 2023;32(2):155–164.</li>
                    <li>Smolen JS et al. EULAR recommendations for the management of rheumatoid arthritis. <em>Ann Rheum Dis.</em> 2023;82:3–18.</li>
                    <li>Allison AC, Eugui EM. Mycophenolate mofetil and its mechanisms of action. <em>Immunopharmacology.</em> 2000;47:85–118.</li>
                    <li>FDA Prescribing Information — Azathioprine (Imuran). Revised 2020.</li>
                    <li>Patel A et al. TPMT and NUDT15 pharmacogenomics: a systematic review. <em>Pharmacogenomics.</em> 2022;23:185–197.</li>
                    <li>UpToDate — Overview of immunosuppressive agents used in solid organ transplantation. 2024.</li>
                </ol>
            </section>""",
        "refs_en": """<section id="refs" class="pt-6 border-t border-gray-200">
                <h2 class="text-lg font-bold text-gray-900 mb-4">References</h2>
                <ol class="list-decimal list-inside text-xs text-gray-500 space-y-2">
                    <li>Ponticelli C, Moroni G. Azathioprine in lupus nephritis. <em>Lupus.</em> 2023;32(2):155–164.</li>
                    <li>Smolen JS et al. EULAR recommendations for the management of rheumatoid arthritis. <em>Ann Rheum Dis.</em> 2023;82:3–18.</li>
                    <li>Allison AC, Eugui EM. Mycophenolate mofetil and its mechanisms of action. <em>Immunopharmacology.</em> 2000;47:85–118.</li>
                    <li>FDA Prescribing Information — Azathioprine (Imuran). Revised 2020.</li>
                    <li>Patel A et al. TPMT and NUDT15 pharmacogenomics: a systematic review. <em>Pharmacogenomics.</em> 2022;23:185–197.</li>
                    <li>UpToDate — Overview of immunosuppressive agents used in solid organ transplantation. 2024.</li>
                </ol>
            </section>""",
    },
    # ─────────────────────────────────────────────────────────────────────────
    # 2. Azathioprine in organ transplantation
    # ─────────────────────────────────────────────────────────────────────────
    {
        "slug": "azathioprine-organ-transplant",
        "title_fa": "آزاتیوپرین در پیوند اعضا",
        "title_en": "Azathioprine in organ transplantation",
        "abstract_fa": "نقش آزاتیوپرین در پیشگیری از رد پیوند، رژیم‌های ترکیبی، دوزدهی، پایش آزمایشگاهی، و مراقبت بلندمدت در بیماران پیوندی.",
        "abstract_en": "Role of azathioprine in rejection prophylaxis, combination regimens, dosing, monitoring, and long-term care of transplant recipients.",
        "summary_id": "sec-summary",
        "toc_fa": [
            ("sec-intro", "مرور"),
            ("sec-reject", "پیشگیری از رد"),
            ("sec-combo", "ترکیب با سایر داروها"),
            ("sec-monitor", "پایش"),
            ("sec-life", "سبک زندگی"),
            ("sec-summary", "جمع‌بندی"),
        ],
        "toc_en": [
            ("sec-intro", "Overview"),
            ("sec-reject", "Rejection prophylaxis"),
            ("sec-combo", "Combination therapy"),
            ("sec-monitor", "Monitoring"),
            ("sec-life", "Lifestyle"),
            ("sec-summary", "Summary"),
        ],
        "body_fa": """<h2 id="sec-intro" class="text-xl font-bold text-text-header mb-3">مرور</h2>
            <p class="mb-4 text-justify text-gray-700">پیوند کلیه، کبد، قلب، و ریه از میان پیشرفت‌های پزشکی قرن بیستم، وابسته‌ترین دستاوردها به دارودرمانی مزمن هستند. سیستم ایمنی گیرنده پیوند به‌طور طبیعی آنتی‌ژن‌های بافت دهنده را بیگانه تشخیص داده و پاسخ رد (rejection) را آغاز می‌کند. بدون سرکوب کافی ایمنی، رد حاد و مزمن پیوند غیرقابل اجتناب است. آزاتیوپرین از اوایل دهه ۱۹۶۰ — از زمانی که دکتر جوزف موری اولین پیوند کلیه موفق را در دو توأم انجام داد — در کنار گلوکوکورتیکوئیدها به‌عنوان پایه سرکوب ایمنی در پیوند استفاده شده است.</p>
            <p class="mb-4 text-justify text-gray-700">امروزه پروتکل‌های پیوند اغلب ترکیبی از سه دارو را به‌کار می‌گیرند: یک مهارکننده کلسی‌نئورین (تاکرولیموس یا سیکلوسپورین)، یک آنتی‌متابولیت (میکوفنولات موفتیل یا آزاتیوپرین)، و یک گلوکوکورتیکوئید (پردنیزولون). در بعضی مراکز و برای بعضی بیماران، AZA هنوز جایگاه معتبری به‌عنوان آنتی‌متابولیت ترجیحی دارد — به‌ویژه در بیماران با عوارض گوارشی MMF یا بارداری برنامه‌ریزی‌شده.</p>
            <h2 id="sec-reject" class="text-xl font-bold text-text-header mb-3">پیشگیری از رد</h2>
            <p class="mb-4 text-justify text-gray-700">رد پیوند بر اساس زمان وقوع به چند دسته تقسیم می‌شود: رد فوق حاد (hyperacute) که ظرف دقیقه تا ساعت پس از پیوند رخ می‌دهد و ناشی از آنتی‌بادی‌های از پیش موجود است؛ رد حاد (acute) که معمولاً در هفته‌ها تا ماه‌های اول پس از پیوند رخ می‌دهد و با واسطه T-cell است؛ و رد مزمن (chronic) که طی سال‌ها به تدریج پیوند را از کار می‌اندازد. آزاتیوپرین با مهار تکثیر لنفوسیتی، عمدتاً رد حاد و بخشی از رد مزمن واسطه T-cell را کنترل می‌کند.</p>
            <p class="mb-4 text-justify text-gray-700">دوز معمول AZA در پیوند ۱ تا ۲ میلی‌گرم/کیلوگرم/روز است. دوز باید با توجه به پاسخ CBC تنظیم شود. کاهش لکوسیت‌ها به زیر ۳۵۰۰ در هر میلی‌متر مکعب نشانه‌ای برای کاهش دوز یا قطع موقت است. هرگز بدون مشاوره تیم پیوند دوز را تغییر ندهید یا دارو را قطع نکنید؛ قطع ناگهانی می‌تواند زمینه‌ساز رد حاد باشد.</p>
            <h2 id="sec-combo" class="text-xl font-bold text-text-header mb-3">ترکیب با سایر داروها</h2>
            <p class="mb-4 text-justify text-gray-700">رژیم سه‌دارویی استاندارد (مهارکننده کلسی‌نئورین + آنتی‌متابولیت + کورتیکوستروئید) پایه اکثر پروتکل‌های پیوند است. تاکرولیموس در مقایسه با سیکلوسپورین در اکثر مطالعات نرخ رد حاد کمتری نشان داده و جایگاه غالب‌تری پیدا کرده است. MMF نسبت به AZA در کاهش رد حاد مزیت‌هایی دارد، اما AZA در بیمارانی که MMF را تحمل نمی‌کنند یا در شرایط خاص (مثلاً برنامه بارداری) جایگزین مناسبی است.</p>
            <p class="mb-4 text-justify text-gray-700">تداخلات دارویی در بیماران پیوندی بسیار اهمیت دارد. آنتی‌بیوتیک‌های فلوروکینولون، آنتی‌فانگال‌های آزول (فلوکونازول، وریکونازول) سطح تاکرولیموس/سیکلوسپورین را افزایش می‌دهند. برخی ضد تشنج‌ها (فنیتوئین، فنوباربیتال)، ریفامپین، و داروهای ضد HIV سطح مهارکننده‌های کلسی‌نئورین را کاهش می‌دهند. هر داروی جدید — حتی مکمل و گیاهی — باید با پزشک یا داروساز پیوند هماهنگ شود. گریپ‌فروت و آب گریپ‌فروت به علت مهار CYP3A4 روده‌ای باید از رژیم غذایی حذف شوند.</p>
            <h2 id="sec-monitor" class="text-xl font-bold text-text-header mb-3">پایش</h2>
            <p class="mb-4 text-justify text-gray-700">پیگیری منظم در بیماران پیوندی حیاتی است. آزمایش‌های روتین شامل شمارش کامل خون (برای پایش سمیت مغز استخوان AZA)، کراتینین سرم و ادرار (عملکرد کلیه)، آنزیم‌های کبدی (AST، ALT)، سطح خونی تاکرولیموس یا سیکلوسپورین، قند خون ناشتا (ریسک دیابت بعد از پیوند)، و لیپیدها می‌شود. فرکانس آزمایش‌ها در ماه‌های اول پس از پیوند بیشتر است و با گذشت زمان و تثبیت وضعیت کاهش می‌یابد — اما هرگز به صفر نمی‌رسد.</p>
            <p class="mb-4 text-justify text-gray-700">علائمی که باید فوری گزارش شوند: تب (حتی خفیف) یا لرز، کاهش ادرار یا تغییر رنگ آن، درد یا التهاب در ناحیه پیوند، کاهش ناگهانی فشار خون، زردی، خستگی شدید ناگهانی، یا هر علامت غیرمعمول دیگر. عفونت‌های فرصت‌طلب (CMV، BK ویروس، قارچ‌های تهاجمی) در بیماران پیوندی خطرناک‌تر از جمعیت عمومی هستند و تشخیص و درمان سریع ضروری است.</p>
            <h2 id="sec-life" class="text-xl font-bold text-text-header mb-3">سبک زندگی</h2>
            <p class="mb-4 text-justify text-gray-700">واکسیناسیون بخش مهمی از مراقبت پس از پیوند است. واکسن‌های غیرزنده (آنفلوآنزا، پنوموکوک، هپاتیت B) طبق توصیه تیم پیوند باید به‌روز باشند. واکسن‌های زنده تضعیف‌شده (MMR، واریسلا، زردشدگی زنده) در بیشتر موارد در بیماران دریافت‌کننده سرکوب ایمنی سیستمیک ممنوع هستند مگر با تأیید صریح پزشک. اطرافیان خانواده نیز باید واکسیناسیون خود را تکمیل کنند.</p>
            <p class="mb-4 text-justify text-gray-700">رژیم غذایی سالم (کم‌سدیم، کم‌چرب اشباع، سرشار از میوه و سبزی)، حفظ وزن در محدوده سالم، و فعالیت جسمانی منظم طبق توصیه پزشک مهم هستند. قرار گرفتن در معرض آفتاب مستقیم به دلیل افزایش ریسک سرطان‌های پوستی باید محدود شود و از ضد آفتاب با SPF بالا استفاده شود. مصرف دخانیات و الکل ممنوع است. تماس با افراد بیمار، به‌ویژه کسانی که بیماری‌های تنفسی یا عفونت‌های فعال دارند، باید به‌حداقل برسد.</p>
            <h2 id="sec-summary" class="text-xl font-bold text-text-header mb-3">جمع‌بندی</h2>
            <p class="mb-6 text-justify text-gray-700">آزاتیوپرین همچنان در بسیاری از پروتکل‌های پیوند نقش دارد، به‌ویژه در بیمارانی که MMF را تحمل نمی‌کنند. موفقیت بلندمدت پیوند به پایبندی دقیق به دارودرمانی، پیگیری منظم آزمایشگاهی، شناخت تداخلات دارویی، رعایت نکات سبک زندگی، و ارتباط مستمر با تیم پیوند وابسته است. بیمار آگاه، فعال و مشارکت‌کننده در درمان خود، بهترین نتایج پیوند را تجربه می‌کند.</p>""",
        "body_en": """<h2 id="sec-intro" class="text-xl font-bold text-text-header mb-3">Overview</h2>
            <p class="mb-4 text-justify text-gray-700">Kidney, liver, heart, and lung transplantation represent some of medicine's most consequential achievements—and among its most pharmacologically demanding. The recipient's immune system recognises donor antigens as foreign and launches a rejection response unless that response is continuously suppressed. Without adequate immunosuppression, both acute and chronic rejection are inevitable. Azathioprine has been used as a core component of post-transplant therapy since the early 1960s, when Dr. Joseph Murray performed the first successful kidney transplant using AZA alongside corticosteroids.</p>
            <p class="mb-4 text-justify text-gray-700">Contemporary transplant protocols typically employ a three-drug combination: a calcineurin inhibitor (tacrolimus or cyclosporine), an antimetabolite (mycophenolate mofetil or azathioprine), and a corticosteroid (prednisolone). In many centres AZA retains a valued role as the antimetabolite of choice when MMF is not tolerated or is contraindicated—for example, in patients planning pregnancy or those with severe MMF-related gastrointestinal toxicity.</p>
            <h2 id="sec-reject" class="text-xl font-bold text-text-header mb-3">Rejection prophylaxis</h2>
            <p class="mb-4 text-justify text-gray-700">Transplant rejection is classified by timing: hyperacute rejection (minutes to hours post-transplant, mediated by pre-formed antibodies); acute rejection (days to months, predominantly T-cell-mediated); and chronic rejection (months to years, involving both cellular and humoral mechanisms). Azathioprine, by inhibiting lymphocyte proliferation, primarily counteracts acute T-cell-mediated rejection and contributes to chronic rejection prevention as part of maintenance regimens.</p>
            <p class="mb-4 text-justify text-gray-700">In the transplant setting, AZA is typically dosed at 1–2 mg/kg/day. The dose should be titrated to the CBC response: a white cell count falling below 3,500/mm³ is a signal to reduce or temporarily hold the dose. Dose changes and discontinuation must always be coordinated with the transplant team; abrupt cessation can precipitate acute rejection.</p>
            <h2 id="sec-combo" class="text-xl font-bold text-text-header mb-3">Combination therapy</h2>
            <p class="mb-4 text-justify text-gray-700">The standard triple-therapy regimen (calcineurin inhibitor + antimetabolite + corticosteroid) underpins most transplant protocols. Tacrolimus has largely replaced cyclosporine as the preferred calcineurin inhibitor, with lower acute rejection rates in most studies. MMF demonstrates some advantages over AZA in reducing acute rejection, but AZA remains a valuable alternative when MMF is not tolerated or when a patient is planning pregnancy (MMF is teratogenic; AZA is classified as relatively safer in pregnancy under transplant team guidance).</p>
            <p class="mb-4 text-justify text-gray-700">Drug interactions are critically important in transplant patients. Fluoroquinolone antibiotics and azole antifungals (fluconazole, voriconazole) raise tacrolimus and cyclosporine levels significantly. Enzyme inducers such as rifampicin, phenytoin, phenobarbital, and some antiretrovirals lower calcineurin inhibitor levels and can precipitate rejection. Every new medication—including supplements, herbal products, and over-the-counter drugs—must be cleared with the transplant pharmacist or physician. Grapefruit and grapefruit juice must be avoided, as they inhibit intestinal CYP3A4 and raise calcineurin inhibitor levels unpredictably.</p>
            <h2 id="sec-monitor" class="text-xl font-bold text-text-header mb-3">Monitoring</h2>
            <p class="mb-4 text-justify text-gray-700">Structured surveillance is a lifelong requirement after transplantation. Routine panels include: complete blood count (to detect AZA-related myelosuppression), serum creatinine and urinalysis (allograft function), liver enzymes (AST, ALT), tacrolimus or cyclosporine trough levels, fasting glucose (post-transplant diabetes mellitus risk), and a fasting lipid panel. Monitoring frequency is highest in the first weeks post-transplant and is tapered as the patient stabilises—but it never stops.</p>
            <p class="mb-4 text-justify text-gray-700">Symptoms requiring urgent reporting include: any fever or rigours (even low-grade), reduced or discoloured urine output, pain or swelling over the transplant site, sudden blood pressure changes, jaundice, unexplained fatigue, or any unusual symptoms. Opportunistic infections (CMV, BK virus, invasive fungal disease) are far more dangerous in transplant recipients than in immunocompetent individuals; early identification and treatment are essential.</p>
            <h2 id="sec-life" class="text-xl font-bold text-text-header mb-3">Lifestyle</h2>
            <p class="mb-4 text-justify text-gray-700">Vaccination is an integral part of post-transplant care. All inactivated vaccines (influenza, pneumococcal, hepatitis B, tetanus) should be kept up to date per transplant team scheduling. Live attenuated vaccines (MMR, varicella, live yellow fever) are generally contraindicated under systemic immunosuppression unless explicitly approved by the transplant physician. Close household contacts should also maintain current vaccinations to protect the recipient through herd immunity.</p>
            <p class="mb-4 text-justify text-gray-700">A heart-healthy diet (low sodium, low saturated fat, rich in vegetables and fruit), maintenance of a healthy weight, and regular physical activity as guided by the team all improve long-term outcomes. Sun protection is particularly important: the risk of squamous cell carcinoma of the skin is substantially elevated in long-term immunosuppressed patients. Broad-spectrum high-SPF sunscreen, protective clothing, and regular dermatological review are recommended. Tobacco and alcohol must be avoided. Exposure to individuals with active respiratory or other infections should be minimised.</p>
            <h2 id="sec-summary" class="text-xl font-bold text-text-header mb-3">Summary</h2>
            <p class="mb-6 text-justify text-gray-700">Azathioprine continues to play a role in transplant maintenance regimens, particularly for patients who cannot tolerate MMF. Long-term transplant success depends on strict medication adherence, regular laboratory monitoring, awareness of drug interactions, attention to lifestyle factors, and sustained engagement with the transplant team. An informed, active patient who communicates openly with their care team achieves the best long-term transplant outcomes.</p>""",
        "img": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1600&q=80",
        "img_alt_fa": "مراقبت بیمارستانی پس از پیوند",
        "img_alt_en": "Post-transplant hospital care",
        "cap_fa": "مراقبت تیمی و پایش مستمر در بیماران پیوندی برای پیشگیری از رد پیوند حیاتی است.",
        "cap_en": "Team-based care and continuous monitoring are critical for long-term transplant success.",
        "refs_fa": """<section id="refs" class="pt-6 border-t border-gray-200">
                <h2 class="text-lg font-bold text-gray-900 mb-4">منابع</h2>
                <ol class="list-decimal list-inside text-xs text-gray-500 space-y-2" dir="ltr">
                    <li>KDIGO Clinical Practice Guideline for the Care of Kidney Transplant Recipients. <em>Am J Transplant.</em> 2009;9(Suppl 3):S1–S155.</li>
                    <li>Halloran PF. Immunosuppressive drugs for kidney transplantation. <em>N Engl J Med.</em> 2004;351:2715–2729.</li>
                    <li>Vincenti F et al. A phase III study of belatacept versus cyclosporine in kidney transplants. <em>Am J Transplant.</em> 2010;10:535–546.</li>
                    <li>BNF — Azathioprine monograph. BMJ/NICE. 2024.</li>
                    <li>UpToDate — Immunosuppressive regimens for kidney transplant recipients at standard risk. 2024.</li>
                    <li>European Society for Organ Transplantation (ESOT) Guidelines on immunosuppression. 2022.</li>
                </ol>
            </section>""",
        "refs_en": """<section id="refs" class="pt-6 border-t border-gray-200">
                <h2 class="text-lg font-bold text-gray-900 mb-4">References</h2>
                <ol class="list-decimal list-inside text-xs text-gray-500 space-y-2">
                    <li>KDIGO Clinical Practice Guideline for the Care of Kidney Transplant Recipients. <em>Am J Transplant.</em> 2009;9(Suppl 3):S1–S155.</li>
                    <li>Halloran PF. Immunosuppressive drugs for kidney transplantation. <em>N Engl J Med.</em> 2004;351:2715–2729.</li>
                    <li>Vincenti F et al. A phase III study of belatacept versus cyclosporine in kidney transplants. <em>Am J Transplant.</em> 2010;10:535–546.</li>
                    <li>BNF — Azathioprine monograph. BMJ/NICE. 2024.</li>
                    <li>UpToDate — Immunosuppressive regimens for kidney transplant recipients at standard risk. 2024.</li>
                    <li>European Society for Organ Transplantation (ESOT) Guidelines on immunosuppression. 2022.</li>
                </ol>
            </section>""",
    },
    # ─────────────────────────────────────────────────────────────────────────
    # 3. Carbamazepine: uses, HLA, and drug interactions
    # ─────────────────────────────────────────────────────────────────────────
    {
        "slug": "carbamazepine-dd-interactions",
        "title_fa": "کاربامازپین: کاربردها، ایمنی ژنتیکی (HLA) و تداخلات",
        "title_en": "Carbamazepine: uses, genetic safety (HLA), and drug interactions",
        "abstract_fa": "راهنمای جامع بیمار درباره موارد مصرف کاربامازپین، اهمیت آزمایش HLA-B*15:02، تداخلات مهم دارویی، و پایش ایمنی برای استفاده آگاهانه و بی‌خطر.",
        "abstract_en": "A comprehensive patient-oriented overview of carbamazepine indications, the importance of HLA-B*15:02 testing, major drug interactions, and safety monitoring for safe and effective use.",
        "summary_id": "sec-summary",
        "toc_fa": [
            ("sec-intro", "مرور"),
            ("sec-use", "موارد مصرف"),
            ("sec-hla", "ایمنی ژنتیکی HLA"),
            ("sec-ddi", "تداخلات مهم"),
            ("sec-monitor", "پایش"),
            ("sec-summary", "جمع‌بندی"),
        ],
        "toc_en": [
            ("sec-intro", "Overview"),
            ("sec-use", "Indications"),
            ("sec-hla", "HLA &amp; genetic safety"),
            ("sec-ddi", "Drug interactions"),
            ("sec-monitor", "Monitoring"),
            ("sec-summary", "Summary"),
        ],
        "body_fa": """<h2 id="sec-intro" class="text-xl font-bold text-text-header mb-3">مرور</h2>
            <p class="mb-4 text-justify text-gray-700">کاربامازپین (Carbamazepine یا CBZ) داروی ضد تشنج و تثبیت‌کننده خلق است که از دهه ۱۹۶۰ میلادی در بالین مورد استفاده قرار می‌گیرد. مکانیسم اصلی آن بلوک کانال‌های سدیم ولتاژ-وابسته در غشای عصبی است که انتشار دشارژ‌های صرعی را مهار می‌کند. علاوه بر صرع، در درمان درد عصبی و برخی اختلالات روانپزشکی نیز نقش دارد. این دارو دارای چند خصوصیت منحصر به فرد دارویی است که آشنایی بیمار با آنها برای استفاده ایمن ضروری است.</p>
            <p class="mb-4 text-justify text-gray-700">یکی از مهم‌ترین خصوصیات کاربامازپین، القای آنزیم‌های کبدی سیتوکروم P450 (به‌ویژه CYP3A4) است. این ویژگی منجر به تسریع متابولیسم بسیاری از داروهای دیگر و خود کاربامازپین می‌شود — پدیده‌ای که به اتواینداکشن (autoinduction) معروف است. در هفته‌های اول درمان، سطح خونی CBZ پس از چند هفته به‌طور معناداری کاهش می‌یابد، بنابراین تنظیم مجدد دوز ممکن است لازم باشد.</p>
            <h2 id="sec-use" class="text-xl font-bold text-text-header mb-3">موارد مصرف</h2>
            <p class="mb-4 text-justify text-gray-700">کاربامازپین در درمان انواع تشنج‌های جزئی (focal/partial) با یا بدون تعمیم ثانوی، تشنج‌های تونیک‌کلونیک تعمیم‌یافته (Grand Mal)، و ترکیبی از این‌ها کاربرد دارد. این دارو در صرع آبسانس (absence) و صرع میوکلونیک جوانان (JME) توصیه نمی‌شود و حتی می‌تواند این نوع تشنج‌ها را تشدید کند. تشخیص نوع صرع توسط متخصص مغز و اعصاب برای انتخاب صحیح دارو الزامی است.</p>
            <p class="mb-4 text-justify text-gray-700">نورالژی عصب سه‌قلابی (Trigeminal Neuralgia) — که با درد شدید، ضربه‌ای، و برق‌آسا در صورت مشخص می‌شود — یکی از مؤثرترین موارد مصرف کاربامازپین است. در این کاربرد، CBZ نخستین خط درمان به شمار می‌رود. درد نوروپاتیک دیگر مانند نورالژی پس از تبخال (post-herpetic neuralgia) نیز از موارد استفاده است. در روانپزشکی، کاربامازپین به‌عنوان داروی تثبیت‌کننده خلق در اختلال دوقطبی — به‌ویژه در بیمارانی که با لیتیوم پاسخ کافی ندارند — به‌کار می‌رود.</p>
            <h2 id="sec-hla" class="text-xl font-bold text-text-header mb-3">ایمنی ژنتیکی HLA</h2>
            <p class="mb-4 text-justify text-gray-700">کاربامازپین با یک واکنش جانبی پوستی نادر اما بالقوه کشنده همراه است: سندروم استیونز–جانسون (Stevens–Johnson Syndrome یا SJS) و نکرولیز اپیدرمی سمی (Toxic Epidermal Necrolysis یا TEN). این واکنش‌ها — که با تاول‌های گسترده پوستی، ضایعات مخاطی، و نارسایی احتمالی اعضا همراهند — می‌توانند در کمتر از دو هفته پس از شروع دارو بروز کنند و نرخ مرگ‌ومیر بالایی دارند.</p>
            <p class="mb-4 text-justify text-gray-700">مطالعات ژنتیکی بزرگ نشان داده‌اند که آلل HLA-B*15:02 ریسک SJS/TEN ناشی از کاربامازپین را به‌شدت افزایش می‌دهد. این آلل در آسیایی‌های جنوب و جنوب شرقی (چینی‌ها، تایوانی‌ها، تایلندی‌ها، هندی‌ها، ویتنامی‌ها، فیلیپینی‌ها) با شیوع بالاتری دیده می‌شود؛ در ایرانیان شیوع متوسطی گزارش شده است. سازمان FDA ایالات متحده و سازمان‌های نظارت دارویی معتبر توصیه می‌کنند که پیش از شروع CBZ در بیماران با منشأ آسیایی (و در صورت امکان در سایر گروه‌های قومی)، غربالگری HLA-B*15:02 انجام شود.</p>
            <p class="mb-4 text-justify text-gray-700">آلل دیگری به نام HLA-A*31:01 نیز با واکنش‌های پوستی خفیف‌تر (ددرماتیت دارویی، اگزانتم ماکولوپاپولار) در جمعیت‌های اروپایی و ژاپنی مرتبط است. نتیجه آزمایش HLA را با پزشک خود در میان بگذارید؛ تصمیم درباره شروع یا ادامه درمان باید با در نظر گرفتن سود بالینی در مقابل ریسک ژنتیکی و توسط پزشک متخصص اتخاذ شود.</p>
            <h2 id="sec-ddi" class="text-xl font-bold text-text-header mb-3">تداخلات مهم</h2>
            <p class="mb-4 text-justify text-gray-700">کاربامازپین یک القاکننده قوی آنزیم‌های سیتوکروم P450 (CYP3A4، CYP2C9، CYP2C19) و گلیکوپروتئین-P است. این بدان معناست که CBZ متابولیسم داروهای زیادی را تسریع کرده و سطح آنها را کاهش می‌دهد. مهم‌ترین تداخلات عبارتند از:</p>
            <p class="mb-4 text-justify text-gray-700"><strong>ضد انعقادهای خوراکی:</strong> CBZ سطح وارفارین و نوار آنتی‌کواگولان‌های جدید مثل ریواروکسابان را کاهش می‌دهد و پوشش ضد انعقادی را به خطر می‌اندازد. پایش INR مکرر و احتمالاً تنظیم دوز ضروری است. <strong>ضد ویروس‌های HIV:</strong> پروتئاز اینهیبیتورها و بسیاری از داروهای ضد HIV با CBZ تداخل شدید دارند. <strong>ضد تشنج‌های دیگر:</strong> فنیتوئین، والپروات، لاموتریژین، توپیرامات — همگی ممکن است سطح‌شان تغییر کند. <strong>قرص‌های ضدبارداری خوراکی:</strong> CBZ سطح استروژن و پروژستین را کاهش می‌دهد و پوشش پیشگیری از بارداری را از بین می‌برد؛ روش‌های غیرهورمونال یا دوز بالاتر باید بررسی شوند.</p>
            <p class="mb-4 text-justify text-gray-700">همچنین برخی داروها سطح CBZ را افزایش می‌دهند که می‌تواند به مسمومیت منجر شود: اریترومایسین، کلاریترومایسین، ایزونیازید، آنتی‌فانگال‌های آزول، داروهای ضد افسردگی برخی کلاس‌ها. اگزوبند (آنتاگونیست CYP3A4) سطح CBZ را نیز تغییر می‌دهد. هر تغییر در دارودرمانی باید با پزشک یا داروساز هماهنگ شود. لیست کامل داروها، مکمل‌ها، و گیاهان دارویی را همیشه به‌روز نگه دارید.</p>
            <h2 id="sec-monitor" class="text-xl font-bold text-text-header mb-3">پایش</h2>
            <p class="mb-4 text-justify text-gray-700">پایش استاندارد در طول درمان با CBZ شامل شمارش کامل خون (لکوپنی و آپلازی آرار گلبول قرمز از عوارض نادر اما جدی هستند)، عملکرد کبد (هپاتوتوکسیسیتی نادر اما گزارش شده)، و سطح سدیم خون (هیپوناترمی از عوارض نسبتاً شایع‌تر است) می‌شود. اندازه‌گیری سطح خونی CBZ در صورت عدم کنترل تشنج، بروز علائم مسمومیت (دیپلوپی، آتاکسی، تهوع، گیجی)، شک به عدم پایبندی، یا تداخلات دارویی توصیه می‌شود.</p>
            <p class="mb-4 text-justify text-gray-700">علائمی که نیاز به مراجعه فوری دارند: راش پوستی گسترده یا تاول — حتی اگر ابتدا خفیف به نظر برسد؛ زخم‌های دهانی یا چشمی؛ تب همراه با علائم پوستی؛ زردی پوست یا چشم‌ها؛ خونریزی یا کبودی غیرعادی؛ تشنج‌های جدید یا تغییر الگوی تشنج؛ و احساس شدید خواب‌آلودگی، عدم تعادل، یا دیدن دوتایی که با دوز جدید مرتبط باشد.</p>
            <h2 id="sec-summary" class="text-xl font-bold text-text-header mb-3">جمع‌بندی</h2>
            <p class="mb-6 text-justify text-gray-700">کاربامازپین با پایش مناسب، غربالگری ژنتیکی در جمعیت‌های در معرض خطر، و مدیریت دقیق تداخلات دارویی می‌تواند داروی مؤثر و ایمنی باشد. آگاهی بیمار از علائم هشداردهنده، اهمیت عدم قطع ناگهانی دارو، و لزوم هماهنگی همه تغییرات دارویی با تیم درمان، ارکان اصلی یک درمان موفق هستند. هر علامت پوستی یا سیستمیک جدید را به‌عنوان یک هشدار جدی تلقی کنید.</p>""",
        "body_en": """<h2 id="sec-intro" class="text-xl font-bold text-text-header mb-3">Overview</h2>
            <p class="mb-4 text-justify text-gray-700">Carbamazepine (CBZ) is a dibenzazepine anticonvulsant and mood-stabiliser that has been in clinical use since the 1960s. Its primary mechanism is voltage-gated sodium channel blockade in neuronal membranes, which suppresses the propagation of epileptic discharges. Beyond epilepsy, CBZ is established treatment for neuropathic pain and certain psychiatric conditions. Understanding its pharmacological peculiarities—above all, its powerful enzyme-inducing properties—is essential for safe use.</p>
            <p class="mb-4 text-justify text-gray-700">One of CBZ's most clinically important characteristics is its induction of hepatic cytochrome P450 enzymes, particularly CYP3A4. This accelerates the metabolism of many co-prescribed drugs and of CBZ itself—a phenomenon called autoinduction. During the first 2–4 weeks of therapy, CBZ plasma levels fall substantially as autoinduction develops, so dose re-titration is often necessary. Awareness of this process helps explain why initial symptom control may wane before a stable therapeutic level is achieved.</p>
            <h2 id="sec-use" class="text-xl font-bold text-text-header mb-3">Indications</h2>
            <p class="mb-4 text-justify text-gray-700">Carbamazepine is indicated for focal (partial) seizures—with or without secondary generalisation—and for tonic-clonic (Grand Mal) seizures. It is not recommended for absence epilepsy or juvenile myoclonic epilepsy (JME), where it may paradoxically worsen seizure control. Accurate epilepsy-syndrome classification by a neurologist is therefore mandatory before prescribing CBZ; using it in the wrong epilepsy type causes harm. The usual starting dose is 100–200 mg once or twice daily, titrated over several weeks to the effective maintenance dose of 400–1200 mg/day in divided doses.</p>
            <p class="mb-4 text-justify text-gray-700">Trigeminal neuralgia—characterised by paroxysmal, electric-shock-like facial pain—is one of CBZ's most well-established indications, where it is considered first-line therapy. CBZ is also used in other neuropathic pain syndromes and as a mood stabiliser in bipolar disorder, particularly in patients who have an inadequate response to or cannot tolerate lithium. In psychiatric use, CBZ is typically reserved for specialist initiation and requires close monitoring.</p>
            <h2 id="sec-hla" class="text-xl font-bold text-text-header mb-3">HLA &amp; genetic safety</h2>
            <p class="mb-4 text-justify text-gray-700">Carbamazepine is associated with a rare but potentially fatal cutaneous adverse reaction: Stevens–Johnson Syndrome (SJS) and Toxic Epidermal Necrolysis (TEN). These immune-mediated hypersensitivity reactions—involving extensive epidermal detachment, mucosal involvement, and potential multi-organ failure—can appear within the first two weeks of therapy and carry mortality rates of 10–30%. The reactions are largely irreversible once established, making prevention paramount.</p>
            <p class="mb-4 text-justify text-gray-700">Large pharmacogenomic studies, originating largely from Taiwan and subsequently replicated across Asia, demonstrated that the HLA-B*15:02 allele is a strong predictor of CBZ-induced SJS/TEN. This allele is carried by 6–8% of Han Chinese, ~8% of Thai people, ~6% of Malaysians, and ~2–3% of South Asians; the prevalence in populations of European or Iranian origin is considerably lower. The US FDA and multiple international regulatory bodies now recommend HLA-B*15:02 screening before initiating CBZ in patients of Asian ancestry.</p>
            <p class="mb-4 text-justify text-gray-700">A second allele, HLA-A*31:01, is associated with less severe but still clinically significant hypersensitivity reactions (maculopapular exanthem, drug reaction with eosinophilia and systemic symptoms) predominantly in European and Japanese populations. Results of HLA testing should be reviewed with the prescribing physician. The decision to initiate or continue CBZ must weigh clinical benefit against genetic risk and is ultimately a specialist judgement. A negative test does not eliminate all SJS risk; vigilance for cutaneous symptoms remains necessary regardless.</p>
            <h2 id="sec-ddi" class="text-xl font-bold text-text-header mb-3">Drug interactions</h2>
            <p class="mb-4 text-justify text-gray-700">Carbamazepine is one of the most potent inducers of cytochrome P450 enzymes (CYP3A4, CYP2C9, CYP2C19) and P-glycoprotein in clinical medicine. This means CBZ accelerates the metabolism of a very large number of co-prescribed drugs, often reducing their plasma concentrations to subtherapeutic levels. Key interactions include:</p>
            <p class="mb-4 text-justify text-gray-700"><strong>Oral anticoagulants:</strong> CBZ substantially lowers warfarin and direct oral anticoagulant (DOAC) levels, compromising anticoagulation. Frequent INR monitoring and dose adjustment are required. <strong>Antiretrovirals:</strong> Many HIV protease inhibitors and non-nucleoside reverse transcriptase inhibitors have serious pharmacokinetic interactions with CBZ; co-prescription generally requires specialist review. <strong>Other antiseizure medicines:</strong> Levels of phenytoin, lamotrigine, topiramate, and valproate may all be altered; effects are bidirectional. <strong>Hormonal contraceptives:</strong> CBZ reduces oestrogen and progestogen levels, abolishing contraceptive efficacy. Non-hormonal contraception or specialist-guided alternative methods are required.</p>
            <p class="mb-4 text-justify text-gray-700">Conversely, some drugs raise CBZ levels, risking toxicity: erythromycin and clarithromycin, isoniazid, azole antifungals, some calcium channel blockers, and certain antidepressants. Toxic signs of elevated CBZ include diplopia, ataxia, nausea, vomiting, and confusion. Always provide a complete and updated medication list—including supplements and herbal preparations—to every prescriber and pharmacist you see.</p>
            <h2 id="sec-monitor" class="text-xl font-bold text-text-header mb-3">Monitoring</h2>
            <p class="mb-4 text-justify text-gray-700">Standard monitoring during CBZ therapy includes: complete blood count (aplastic anaemia and agranulocytosis are rare but serious), liver function tests (hepatotoxicity is uncommon but reported), and serum sodium (hyponatraemia due to SIADH-like effect occurs in up to 5% of patients, particularly the elderly). Measurement of plasma CBZ levels is recommended when seizures are not controlled, signs of toxicity appear, non-adherence is suspected, or significant drug interactions occur. Therapeutic plasma concentrations are generally 4–12 mg/L.</p>
            <p class="mb-4 text-justify text-gray-700">Seek emergency care immediately for: any rash—even initially mild—especially if accompanied by fever, mucosal lesions, or eye pain; mouth sores or eye redness; jaundice; unusual bleeding or bruising; new or worsening seizures; and severe dizziness, imbalance, or double vision that correlates with a dose change. These signs may herald serious, rapidly progressive adverse reactions where early intervention is life-saving.</p>
            <h2 id="sec-summary" class="text-xl font-bold text-text-header mb-3">Summary</h2>
            <p class="mb-6 text-justify text-gray-700">With appropriate genetic screening, structured monitoring, and careful management of drug interactions, carbamazepine can be both effective and safe. Patient awareness of warning signs, adherence to prescribed dosing schedules, avoidance of abrupt discontinuation (which can precipitate rebound seizures), and coordination of all medication changes through the treating team are the pillars of successful long-term therapy. Treat any new skin, mucosal, or systemic symptom as a potential warning sign and seek prompt medical attention.</p>""",
        "img": "https://images.unsplash.com/photo-1579684385127-1ef15d5081c8?auto=format&fit=crop&w=1600&q=80",
        "img_alt_fa": "داروهای ضد تشنج",
        "img_alt_en": "Antiseizure medication",
        "cap_fa": "مصرف کاربامازپین نیازمند پایش منظم، غربالگری ژنتیکی، و مدیریت دقیق تداخلات دارویی است.",
        "cap_en": "Carbamazepine therapy requires regular monitoring, genetic screening, and careful management of drug interactions.",
        "refs_fa": """<section id="refs" class="pt-6 border-t border-gray-200">
                <h2 class="text-lg font-bold text-gray-900 mb-4">منابع</h2>
                <ol class="list-decimal list-inside text-xs text-gray-500 space-y-2" dir="ltr">
                    <li>Chen P et al. Carbamazepine-induced toxic effects and HLA-B*15:02 screening in Taiwan. <em>N Engl J Med.</em> 2011;364:1126–1133.</li>
                    <li>CPIC Guideline for HLA genotype and use of carbamazepine and oxcarbazepine. <em>Clin Pharmacol Ther.</em> 2023;113:239–264.</li>
                    <li>FDA Drug Safety Communication — Dangerous or even fatal skin reactions with carbamazepine. 2013.</li>
                    <li>Patsalos PN et al. Antiepileptic drug interactions — A clinical guide. <em>Epilepsia.</em> 2016;57:1323–1358.</li>
                    <li>UpToDate — Carbamazepine: drug information. 2024.</li>
                    <li>Man CB et al. Association between HLA-B*15:02 allele and antiepileptic drug-induced cutaneous reactions. <em>Epilepsia.</em> 2007;48:1015–1018.</li>
                </ol>
            </section>""",
        "refs_en": """<section id="refs" class="pt-6 border-t border-gray-200">
                <h2 class="text-lg font-bold text-gray-900 mb-4">References</h2>
                <ol class="list-decimal list-inside text-xs text-gray-500 space-y-2">
                    <li>Chen P et al. Carbamazepine-induced toxic effects and HLA-B*15:02 screening in Taiwan. <em>N Engl J Med.</em> 2011;364:1126–1133.</li>
                    <li>CPIC Guideline for HLA genotype and use of carbamazepine and oxcarbazepine. <em>Clin Pharmacol Ther.</em> 2023;113:239–264.</li>
                    <li>FDA Drug Safety Communication — Dangerous or even fatal skin reactions with carbamazepine. 2013.</li>
                    <li>Patsalos PN et al. Antiepileptic drug interactions — A clinical guide. <em>Epilepsia.</em> 2016;57:1323–1358.</li>
                    <li>UpToDate — Carbamazepine: drug information. 2024.</li>
                    <li>Man CB et al. Association between HLA-B*15:02 allele and antiepileptic drug-induced cutaneous reactions. <em>Epilepsia.</em> 2007;48:1015–1018.</li>
                </ol>
            </section>""",
    },
    # ─────────────────────────────────────────────────────────────────────────
    # 4. Carbamazepine: safety tips and usage guide
    # ─────────────────────────────────────────────────────────────────────────
    {
        "slug": "carbaram-safe-usage",
        "title_fa": "کاربامازپین: نکات ایمنی و راهنمای کامل مصرف",
        "title_en": "Carbamazepine: complete safety tips and usage guide",
        "abstract_fa": "راهنمای عملی برای بیماران درباره مصرف صحیح، دوزدهی، آزمایش‌های دوره‌ای، علائم هشدار، و توصیه‌هایی برای زندگی بهتر با کاربامازپین.",
        "abstract_en": "A practical patient guide covering correct use, dosing schedules, periodic testing, warning signs, and lifestyle recommendations for people taking carbamazepine.",
        "summary_id": "sec-summary",
        "toc_fa": [
            ("sec-intro", "مرور"),
            ("sec-dose", "دوز و زمان مصرف"),
            ("sec-tests", "آزمایش‌های دوره‌ای"),
            ("sec-warn", "علائم هشدار"),
            ("sec-summary", "جمع‌بندی"),
        ],
        "toc_en": [
            ("sec-intro", "Overview"),
            ("sec-dose", "Dosing schedule"),
            ("sec-tests", "Periodic tests"),
            ("sec-warn", "Warning signs"),
            ("sec-summary", "Summary"),
        ],
        "body_fa": """<h2 id="sec-intro" class="text-xl font-bold text-text-header mb-3">مرور</h2>
            <p class="mb-4 text-justify text-gray-700">کاربامازپین داروی بلندمدتی است که کنترل تشنج، درد عصبی، یا ثبات خلق را فقط در صورت پایبندی منظم حفظ می‌کند. قطع ناگهانی دارو، فراموش کردن چند دوز پیاپی، یا دوزدهی نامنظم می‌تواند به تشنج بازگشتی (rebound seizures)، ناپایداری خلق، یا شدت‌گرفتن درد منجر شود. درک اصول درست مصرف دارو به بیمار اجازه می‌دهد از حداکثر فایده درمانی بهره‌مند شود و عوارض را به حداقل برساند.</p>
            <p class="mb-4 text-justify text-gray-700">کاربامازپین ویژگی «اتواینداکشن» دارد: در هفته‌های اول درمان، آنزیم‌های کبدی که کاربامازپین را تجزیه می‌کنند به‌تدریج فعال‌تر می‌شوند و سطح دارو در خون کاهش می‌یابد. این پدیده طبیعی است و پزشک ممکن است دوز را چند هفته پس از شروع افزایش دهد. همچنین بیماری، استرس، سایر داروها، و حتی برخی غذاها می‌توانند سطح کاربامازپین را تغییر دهند.</p>
            <h2 id="sec-dose" class="text-xl font-bold text-text-header mb-3">دوز و زمان مصرف</h2>
            <p class="mb-4 text-justify text-gray-700">کاربامازپین در فرمولاسیون‌های مختلفی عرضه می‌شود: قرص استاندارد (معمولاً ۲ تا ۴ بار در روز)، کپسول و قرص آهسته‌رهش (Controlled/Extended Release — معمولاً ۲ بار در روز)، و شربت (برای کودکان یا بیمارانی که قرص را نمی‌توانند ببلعند). فرمولاسیون آهسته‌رهش سطح خونی یکنواخت‌تری ایجاد می‌کند و عوارض جانبی وابسته به قله (مثل سرگیجه و دوبینی) را کاهش می‌دهد.</p>
            <p class="mb-4 text-justify text-gray-700">قرص‌های آهسته‌رهش را نشکنید، آسیاب نکنید، یا نجوید مگر اینکه پزشک یا داروساز صریحاً اجازه داده باشد — شکستن این قرص‌ها آزاد‌سازی کنترل‌شده را مختل کرده و ممکن است دوز بیش از حد یا دوز ناکافی ایجاد کند. دارو را ترجیحاً همراه با غذا مصرف کنید؛ این کار جذب را منظم‌تر می‌کند و عوارض گوارشی (تهوع، سوء‌هاضمه) را کاهش می‌دهد. دوزها را در فاصله‌های زمانی برابر مصرف کنید — برای نمونه، اگر دو بار در روز تجویز شده، هر ۱۲ ساعت یک بار.</p>
            <p class="mb-4 text-justify text-gray-700">اگر یک دوز را فراموش کردید: اگر زمان زیادی نگذشته، بلافاصله بخورید. اما اگر به وقت دوز بعدی نزدیک شده‌اید، دوز فراموش‌شده را نخورید و ادامه دهید — هرگز دو دوز را با هم نخورید. مصرف همزمان با الکل توصیه نمی‌شود زیرا می‌تواند تأثیر سدیم کانال‌ها را تغییر داده و اثرات جانبی CNS (خواب‌آلودگی، سرگیجه) را تشدید کند.</p>
            <h2 id="sec-tests" class="text-xl font-bold text-text-header mb-3">آزمایش‌های دوره‌ای</h2>
            <p class="mb-4 text-justify text-gray-700">آزمایش‌هایی که پزشک معمولاً در طول درمان با کاربامازپین درخواست می‌کند عبارتند از:</p>
            <p class="mb-4 text-justify text-gray-700"><strong>شمارش کامل خون (CBC):</strong> برای پایش لکوسیت‌ها، اریتروسیت‌ها، و پلاکت‌ها. کاربامازپین به‌ندرت می‌تواند سرکوب مغز استخوان ایجاد کند. <strong>آنزیم‌های کبدی (ALT، AST، ALP):</strong> کبد عضو اصلی متابولیسم CBZ است. افزایش خفیف آنزیم‌ها در اوایل درمان نسبتاً شایع و اغلب گذراست، اما افزایش پیش‌رونده نیاز به توجه دارد. <strong>سدیم سرم (Na+):</strong> CBZ می‌تواند از طریق مکانیسمی شبیه SIADH باعث هیپوناترمی (کاهش سدیم خون) شود — به‌ویژه در افراد مسن. علائم هیپوناترمی شامل سردرد، تهوع، خواب‌آلودگی، و گیجی است. <strong>سطح کاربامازپین در خون:</strong> معمولاً وقتی تشنج‌ها کنترل نمی‌شوند، علائم مسمومیت وجود دارد، یا تداخل دارویی مشکوک است اندازه‌گیری می‌شود. محدوده درمانی معمول ۴ تا ۱۲ میکروگرم در میلی‌لیتر است.</p>
            <p class="mb-4 text-justify text-gray-700">آزمایش‌ها را در فواصل تعیین‌شده انجام دهید حتی اگر احساس می‌کنید کاملاً خوب هستید. نتایج آزمایش‌ها اغلب قبل از بروز علائم قابل مشاهده تغییر می‌کنند. نتایج را نزد خود نگه دارید و در هر ویزیت با پزشک مرور کنید.</p>
            <h2 id="sec-warn" class="text-xl font-bold text-text-header mb-3">علائم هشدار</h2>
            <p class="mb-4 text-justify text-gray-700">بلافاصله با اورژانس تماس بگیرید یا به اورژانس بیمارستان مراجعه کنید اگر یکی از موارد زیر رخ داد: <strong>راش پوستی گسترده</strong> — به‌ویژه اگر با تاول، پوسته‌پوسته‌شدن، یا درگیری صورت همراه باشد؛ <strong>زخم‌های دهانی یا لثه‌ای؛ درد یا قرمزی چشم‌ها؛</strong> تب همزمان با هر کدام از علائم فوق — این ترکیب می‌تواند نشانه SJS/TEN باشد که یک اورژانس پزشکی است.</p>
            <p class="mb-4 text-justify text-gray-700">همچنین در اسرع وقت با پزشک تماس بگیرید اگر: <strong>زردی پوست یا سفیدی چشم‌ها</strong> (نشانه احتمالی اختلال کبدی)؛ <strong>خونریزی یا کبودی غیرمعمول</strong> (نشانه احتمالی سرکوب مغز استخوان)؛ <strong>تشنج جدید یا تغییر شکل تشنج‌های موجود؛ کاهش شدید سطح هوشیاری یا گیجی؛ تورم دست‌ها یا پاها؛</strong> یا هر گونه علامت ناخوشایند جدیدی که با شروع یا تغییر دوز کاربامازپین مصادف شده باشد.</p>
            <p class="mb-4 text-justify text-gray-700">درباره رانندگی و کار با ماشین‌آلات: کاربامازپین می‌تواند در ابتدا باعث خواب‌آلودگی، سرگیجه، یا کندی واکنش شود. تا زمانی که اثر دارو بر شما مشخص نشده، از رانندگی و کارهای نیازمند هوشیاری کامل خودداری کنید. وضعیت قانونی رانندگی بیماران مبتلا به صرع در هر کشور متفاوت است و باید از پزشک استعلام گرفته شود.</p>
            <h2 id="sec-summary" class="text-xl font-bold text-text-header mb-3">جمع‌بندی</h2>
            <p class="mb-6 text-justify text-gray-700">با انضباط در مصرف دارو، انجام منظم آزمایش‌های دوره‌ای، شناخت علائم هشدار، و ارتباط باز با تیم درمان، می‌توان از کاربامازپین به‌صورت ایمن و مؤثر بهره برد. هرگز دارو را بدون مشاوره پزشک قطع نکنید — حتی اگر احساس بهبود کامل می‌کنید. قطع ناگهانی می‌تواند خطرناک باشد. بیمار آگاه، پرسشگر، و همکار با پزشک بهترین نتایج درمانی را تجربه می‌کند.</p>""",
        "body_en": """<h2 id="sec-intro" class="text-xl font-bold text-text-header mb-3">Overview</h2>
            <p class="mb-4 text-justify text-gray-700">Carbamazepine is a long-term medication that maintains seizure control, neuropathic pain relief, or mood stability only through consistent, uninterrupted use. Abrupt discontinuation, missing several consecutive doses, or irregular dosing can trigger rebound seizures, mood instability, or pain flares. Understanding correct usage principles allows patients to maximise therapeutic benefit while minimising the risk of avoidable complications.</p>
            <p class="mb-4 text-justify text-gray-700">CBZ undergoes autoinduction: during the first 2–4 weeks of therapy, the hepatic enzymes responsible for CBZ metabolism become increasingly active, causing plasma drug levels to fall. This natural process means the prescriber may need to increase the dose after the initial stabilisation period. Intercurrent illness, other medications, and even certain foods can also alter CBZ plasma concentrations.</p>
            <h2 id="sec-dose" class="text-xl font-bold text-text-header mb-3">Dosing schedule</h2>
            <p class="mb-4 text-justify text-gray-700">Carbamazepine is available in several formulations: standard-release tablets (usually 2–4 times daily), controlled- or extended-release tablets and capsules (usually twice daily), and oral suspension (for children or patients who cannot swallow tablets). Controlled-release formulations produce more stable plasma levels, reducing peak-related adverse effects such as dizziness and double vision. Do not crush, break, or chew extended-release tablets unless the prescriber or pharmacist has explicitly confirmed it is safe for that particular product—doing so disrupts controlled delivery and risks under- or overdosing.</p>
            <p class="mb-4 text-justify text-gray-700">Take CBZ with food whenever possible: this smooths absorption and reduces gastrointestinal side effects such as nausea. Space doses evenly throughout the day—for a twice-daily regimen, approximately every 12 hours. If you miss a dose: take it as soon as you remember, unless it is close to the time of your next scheduled dose—in which case skip the missed dose and continue normally. Never take a double dose to make up for a missed one. Avoid alcohol, which can amplify CNS side effects (drowsiness, dizziness) and destabilise sodium channel function.</p>
            <p class="mb-4 text-justify text-gray-700">When travelling across time zones, discuss the timing adjustment with your pharmacist in advance. Carry an adequate supply of medication and a letter from your prescriber (particularly when travelling internationally). Keep CBZ at room temperature, away from moisture and direct sunlight; do not store it in the bathroom or glove compartment.</p>
            <h2 id="sec-tests" class="text-xl font-bold text-text-header mb-3">Periodic tests</h2>
            <p class="mb-4 text-justify text-gray-700">Tests your doctor will typically request during CBZ therapy include:</p>
            <p class="mb-4 text-justify text-gray-700"><strong>Complete blood count (CBC):</strong> Monitors white cells, red cells, and platelets. Although rare, CBZ can cause leucopenia or aplastic anaemia. <strong>Liver enzymes (ALT, AST, ALP):</strong> Mild early rises are common and often transient; progressive elevation requires evaluation. <strong>Serum sodium (Na+):</strong> CBZ can cause hyponatraemia through an SIADH-like mechanism, especially in older adults. Symptoms include headache, nausea, drowsiness, and confusion. <strong>Plasma CBZ concentration:</strong> Measured when seizures break through, toxicity signs appear, non-adherence is suspected, or significant drug interactions occur. The usual therapeutic range is 4–12 mcg/mL.</p>
            <p class="mb-4 text-justify text-gray-700">Complete all scheduled tests even when feeling entirely well—laboratory abnormalities often precede clinical symptoms by days to weeks. Keep copies of all results and review them at each clinic visit. Use a medication record card or app to track test dates and values over time.</p>
            <h2 id="sec-warn" class="text-xl font-bold text-text-header mb-3">Warning signs</h2>
            <p class="mb-4 text-justify text-gray-700">Call emergency services or go to the nearest emergency department immediately if you develop: <strong>a widespread skin rash</strong>—especially with blistering, peeling, or facial involvement; <strong>mouth sores or gum ulcers; painful or red eyes;</strong> or <strong>fever</strong> occurring together with any of the above. This combination may indicate Stevens–Johnson Syndrome or Toxic Epidermal Necrolysis (SJS/TEN), which is a dermatological emergency requiring immediate hospitalisation.</p>
            <p class="mb-4 text-justify text-gray-700">Contact your doctor promptly (same day if possible) for: <strong>yellowing of the skin or whites of the eyes</strong> (possible liver injury); <strong>unexplained bruising or bleeding</strong> (possible bone marrow suppression); <strong>new or different seizures;</strong> <strong>severe or sudden confusion or loss of consciousness;</strong> <strong>swelling of hands or feet;</strong> or any new, distressing symptom that coincides with starting CBZ or changing the dose. Patients on CBZ who develop suicidal thoughts should contact their mental health care team or emergency services immediately—antiseizure medicines can rarely affect mood.</p>
            <p class="mb-4 text-justify text-gray-700">Regarding driving and operating machinery: CBZ may cause drowsiness, dizziness, blurred vision, or slowed reaction times, particularly during initiation and dose increases. Avoid driving or performing tasks requiring full alertness until you know how the medication affects you. Legal driving restrictions for people with epilepsy vary by country; ask your physician what applies in your jurisdiction.</p>
            <h2 id="sec-summary" class="text-xl font-bold text-text-header mb-3">Summary</h2>
            <p class="mb-6 text-justify text-gray-700">By adhering to prescribed doses, completing all scheduled laboratory tests, recognising warning signs early, and maintaining open communication with the treatment team, carbamazepine can be used safely and effectively long-term. Never stop CBZ without medical guidance—even if you feel completely well—as abrupt discontinuation carries a real risk of rebound seizures. An informed, questioning, and collaborative patient achieves the best treatment outcomes.</p>""",
        "img": "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?auto=format&fit=crop&w=1600&q=80",
        "img_alt_fa": "قرص‌های کاربامازپین",
        "img_alt_en": "Carbamazepine tablets",
        "cap_fa": "رعایت دقیق دستورالعمل پزشک در مصرف کاربامازپین برای کنترل ایمن تشنج ضروری است.",
        "cap_en": "Careful adherence to prescribing instructions is essential for safe seizure control with carbamazepine.",
        "refs_fa": """<section id="refs" class="pt-6 border-t border-gray-200">
                <h2 class="text-lg font-bold text-gray-900 mb-4">منابع</h2>
                <ol class="list-decimal list-inside text-xs text-gray-500 space-y-2" dir="ltr">
                    <li>FDA Prescribing Information — Carbamazepine (Tegretol). Revised 2023.</li>
                    <li>Zaccara G, Perucca E. Interactions between antiepileptic drugs, and between antiepileptic drugs and other drugs. <em>Epileptic Disord.</em> 2014;16:409–431.</li>
                    <li>Perucca E et al. Optimizing the clinical use of antiepileptic drugs. <em>Epilepsia.</em> 2018;59(Suppl 3):S1–S11.</li>
                    <li>UpToDate — Management of epilepsy in adults. 2024.</li>
                    <li>BNF — Carbamazepine: prescribing information. NICE. 2024.</li>
                    <li>Glauser T et al. ILAE Updated Guideline Evidence-Based Antiepileptic Drug Treatment. <em>Epilepsia.</em> 2013;54:551–563.</li>
                </ol>
            </section>""",
        "refs_en": """<section id="refs" class="pt-6 border-t border-gray-200">
                <h2 class="text-lg font-bold text-gray-900 mb-4">References</h2>
                <ol class="list-decimal list-inside text-xs text-gray-500 space-y-2">
                    <li>FDA Prescribing Information — Carbamazepine (Tegretol). Revised 2023.</li>
                    <li>Zaccara G, Perucca E. Interactions between antiepileptic drugs, and between antiepileptic drugs and other drugs. <em>Epileptic Disord.</em> 2014;16:409–431.</li>
                    <li>Perucca E et al. Optimizing the clinical use of antiepileptic drugs. <em>Epilepsia.</em> 2018;59(Suppl 3):S1–S11.</li>
                    <li>UpToDate — Management of epilepsy in adults. 2024.</li>
                    <li>BNF — Carbamazepine: prescribing information. NICE. 2024.</li>
                    <li>Glauser T et al. ILAE Updated Guideline Evidence-Based Antiepileptic Drug Treatment. <em>Epilepsia.</em> 2013;54:551–563.</li>
                </ol>
            </section>""",
    },
]


def write_fa(spec):
    title = spec["title_fa"]
    refs = spec.get("refs_fa", REFS_FA)
    out = prefix.replace(
        "<title>آنفلوآنزا — پیشگیری با واکسیناسیون، درمان و راهنمای جامع | راموفارمین</title>",
        f"<title>{title} | راموفارمین</title>",
    )
    out = replace_sidebar_toc(out, toc_fa(spec["toc_fa"]))
    out = replace_sidebar_abstract(out, title, spec["abstract_fa"], spec["summary_id"])
    fig = f"""<figure class="a-secmedia mb-6">
                <img loading="lazy" src="{spec["img"]}" alt="{spec["img_alt_fa"]}" class="w-full h-auto object-cover rounded-lg border border-gray-200">
                <figcaption class="text-xs text-gray-500 mt-2">{spec["cap_fa"]}</figcaption>
            </figure>"""
    inner = build_article_inner(
        fa_header(title, spec["abstract_fa"]),
        fig,
        spec["body_fa"],
        refs,
        '{"@context":"https://schema.org","@type":"Article","headline":"'
        + title.replace('"', "'")
        + '","inLanguage":"fa","author":{"@type":"Organization","name":"Ramopharmin Editorial"}}',
    )
    new_art = f'<article class="lg:col-span-6 bg-white shadow-sm border border-gray-200 rounded-lg p-6 md:p-10">\n\n            {inner}\n\n        </article>'
    out = out + new_art + suffix
    (ROOT / "articles" / f"{spec['slug']}.html").write_text(out, encoding="utf-8")


def en_base_prefix():
    o = prefix.replace("lang=\"fa\"", "lang=\"en\"").replace('dir="rtl"', 'dir="ltr"')
    o = o.replace(
        "https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap",
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    )
    o = o.replace("['Vazirmatn', 'sans-serif']", "['Inter', 'system-ui', 'sans-serif']")
    o = o.replace("مجله علمی راموفارمین", "Ramopharmin Health Journal")
    o = o.replace(
        'href="../fa/index.html" class="text-lg font-medium no-underline text-gray-700 hover:text-ramo-blue">خانه</a>',
        'href="../en/index.html" class="text-lg font-medium no-underline text-gray-700 hover:text-ramo-blue">Home</a>',
    )
    o = o.replace("درباره ما", "About")
    o = o.replace("اعضای هیات مدیره", "Board of directors")
    o = o.replace("مدیران اجرایی", "Management")
    o = o.replace("محصولات", "Products")
    o = o.replace("بر اساس شکل دارویی", "By dosage form")
    o = o.replace("بر اساس گروه درمانی", "By therapeutic class")
    o = o.replace(
        'href="../fa/magazine/" class="text-lg font-medium no-underline text-gray-700 hover:text-ramo-blue">مجله سلامت</a>',
        'href="../fa/magazine/" class="text-lg font-medium no-underline text-gray-700 hover:text-ramo-blue">Magazine</a>',
    )
    o = o.replace("جستجو", "Search")
    o = o.replace("دانلود PDF", "Print / PDF")
    o = o.replace(
        'href="../fa/index.html" class="block py-3 px-2 rounded hover:bg-gray-50 text-gray-800">خانه</a>',
        'href="../en/index.html" class="block py-3 px-2 rounded hover:bg-gray-50 text-gray-800">Home</a>',
    )
    o = o.replace('<span>درباره ما</span>', "<span>About</span>")
    o = o.replace('<span>محصولات</span>', "<span>Products</span>")
    o = o.replace(
        'class="block py-3 px-2 rounded hover:bg-gray-50 text-gray-800">مجله سلامت</a>',
        'class="block py-3 px-2 rounded hover:bg-gray-50 text-gray-800">Magazine</a>',
    )
    o = o.replace('<div class="text-sm font-bold text-ramo-blue">راموفارمین</div>', '<div class="text-sm font-bold text-ramo-blue">Ramopharmin</div>')
    return o


def write_en(spec):
    title = spec["title_en"]
    refs = spec.get("refs_en", REFS_EN)
    p = en_base_prefix()
    p = p.replace(
        "<title>آنفلوآنزا — پیشگیری با واکسیناسیون، درمان و راهنمای جامع | راموفارمین</title>",
        f"<title>{title} | Ramopharmin</title>",
    )
    # TOC title + ul
    p = replace_sidebar_toc(p, toc_en(spec["toc_en"]), "فهرست مطالب")
    p = p.replace(
        '<h3 class="font-bold text-gray-900 mb-3 text-sm border-b pb-2">فهرست مطالب</h3>',
        '<h3 class="font-bold text-gray-900 mb-3 text-sm border-b pb-2">Contents</h3>',
    )
    p = replace_sidebar_abstract(p, title, spec["abstract_en"], spec["summary_id"])
    p = p.replace("عنوان مقاله", "Article")
    fig = f"""<figure class="a-secmedia mb-6">
                <img loading="lazy" src="{spec["img"]}" alt="{spec["img_alt_en"]}" class="w-full h-auto object-cover rounded-lg border border-gray-200">
                <figcaption class="text-xs text-gray-500 mt-2">{spec["cap_en"]}</figcaption>
            </figure>"""
    inner = build_article_inner_en(
        en_header(title, spec["abstract_en"]),
        fig,
        spec["body_en"],
        refs,
        '{"@context":"https://schema.org","@type":"Article","headline":"'
        + title.replace('"', "'")
        + '","inLanguage":"en","author":{"@type":"Organization","name":"Ramopharmin Editorial"}}',
    )
    new_art = f'<article class="lg:col-span-6 bg-white shadow-sm border border-gray-200 rounded-lg p-6 md:p-10">\n\n            {inner}\n\n        </article>'
    p = p + new_art + suffix
    p = (
        p.replace("درباره نویسندگان", "About the authors")
        .replace("واحد تحریریه راموفارمین", "Ramopharmin Editorial")
        .replace("تحریریه مجله سلامت راموفارمین", "Ramopharmin Health Desk")
        .replace("ارتباط با تحریریه", "Contact editorial")
        .replace("بیشتر بدانید", "Learn more")
        .replace("داروسازی راموفارمین", "Ramopharmin Pharmaceuticals")
    )
    p = p.replace("مشاهده جمع‌بندی", "Summary")
    (ROOT / "articles" / f"{spec['slug']}-en.html").write_text(p, encoding="utf-8")


def main():
    for spec in SPECS:
        write_fa(spec)
        write_en(spec)
    print("Wrote", len(SPECS) * 2, "files under articles/")


if __name__ == "__main__":
    main()
