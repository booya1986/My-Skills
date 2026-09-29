---
name: verified-research
description: >
  Verified-research pipeline: decode → discover → gather → verify → critic →
  consolidate, with an optional publish step (a designed HTML report with
  infographics on GitHub Pages) that the user opts into. Use it whenever the user
  wants research they can act on or share: "do verified research on X",
  "deep-research Y with sources", "what's the latest on Z, checked", "prepare a
  report on…", and also for decision-shaped questions ("should I take/build/buy X",
  "what do I need to know before…") even if the word research never comes up.
  Enforces both formal (analyst/academic/regulator) and community (Reddit/HN/X)
  sources, fact-checks every number against a growing list of debunked statistics,
  scores every surviving source 0–100 into a persistent Source Ledger, and writes a
  readable, linked, confidence-tagged note in the user's language.
---

# Verified Research

A research pipeline built for one thing: **answers you can defend**. Instead of a single
web-search pass, it runs a chain of specialized steps with an adversarial verification
layer in the middle, so every claim in the final note is either corroborated by 2+
independent sources or explicitly labeled as weaker.

## Why this exists

Unverified research is worse than none: a confident report with a folklore statistic in
it gets quoted in a meeting and then has to be walked back. The chain is built so that
every number in the final note has a source you can open, a date, a confidence level,
and a reason it survived. The community tier exists because analyst reports tell you
what should happen and practitioners tell you what actually breaks.

## Setup (once per environment)

Define these locations (defaults shown; override to fit your setup):

| What | Purpose | Default |
|---|---|---|
| `OUTPUT_DIR` | Working artifacts per research run | `./verified-research-<slug>/` |
| `NOTES_DIR` | Where finished research notes live (e.g., your notes app folder) | `./research-notes/` |
| `LEDGER` | The persistent ranked Source Ledger (see references/ledger.md) | `<NOTES_DIR>/Source Ledger.md` |
| `VENUE_MAP` | Where-to-look map per domain (see references/tiers.md) | `<NOTES_DIR>/_meta/research-venues.json` |

Below, `ART/` = the run's `OUTPUT_DIR`, and `<skill>` = this skill's folder.

## The chain (never skip a step)

| Step | Does | Reference |
|------|------|-----------|
| 1 `decode` | Break the question into topics and sub-questions. If the question is decision-shaped ("should I…", "what do I need before…"), ask framing questions first and plan the decision angles. | [steps.md](references/steps.md), [decision-questions.md](references/decision-questions.md) |
| 2 `discover` | One subagent per lens finds 4–8 fresh sources, both tiers enforced, unreachable venues named. | [steps.md](references/steps.md), [tiers.md](references/tiers.md) |
| 3 `gather` | Read and summarize each source's claims with who/when/sample. | [steps.md](references/steps.md) |
| 4 `verify` | Cross-check every claim, drop or caveat the weak ones, score every survivor with `scripts/score.py`. Read-only. | [steps.md](references/steps.md), [ledger.md](references/ledger.md), [debunked-statistics.md](references/debunked-statistics.md) |
| 5 `critic` | Surface gaps; iterate (cap 2 rounds) or finalize. For decision-shaped questions a second, targeted round is the default. | [steps.md](references/steps.md) |
| 6 `consolidate` | Write the note (TL;DR, insights, data, bottom line, limits, tiered linked sources, do-not-cite table) in a native, spoken voice, and upsert the ledger. | [steps.md](references/steps.md), [writing-voice.md](references/writing-voice.md), [ledger.md](references/ledger.md) |
| 7 `publish` (optional) | Only when the user says yes: a standalone HTML report with a design contract, interactive components and infographics, on GitHub Pages, linked from the note. | [publish.md](references/publish.md) |

## How to run it

Trigger: `/verified-research <question>` or natural language ("do verified research on…").

1. Read `references/steps.md`, `references/tiers.md` and `references/ledger.md` before
   spawning anything.
2. Ask the framing questions from `decode` when the request is decision-shaped or the
   language / destination folder / scope is unclear. A few good questions up front
   save whole extra rounds later.
3. Spawn one subagent per lens for discover+gather (one file pair per lens), then one
   verify subagent, then act as critic and consolidator yourself: the orchestrator
   already holds the whole context, and hand-offs lose it.
4. Use portable tools: `WebSearch` / `WebFetch` for discovery and gathering. Optional
   scraping helpers (Firecrawl, Apify, etc.) upgrade the community tier if you have
   them. When they are MCP tools, **the orchestrator runs the community supplement
   itself**, because subagents often are not given MCP tools and will report Reddit as
   empty when it is not (see the playbook in references/tiers.md).
5. Use absolute paths in every shell command and every subagent prompt: the working
   directory can reset between commands.
6. The consolidate step writes the note to `NOTES_DIR` and upserts the `LEDGER`.
7. At the end, offer the publish step in one line. Do not build it unless asked.

No subagent runner? The chain also works inline: execute the steps yourself in order,
writing each step's artifact before starting the next.

## Shared state

- **Source ledger** `LEDGER`: scored in verify, written in consolidate.
- **Venue map** `VENUE_MAP`: read and appended by discover.
- **Debunked statistics** `references/debunked-statistics.md` in this skill: read by
  verify, appended by consolidate whenever a famous number fails.

## Hard rules

- **Tier balance.** Every lens covers both formal and community sources, or states the
  gap explicitly. A silent gap reads as "covered" (see references/tiers.md).
- **Every surviving source is scored and logged.** Use `scripts/score.py`, not mental
  arithmetic; hand-computed scores drift.
- **Every source is a clickable link**, `[title](url)`, with a publication date and a
  confidence tag, both in the sources list and at the spot in the text where it is
  named. No bare names.
- **Every number carries who/when/sample or a caveat.** Famous statistics that cannot
  be traced to a primary study go in the do-not-cite table, with what to say instead.
- **Computed metrics get an arithmetic check:** any X-per-Y figure is traced to both
  inputs and labeled reported-vs-computed.
- **Right-to-left notes render right-to-left.** For RTL languages (Arabic, Hebrew,
  Persian, Urdu…): no left-to-right mermaid flows, no ASCII bar charts or trees, no
  monospace diagrams; use top-down flows or tables. Arrows that mean "next" point left,
  or down when stacked.
- **Confidential/employer topics stay out.** This pipeline is for public-source
  research. A topic that touches the user's employer is fine when written generically
  (no employer name, internal systems, or people); never mix in private or internal
  material.
- **Locate the note by glob, not by remembered name.** Users rename notes while a run is
  in progress.
- **Never delete without approval; report every file touched at the end.**

## Writing the note

Accuracy is not enough: an accurate note the reader cannot follow gets rewritten. Before
writing, read `references/writing-voice.md`. The short version: write like a native
speaker of the note's language, start from the answer, one everyday picture per hard
idea, short spoken paragraphs, every number next to what it means, every jargon term
explained once, and a read-aloud test on every section.

## After the note

Say what was found in plain terms, name the gaps honestly (an empty community tier for
a niche local-market or enterprise topic is a finding, not a failure), and offer the
publish step in a single line. If the user wants the HTML report, follow
`references/publish.md` end to end, including real-browser verification and cleanup.

## Why it works (design notes)

- **Formal sources give authority and numbers; community sources catch what's breaking**
  and what practitioners actually hit. You need both to be trustworthy AND current.
- **The verify step is adversarial by design:** it drops or downgrades weak sources,
  reconciles contradictions (often by time-horizon or gross-vs-net framing), and forces
  high-impact claims back to primary sources.
- **The ledger compounds.** Sources that keep re-passing verification rise via a Reuse
  bonus; over time you accumulate a battle-tested source list per domain.
- **The debunked-statistics list compounds too.** Every famous number that fails once is
  never chased again, and the next writer gets a verified replacement.
