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
  action?: "ask_more" | "update_draft" | "publish_now" | "out_of_scope";
  type?: ContentType;
  title?: string;
  summary?: string;
  body?: string;
  language?: "fa" | "en";
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
2) Classify/confirm content type (news vs health_magazine_article) if inferable from context.
3) Generate, expand, and polish draft text proactively from messy user input.
4) If user asks for edits, revise naturally and improve writing quality.
5) Decide when content is publish-ready and set action=publish_now.
6) If more information is needed, set action=ask_more and ask only the missing details.
7) If request is outside publishing scope, set action=out_of_scope and explain briefly.
8) Keep responses concise, human, and natural — not robotic templates.
9) Default language is Persian. Only switch to English if user explicitly requests English.

Return STRICT JSON only with shape:
{
  "reply": "string (Persian response for user)",
  "action": "ask_more|update_draft|publish_now|out_of_scope",
  "type": "news|health_magazine_article|null",
  "title": "string|null",
  "summary": "string|null",
  "body": "string|null",
  "language": "fa|en|null",
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
      return { reply: "متوجه شدم. لطفا کمی دقیق‌تر بفرمایید تا پیش‌نویس مناسب آماده کنم.", action: "ask_more" };
    }
    const parsed = JSON.parse(jsonText) as CloudConversationResult & {
      type?: ContentType | null;
      language?: "fa" | "en" | null;
    };
    return {
      reply: parsed.reply || "متن شما دریافت شد.",
      action: parsed.action ?? (parsed.outOfScope ? "out_of_scope" : "update_draft"),
      type: parsed.type ?? undefined,
      title: parsed.title ?? undefined,
      summary: parsed.summary ?? undefined,
      body: parsed.body ?? undefined,
      language: parsed.language ?? undefined,
      outOfScope: Boolean(parsed.outOfScope)
    };
  } catch (err) {
    if (err instanceof CursorAgentError) {
      throw new Error(`Cursor conversation startup failure: ${err.message}; retryable=${err.isRetryable}`);
    }
    throw err;
  }
};
