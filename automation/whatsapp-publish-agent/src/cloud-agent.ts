import { Agent, CursorAgentError } from "@cursor/sdk";
import { config } from "./config.js";
import { ContentRecord } from "./types.js";

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
