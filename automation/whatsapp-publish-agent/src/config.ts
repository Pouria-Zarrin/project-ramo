import path from "node:path";
import dotenv from "dotenv";

dotenv.config();

const required = (name: string): string => {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required env var: ${name}`);
  }
  return value;
};

const optionalForLocalTest = (name: string, fallback = "test-value"): string => {
  const value = process.env[name];
  if (value) return value;
  if (process.env.SKIP_TWILIO_SIGNATURE_FOR_LOCAL_TEST === "true") return fallback;
  throw new Error(`Missing required env var: ${name}`);
};

const optional = (name: string, fallback = ""): string => process.env[name] ?? fallback;

const whatsappProvider = process.env.WHATSAPP_PROVIDER ?? "meta";

export const config = {
  port: Number(process.env.PORT ?? 8787),
  whatsappProvider,
  twilioAuthToken:
    whatsappProvider === "twilio"
      ? optionalForLocalTest("TWILIO_AUTH_TOKEN")
      : optional("TWILIO_AUTH_TOKEN"),
  cursorApiKey: optionalForLocalTest("CURSOR_API_KEY"),
  cloudRepoUrl: process.env.CLOUD_REPO_URL ?? "https://github.com/Pouria-Zarrin/project-ramo.git",
  repoRoot: process.env.REPO_ROOT ?? path.resolve(__dirname, "../../.."),
  siteBaseUrl: process.env.SITE_BASE_URL ?? "https://pouria-zarrin.github.io/project-ramo",
  publishDryRun: process.env.PUBLISH_DRY_RUN === "true",
  skipTwilioSignatureForLocalTest: process.env.SKIP_TWILIO_SIGNATURE_FOR_LOCAL_TEST === "true",
  metaVerifyToken: process.env.META_VERIFY_TOKEN ?? "ramo_meta_verify_2026",
  metaAccessToken: process.env.META_ACCESS_TOKEN ?? "",
  metaPhoneNumberId: process.env.META_PHONE_NUMBER_ID ?? "",
  liveCheckTimeoutMs: Number(process.env.LIVE_CHECK_TIMEOUT_MS ?? 180000),
  liveCheckPollMs: Number(process.env.LIVE_CHECK_POLL_MS ?? 10000)
};
