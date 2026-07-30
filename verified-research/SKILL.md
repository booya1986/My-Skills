---
name: verified-research
description: >
  Verified-research pipeline — decode → discover → gather → verify → critic →
  consolidate, with adversarial fact-checking, mandatory formal+community source
  balance, a 0–100 score for every surviving source, and a persistent ranked
  Source Ledger. Use when the user wants a trustworthy, multi-source, fact-checked
  research note on any topic ("do verified research on X", "deep-research Y with
  sources", "what's the latest on Z, checked"). Produces a readable note with a
  tiered, linked, confidence-tagged source list.
---

# Verified Research

A research pipeline built for one thing: **answers you can defend**. Instead of a single
web-search pass, it runs a chain of specialized steps with an adversarial verification
layer in the middle — so every claim in the final note is either corroborated by 2+
independent sources or explicitly labeled as weaker.

## Setup (once per environment)

Define three locations (defaults shown — override to fit your setup):

| What | Purpose | Default |
|---|---|---|
| `OUTPUT_DIR` | Working artifacts per research run | `./verified-research-<slug>/` |
| `NOTES_DIR` | Where finished research notes live (e.g., your Obsidian vault) | `./research-notes/` |
| `LEDGER` | The persistent ranked Source Ledger (see references/ledger.md) | `<NOTES_DIR>/Source Ledger.md` |
| `VENUE_MAP` | Where-to-look map per domain (see references/tiers.md) | `<NOTES_DIR>/_meta/research-venues.json` |

Below, `ART/` = the run's `OUTPUT_DIR`.

## The chain (never skip a step)

| Step | id | Does |
|------|------|------|
| 1 | `decode` | Break the question into topics, sub-questions, domain map |
| 2 | `discover` | Find the latest good sources per topic — **both tiers enforced** |
| 3 | `gather` | Fetch + summarize each source's key claims + dates |
| 4 | `verify` | Credibility + recency + cross-source fact-check; **score each source**; emit primary-source flags + a do-not-cite list |
| 5 | `critic` | Surface gaps / non-obvious angles; iterate (cap 2 rounds) or finalize; spawn surgical flag-checks |
| 6 | `consolidate` | Write the polished tiered note **with a clickable link on every source** + upsert the Source Ledger |

Full per-step role prompts: [references/steps.md](references/steps.md).
Tier rules + venue map + community fetch playbook: [references/tiers.md](references/tiers.md).
Source-ledger schema + score rubric: [references/ledger.md](references/ledger.md).

## How to run it

Trigger: `/verified-research <question>` or natural language ("do verified research on…").

1. Read all three `references/` files.
2. Spawn one subagent per step, in order, each carrying that step's prompt from
   `references/steps.md`. Discovery fans out — one subagent per lens (a lens can be a
   topic or a source-tier); everything after discovery runs on the merged set.
3. Use portable tools: `WebSearch` / `WebFetch` for discovery + gathering. Optional
   scraping helpers (Firecrawl, Apify, etc.) upgrade the community tier if you have them;
   the pipeline works without them (see the playbook in references/tiers.md).
4. The consolidate step writes the final note to `NOTES_DIR` and upserts the `LEDGER`.

No subagent runner? The chain also works inline: execute the steps yourself in order,
writing each step's artifact before starting the next.

## Hard rules

- **Tier balance:** every research covers BOTH formal (authoritative/academic) AND
  community (Reddit/X/HN) sources; a missing tier is stated explicitly, never silently
  omitted (see references/tiers.md).
- **Every good source is scored + logged** to the ledger (see references/ledger.md).
- **Every source in the final note is a clickable link** `[title](url)` with a
  publication date and a confidence tag — no bare names.
- **Computed metrics get an arithmetic check:** any X-per-Y figure is traced to both
  inputs and labeled reported-vs-computed.
- **Confidential/employer topics are out of scope** — this pipeline is for public-source
  research; never mix in private or internal material.
- **Never delete without approval; report every file touched at the end.**

## Why it works (design notes)

- **Formal sources give authority and numbers; community sources catch what's breaking**
  and what practitioners actually hit. You need both to be trustworthy AND current.
- **The verify step is adversarial by design** — it exists to drop or downgrade weak
  sources, reconcile contradictions (often by time-horizon or gross-vs-net framing),
  and force high-impact claims back to primary sources.
- **The ledger compounds.** Sources that keep re-passing verification across researches
  rise via a Reuse bonus — over time you accumulate a battle-tested source list per domain.
