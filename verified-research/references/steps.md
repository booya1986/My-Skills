# Step specs — the 5+1 chain

Self-contained role prompts, so the pipeline runs in any Claude Code session with
WebSearch/WebFetch. `ART/` = the run's working folder (see SKILL.md Setup).

---

## decode  (model hint: small/fast)

**Role:** Decompose the research question into the real work. **Do not answer it.**
**Output → `ART/topics.md`:** (1) main topics, (2) sub-questions per topic, (3) the
domain(s) it falls under (map to venue-map domain keys — see references/tiers.md),
(4) suggested search terms per topic. Keep it tight; this is a map, not prose.

## discover  (fan out — one subagent per lens)

**Role:** For your assigned lens/topic, find 4–6 of the LATEST high-quality sources
(scale up when the user asks for exhaustive coverage).
**Read** the venue map for the domain's known venues as a starting point, and record
newly-validated venues for appending (per references/tiers.md).
**Enforce tier balance:** your set MUST include ≥1 formal (authoritative/academic) AND ≥1
community (Reddit/X/HN) source when they exist; if a tier has none for your lens, write
`"<tier>: none found for <topic>"` — never omit silently.
**Fetch:** `WebSearch` + `WebFetch`. Capture publication date + author/org. For the
community tier, follow the Community fetch playbook in references/tiers.md.
**Output → `ART/sources-<lens>.md`:** per source — title, URL, tier, date, 1-line relevance.
**Turn-budget guard:** write the output file BEFORE running low on turns — draft it
incrementally or reserve the final ~5 turns for writing. A partial file with 8 sources
beats a dead agent holding 15 in memory. (Field lesson: a gather agent once burned all
its turns searching and wrote nothing; it was rescued only by resuming it with
"STOP searching, write the file NOW".)

## gather

**Role:** Read the discovered sources; fetch clean content for each.
**Output → `ART/gathered.md`:** per source, a short summary of its key claims (not verbatim),
publication date, author/org, and which topic it answers. Group by topic.
*(In practice discover+gather merge well into one subagent per lens — find AND read in
the same pass; the turn-budget guard above applies doubly.)*

## verify  ← scores sources (read-only; does NOT write the ledger)

**Role:** Vet every source and claim. (1) **Credibility** — primary/official/reputable vs
SEO filler; drop aggregators that add no original reporting, tag commercial-conflict
sources "low confidence — illustration only". (2) **Recency** — flag stale items for
fast-moving topics; prefer the last 12–18 months. (3) **Fact-check** — cross-reference
each key claim against ≥2 independent sources. Reconcile apparent contradictions
explicitly (they usually dissolve on time-horizon, gross-vs-net, or announced-vs-actual
axes — spell the reconciliation out; it's often the most valuable analysis in the run).
**Then, for each surviving source:** compute its composite score per references/ledger.md
and emit a **scored table** (source, domain, normalized URL, the four itemized components +
composite). Confirm tier balance held; if a whole tier is missing, note it for the critic.
**Also:** (a) for any COMPUTED metric (X-per-Y ratios etc.), trace BOTH inputs to their
sources, check the arithmetic, and label each figure reported-vs-computed (stale inputs
get an explicit caveat); (b) end with a **primary-source flag list** — high-impact claims
resting only on secondary sources, each with the primary venue to check; (c) end with a
**do-not-cite list** the consolidator must honor (dropped sources + claims allowed only
with caveats).
**Do not write to the ledger** — the consolidate step persists these scores.
**Output → `ART/verified.md`.**

## critic

**Role:** Read everything so far. List the non-obvious insights and the gaps /
contradictions / unexamined angles. Then decide: **another round** (scoped discover→gather→
verify→critic on the new angles) if significant angles remain AND round < cap (2), OR
**finalize** (spawn consolidate). Default to finalizing past round 1 when in doubt.
A "significant new angle" is one that could change the conclusion or that the reader
would regret not seeing — not a nice-to-have. Two angle types that are chronically
missing from round 1 and worth checking for: (a) the field's own counter-force
(regulators, skeptics, failure data) when round 1 skews optimistic; (b) sources the
user explicitly named that nobody searched yet.
**Flag-check task:** when verify emitted primary-source flags, spawn a surgical
**flag-check researcher** (WebSearch/WebFetch only) in PARALLEL to any round-2 discovery.
Its verdicts (CONFIRMED-PRIMARY / CONFIRMED-SECONDARY-ONLY / REFUTED / STILL-PROPOSED)
bind the consolidator.
**Round cap scope:** the cap applies to critic-initiated rounds; USER-requested
supplementary rounds are always allowed — they run the same discover→verify rigor,
then update the note + ledger.
**Output:** a short critique + the decision.

## consolidate

**Role:** Read ALL artifacts (every round's verified sources + critique notes + flag-check
verdicts + the do-not-cite list). Write a note ANYONE can understand — plain language,
define jargon on first use.
**Required structure:** (1) **TL;DR** (2–3 sentences a non-expert gets); (2) **Key insights**
(non-obvious first, short bullets); (3) **The data** (concrete numbers/findings in markdown
tables + at least one simple visual — comparison table, mermaid diagram, or inline ASCII bars
like `48% ▆▆▆▆▆`); (4) **Bottom line / what to do**; (5) **Sources** — tiered (Authoritative /
Academic / Practitioner / Community), each with publication date + confidence (high/medium/low)
**+ a clickable markdown link `[title](url)` for every source that has a URL** — a reader must
be able to open each source directly from the note; no bare names.
Honor every do-not-cite entry and carry flag-check verdicts into the wording (e.g., "per the
company's own disclosure, not independently audited").
**Output → `NOTES_DIR/<short-kebab-title>.md`** with YAML frontmatter
(`title`, `created`, `source: verified-research`, `topic`). Also copy to `ART/research-note.md`.
**Then upsert the Source Ledger** per references/ledger.md (match by normalized URL, bump
Reuse on returning sources, re-sort each touched domain by Score, update the rollup).
