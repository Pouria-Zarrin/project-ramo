import crypto from "node:crypto";
import express from "express";
import twilio from "twilio";
import { z } from "zod";
import { config } from "./config.js";
import { SessionStore } from "./session-store.js";
import { cleanClientText, textToSimpleHtml } from "./content-cleaner.js";
import { ContentRecord, ContentType } from "./types.js";
import { publishRecord } from "./publisher.js";
import { runCloudPublishAgent } from "./cloud-agent.js";

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

  if (containsOutOfScopeRequest(body)) {
    return "این درخواست خارج از قابلیت‌های فعلی این بات است. لطفا برای این مورد با توسعه‌دهنده وب تماس بگیرید.\n\nمن فقط می‌توانم دریافت/پاکسازی متن خبر یا مقاله سلامت، پیش‌نمایش، و انتشار خودکار را انجام دهم.";
  }

  if (!draft.type) {
    draft.type = parseType(body);
    sessions.save(from, draft);
    if (!draft.type) {
      return "سلام، خوش آمدید 🌿\nبرای شروع لطفا نوع محتوا را مشخص کنید:\n- خبر\n- مقاله سلامت";
    }
  }

  draft.title = parseLabeledField(body, "title") ?? draft.title;
  draft.summary = parseLabeledField(body, "summary") ?? draft.summary;
  draft.body = parseLabeledField(body, "body") ?? draft.body;
  draft.language = body.includes("language: en") ? "en" : (draft.language ?? "fa");

  if (!draft.requiresConfirmation && requiredForPreview(draft)) {
    draft.cleanedPreview = cleanClientText({
      title: draft.title!,
      summary: draft.summary!,
      body: draft.body!
    });
    draft.requiresConfirmation = true;
    sessions.save(from, draft);
    return `پیش‌نمایش ویرایش‌شده:\n\nعنوان: ${draft.cleanedPreview.title}\nخلاصه: ${draft.cleanedPreview.summary}\n\nبرای انتشار بنویسید: تایید انتشار\n\nاگر اصلاحی دارید همان‌جا بنویسید تا دوباره پاکسازی کنم.`;
  }

  if (
    draft.requiresConfirmation &&
    (body.trim().toUpperCase() === "CONFIRM PUBLISH" || body.trim() === "تایید انتشار") &&
    draft.cleanedPreview
  ) {
    const slug = createSlug(draft.cleanedPreview.title);
    const record: ContentRecord = {
      slug,
      type: draft.type!,
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
    try {
      if (useCloud) {
        await runCloudPublishAgent(record);
      }
      const result = await publishRecord(record);
      sessions.clear(from);
      const status = result.deployLive ? "Published" : "Deploy in progress";
      return `${status}\n\nلینک(ها):\n${result.liveUrls.join("\n")}\n\ncommit: ${result.commitSha ?? "n/a"}`;
    } catch (error) {
      sessions.save(from, draft);
      return `خطا در انتشار: ${(error as Error).message}\nپیش‌نویس ذخیره شد. دوباره تلاش کنید.`;
    }
  }

  sessions.save(from, draft);
  return "خیلی خوب. لطفا متن را با این قالب بفرستید تا بخوانم و پاکسازی کنم:\ntitle: ...\nsummary: ...\nbody: ...\nlanguage: fa|en\n\nاگر تصویر دارید، بعد از متن ارسال کنید.";
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
