import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { config } from "./config.js";
import { PublishResult, ContentRecord } from "./types.js";
import { renderFromTemplate } from "./template-renderer.js";
import { buildReferencesHtml, buildTocHtml, updateFeeds } from "./feed-updater.js";

const contentDir = (repoRoot: string): string => path.join(repoRoot, "automation/whatsapp-publish-agent/content-manifests");
const logDir = (repoRoot: string): string => path.join(repoRoot, "automation/whatsapp-publish-agent/logs");

const ensureDir = (dir: string): void => {
  fs.mkdirSync(dir, { recursive: true });
};

const writeManifest = (repoRoot: string, record: ContentRecord): string => {
  const dir = contentDir(repoRoot);
  ensureDir(dir);
  const file = path.join(dir, `${record.slug}.json`);
  fs.writeFileSync(file, JSON.stringify(record, null, 2), "utf8");
  return file;
};

const writeLog = (repoRoot: string, slug: string, payload: object): void => {
  ensureDir(logDir(repoRoot));
  fs.writeFileSync(path.join(logDir(repoRoot), `${slug}.json`), JSON.stringify(payload, null, 2), "utf8");
};

const runGit = (cmd: string): string =>
  execSync(cmd, {
    cwd: config.repoRoot,
    stdio: "pipe",
    encoding: "utf8"
  }).trim();

const commitAndPush = (changedPaths: string[], slug: string): string => {
  const escaped = changedPaths.map((p) => `"${p}"`).join(" ");
  runGit(`git add ${escaped}`);
  runGit(`git commit -m "feat(content): publish ${slug} via whatsapp intake"`);
  runGit(`git push origin main`);
  return runGit("git rev-parse HEAD");
};

const checkLive = async (urls: string[]): Promise<boolean> => {
  const start = Date.now();
  while (Date.now() - start < config.liveCheckTimeoutMs) {
    let allOk = true;
    for (const url of urls) {
      try {
        const res = await fetch(url, { method: "GET" });
        if (!res.ok) {
          allOk = false;
          break;
        }
      } catch {
        allOk = false;
        break;
      }
    }
    if (allOk) return true;
    await new Promise((resolve) => setTimeout(resolve, config.liveCheckPollMs));
  }
  return false;
};

export const publishRecord = async (record: ContentRecord): Promise<PublishResult> => {
  const pageDir = record.type === "news" ? "V0/news" : "V0/articles";
  const pagePath = path.join(config.repoRoot, pageDir, `${record.slug}.html`);

  const tocHtml = buildTocHtml(record);
  const refsHtml = buildReferencesHtml(record);
  const canonicalUrl = `${config.siteBaseUrl}/${pageDir.replace("V0/", "")}/${record.slug}.html`;
  const rendered = renderFromTemplate(config.repoRoot, record.type === "news" ? "news" : "article", {
    record,
    canonicalUrl,
    tocItemsHtml: tocHtml,
    referencesHtml: refsHtml
  });

  if (!config.publishDryRun) {
    fs.writeFileSync(pagePath, rendered, "utf8");
    updateFeeds(config.repoRoot, record);
  } else {
    const dryDir = path.join(config.repoRoot, "automation/whatsapp-publish-agent/dry-run-output");
    ensureDir(dryDir);
    fs.writeFileSync(path.join(dryDir, `${record.slug}.html`), rendered, "utf8");
  }
  const manifestPath = writeManifest(config.repoRoot, record);

  let changed: string[] = [];
  let commitSha = "dry-run";
  if (!config.publishDryRun) {
    changed = runGit("git status --porcelain")
      .split("\n")
      .map((line) => line.slice(3))
      .filter(Boolean);
    commitSha = commitAndPush(changed, record.slug);
  }
  const liveUrls = [canonicalUrl];
  const deployLive = config.publishDryRun ? false : await checkLive(liveUrls);

  writeLog(config.repoRoot, record.slug, {
    runAt: new Date().toISOString(),
    commitSha,
    changed,
    liveUrls,
    deployLive,
    manifestPath
  });

  return {
    publishedPaths: [pagePath, manifestPath, ...changed.filter((p) => p !== pagePath && p !== manifestPath)],
    liveUrls,
    commitSha,
    deployLive
  };
};
