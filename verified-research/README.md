# verified-research

**A multi-agent research pipeline that produces answers you can defend** — every claim
cross-checked against 2+ independent sources, every source scored 0–100 and linked, and a
persistent ranked Source Ledger that gets smarter with every research you run.

## The problem it solves

A single "search the web and summarize" pass produces confident-sounding notes built on
whatever ranked first — SEO farms, vendor marketing, stale numbers, and claims nobody
checked. This skill replaces that with a chain:

```
decode → discover → gather → verify → critic → consolidate
  map      find       read     attack    judge      write
```

The two steps that do the heavy lifting:

- **verify** is adversarial: it drops aggregators, tags commercial-conflict sources,
  cross-references every key claim, reconciles "contradicting" numbers (usually a
  time-horizon or gross-vs-net illusion), checks the arithmetic behind computed metrics,
  and outputs a **do-not-cite list** plus **primary-source flags** for claims that rest
  only on secondary reporting.
- **critic** hunts what round 1 missed — typically the field's own counter-force
  (regulators, failure data, skeptics) and sources the user explicitly asked for — then
  either spawns one more targeted round (cap: 2) or finalizes. Primary-source flags get
  resolved by a surgical fact-checking agent running in parallel.

## What you get

1. **A readable research note**: TL;DR → non-obvious key insights → data tables with at
   least one visual → bottom line → tiered source list where **every source is a
   clickable link** with a publication date and a high/medium/low confidence tag.
2. **A Source Ledger** that persists across researches: every surviving source scored
   (Tier 40 + Recency 25 + Corroboration 20 + Reuse 15), ranked per domain. Sources that
   keep re-passing verification rise via the Reuse bonus — over time you accumulate a
   battle-tested source list per domain.
3. **A venue map** that remembers where the good sources live per domain, and grows.

## Install

```bash
git clone https://github.com/booya1986/My-Skills.git
cp -r My-Skills/verified-research ~/.claude/skills/
```

Then in Claude Code: *"do verified research on &lt;your question&gt;"*.
Set your paths once (notes folder, ledger location) — see the Setup table in `SKILL.md`.

## Design rules that make it trustworthy

- **Tier balance is enforced**: every topic must include both formal sources
  (regulators, analysts, academia) and community signal (HN/Reddit/X) — and when a tier
  is genuinely empty, the note says so instead of silently looking "covered".
- **No bare citations**: every source is a link + date + confidence tag.
- **Computed metrics get audited**: any X-per-Y ratio is traced to both inputs, the
  arithmetic is checked, and the figure is labeled reported-vs-computed.
- **Field-tested failure guards**: gather agents write output incrementally (a partial
  file beats a dead agent), parallel agents never co-write shared files, and community
  scraping has a documented fallback chain for environments without shell access.

## Files

```
verified-research/
├── SKILL.md               The pipeline: chain, setup, hard rules
├── README.md              You are here
└── references/
    ├── steps.md           Per-step role prompts (decode → consolidate)
    ├── tiers.md           Source tiers, venue map, community fetch playbook
    └── ledger.md          Score rubric + Source Ledger schema + upsert protocol
```

## Origin

Extracted from a personal AI-assistant project where it runs as a 6-step multi-agent
pipeline. Battle-tested on real research runs (deep-dives into AI-era banking
transformation, TTS engine selection, token-economics — each 60–125 scored sources,
2–3 rounds). The lessons those runs taught (turn-budget guards, primary-source flag
checks, do-not-cite lists, computed-metric audits) are baked into the step specs.
