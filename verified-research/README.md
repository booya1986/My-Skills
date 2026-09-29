# verified-research

**A multi-agent research pipeline that produces answers you can defend** — every claim
cross-checked against 2+ independent sources, every source scored 0–100 and linked, and a
persistent ranked Source Ledger that gets smarter with every research you run.

## The problem it solves

A single "search the web and summarize" pass produces confident-sounding notes built on
whatever ranked first — SEO farms, vendor marketing, stale numbers, and claims nobody
checked. This skill replaces that with a chain:

```
decode → discover → gather → verify → critic → consolidate → publish (optional)
  map      find       read     attack    judge      write        share
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
4. **A debunked-statistics list** that grows too: famous numbers that failed
   fact-checking, each with a verified replacement, so they are never chased twice.
5. **Optionally, a designed HTML report**: when you say yes, the note becomes a
   standalone editorial page (floating contents, interactive components, infographics,
   left-to-right or right-to-left) on GitHub Pages, with a `DESIGN.md` contract.

### Decision-shaped questions

Ask "should I take / build / buy X?" and the skill asks a few framing questions first,
then covers the angles a "what is X" report misses: the readings of the mandate, who
wins and loses, the end user's view, alternatives to doing it at all, cost and the
promises you'll be measured on, personal fit, a pre-mortem, an interview guide, and a
measurement framework.

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
- **No bare citations**: every source is a link + date + confidence tag, both in the
  sources list and inline where the text names it.
- **Every number carries who/when/sample**; untraceable famous statistics go to a
  do-not-cite table with what to say instead.
- **Scores come from a script** (`scripts/score.py`), not from an agent's arithmetic.
- **Readable, native voice**: the note is written the way a native speaker of its
  language would explain it out loud, with a read-aloud test on every section.
- **Computed metrics get audited**: any X-per-Y ratio is traced to both inputs, the
  arithmetic is checked, and the figure is labeled reported-vs-computed.
- **Field-tested failure guards**: gather agents write output incrementally (a partial
  file beats a dead agent), parallel agents never co-write shared files, and community
  scraping has a documented fallback chain (including a Firecrawl route for Reddit) for
  environments without shell access.

## Files

```
verified-research/
├── SKILL.md                    The pipeline: chain, setup, hard rules
├── README.md                   You are here
├── CHANGELOG.md                What changed, by date
├── references/
│   ├── steps.md                Per-step role prompts (decode → consolidate → publish)
│   ├── tiers.md                Source tiers, venue map, community fetch playbook
│   ├── ledger.md               Score rubric + Source Ledger schema + upsert protocol
│   ├── decision-questions.md   The nine angles for decision-shaped questions
│   ├── debunked-statistics.md  Famous numbers that failed fact-checking + replacements
│   ├── writing-voice.md        How to write the note like a native speaker
│   └── publish.md              Optional designed HTML report on GitHub Pages
├── scripts/
│   └── score.py                Computes ledger scores and prints ready rows
├── assets/publish-kit/         build.py, components.py, template.html, DESIGN.md,
│                               style-reference.png (copied per report)
└── evals/evals.json            Test prompts with expected behavior
```

Quick check of the scorer:

```bash
printf 'Example paper | https://example.org/paper | academic | 2026-06-01 | 2\n' \
  | python3 verified-research/scripts/score.py
```

## Origin

Extracted from a personal AI-assistant project where it runs as a multi-agent pipeline.
Battle-tested on real research runs (deep-dives into AI-era industry transformation, TTS
engine selection, token economics, and organizational decisions — each 60–125 scored
sources, 2–3 rounds). The lessons those runs taught (turn-budget guards, primary-source
flag checks, do-not-cite lists, computed-metric audits, decision angles, readable voice)
are baked into the step specs. See `CHANGELOG.md` for what changed when.
