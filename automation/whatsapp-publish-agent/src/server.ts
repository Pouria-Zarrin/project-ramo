import crypto from "node:crypto";
import express from "express";
import twilio from "twilio";
import { z } from "zod";
import { config } from "./config.js";
import { SessionStore } from "./session-store.js";
import { cleanClientText, textToSimpleHtml } from "./content-cleaner.js";
import { ContentRecord, ContentType } from "./types.js";
import { publishRecord } from "./publisher.js";
import { runCloudConversationAgent, runCloudPublishAgent } from "./cloud-agent.js";

const app = express();
app.use(express.urlencoded({ extended: false }));
app.use(express.json());

const sessions = new SessionStore();
const idempotencyKeys = new Set<string>();

const bodySchema = z.object({
  From: z.string().min(1),
  Body: z.string().optional(),
  MessageSid: z.string().min(1),
  NumMedia: z.string().optional()
});

const parseType = (value: string): ContentType | undefined => {
  const v = value.toLowerCase();
  if (v.includes("news") || v.includes("خبر")) return "news";
  if (v.includes("article") || v.includes("مقاله")) return "health_magazine_article";
  return undefined;
};

const parseLabeledField = (body: string, label: string): string | undefined => {
  const regex = new RegExp(`${label}\\s*:\\s*([\\s\\S]+?)(?:\\n\\w+\\s*:|$)`, "i");
  const m = body.match(regex);
  return m?.[1]?.trim();
};

const cleanLine = (line: string): string => line.trim().replace(/\s+/g, " ");

const splitParagraphs = (text: string): string[] =>
  text
    .split(/\n{2,}/)
    .map((p) => cleanLine(p))
    .filter(Boolean);

const guessSummaryFromBody = (body: string): string => {
  const compact = body.replace(/\n+/g, " ").trim();
  if (!compact) return "";
  const sentence = compact.split(/[.!؟\n]/).map((s) => s.trim()).find(Boolean) ?? compact;
  return sentence.slice(0, 220);
};

const parseFreeformText = (
  raw: string
): {
  title?: string;
  summary?: string;
  body?: string;
  language?: "fa" | "en";
} => {
  const text = raw.trim();
  if (!text) return {};

  const normalized = text.replace(/\r/g, "");
  const lines = normalized
    .split("\n")
    .map((l) => cleanLine(l))
    .filter(Boolean);

  const explicitTitle = parseLabeledField(normalized, "title");
  const explicitSummary = parseLabeledField(normalized, "summary");
  const explicitBody = parseLabeledField(normalized, "body");
  const explicitLang = normalized.match(/language\s*:\s*(fa|en)/i)?.[1]?.toLowerCase();

  const looksLikeLabeled = /title\s*:|summary\s*:|body\s*:/i.test(normalized);
  if (looksLikeLabeled) {
    return {
      title: explicitTitle,
      summary: explicitSummary,
      body: explicitBody,
      language: explicitLang === "en" ? "en" : explicitLang === "fa" ? "fa" : undefined
    };
  }

  const paragraphs = splitParagraphs(normalized);
  const firstLine = lines[0] ?? "";
  const titleCandidate = firstLine.length <= 90 ? firstLine : undefined;
  const bodyCandidate =
    paragraphs.length > 1
      ? paragraphs.join("\n\n")
      : lines.length > 1
        ? lines.slice(1).join("\n")
        : titleCandidate
          ? ""
          : normalized;

  const summaryCandidate = bodyCandidate ? guessSummaryFromBody(bodyCandidate) : undefined;
  const hasEnglish = /[a-zA-Z]/.test(normalized);

  return {
    title: titleCandidate,
    summary: summaryCandidate,
    body: bodyCandidate || undefined,
    language: hasEnglish ? "en" : "fa"
  };
};

const isEditIntent = (text: string): boolean => {
  const v = text.toLowerCase();
  return [
    "اصلاح",
    "ویرایش",
    "تغییر",
    "edit",
    "change",
    "rewrite",
    "عنوان جدید",
    "خلاصه جدید",
    "متن جدید"
  ].some((k) => v.includes(k));
};

const isGenerationIntent = (text: string): boolean => {
  const v = text.toLowerCase();
  const direct = [
    "تولید متن",
    "تولید کن",
    "متن بساز",
    "نمونه متن",
    "یه متن بنویس",
    "یک متن بنویس",
    "خبر بنویس",
    "خبر کامل بنویس",
    "مقاله بنویس",
    "پیش نویس بنویس",
    "پیش‌نویس بنویس",
    "long draft",
    "generate text",
    "write sample",
    "write a draft",
    "draft this"
  ].some((k) => v.includes(k));
  const fuzzyFa =
    ((v.includes("متن") || v.includes("خبر") || v.includes("مقاله")) &&
      (v.includes("بنویس") || v.includes("تولید") || v.includes("بساز"))) ||
    (v.includes("بلند") && (v.includes("متن") || v.includes("خبر")));
  return direct || fuzzyFa;
};

const isExpandIntent = (text: string): boolean => {
  const v = text.toLowerCase();
  return [
    "متن رو بیشتر کن",
    "متن را بیشتر کن",
    "بیشترش کن",
    "طولانی تر",
    "طولانی‌تر",
    "مفصل تر",
    "مفصل‌تر",
    "longer",
    "expand",
    "more detail"
  ].some((k) => v.includes(k));
};

const extractBrief = (text: string): string =>
  text
    .replace(/(تولید متن|متن بساز|نمونه متن|یه متن بنویس|خبر بنویس|مقاله بنویس|generate text|write sample|draft this)/gi, "")
    .replace(/\s+/g, " ")
    .trim();

type DraftLength = "short" | "medium" | "long" | "very_long";

const detectRequestedLength = (text: string): DraftLength => {
  const v = text.toLowerCase();
  if (
    v.includes("خیلی بلند") ||
    v.includes("خیلی کامل") ||
    v.includes("مفصل") ||
    v.includes("detailed")
  ) {
    return "very_long";
  }
  if (
    v.includes("بلند") ||
    v.includes("کامل") ||
    v.includes("full") ||
    v.includes("long")
  ) {
    return "long";
  }
  if (v.includes("کوتاه") || v.includes("خلاصه") || v.includes("short")) {
    return "short";
  }
  return "medium";
};

const generateSampleContent = (
  brief: string,
  type: ContentType,
  language: "fa" | "en",
  length: DraftLength
): { title: string; summary: string; body: string } => {
  const topic = brief || (language === "fa" ? "به‌روزرسانی فعالیت شرکت" : "company update");
  if (language === "fa") {
    const title = type === "news" ? `خبر: ${topic}` : `مقاله سلامت: ${topic}`;
    const summary = `این متن نمونه بر اساس توضیح شما تهیه شده و قابل ویرایش است: ${topic}.`;
    const baseParagraphs = [
      `بر اساس توضیح ارائه‌شده، این ${type === "news" ? "خبر" : "مقاله"} با تمرکز بر «${topic}» تهیه شده است و تلاش می‌کند پیام اصلی را شفاف و قابل انتشار منتقل کند.`,
      "در این نسخه، جزئیات کلیدی موضوع به زبان ساده و حرفه‌ای تنظیم شده تا مخاطب بتواند به‌سرعت تصویری روشن از اهمیت موضوع، هدف اقدام انجام‌شده و اثرات مورد انتظار دریافت کند.",
      "از نظر لحن و ساختار نیز متن به‌گونه‌ای تنظیم شده که هم برای انتشار در کانال‌های رسمی مناسب باشد و هم قابلیت ویرایش سریع برای افزودن اطلاعات دقیق‌تر مانند تاریخ، نام افراد، آمار یا نقل‌قول‌های رسمی را داشته باشد.",
      "در صورت نیاز می‌توان تاکید متن را بر جنبه‌های فنی، مدیریتی، اقتصادی یا پیام‌های مسئولیت اجتماعی قرار داد تا پیام نهایی دقیق‌تر با هدف ارتباطی برند همراستا شود.",
      "همچنین پیشنهاد می‌شود برای نسخه نهایی، یک پاراگراف اختصاصی درباره دستاوردهای عملی، اثر مستقیم بر مخاطبان هدف، و مسیر اقدامات بعدی اضافه شود تا متن از نظر خبری کامل‌تر و اثرگذارتر باشد.",
      "اگر اطلاعات تکمیلی شامل اعداد دقیق، جدول زمان‌بندی، نقل‌قول مدیران، یا نام واحدهای اجرایی ارسال شود، نسخه نهایی می‌تواند با دقت بیشتر و آمادگی کامل برای انتشار رسمی آماده گردد."
    ];

    const paragraphCount =
      length === "short" ? 2 : length === "medium" ? 4 : length === "long" ? 6 : 8;
    const extension = [
      "در جمع‌بندی، این اقدام می‌تواند گامی عملی در مسیر ارتقای کیفیت، افزایش ظرفیت و تقویت اعتماد مخاطبان تلقی شود و تصویر حرفه‌ای‌تری از روند توسعه ارائه دهد.",
      "در صورت تایید شما، همین پیش‌نویس می‌تواند در نسخه بعدی با جزئیات نهایی تکمیل شده و مستقیما برای انتشار در وب‌سایت آماده شود."
    ];
    const body = [...baseParagraphs, ...extension].slice(0, paragraphCount).join("\n\n");
    return { title, summary, body };
  }

  const title = type === "news" ? `News: ${topic}` : `Health Article: ${topic}`;
  const summary = `This is a generated sample draft based on your brief: ${topic}.`;
  const enParagraphs = [
    `Based on your brief, this draft focuses on ${topic}.`,
    "The structure is designed to communicate the core message clearly while remaining suitable for publication channels.",
    "This version can be quickly refined by inserting exact names, dates, figures, and approved quotes from stakeholders.",
    "If needed, the final copy can emphasize technical outcomes, operational impact, or broader public-facing messaging.",
    "A stronger final version usually includes measurable outcomes, timeline context, and a clear next-step statement.",
    "Share any factual additions and I will produce a publication-ready final draft."
  ];
  const enCount = length === "short" ? 2 : length === "medium" ? 4 : length === "long" ? 6 : 6;
  const body = enParagraphs.slice(0, enCount).join("\n\n");
  return { title, summary, body };
};

const deriveTitleFromBody = (body: string, language: "fa" | "en"): string => {
  const cleaned = body.replace(/\n+/g, " ").trim();
  const firstSentence = cleaned.split(/[.!؟]/).map((s) => s.trim()).find(Boolean) ?? cleaned;
  const words = firstSentence.split(/\s+/).filter(Boolean).slice(0, 9);
  const candidate = words.join(" ").trim();
  if (!candidate) return language === "fa" ? "خبر جدید" : "New update";
  return candidate.length > 90 ? candidate.slice(0, 90) : candidate;
};

const expandDraftBody = (
  body: string,
  type: ContentType,
  language: "fa" | "en"
): string => {
  const extensionFa = [
    "در ادامه این خبر، می‌توان به ابعاد عملیاتی پروژه نیز اشاره کرد؛ از جمله ظرفیت‌سازی جدید، تاثیر بر پایداری زنجیره تامین، و ارتقای سرعت پاسخ‌گویی به نیاز بازار.",
    "از منظر کیفیت، هم‌راستایی با استانداردهای جهانی زمانی ارزشمندتر می‌شود که با نظام پایش مستمر، آموزش نیروی انسانی و شفافیت شاخص‌های عملکرد همراه باشد.",
    "همچنین پیام این اقدام برای ذی‌نفعان داخلی و خارجی این است که مسیر توسعه بر مبنای برنامه‌ریزی بلندمدت، استانداردسازی و بهبود تجربه مصرف‌کننده دنبال می‌شود.",
    "در صورت تایید، نسخه نهایی می‌تواند با اضافه شدن آمار دقیق، زمان‌بندی اجرایی و نقل‌قول رسمی مدیران، برای انتشار رسانه‌ای کاملا آماده شود."
  ];
  const extensionEn = [
    "Operationally, this initiative can be framed as a capacity and resilience improvement with direct impact on supply continuity.",
    "From a quality standpoint, alignment with international standards is most credible when paired with continuous monitoring and transparent performance indicators.",
    "The broader message to stakeholders is that growth is being executed through disciplined planning, standardization, and measurable outcomes.",
    "If needed, the final version can be enriched with exact metrics, dates, and leadership quotes for publication-readiness."
  ];
  const extra = language === "fa" ? extensionFa.join("\n\n") : extensionEn.join("\n\n");
  const prefix = type === "news"
    ? (language === "fa" ? "تکمیل خبر:" : "News expansion:")
    : (language === "fa" ? "تکمیل مقاله:" : "Article expansion:");
  return `${body.trim()}\n\n${prefix}\n\n${extra}`;
};

const containsOutOfScopeRequest = (body: string): boolean => {
  const text = body.toLowerCase();
  const triggers = [
    "طراحی سایت",
    "ریدیزاین",
    "تغییر هدر",
    "تغییر فوتر",
    "سئو تکنیکال",
    "ساخت صفحه جدید",
    "کدنویسی",
    "debug",
    "api جدید",
    "integration جدید"
  ];
  return triggers.some((t) => text.includes(t));
};

const buildMedia = (raw: Record<string, string>): { mediaUrl: string; contentType?: string }[] => {
  const count = Number(raw.NumMedia ?? "0");
  const output: { mediaUrl: string; contentType?: string }[] = [];
  for (let i = 0; i < count; i += 1) {
    const mediaUrl = raw[`MediaUrl${i}`];
    const contentType = raw[`MediaContentType${i}`];
    if (mediaUrl) output.push({ mediaUrl, contentType });
  }
  return output;
};

const createSlug = (title: string): string =>
  title
    .toLowerCase()
    .replace(/[^a-z0-9\u0600-\u06FF]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 80);

const toTwiml = (message: string): string => {
  const twiml = new twilio.twiml.MessagingResponse();
  twiml.message(message);
  return twiml.toString();
};

const verifySignature = (req: express.Request): boolean => {
  if (config.skipTwilioSignatureForLocalTest) return true;
  const signature = req.header("x-twilio-signature");
  if (!signature) return false;
  const url = `${req.protocol}://${req.get("host")}${req.originalUrl}`;
  const params = req.body as Record<string, string>;
  return twilio.validateRequest(config.twilioAuthToken, signature, url, params);
};

const requiredForPreview = (draft: {
  type?: ContentType;
  title?: string;
  summary?: string;
  body?: string;
}): boolean => Boolean(draft.type && draft.title && draft.summary && draft.body);

const runConversationFlow = async (from: string, key: string, body: string, media: { mediaUrl: string; contentType?: string }[]): Promise<string> => {
  if (idempotencyKeys.has(key)) {
    return "پیام تکراری شناسایی شد. در حال پردازش همان درخواست قبلی هستیم.";
  }
  idempotencyKeys.add(key);

  const draft = sessions.getOrCreate(from);
  if (media.length) draft.media.push(...media.filter((m) => (m.contentType ?? "").startsWith("image/")));
  try {
    const cloud = await runCloudConversationAgent(body, draft);
    if (cloud.outOfScope || cloud.action === "out_of_scope") {
      return cloud.reply;
    }

    draft.type = cloud.type ?? draft.type;
    draft.title = cloud.title ?? draft.title;
    draft.summary = cloud.summary ?? draft.summary;
    draft.body = cloud.body ?? draft.body;
    draft.language = cloud.language ?? draft.language ?? "fa";

    // Agent decides when to publish.
    if (
      cloud.action === "publish_now" &&
      draft.type &&
      draft.title &&
      draft.summary &&
      draft.body
    ) {
      draft.cleanedPreview = cleanClientText({
        title: draft.title,
        summary: draft.summary,
        body: draft.body
      });
      const slug = createSlug(draft.cleanedPreview.title);
      const record: ContentRecord = {
        slug,
        type: draft.type,
        title: draft.cleanedPreview.title,
        summary: draft.cleanedPreview.summary,
        bodyHtml: textToSimpleHtml(draft.cleanedPreview.body),
        language: draft.language ?? "fa",
        imageUrl: draft.media[0]?.mediaUrl ?? "https://dummyimage.com/1200x675/e5e7eb/334155&text=Ramopharmin",
        imageAlt: draft.cleanedPreview.title,
        imageCaption: draft.cleanedPreview.summary,
        createdAtIso: new Date().toISOString()
      };

      const useCloud = process.env.USE_CLOUD_AGENT === "true";
      if (useCloud) {
        await runCloudPublishAgent(record);
      }
      const result = await publishRecord(record);
      sessions.clear(from);
      const status = result.deployLive ? "Published" : "Deploy in progress";
      return `${cloud.reply}\n\n${status}\n\nلینک(ها):\n${result.liveUrls.join("\n")}\n\ncommit: ${result.commitSha ?? "n/a"}`;
    }

    sessions.save(from, draft);
    return cloud.reply || "متن شما دریافت شد. ادامه بدهیم.";
  } catch (error) {
    sessions.save(from, draft);
    return `ارتباط هوشمند موقتاً در دسترس نیست (${(error as Error).message}). لطفا چند لحظه دیگر دوباره پیام دهید.`;
  }
};

const sendMetaText = async (to: string, text: string): Promise<void> => {
  if (!config.metaAccessToken || !config.metaPhoneNumberId) return;
  await fetch(`https://graph.facebook.com/v22.0/${config.metaPhoneNumberId}/messages`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${config.metaAccessToken}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      messaging_product: "whatsapp",
      to,
      type: "text",
      text: { body: text }
    })
  });
};

const sendTelegramText = async (chatId: string, text: string): Promise<void> => {
  if (!config.telegramBotToken) return;
  await fetch(`https://api.telegram.org/bot${config.telegramBotToken}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text
    })
  });
};

const getTelegramMediaUrl = async (fileId: string): Promise<string | undefined> => {
  if (!config.telegramBotToken) return undefined;
  const fileRes = await fetch(`https://api.telegram.org/bot${config.telegramBotToken}/getFile?file_id=${encodeURIComponent(fileId)}`);
  if (!fileRes.ok) return undefined;
  const fileJson = (await fileRes.json()) as { ok: boolean; result?: { file_path?: string } };
  const filePath = fileJson.result?.file_path;
  if (!filePath) return undefined;
  return `https://api.telegram.org/file/bot${config.telegramBotToken}/${filePath}`;
};

app.post("/webhooks/twilio/whatsapp", async (req, res) => {
  if (!verifySignature(req)) {
    res.status(401).send("invalid signature");
    return;
  }

  const parsed = bodySchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).send("invalid payload");
    return;
  }

  const reply = await runConversationFlow(
    parsed.data.From,
    parsed.data.MessageSid,
    parsed.data.Body ?? "",
    buildMedia(req.body as Record<string, string>)
  );
  res.type("text/xml").send(toTwiml(reply));
});

app.get("/webhooks/meta/whatsapp", (req, res) => {
  const mode = req.query["hub.mode"];
  const verifyToken = req.query["hub.verify_token"];
  const challenge = req.query["hub.challenge"];
  if (mode === "subscribe" && verifyToken === config.metaVerifyToken && typeof challenge === "string") {
    res.status(200).type("text/plain").send(challenge);
    return;
  }
  res.sendStatus(403);
});

app.post("/webhooks/meta/whatsapp", async (req, res) => {
  const message = req.body?.entry?.[0]?.changes?.[0]?.value?.messages?.[0];
  if (!message) {
    res.sendStatus(200);
    return;
  }

  const from = message.from as string;
  const body = (message.text?.body as string | undefined) ?? "";
  const key = (message.id as string | undefined) ?? `${from}:${Date.now()}`;
  const reply = await runConversationFlow(from, key, body, []);
  await sendMetaText(from, reply);
  res.sendStatus(200);
});

app.post("/webhooks/telegram", async (req, res) => {
  if (config.telegramWebhookSecret) {
    const secretHeader = req.header("x-telegram-bot-api-secret-token");
    if (secretHeader !== config.telegramWebhookSecret) {
      res.sendStatus(401);
      return;
    }
  }

  const message = req.body?.message ?? req.body?.edited_message;
  if (!message) {
    res.sendStatus(200);
    return;
  }

  const chatId = String(message.chat?.id ?? "");
  const from = String(message.from?.id ?? chatId);
  const body = String(message.text ?? message.caption ?? "");
  const key = String(message.message_id ?? `${from}:${Date.now()}`);
  const media: { mediaUrl: string; contentType?: string }[] = [];

  if (Array.isArray(message.photo) && message.photo.length > 0) {
    const largest = message.photo[message.photo.length - 1];
    const fileId = largest?.file_id as string | undefined;
    if (fileId) {
      const mediaUrl = await getTelegramMediaUrl(fileId);
      if (mediaUrl) media.push({ mediaUrl, contentType: "image/jpeg" });
    }
  }

  const reply = await runConversationFlow(from, key, body, media);
  await sendTelegramText(chatId, reply);
  res.sendStatus(200);
});

app.get("/health", (_req, res) => {
  res.json({ ok: true });
});

app.listen(config.port, () => {
  // eslint-disable-next-line no-console
  console.log(`whatsapp publish service listening on :${config.port}`);
});
