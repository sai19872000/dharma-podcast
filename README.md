# dharma-podcast

AI-generated 5–8 min East-West dharma podcast — pairing primary-source
East-lineage dharma traditions (Vyāsa, Patañjali, Buddha-as-Sujato, Śaṅkara)
with modern consciousness science (Capra, Kastrup, Seth).

Two voices, license-clean PD/CC0/CC-BY-NC-SA-4.0 sources only.

## Three layers

1. **`soul.md`** — the show's worldview, voice, source-discipline, and
   anti-pattern list. Loaded as the system-prompt prefix on every script
   generation. Hand-edited; agents read but never silently rewrite.
2. **`engine/`** — Python pipeline. `concept_queue → corpus_loader →
   script_gen → tts → stitch → normalize → artifacts → tg_notify`,
   plus `publish.py` for the R2 + RSS distribution step.
3. **`web/` + Cloudflare Worker** — Aura-branded landing page +
   `/feed.xml` RSS at `https://dharma.saiteja.ai`.

## Quick start (when engine is implemented)

```bash
# Required env vars (set in your shell — never committed):
export ELEVENLABS_API_KEY=…
export ELEVENLABS_VOICE_ID_SAI=…       # Voice A: teacher
export ELEVENLABS_VOICE_STUDENT=…      # Voice B: student
export ANTHROPIC_API_KEY=…             # for script_gen.py

# Generate Episode 001 end-to-end (HALT after Telegram delivery):
python -m engine.run --episode 1 --concept vairagya
```

## Episode 001 publish (HALT-guarded)

`publish.py` refuses to upload Ep001 to R2 unless `DHARMA_EP001_APPROVED=1`
is set in the env. This is intentional: Episode 001 is the format-lock
moment, and Sai must approve the final artifact on Telegram before any
public RSS asset goes live. Episode 002+ ignores the guard.

## Distribution

- RSS: `https://dharma.saiteja.ai/feed.xml`
- R2 bucket: `dharma-podcast-audio` (audio + show notes)
- Worker: `dharma-podcast-rss` (single Worker for `/feed.xml` + landing)
- DNS: `dharma.saiteja.ai` → CF Worker, orange-cloud, **no CF Access**
  (RSS readers, Spotify, Apple must reach anonymously)

## Source-discipline

| Source                      | License | Cite as                         | URL pattern                                |
|-----------------------------|---------|---------------------------------|--------------------------------------------|
| Bhagavad Gita               | PD      | Edwin Arnold (1885)             | sacred-texts.com/hin/gita/                 |
| Yoga Sūtras                 | PD      | Vivekananda 1896 / Woods 1914   | sacred-texts.com / archive.org             |
| Sujato Pāli translations    | CC0     | Sujato (2018), SuttaCentral     | suttacentral.net/<id>/en/sujato            |
| Upaniṣads                   | PD      | Max Müller, SBE vols 1, 15      | sacred-texts.com/hin/sbe01/                |
| Tao Te Ching                | PD      | James Legge (1891)              | sacred-texts.com/tao/sbe39/                |
| Sanskrit originals          | PD      | GRETIL                          | gretil.sub.uni-goettingen.de               |
| Modern thinkers             | ©       | **Paraphrase only**, cite talks | YouTube / arXiv / personal site            |

Hard rule (engine-enforced in `artifacts.py`): every row in
`citations.jsonl` MUST have `license` ∈ `{PD, CC0, CC-BY-NC-SA-4.0}`.

## References

- Architecture spec: `~/factory/outputs/20260508_212326/architect_dharma_podcast_20260508_212328.md`
- Soul (worldview canon): [`soul.md`](./soul.md)
- Concept queue (state machine): `concept_queue.json` (data agent seeds)
- Project registry: `dharma-podcast` in `~/factory/memory/projects.json`

## License

Code: MIT (TBD on first ship). Audio + show notes: CC-BY-NC-SA-4.0.
Quoted PD/CC0 sources retain their upstream licenses.
