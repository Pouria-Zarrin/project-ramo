export type ContentType = "news" | "health_magazine_article";

export interface IntakeMedia {
  mediaUrl: string;
  contentType?: string;
}

export interface IntakePayload {
  from: string;
  body: string;
  media: IntakeMedia[];
}

export interface ClientDraft {
  type?: ContentType;
  title?: string;
  summary?: string;
  body?: string;
  language?: "fa" | "en";
  media: IntakeMedia[];
  requiresConfirmation: boolean;
  cleanedPreview?: {
    title: string;
    summary: string;
    body: string;
  };
}

export interface ContentRecord {
  slug: string;
  type: ContentType;
  title: string;
  summary: string;
  bodyHtml: string;
  language: "fa" | "en";
  imageUrl: string;
  imageAlt: string;
  imageCaption: string;
  createdAtIso: string;
}

export interface PublishResult {
  publishedPaths: string[];
  liveUrls: string[];
  commitSha?: string;
  deployLive: boolean;
}
