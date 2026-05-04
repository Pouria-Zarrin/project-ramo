#!/usr/bin/env python3
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
    {
        "slug": "azathioprine-comparison",
        "title_fa": "آزاتیوپرین در مقایسه با سایر مهارکننده‌های ایمنی",
        "title_en": "Azathioprine compared with other immunosuppressants",
        "abstract_fa": "مروری بر تفاوت‌های اثربخشی، ایمنی، پایش آزمایشگاهی و هزینه بین آزاتیوپرین و سایر مهارکننده‌های رایج برای تصمیم‌گیری بالینی آگاهانه‌تر.",
        "abstract_en": "A concise comparison of efficacy, safety, laboratory monitoring, and cost between azathioprine and other common immunosuppressants.",
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
            ("sec-monitor", "Monitoring"),
            ("sec-summary", "Summary"),
        ],
        "body_fa": """<h2 id="sec-intro" class="text-xl font-bold text-text-header mb-3">مرور</h2>
            <p class="mb-4 text-justify text-gray-700">مهارکننده‌های ایمنی در بیماری‌های خودایمنی و پیوند عضو ستون فقرات درمان مدرن هستند. آزاتیوپرین پس از متابولیسم به متابولیت‌های فعال تیوپورین تبدیل می‌شود و تکثیر لنفوسیت‌ها را مهار می‌کند. انتخاب دارو به تشخیص، سن، باروری، عملکرد کبد و کلیه و خطر عفونت بستگی دارد.</p>
            <h2 id="sec-aza" class="text-xl font-bold text-text-header mb-3">نقش آزاتیوپرین</h2>
            <p class="mb-4 text-justify text-gray-700">در لوپوس، آرتریت روماتوئید، واسکولیت‌ها و پیوند، AZA سابقه طولانی دارد. پایش TPMT/NUDT15 در شروع، شمارش خون دوره‌ای و آنزیم‌های کبدی ضروری است. تداخل خطرناک با آلوپورینول بدون تنظیم دوز تخصصی ممنوع است.</p>
            <h2 id="sec-mmf" class="text-xl font-bold text-text-header mb-3">میکوفنولات موفتیل</h2>
            <p class="mb-4 text-justify text-gray-700">MMF در لوپوس کلیوی و پیوند رایج است و مهار مسیر سنتز نوکلئوتید پورین را هدف می‌گیرد. تحمل گوارشی گاه مانع دوز هدف می‌شود؛ پایش عفونت و خون ادامه دارد.</p>
            <h2 id="sec-mtx" class="text-xl font-bold text-text-header mb-3">متوترکسات و سایرین</h2>
            <p class="mb-4 text-justify text-gray-700">MTX پایه درمان آرتریت روماتوئید است. سیکلوسپورین/تاکرولیموس در پیوند برجسته‌اند. بیولوژیک‌ها در بیماری مقاوم نقش دارند اما عفونت و هزینه را وزن کنید.</p>
            <h2 id="sec-monitor" class="text-xl font-bold text-text-header mb-3">پایش و انتخاب</h2>
            <p class="mb-4 text-justify text-gray-700">همه این داروها نیازمند پیگیری منظم آزمایشگاهی و بالینی‌اند. تصمیم نهایی باید با متخصص گرفته شود؛ این متن جایگزین ویزیت پزشکی نیست.</p>
            <h2 id="sec-summary" class="text-xl font-bold text-text-header mb-3">جمع‌بندی</h2>
            <p class="mb-6 text-justify text-gray-700">آزاتیوپرین همچنان گزینه معتبر در بسیاری از مسیرهای درمانی است؛ بهترین انتخاب فردی و تیمی است.</p>""",
        "body_en": """<h2 id="sec-intro" class="text-xl font-bold text-text-header mb-3">Overview</h2>
            <p class="mb-4 text-justify text-gray-700">Immunosuppressants anchor autoimmune and transplant care. Azathioprine is metabolized to active thiopurines that limit lymphocyte proliferation. Selection depends on diagnosis, organ function, fertility, and infection risk.</p>
            <h2 id="sec-aza" class="text-xl font-bold text-text-header mb-3">Azathioprine</h2>
            <p class="mb-4 text-justify text-gray-700">Long track record in lupus, arthritis, vasculitis, and transplant. Requires TPMT/NUDT15 assessment where available, CBC and liver monitoring. Allopurinol co-therapy can be lethal without specialist dose adjustment.</p>
            <h2 id="sec-mmf" class="text-xl font-bold text-text-header mb-3">Mycophenolate</h2>
            <p class="mb-4 text-justify text-gray-700">Common in lupus nephritis and transplant; GI tolerance may limit dose. Ongoing CBC and infection surveillance remain essential.</p>
            <h2 id="sec-mtx" class="text-xl font-bold text-text-header mb-3">Methotrexate & others</h2>
            <p class="mb-4 text-justify text-gray-700">MTX is foundational in RA. Calcineurin inhibitors dominate many transplant protocols. Biologics address refractory disease with distinct safety and cost trade-offs.</p>
            <h2 id="sec-monitor" class="text-xl font-bold text-text-header mb-3">Monitoring</h2>
            <p class="mb-4 text-justify text-gray-700">All agents need scheduled labs and clinical review. This article is educational only—not a substitute for specialist care.</p>
            <h2 id="sec-summary" class="text-xl font-bold text-text-header mb-3">Summary</h2>
            <p class="mb-6 text-justify text-gray-700">Azathioprine remains a valid option; the best regimen is individualized with your physician.</p>""",
        "img": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1600&q=80",
        "img_alt_fa": "آزمایشگاه",
        "img_alt_en": "Laboratory",
        "cap_fa": "پایش آزمایشگاهی در درمان‌های ایمنی‌سرکوب کننده اهمیت دارد.",
        "cap_en": "Laboratory monitoring is central to safe immunosuppressive therapy.",
    },
    {
        "slug": "azathioprine-organ-transplant",
        "title_fa": "آزاتیوپرین در پیوند اعضا",
        "title_en": "Azathioprine in organ transplantation",
        "abstract_fa": "نقش آزاتیوپرین در پیشگیری از رد پیوند، رژیم‌های ترکیبی، دوزدهی، پایش آزمایشگاهی و مراقبت بلندمدت در بیماران پیوندی.",
        "abstract_en": "Role of azathioprine in rejection prophylaxis, combination regimens, dosing, monitoring, and long-term transplant care.",
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
            <p class="mb-4 text-justify text-gray-700">پیوند کلیه، کبد یا قلب نیازمند سرکوب ایمنی هدفمند است. آزاتیوپرین دهه‌ها در کنار گلوکورتیکوئید و سیکلوسپورین/تاکرولیموس یا میکوفنولات استفاده شده است.</p>
            <h2 id="sec-reject" class="text-xl font-bold text-text-header mb-3">پیشگیری از رد</h2>
            <p class="mb-4 text-justify text-gray-700">هدف مهار پاسخ T و B علیه آنتی‌ژن‌های پیوند است. رژیم دقیق بسته به پروتکل مرکز و نوع پیوند متفاوت است؛ هرگز دوز یا قطع دارو بدون هماهنگی تیم پیوند انجام نشود.</p>
            <h2 id="sec-combo" class="text-xl font-bold text-text-header mb-3">ترکیب با سایر داروها</h2>
            <p class="mb-4 text-justify text-gray-700">MMF یا اینیبیتور کلسی‌نئورین اغلب همراه AZA یا به‌جای آن به‌کار می‌روند. تداخلات دارویی (آنتی‌بیوتیک‌ها، ضد قارچ، برخی ضد تشنج‌ها) شایع است؛ داروی جدید فقط با تجویز پزشک.</p>
            <h2 id="sec-monitor" class="text-xl font-bold text-text-header mb-3">پایش</h2>
            <p class="mb-4 text-justify text-gray-700">شمارش خون، کراتینین، آنزیم‌های کبدی، سطح داروهای کلسی‌نئورین در صورت تجویز، و معاینات منظم. علائم عفونت یا تب فوری گزارش شود.</p>
            <h2 id="sec-life" class="text-xl font-bold text-text-header mb-3">سبک زندگی</h2>
            <p class="mb-4 text-justify text-gray-700">واکسن‌های غیرزنده طبق برنامه تیم پیوند؛ از واکسن زنده بدون مجوز پرهیز. رژیم غذایی سالم، فعالیت مجاز، و پرهیز از دخانیات.</p>
            <h2 id="sec-summary" class="text-xl font-bold text-text-header mb-3">جمع‌بندی</h2>
            <p class="mb-6 text-justify text-gray-700">آزاتیوپرین همچنان در بسیاری از پروتکل‌ها نقش دارد؛ پایبندی به پیگیری و ارتباط با تیم درمان پیوند حیاتی است.</p>""",
        "body_en": """<h2 id="sec-intro" class="text-xl font-bold text-text-header mb-3">Overview</h2>
            <p class="mb-4 text-justify text-gray-700">Solid-organ transplant requires targeted immunosuppression. Azathioprine has been combined with corticosteroids and calcineurin inhibitors or MMF depending on era and center protocol.</p>
            <h2 id="sec-reject" class="text-xl font-bold text-text-header mb-3">Rejection prophylaxis</h2>
            <p class="mb-4 text-justify text-gray-700">The goal is to blunt T- and B-cell allo-responses. Regimens are center-specific; never change doses or stop drugs without the transplant team.</p>
            <h2 id="sec-combo" class="text-xl font-bold text-text-header mb-3">Combination therapy</h2>
            <p class="mb-4 text-justify text-gray-700">CNIs and MMF frequently partner with or replace AZA. Drug interactions are common—coordinate all new prescriptions with your team.</p>
            <h2 id="sec-monitor" class="text-xl font-bold text-text-header mb-3">Monitoring</h2>
            <p class="mb-4 text-justify text-gray-700">CBC, renal and liver panels, CNI levels when prescribed, and prompt reporting of fever or infection signs.</p>
            <h2 id="sec-life" class="text-xl font-bold text-text-header mb-3">Lifestyle</h2>
            <p class="mb-4 text-justify text-gray-700">Inactivated vaccines per team guidance; avoid live vaccines unless cleared. Healthy diet, permitted exercise, no smoking.</p>
            <h2 id="sec-summary" class="text-xl font-bold text-text-header mb-3">Summary</h2>
            <p class="mb-6 text-justify text-gray-700">Azathioprine remains useful in many pathways; adherence and transplant-team communication are essential.</p>""",
        "img": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1600&q=80",
        "img_alt_fa": "مراقبت بیمارستانی",
        "img_alt_en": "Hospital care",
        "cap_fa": "مراقبت تیمی در بیماران پیوندی اهمیت بالینی دارد.",
        "cap_en": "Team-based care is critical for transplant recipients.",
    },
    {
        "slug": "carbamazepine-dd-interactions",
        "title_fa": "کاربامازپین: کاربردها و ایمنی ژنتیکی",
        "title_en": "Carbamazepine: uses and genetic safety (HLA)",
        "abstract_fa": "راهنمای بیمار درباره موارد مصرف، اهمیت آزمایش HLA، تداخلات مهم و پایش ایمنی.",
        "abstract_en": "Patient-oriented overview of indications, HLA testing, major interactions, and safety monitoring.",
        "summary_id": "sec-summary",
        "toc_fa": [
            ("sec-intro", "مرور"),
            ("sec-use", "موارد مصرف"),
            ("sec-hla", "ایمنی ژنتیکی HLA"),
            ("sec-ddi", "تداخلات"),
            ("sec-monitor", "پایش"),
            ("sec-summary", "جمع‌بندی"),
        ],
        "toc_en": [
            ("sec-intro", "Overview"),
            ("sec-use", "Indications"),
            ("sec-hla", "HLA & genetics"),
            ("sec-ddi", "Interactions"),
            ("sec-monitor", "Monitoring"),
            ("sec-summary", "Summary"),
        ],
        "body_fa": """<h2 id="sec-intro" class="text-xl font-bold text-text-header mb-3">مرور</h2>
            <p class="mb-4 text-justify text-gray-700">کاربامازپین در صرع جزئی و کلی و برخی دردهای عصبی کاربرد دارد. به‌دلیل خطر واکنش‌های جدی پوستی در نژادهای با شیوع بالاتر آلل HLA-B*15:02، غربالگری ژنتیکی طبق راهنمای محلی توصیه می‌شود.</p>
            <h2 id="sec-use" class="text-xl font-bold text-text-header mb-3">موارد مصرف</h2>
            <p class="mb-4 text-justify text-gray-700">تنظیم تشنج و کنترل درد عصب سه‌قلابی از مصارف رایج‌اند. شروع دوز معمولاً تدریجی است تا تحمل گوارشی و سرگیجه ارزیابی شود.</p>
            <h2 id="sec-hla" class="text-xl font-bold text-text-header mb-3">ایمنی ژنتیکی</h2>
            <p class="mb-4 text-justify text-gray-700">آزمایش HLA-B*15:02 قبل از شروع در جمعیت‌های پرخطر می‌تواند خطر SJS/TEN را کاهش دهد. نتیجه آزمایش را با پزشک خود مرور کنید؛ قطع یا شروع دارو فقط با دستور پزشک.</p>
            <h2 id="sec-ddi" class="text-xl font-bold text-text-header mb-3">تداخلات مهم</h2>
            <p class="mb-4 text-justify text-gray-700">کاربامازپین القاکننده CYP3A4 است و سطح بسیاری از داروها (از جمله ضد انعقاد خوراکی، ضد ویروس، ضد تشنج دیگر) را تغییر می‌دهد. لیست داروهای خود را کامل به پزشک و داروساز بدهید.</p>
            <h2 id="sec-monitor" class="text-xl font-bold text-text-header mb-3">پایش</h2>
            <p class="mb-4 text-justify text-gray-700">شمارش خون، سطح دارو در صورت نیاز، و علائم راش پوستی، تب، گلودرد یا زخم دهان فوری گزارش شود.</p>
            <h2 id="sec-summary" class="text-xl font-bold text-text-header mb-3">جمع‌بندی</h2>
            <p class="mb-6 text-justify text-gray-700">کاربامازپین با پایش و غربالگری مناسب می‌تواند ایمن و مؤثر باشد؛ هر علامت جدید جدی را جدی بگیرید.</p>""",
        "body_en": """<h2 id="sec-intro" class="text-xl font-bold text-text-header mb-3">Overview</h2>
            <p class="mb-4 text-justify text-gray-700">Carbamazepine treats focal/generalized seizures and some neuropathic pain. HLA-B*15:02 screening before initiation is recommended in higher-risk ancestries to reduce severe cutaneous adverse reaction risk.</p>
            <h2 id="sec-use" class="text-xl font-bold text-text-header mb-3">Indications</h2>
            <p class="mb-4 text-justify text-gray-700">Seizure control and trigeminal neuralgia are common uses. Dosing is usually titrated to improve tolerability.</p>
            <h2 id="sec-hla" class="text-xl font-bold text-text-header mb-3">HLA & genetics</h2>
            <p class="mb-4 text-justify text-gray-700">Discuss test results with your clinician; do not start or stop CBZ without medical guidance.</p>
            <h2 id="sec-ddi" class="text-xl font-bold text-text-header mb-3">Interactions</h2>
            <p class="mb-4 text-justify text-gray-700">Strong CYP3A4 induction can lower levels of many drugs and complicate anticoagulation, antivirals, and other antiseizure medications. Keep medication lists updated.</p>
            <h2 id="sec-monitor" class="text-xl font-bold text-text-header mb-3">Monitoring</h2>
            <p class="mb-4 text-justify text-gray-700">CBC, drug levels when indicated, and urgent reporting of rash, fever, sore throat, or mouth ulcers.</p>
            <h2 id="sec-summary" class="text-xl font-bold text-text-header mb-3">Summary</h2>
            <p class="mb-6 text-justify text-gray-700">With screening and follow-up, carbamazepine can be effective and safer; treat new warning signs as urgent.</p>""",
        "img": "https://images.unsplash.com/photo-1579684385127-1ef15d5081c8?auto=format&fit=crop&w=1600&q=80",
        "img_alt_fa": "دارو",
        "img_alt_en": "Medication",
        "cap_fa": "مصرف داروهای ضد تشنج فقط با نظارت پزشکی.",
        "cap_en": "Antiseizure therapy should always be medically supervised.",
    },
    {
        "slug": "carbaram-safe-usage",
        "title_fa": "کاربامازپین: نکات ایمنی و راهنمای مصرف",
        "title_en": "Carbamazepine: safety tips and usage guide",
        "abstract_fa": "مصرف صحیح، آزمایش‌های دوره‌ای، علائم هشدار و توصیه‌های عملی برای بیماران.",
        "abstract_en": "Practical guidance on correct use, periodic testing, warning signs, and adherence.",
        "summary_id": "sec-summary",
        "toc_fa": [
            ("sec-intro", "مرور"),
            ("sec-dose", "دوز و زمان مصرف"),
            ("sec-tests", "آزمایش‌ها"),
            ("sec-warn", "هشدارها"),
            ("sec-summary", "جمع‌بندی"),
        ],
        "toc_en": [
            ("sec-intro", "Overview"),
            ("sec-dose", "Dosing schedule"),
            ("sec-tests", "Tests"),
            ("sec-warn", "Warnings"),
            ("sec-summary", "Summary"),
        ],
        "body_fa": """<h2 id="sec-intro" class="text-xl font-bold text-text-header mb-3">مرور</h2>
            <p class="mb-4 text-justify text-gray-700">رعایت برنامه دوز، پرهیز از خودسرانه افزایش یا قطع ناگهانی، و پیگیری منظم برای ایمنی ضروری است. قطع ناگهانی می‌تواند تشنج بازگشتی شدید ایجاد کند.</p>
            <h2 id="sec-dose" class="text-xl font-bold text-text-header mb-3">دوز و زمان مصرف</h2>
            <p class="mb-4 text-justify text-gray-700">طبق تجویز پزشک با فاصله زمانی یکسان مصرف شود. فرمولاسیون‌های آهسته‌رهش قابل شکستن نیستند مگر طبق دستور. از نوشیدن همزمان با الکل پرهیز شود.</p>
            <h2 id="sec-tests" class="text-xl font-bold text-text-header mb-3">آزمایش‌ها</h2>
            <p class="mb-4 text-justify text-gray-700">شمارش خون و در صورت نیاز سطح دارو و عملکرد کبد/کلیه طبق برنامه پزشک. نتایج را پیگیری کنید.</p>
            <h2 id="sec-warn" class="text-xl font-bold text-text-header mb-3">هشدارها</h2>
            <p class="mb-4 text-justify text-gray-700">راش پوستی گسترده، زخم دهان، تب، زردی چشم یا پوست، خونریزی غیرطبیعی یا کبودی آسان — فوراً با اورژانس یا پزشک تماس بگیرید.</p>
            <h2 id="sec-summary" class="text-xl font-bold text-text-header mb-3">جمع‌بندی</h2>
            <p class="mb-6 text-justify text-gray-700">با انضباط در مصرف و ارتباط با تیم درمان، بیشترین منفعت و کمترین ریسک حاصل می‌شود.</p>""",
        "body_en": """<h2 id="sec-intro" class="text-xl font-bold text-text-header mb-3">Overview</h2>
            <p class="mb-4 text-justify text-gray-700">Adherence, gradual titration, and planned follow-up improve safety. Abrupt discontinuation can provoke rebound seizures.</p>
            <h2 id="sec-dose" class="text-xl font-bold text-text-header mb-3">Dosing schedule</h2>
            <p class="mb-4 text-justify text-gray-700">Take doses evenly spaced as prescribed. Do not split extended-release tablets unless directed. Avoid alcohol unless cleared.</p>
            <h2 id="sec-tests" class="text-xl font-bold text-text-header mb-3">Tests</h2>
            <p class="mb-4 text-justify text-gray-700">CBC and drug levels or metabolic panels per clinician schedule—follow up on results.</p>
            <h2 id="sec-warn" class="text-xl font-bold text-text-header mb-3">Warnings</h2>
            <p class="mb-4 text-justify text-gray-700">Seek urgent care for widespread rash, mouth sores, fever, jaundice, unusual bleeding, or severe dizziness.</p>
            <h2 id="sec-summary" class="text-xl font-bold text-text-header mb-3">Summary</h2>
            <p class="mb-6 text-justify text-gray-700">Structured use and open communication with your care team maximize benefit and reduce risk.</p>""",
        "img": "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?auto=format&fit=crop&w=1600&q=80",
        "img_alt_fa": "قرص‌ها",
        "img_alt_en": "Tablets",
        "cap_fa": "رعایت دستور پزشک در مصرف داروهای ضد تشنج.",
        "cap_en": "Follow prescribing instructions for antiseizure medications.",
    },
]


def write_fa(spec):
    title = spec["title_fa"]
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
        REFS_FA,
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
        REFS_EN,
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
