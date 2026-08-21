# tn-watch — Zero-Cost Business Watchdog (Set-up + Running Service)

## ONE-LINE PITCH
A done-for-you monitoring bot that watches any website, RSS feed, or API for
the keywords YOU care about — and sends you a daily digest of what's NEW.
No subscriptions. No installs. 30 TND (~$10) one-time set-up, then I run it for you.

## WHAT YOU GET
- A working `tn-watch` instance configured for YOUR need (tenders, jobs,
  competitor prices, compliance updates, sector news — anything with a feed/API).
- Keywords: you tell me what to watch; I wire them in.
- Daily digest delivered to your email or WhatsApp.
- The full open-source repo + your personal config, so you own it.
- Zero infrastructure cost — runs on a free tier.

## WHO IT'S FOR
- Tunisian agencies & freelancers tracking **government tenders / appels d'offres**
- E-commerce shops watching **competitor prices / stock drops**
- Consultants following **regulation / compliance changes**
- Anyone who's tired of manually refreshing the same 5 websites

## HOW IT WORKS (technical, but you don't need to read this)
`tn-watch` is a pure-Python (stdlib only, no pip) monitor:
- Sources: RSS / Atom / JSON API / HTML
- Keywords: case-insensitive; matches title or body
- Dedupe: seen items are remembered, so you never get the same alert twice
- It's proven by a green-check test (`python tests/test_tnwatch.py` → ALL GREEN ✓)
  and runs against live data (verified on Hacker News' API).

## DELIVERY
1. You buy here (Gumroad handles payment — I never see your card).
2. You message me: **what to watch + which keywords + where to send the digest.**
3. Within 24h you get the running config + your first digest.

## PRICE
30 TND one-time (~$10). No monthly lock-in — but if you want me to keep it
running and delivering daily, that's an optional 30 TND/month.

## PROOF
- Public repo: https://github.com/cy1ingachref/tn-watch
- Live demo config pulls real "security" stories from Hacker News and prints them.
- CI runs the green-check on every push (visible in the repo).

> Built and verified, not promised.
