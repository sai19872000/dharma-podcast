# Deployment runbook — dharma-podcast

> Devops-owned. Updated by the deploying agent on every change.

## Topology

| Component | Vendor / Host | Resource name | IaC / Config |
|-----------|---------------|---------------|--------------|
| Repo | GitHub | `sai19872000/dharma-podcast` | this repo |
| Local clone | `~/dharma-podcast` | — | — |
| Audio + RSS storage | Cloudflare R2 | `dharma-podcast-audio` (public read) | TBD `wrangler.toml` |
| RSS + landing Worker | Cloudflare Workers | `dharma-podcast-rss` | TBD `worker/wrangler.toml` |
| DNS | Cloudflare zone `saiteja.ai` | `dharma.saiteja.ai` CNAME → Worker, **no Access** | CF dashboard / API |

## Bootstrap status (run `20260509_085103` — PARTIAL deploy, static-only)

| Step | Status | Notes |
|------|--------|-------|
| GitHub repo created | ✅ | `gh repo create sai19872000/dharma-podcast --public` |
| Project registered | ✅ | `~/factory/scripts/update_projects.sh add …` |
| Local clone | ✅ | `~/dharma-podcast` |
| Repo skeleton (PR #1) | ✅ | merged 2026-05-08 |
| `soul.md` checked in | ✅ | Verbatim from research_lead delivery |
| `concept_queue.json` seeded | ✅ | 9 concepts; vairagya `drafted`, rest `queued` |
| Engine (PR #4) | ✅ merged | publish.py + feed XML render + iter-2 P0/P1 fixes |
| Aura landing (PR #2) | ⏸ open | `feat/web-landing` — deployed from branch via Worker assets, awaiting T3 QA verdict before merge |
| R2 bucket `dharma-podcast-audio` | ⚠️ **BLOCKED-ON-SAI** | R2 not enabled at the account level (10042). One-click toggle at `https://dash.cloudflare.com/?to=/:account/r2`. L3 ping sent 2026-05-09 13:05Z. |
| Audio upload `audio/001.mp3` | ⏸ deferred | After R2 toggle. Source: `episodes/001/episode_001.mp3` (6,201,722 bytes; sha256 `b50f27931cd4f07a56b1eb458db4eb2788fc8648ba941878ecfafc13dec59d0c`) |
| Worker `dharma-podcast-rss` | ✅ deployed | Version `d5d71a3d-298a-456e-9779-9498d981703d` (2026-05-09); serves `web/` via `[assets]` binding. Route: `dharma.saiteja.ai/*`. |
| DNS `dharma.saiteja.ai` CNAME | ✅ live | proxied → `dharma-podcast-rss.workers.dev`, record id `a6499f9ba67d790998171fbadf592faf`. No CF Access (RSS readers need anonymous reach). |
| `web/feed.xml` rendered | ✅ static | Single Episode 001 item; SHOW dict mirrors `engine/publish.py`. Re-render via `engine.publish` once R2 enabled (replaces this static file with one whose enclosure URL works). |
| Episode 001 publish (audio → R2) | ⏸ HALT-guarded | `DHARMA_EP001_APPROVED=1` AND R2 enabled |

### Verification (2026-05-09 13:06Z)
- `https://dharma.saiteja.ai/` → HTTP 200, 1377 B, `text/html`
- `https://dharma.saiteja.ai/feed.xml` → HTTP 200, 5701 B, `application/xml`, valid RSS, 1 item
- `https://dharma.saiteja.ai/e/001/` → HTTP 200, 3245 B, `text/html`
- `https://dharma-podcast-audio.r2.dev/audio/001.mp3` → HTTP 500 (R2 disabled — expected; player falls back to simulated mode)

## Access blocker

The `CLOUDFLARE_API_TOKEN` and OAuth token both lack R2 scope on this
account. R2 itself is enabled (electionwatch already uses it) — what's
missing is **token-level R2 read/write permission** for the bot context.

**Required action (Sai or human-with-CF-dashboard):** issue a new API
token with scope `R2 → Edit` for the saiteja.ai account, OR add the R2
edit scope to the existing `cfut_…` token. Once the env exposes a
token with R2 perms, devops can:

```bash
# 1. Provision R2 (one-time)
cd /tmp  # avoid factory .env clobbering OAuth
PATH=~/.nvm/versions/node/v22.22.2/bin:$PATH \
  CLOUDFLARE_API_TOKEN=<new-token-with-r2> \
  CLOUDFLARE_ACCOUNT_ID=b02a6a234f0ab516c212d51ece6f3fe8 \
  npx wrangler r2 bucket create dharma-podcast-audio

# 2. Mark public read on the bucket (CF dashboard or API)
curl -X PUT "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/r2/buckets/dharma-podcast-audio" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"settings":{"publicAccess":"enabled"}}'

# 3. Deploy the Worker
cd ~/dharma-podcast/worker
PATH=~/.nvm/versions/node/v22.22.2/bin:$PATH npx wrangler deploy

# 4. Add the DNS CNAME (zone API token scope already works)
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"CNAME","name":"dharma","content":"dharma-podcast-rss.workers.dev","proxied":true}'
```

## Episode-1 publish (HALT-guarded)

```bash
cd ~/dharma-podcast
export ELEVENLABS_API_KEY=…  ELEVENLABS_VOICE_ID_SAI=…  ELEVENLABS_VOICE_STUDENT=…
export ANTHROPIC_API_KEY=…
export DHARMA_EP001_APPROVED=1   # ONLY after Sai's Telegram approval
python -m engine.publish --episode 1
```

`engine/publish.py` is required to refuse `episode_no==1` unless
`DHARMA_EP001_APPROVED` is set in the env (per ADR-5).

## Rollback

- Worker: `npx wrangler rollback` from `~/dharma-podcast/worker/`
- DNS: delete the CNAME via CF dashboard or zone-DNS API
- R2 audio: delete the offending object via `wrangler r2 object delete dharma-podcast-audio/audio/NNN.mp3`
- Feed: regenerate `feed.xml` from `episodes/index.json` and re-upload
