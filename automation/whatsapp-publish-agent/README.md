# WhatsApp Publish Agent

WhatsApp intake service (Meta Cloud API or Twilio) that collects article/news content, runs a minimal cleanup preview, and publishes into the static site.

## Run

1. Copy `.env.example` to `.env` and fill values.
2. Install dependencies:
   - `npm install`
3. Start locally:
   - `npm run dev`

## Meta webhook (recommended)

Configure Meta webhook to:

- `GET /webhooks/meta/whatsapp` (verification)
- `POST /webhooks/meta/whatsapp` (incoming messages)

Set:

- Callback URL: `https://api.ramopharmin.net/webhooks/meta/whatsapp`
- Verify token: same as `META_VERIFY_TOKEN`

## Twilio webhook (optional fallback)

Configure Twilio webhook to:

- `POST /webhooks/twilio/whatsapp`

## Message format

Send:

```text
news
title: ...
summary: ...
body: ...
language: fa
```

Then send `تایید انتشار` after preview response.

## Output behavior

- Generates page in `V0/articles/` or `V0/news/`
- Stores deterministic manifest in `automation/whatsapp-publish-agent/content-manifests/`
- Updates feeds/ticker with cap=5 rules
- Commits and pushes to `origin/main`
- Verifies public live URL and returns publish status

## Deploy on Render (production)

This repo includes `render.yaml` for one-click setup.

1. Push repository to GitHub.
2. In Render: New -> Blueprint -> select this repo.
3. Confirm service `ramo-whatsapp-publish-agent`.
4. Set secret env vars in Render:
   - `META_VERIFY_TOKEN`
   - `META_ACCESS_TOKEN`
   - `META_PHONE_NUMBER_ID`
   - `CURSOR_API_KEY`
5. Attach custom domain: `api.ramopharmin.net`.
6. In DNS provider, add a `CNAME` from `api` to Render target.
7. In Meta dashboard, set callback:
   - `https://api.ramopharmin.net/webhooks/meta/whatsapp`
