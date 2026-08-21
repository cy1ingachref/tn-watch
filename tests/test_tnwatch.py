#!/usr/bin/env python3
"""Green-check: tn-watch must (1) match keyword items, (2) dedupe on re-run."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import tnwatch as tw

FIXTURE = json.dumps({
    "items": [
        {"title": "Cybersecurity tender open in Tunis", "link": "http://x/1", "body": "gov RFP"},
        {"title": "Recipe for cake", "link": "http://x/2", "body": "sugar"},
        {"title": "Another cybersecurity alert", "link": "http://x/3", "body": "CVE drop"},
    ]
})

def fake_fetch(url):
    return FIXTURE

def load_cfg():
    return tw.parse_yaml(open(os.path.join(os.path.dirname(__file__), "config.fixture.yml")).read())

def main():
    tw.fetch = fake_fetch
    seen = os.path.join(os.path.dirname(__file__), ".seen_fixture.json")
    if os.path.exists(seen):
        os.remove(seen)
    cfg = load_cfg()
    r1 = tw.run(cfg)
    n1 = len(r1)
    r2 = tw.run(cfg)  # second run: everything already seen
    n2 = len(r2)
    ok = (n1 == 2) and (n2 == 0)  # 2 of 3 items match keywords (cybersecurity/tender)
    print(f"[{'PASS' if ok else 'FAIL'}] first-run matches={n1} (want 2), second-run matches={n2} (want 0)")
    if not ok:
        print("  first:", [(u, i['title']) for u, i in r1])
        print("  second:", [(u, i['title']) for u, i in r2])
    print("ALL GREEN ✓" if ok else "FAILED")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
