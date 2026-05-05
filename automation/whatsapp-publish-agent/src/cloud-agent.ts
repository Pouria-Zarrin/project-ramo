import { Agent, CursorAgentError } from "@cursor/sdk";
import { config } from "./config.js";
import { ClientDraft, ContentRecord, ContentType } from "./types.js";

const buildPrompt = (record: ContentRecord): string => `
You are publishing one approved WhatsApp content intake.

Constraints:
- Repository is already checked out.
- Do not edit plan files.
- Render content into ${record.type === "news" ? "V0/news" : "V0/articles"} using existing templates.
- Update FA/EN home + relevant indexes + FA ticker with maximum 5 items for home sliders and ticker.
- Commit with: feat(content): publish ${record.slug} via whatsapp intake
- Push to origin/main.

Payload:
${JSON.stringify(record, null, 2)}
`;

export const runCloudPublishAgent = async (record: ContentRecord): Promise<{ runId: string; agentId: string }> => {
  const agent = await Agent.create({
    apiKey: config.cursorApiKey,
    cloud: {
      repos: [{ url: config.cloudRepoUrl, startingRef: "main" }],
      skipReviewerRequest: true
    }
  });

  try {
    const run = await agent.send(buildPrompt(record));
    const result = await run.wait();
    if (result.status === "error") {
      throw new Error(`Cloud run failed: ${result.id}`);
    }
    return { runId: result.id, agentId: agent.agentId };
  } catch (err) {
    if (err instanceof CursorAgentError) {
      throw new Error(`Cursor startup failure: ${err.message}; retryable=${err.isRetryable}`);
    }
    throw err;
  } finally {
    await agent[Symbol.asyncDispose]();
  }
};

export interface CloudConversationResult {
  reply: string;
  type?: ContentType;
  title?: string;
  summary?: string;
  body?: string;
  language?: "fa" | "en";
  readyToPublish?: boolean;
  outOfScope?: boolean;
}

const buildConversationPrompt = (message: string, draft: ClientDraft): string => `
You are a Persian-first publishing assistant for Ramopharmin.

Allowed publish channels only:
- news
- health_magazine_article

Current draft/session state:
${JSON.stringify(draft, null, 2)}

New user message:
${message}

Your job:
1) Be conversational and helpful in Persian.
2) Classify/confirm content type (news vs health_magazine_article) if not confirmed.
3) If user asks, generate or expand long draft text (title/summary/body).
4) If user asks for edits, revise draft naturally.
5) If request is outside publishing scope, mark outOfScope=true and explain briefly.
6) Never publish directly here; only prepare content and ask for confirmation.
7) Do NOT repeatedly ask "news or article" if type is already inferable from the message or existing state.
8) If user asks for generation (e.g., "بنویس", "تولید کن", "متن رو بیشتر کن"), generate/revise directly.
9) Keep responses concise, human, and natural — not robotic templates.
10) Default language is Persian. Only switch to English if user explicitly requests English.

Return STRICT JSON only with shape:
{
  "reply": "string (Persian response for user)",
  "type": "news|health_magazine_article|null",
  "title": "string|null",
  "summary": "string|null",
  "body": "string|null",
  "language": "fa|en|null",
  "readyToPublish": true|false,
  "outOfScope": true|false
}
`;

const extractJsonObject = (text: string): string | null => {
  const fenced = text.match(/```json\s*([\s\S]*?)```/i);
  if (fenced?.[1]) return fenced[1].trim();
  const plain = text.match(/\{[\s\S]*\}/);
  return plain?.[0]?.trim() ?? null;
};

export const runCloudConversationAgent = async (
  message: string,
  draft: ClientDraft
): Promise<CloudConversationResult> => {
  try {
    const result = await Agent.prompt(buildConversationPrompt(message, draft), {
      apiKey: config.cursorApiKey,
      model: { id: "composer-2-fast" },
      cloud: {
        repos: [{ url: config.cloudRepoUrl, startingRef: "main" }],
        skipReviewerRequest: true
      }
    });
    if (result.status === "error") {
      throw new Error(`Cloud conversation failed: ${result.id}`);
    }
    const raw = String(result.result ?? "");
    const jsonText = extractJsonObject(raw);
    if (!jsonText) {
      return { reply: "متوجه شدم. لطفا کمی دقیق‌تر بفرمایید تا پیش‌نویس مناسب آماده کنم.", readyToPublish: false };
    }
    const parsed = JSON.parse(jsonText) as CloudConversationResult & {
      type?: ContentType | null;
      language?: "fa" | "en" | null;
    };
    return {
      reply: parsed.reply || "متن شما دریافت شد.",
      type: parsed.type ?? undefined,
      title: parsed.title ?? undefined,
      summary: parsed.summary ?? undefined,
      body: parsed.body ?? undefined,
      language: parsed.language ?? undefined,
      readyToPublish: Boolean(parsed.readyToPublish),
      outOfScope: Boolean(parsed.outOfScope)
    };
  } catch (err) {
    if (err instanceof CursorAgentError) {
      throw new Error(`Cursor conversation startup failure: ${err.message}; retryable=${err.isRetryable}`);
    }
    throw err;
  }
};
