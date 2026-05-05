import { ClientDraft } from "./types.js";

export class SessionStore {
  private readonly store = new Map<string, ClientDraft>();

  getOrCreate(from: string): ClientDraft {
    const current = this.store.get(from);
    if (current) return current;
    const fresh: ClientDraft = {
      media: [],
      requiresConfirmation: false
    };
    this.store.set(from, fresh);
    return fresh;
  }

  save(from: string, draft: ClientDraft): void {
    this.store.set(from, draft);
  }

  clear(from: string): void {
    this.store.delete(from);
  }
}
