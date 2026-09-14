# tn-watch — Zero-Dependency Change Monitor

A zero-dependency change/digest monitor. Point it at any RSS/Atom feed, JSON API, or HTML page, give it keywords, and it tells you what's *new* — and dedupes so you never get the same alert twice. Pure Python stdlib (no `requests`, no pip), runs anywhere Python 3.8+ exists.

## What it does

- **Sources**: RSS, Atom, JSON APIs, HTML pages
- **Keywords**: Case-insensitive matching against titles and body text
- **Dedupe**: Seen items persisted to a local file, so re-runs stay silent on old content
- **Zero cost**: No API keys, no paid tiers, runs on free-tier cron

## Quick start

```bash
python tnwatch.py config.demo.yml     # live demo: HN "security" stories
python tests/test_tnwatch.py           # green-check (offline, deterministic)
```

## Configuration

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

## Output

Prints a digest of new items matching keywords since the last run. Suitable for piping to email, Slack, or Telegram.

## Tests

```bash
python tests/test_tnwatch.py
```

Verifies keyword matching and dedupe behavior with offline fixtures.

## Requirements

- Python 3.8+
- No external dependencies

## License

MIT
