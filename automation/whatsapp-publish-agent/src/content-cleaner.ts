interface CleanedText {
  title: string;
  summary: string;
  body: string;
}

const normalizeSpaces = (value: string): string =>
  value
    .replace(/\u200c/g, "‌")
    .replace(/[ \t]+/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();

/**
 * Minimal editorial cleanup:
 * - whitespace normalization
 * - unify punctuation spacing
 * - preserve authenticity by avoiding paraphrasing
 */
export const cleanClientText = (input: CleanedText): CleanedText => {
  const tidy = (value: string): string =>
    normalizeSpaces(value)
      .replace(/\s+([،؛:!?])/g, "$1")
      .replace(/([،؛:!?])([^\s\n])/g, "$1 $2");

  return {
    title: tidy(input.title),
    summary: tidy(input.summary),
    body: tidy(input.body)
  };
};

export const textToSimpleHtml = (body: string): string => {
  const paragraphs = body
    .split(/\n{2,}/)
    .map((p) => p.trim())
    .filter(Boolean);
  return paragraphs.map((p) => `<p class="mb-4 text-justify text-gray-700">${escapeHtml(p)}</p>`).join("\n");
};

const escapeHtml = (value: string): string =>
  value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
