# Source ledger — schema, score rubric, upsert protocol

This file is the **single source of truth** for how sources are scored and recorded.
Split of duty: the **verify step** *computes* each source's score and emits a scored table
in its output but writes no file (it stays read-only). The **consolidate step** *performs
the upsert* into the ledger — co-locating the note-write and the ledger-write.

Ledger file: `LEDGER` (see SKILL.md Setup; default `<NOTES_DIR>/Source Ledger.md`).

## Composite score (0–100)

Every source that **survives fact-check** in the verify step gets a score. The four
components sum to the composite, so a reader sees exactly why a source ranks where it does
(the "itemized" view) alongside the final number (the "composite" view).

| Component | Max | What it captures | Rule |
|-----------|-----|------------------|------|
| **Tier** | 40 | *How authoritative the source is* — a peer-reviewed paper / official primary doc outweighs a blog or forum post | `authoritative`/`academic` = 40 · `practitioner` = 20 · `community` = 10 (per references/tiers.md) |
| **Recency** | 25 | *How fresh it is* — in fast-moving fields old claims go stale, so newer sources rank higher | Published ≤90 days ago = 25; then linear decay to 0 at `recency_default_days` (540). Formula: `round(25 * max(0, (540 - age_days) / (540 - 90)))`, capped at 25 for age ≤ 90 |
| **Corroboration** | 20 | *How well independent sources back it up* — a claim confirmed by 2+ unrelated sources is safer than a lone assertion | Independent sources confirming its key claim during verify: 0 → 0 · 1 → 10 · 2+ → 20 |
| **Reuse** | 15 | *How often it keeps proving useful* — every later research that relies on it again lifts battle-tested sources to the top | +5 each time the source recurs in a *later* research and re-passes verify (cap 15). New sources start at 0 |

`Score = Tier + Recency + Corroboration + Reuse`. A brand-new excellent academic source
tops out at 85 (no reuse yet); reuse is what pushes proven sources to the top over time —
this is how the list "manages itself."

## Table schema (one table per domain, sorted by Score desc)

```markdown
## <domain_key>

_Domain rollup: <N> sources · avg <avg> · top: <top source> (<top score>)_

| # | Source | URL | Tier | Score | Tier | Recency | Corrob. | Reuse | Last verified | Used in |
|---|--------|-----|------|-------|------|---------|---------|-------|---------------|---------|
| 1 | <name> | <url> | <tier> | **<score>** | <t> | <r> | <c> | <u> | YYYY-MM-DD | [[research-note]] |
```

- Column 5 **Score** = the composite (bold).
- Columns 6–9 (Tier/Recency/Corrob./Reuse) = the itemized components; they sum to Score.
- **Used in** = links to the consolidated research notes that relied on the source.
- Low-confidence sources that were retained "for illustration only" keep their tag in the
  Source name — the ledger records that they passed with a caveat, not cleanly.

## Upsert protocol (consolidate step)

Using the scored table the verify step emitted, for each surviving source, in its domain section:

1. **Normalize the URL** (strip protocol, `www.`, trailing slash, query/anchor) as the match key.
2. **New source** → append a row with all four components + composite, today as Last verified, and the current research note in "Used in".
3. **Existing source** (key matches) → recompute Tier/Recency/Corroboration from this run,
   **bump Reuse by +5 (cap 15)**, set Last verified = today, and append the current research
   to "Used in" (if not already listed).
4. **Re-sort** the domain table by Score descending and renumber `#`.
5. **Update the rollup line** (count, average score, top source).
6. **Promote the venue** (optional, per references/tiers.md): if a source scored ≥85 and its
   host isn't in the domain's `authoritative` array of the venue map, append it there.

Keep edits surgical — one domain section at a time. Never rewrite the whole file.
