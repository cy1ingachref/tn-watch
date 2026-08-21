#!/usr/bin/env python3
"""tn-watch — zero-dependency change/digest monitor.

Watches one or more sources (RSS/Atom, JSON, or simple HTML <a>/<title>)
for new items matching keywords, dedupes across runs, and prints a digest.

No third-party deps: stdlib only (urllib, xml, html). Runs anywhere
Python 3.8+ exists — including a cron on a free tier.

Config (yaml-ish, same minimal parser as sigma-lab):
  name: my-monitor
  sources:
    - url: https://example.com/feed.xml
      type: rss            # rss | atom | json | html
      item_xpath: ...      # (rss/atom only) ignored; we use <item>/<entry>
    - url: https://api.example.com/jobs.json
      type: json
      items_field: data
      title_field: title
      link_field: url
      text_field: description
  keywords:                # case-insensitive; item matches if ANY keyword in title/text
    - tenders
    - cybersecurity
  seen_file: .tnwatch_seen.json

Run:  python tnwatch.py config.yml
Exit: 0 always (digest printed even if empty); nonzero only on config error.
"""
import sys
import os
import json
import urllib.request
import urllib.error
import re
import html
from datetime import datetime, timezone

# ---- minimal yaml parser (same approach as sigma-lab) ---------------------
def _tokenize(text):
    toks = []
    for raw in text.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        ind = len(raw) - len(raw.lstrip(" "))
        s = raw.strip()
        if ":" not in s:
            continue
        k, _, v = s.partition(":")
        toks.append((ind, k.strip(), v.strip()))
    return toks

def _flow_list(v):
    inner = v.strip()[1:-1]
    out, buf, depth, q = [], "", 0, None
    for ch in inner:
        if q:
            buf += ch
            if ch == q: q = None
        elif ch in "'\"":
            q = ch; buf += ch
        elif ch == "[":
            depth += 1; buf += ch
        elif ch == "]":
            depth -= 1; buf += ch
        elif ch == "," and depth == 0:
            out.append(buf.strip()); buf = ""
        else:
            buf += ch
    if buf.strip(): out.append(buf.strip())
    return [i.strip().strip("'\"") for i in out]

def _unq(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        return v[1:-1]
    return v

def _build(toks, idx, ind):
    node = {}
    while idx < len(toks):
        i, k, v = toks[idx]
        if i < ind: break
        if i > ind: break
        if v == "":
            if idx + 1 < len(toks) and toks[idx + 1][0] > ind:
                child, idx = _build(toks, idx + 1, toks[idx + 1][0])
                # list of dicts (sources:)
                if isinstance(child, dict) and "_listitem" in child:
                    lst = child["_listitem"]
                    node[k] = lst
                else:
                    node[k] = child
                continue
            else:
                node[k] = None; idx += 1; continue
        if v.startswith("["):
            node[k] = _flow_list(v); idx += 1; continue
        node[k] = _unq(v); idx += 1
    return node, idx

def parse_yaml(text):
    toks = _tokenize(text)
    if not toks: return {}
    root, _ = _build(toks, 0, toks[0][0])
    return root

# ---- source fetchers -------------------------------------------------------
UA = {"User-Agent": "tn-watch/1.0 (+https://github.com/cy1ingachref/tn-watch)"}

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "replace")

def parse_rss(xml_text):
    items = []
    # crude but robust: split on <item> / <entry>
    blocks = re.findall(r"<(item|entry)[^>]*>.*?</\1>", xml_text, re.DOTALL | re.IGNORECASE)
    for b in blocks:
        title = re.search(r"<title[^>]*>(.*?)</title>", b, re.DOTALL | re.IGNORECASE)
        link = re.search(r"<(link|id)[^>]*>(.*?)</\1>", b, re.DOTALL | re.IGNORECASE)
        # atom link may be an attribute
        if not link:
            link = re.search(r'<link[^>]*href="([^"]+)"', b, re.IGNORECASE)
            link_url = link.group(1) if link else ""
        else:
            link_url = _strip_tags(link.group(2)) if link else ""
        desc = re.search(r"<(description|summary)[^>]*>(.*?)</\1>", b, re.DOTALL | re.IGNORECASE)
        t = _strip_tags(title.group(1)) if title else "(no title)"
        d = _strip_tags(desc.group(2)) if desc else ""
        items.append({"title": t, "link": link_url, "text": d})
    return items

def parse_json(text, items_field, title_field, link_field, text_field):
    data = json.loads(text)
    if items_field:
        for f in items_field.split("."):
            data = data[f]
    out = []
    for it in data:
        out.append({
            "title": str(it.get(title_field, "")),
            "link": str(it.get(link_field, "")),
            "text": str(it.get(text_field, "")),
        })
    return out

def parse_html(text):
    # pull <a> tags and <title>
    title_m = re.search(r"<title[^>]*>(.*?)</title>", text, re.DOTALL | re.IGNORECASE)
    out = []
    for m in re.finditer(r"<a[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", text, re.DOTALL | re.IGNORECASE):
        href, label = m.group(1), _strip_tags(m.group(2))
        if label.strip():
            out.append({"title": label.strip(), "link": href, "text": label})
    if title_m:
        out.insert(0, {"title": _strip_tags(title_m.group(1)), "link": "", "text": ""})
    return out

def _strip_tags(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    s = html.unescape(s)
    return s.strip()

# ---- matching + dedupe -----------------------------------------------------
def matches(item, keywords):
    hay = (item["title"] + " " + item["text"]).lower()
    return any(k.lower() in hay for k in keywords)

def key_of(item):
    return item.get("link") or item.get("title")

def build_sources(cfg):
    """Assemble source dicts from numbered keys: source_1_url, source_1_type, ..."""
    pat = re.compile(r"^source_(\d+)_(url|type|items_field|title_field|link_field|text_field)$")
    groups = {}
    for k, v in cfg.items():
        m = pat.match(str(k))
        if m:
            groups.setdefault(m.group(1), {})[m.group(2)] = v
    srcs = [groups[n] for n in sorted(groups) if "url" in groups[n]]
    return srcs


def run(cfg, dry=False):
    keywords = cfg.get("keywords", []) or []
    seen_file = cfg.get("seen_file", ".tnwatch_seen.json")
    seen = set()
    if os.path.exists(seen_file):
        try:
            seen = set(json.load(open(seen_file)))
        except Exception:
            seen = set()
    new_items = []
    for src in build_sources(cfg):
        url = src.get("url")
        stype = (src.get("type") or "rss").lower()
        try:
            raw = fetch(url)
        except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
            print(f"[warn] fetch failed {url}: {e}", file=sys.stderr)
            continue
        if stype in ("rss", "atom"):
            items = parse_rss(raw)
        elif stype == "json":
            items = parse_json(raw, src.get("items_field"), src.get("title_field"),
                               src.get("link_field"), src.get("text_field"))
        elif stype == "html":
            items = parse_html(raw)
        else:
            print(f"[warn] unknown type {stype} for {url}", file=sys.stderr)
            continue
        for it in items:
            k = key_of(it)
            if not k or k in seen:
                continue
            if keywords and not matches(it, keywords):
                seen.add(k)  # don't re-alert non-matches, but remember them
                continue
            new_items.append((url, it))
            seen.add(k)
    if not dry:
        json.dump(sorted(seen), open(seen_file, "w"), indent=0)
    return new_items

def main():
    if len(sys.argv) < 2:
        print("usage: python tnwatch.py config.yml", file=sys.stderr)
        return 2
    cfg = parse_yaml(open(sys.argv[1], encoding="utf-8").read())
    items = run(cfg)
    if not items:
        print("tn-watch: no new matches.")
        return 0
    print(f"tn-watch: {len(items)} new match(es) @ {datetime.now(timezone.utc).isoformat()}")
    for src_url, it in items:
        print("-" * 60)
        print(f"  [{it['title']}]")
        if it["link"]:
            print(f"  {it['link']}")
        if it["text"]:
            print(f"  {it['text'][:200]}")
        print(f"  (source: {src_url})")
    return 0

if __name__ == "__main__":
    sys.exit(main())
