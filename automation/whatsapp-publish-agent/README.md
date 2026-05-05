# Publish Agent (Telegram / WhatsApp)

Messaging intake service (Telegram, Meta Cloud API, or Twilio) that collects article/news content, runs a minimal cleanup preview, and publishes into the static site.

## Run

1. Copy `.env.example` to `.env` and fill values.
2. Install dependencies:
   - `npm install`
3. Start locally:
   - `npm run dev`

## Telegram webhook (recommended)

Configure Telegram webhook to:

- `POST /webhooks/telegram`

The bot receives Persian content, sends cleaned preview, and publishes on `تایید انتشار`.

## Meta webhook (optional)

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

## Telegram production walkthrough

1. Create bot in Telegram with [@BotFather](https://t.me/BotFather):
   - `/newbot`
   - Save `TELEGRAM_BOT_TOKEN`.
2. Deploy this service on Render (Blueprint with `render.yaml`).
3. Set Render env vars:
   - `WHATSAPP_PROVIDER=telegram`
   - `TELEGRAM_BOT_TOKEN=<token>`
   - `TELEGRAM_WEBHOOK_SECRET=<random-secret>`
   - `CURSOR_API_KEY=<cursor key>`
4. Attach custom domain: `api.ramopharmin.net`.
5. Register Telegram webhook:

```bash
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://api.ramopharmin.net/webhooks/telegram",
    "secret_token": "<TELEGRAM_WEBHOOK_SECRET>"
  }'
```

6. Verify webhook:

```bash
curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo"
```

7. Start chat in Telegram and send:
   - `خبر` or `مقاله سلامت`
   - `title: ...`
   - `summary: ...`
   - `body: ...`
   - `language: fa`
   - then `تایید انتشار`
