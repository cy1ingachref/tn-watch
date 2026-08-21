# tn-watch

A **zero-dependency** change/digest monitor. Point it at any RSS/Atom feed,
JSON API, or HTML page, give it keywords, and it tells you what's *new* — and
dedupes so you never get the same alert twice. Pure Python stdlib (no
`requests`, no pip), runs anywhere Python 3.8+ exists, including a free-tier
cron.

> The green-check proves it: `python tests/test_tnwatch.py` → `ALL GREEN ✓`
> (matches keyword items on first run, 0 on second run = dedupe works).

## What it does

- **Sources**: `rss` / `atom` / `json` / `html`
- **Keywords**: case-insensitive; an item matches if ANY keyword appears in
  its title or body
- **Dedupe**: seen items persisted to `seen_file`, so re-runs stay silent on
  old news
- **Zero cost**: stdlib only; no API keys, no paid tiers

## Run it

```bash
python tnwatch.py config.demo.yml     # live demo: HN "security" stories
python tests/test_tnwatch.py           # green-check (offline, deterministic)
```

## Config (numbered sources, flow-list keywords)

```yaml
name: my-monitor
source_1_url: 'https://example.com/feed.xml'
source_1_type: rss
source_2_url: 'https://api.example.com/jobs.json'
source_2_type: json
source_2_items_field: data
source_2_title_field: title
source_2_link_field: url
source_2_text_field: description
keywords: [tender, cybersecurity]
seen_file: .tnwatch_seen.json
```

## The offer (Tunisia / MENA)

I'll **configure and run tn-watch for your specific need** — e.g. watch
government tenders, job boards, competitor pricing, compliance updates, or
RSS feeds in your sector — and deliver a daily digest to your email/WhatsApp.

- **30 TND / month** (≈ $10), paid via **Flouci**
- One-time setup included; you get the repo + the running config
- Zero infrastructure cost; runs on a free tier

→ Message me with: *what to watch* + *which keywords* + *where to send the digest*.

## Layout

```
tnwatch.py              the monitor (stdlib only)
config.demo.yml         live HN demo config
tests/                  green-check harness + fixture config
.github/workflows/      CI runs the green-check on every push
```
