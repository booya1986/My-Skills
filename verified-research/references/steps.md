# Step specs — the 6+1 chain

Self-contained role prompts, so the pipeline runs in any Claude Code session with
WebSearch/WebFetch. `ART/` = the run's working folder (see SKILL.md Setup).
Always pass absolute paths to subagents and in shell commands.

---

## decode  (model hint: small/fast, or the orchestrator itself)

**Role:** Decompose the research question into the real work. **Do not answer it.**

**First, decide the shape of the question.**
- *Topic-shaped* ("what is X", "latest on Y"): go straight to the topic map.
- *Decision-shaped* ("should I take/build/buy X", "what do I need to know before…",
  "prepare me for…"): ask framing questions before any research, because the answers
  change what gets researched. Ask up to four (with a structured question tool if you
  have one): **purpose** (what decision this serves), **scope** (how wide to draw the
  topic; offer 2–3 concrete widths), **output** (language and destination folder), and
  **employer link** (generic vs. touching an internal context, which stays out of the
  note). Then include the decision angles from references/decision-questions.md as
  lenses or as a planned round two. Reports that answer only "what is X" come back with
  "and what should I do about it", so plan for that up front.

**Output → `ART/topics.md`:** (1) main topics, (2) sub-questions per topic, (3) the
domain(s) it falls under (map to venue-map domain keys — see references/tiers.md),
(4) suggested search terms per topic, in the local language too when the topic is
tied to a specific market, (5) the lens plan: one lens per topic, decision lenses
marked. Keep it tight; this is a map, not prose.

## discover  (fan out — one subagent per lens)

**Role:** For your assigned lens, find 4–8 of the LATEST high-quality sources (scale
up when the user asks for exhaustive coverage).
**Read** the venue map for the domain's known venues as a starting point, and record
newly-validated venues as candidates for appending (per references/tiers.md).
**Enforce tier balance:** your set MUST include ≥1 formal (authoritative/academic) AND ≥1
community (Reddit/X/HN) source when they exist; if a tier has none for your lens, write
the literal line `"<tier>: none found for <topic>"` and stop retrying after 2–3 variants.
Name every venue tried and unreachable — never omit silently.
**Fetch:** `WebSearch` + `WebFetch`. Capture publication date + author/org for every
source. For the community tier, follow the Community fetch playbook in
references/tiers.md; if you lack the MCP tools it recommends, say so in your output
(the orchestrator runs that pass) rather than declaring Reddit dead.
**Numbers discipline:** for every statistic, record who measured it, when, and on what
sample. If it cannot be traced to a primary study, mark it `UNTRACED` so verify can
chase or drop it. Vendor-claimed figures are labeled as such.
**Output → `ART/sources-<lens>.md`** (title, URL, tier, date, one-line relevance,
unreachable venues, tier-balance statement) **and `ART/gathered-<lens>.md`** (the gather
step's content, below). One agent per lens does both; it saves a hand-off.
**Turn-budget guard:** write the output files BEFORE running low on turns — draft them
incrementally or reserve the final ~5 turns for writing. A partial file with 8 sources
beats a dead agent holding 15 in memory. (Field lesson: a gather agent once burned all
its turns searching and wrote nothing; it was rescued only by resuming it with
"STOP searching, write the file NOW".)

## gather  (same agent as discover)

**Role:** Read the discovered sources; summarize each source's key claims in your own
words (not verbatim) with every concrete number and its who/when/sample, publication
date, author/org, and which sub-question it answers. Group by sub-question. Vague
summaries are useless downstream; quantitative specificity is the point.

## verify  ← scores sources (read-only; does NOT write the ledger)

**Role:** Vet every source and claim.
1. **Credibility:** primary/official/reputable vs SEO filler. Drop aggregators that add
   no original reporting. Content-marketing sites are practitioner tier at best. Vendor
   newsrooms are authoritative for what ships, never for ROI. Tag commercial-conflict
   sources "low confidence — illustration only".
2. **Recency:** flag stale items for fast-moving topics; prefer the last 12–18 months.
3. **Fact-check:** read references/debunked-statistics.md first; anything on that list
   is dropped without re-chasing unless a primary source turns up. Then cross-reference
   each high-impact claim against ≥2 independent sources. Reconcile apparent
   contradictions explicitly (they usually dissolve on time-horizon, gross-vs-net, or
   announced-vs-actual axes — spell the reconciliation out; it's often the most valuable
   analysis in the run).
4. **Computed metrics:** for any X-per-Y figure, trace BOTH inputs to their sources,
   check the arithmetic, and label each figure reported-vs-computed (stale inputs get an
   explicit caveat).
5. **Score every survivor** by running `python3 <skill>/scripts/score.py` (see
   references/ledger.md) and paste the emitted rows. Do not compute scores by hand.
6. **Tier-balance audit** per lens, with the venues that were unreachable. If a whole
   tier is missing, note it for the critic.
**Output → `ART/verified.md`:** findings by topic tagged VERIFIED / SINGLE-SOURCE /
UNTRACED / REFUTED / STALE with corrected figures; the scored table; a
**primary-source flag list** (high-impact claims resting only on secondary sources, each
with the primary venue to check); a **do-not-cite list** the consolidator must honor
(dropped sources and numbers, claims allowed only with caveats, and for each "what to
say instead"); and gaps for the critic.
**Do not write to the ledger** — the consolidate step persists these scores.

## critic  (usually the orchestrator)

**Role:** Read everything so far. List the non-obvious insights and the gaps /
contradictions / unexamined angles. Then decide:
- **Topic-shaped question:** finalize unless a whole tier or a load-bearing claim is
  missing; then one scoped round (discover→gather→verify→critic on the new angles, cap
  2). Default to finalizing past round 1 when in doubt. A "significant new angle" is one
  that could change the conclusion or that the reader would regret not seeing.
- **Decision-shaped question:** run the decision angles from
  references/decision-questions.md that were not covered as a targeted round two
  *before* delivering. The user will ask for them anyway, and it is cheaper now than
  re-opening the note.
Two angle types are chronically missing from round 1: (a) the field's own counter-force
(regulators, skeptics, failure data) when round 1 skews optimistic; (b) sources the user
explicitly named that nobody searched yet.
**Flag-check task:** when verify emitted primary-source flags, run a surgical
**flag-check** (WebSearch/WebFetch or a search MCP, 2–4 calls per flag) in PARALLEL to
any round-two discovery. Its verdicts (CONFIRMED-PRIMARY / CONFIRMED-SECONDARY-ONLY /
REFUTED / STILL-PROPOSED) bind the consolidator.
**Round cap scope:** the cap applies to critic-initiated rounds; USER-requested
supplementary rounds are always allowed — they run the same rigor, then update the note
and ledger.
**Output:** a short critique + the decision.

## consolidate  (usually the orchestrator)

**Role:** Read ALL artifacts (every round's verified sources, critique notes, flag-check
verdicts, the do-not-cite list). Before writing, read references/writing-voice.md: the
note is written the way a native speaker of its language would explain it out loud, not
in the register of the sources. Run the read-aloud test on every section before saving.
A verified note nobody can read gets rewritten, which costs more than writing it plainly
the first time.
**Required structure:**
1. **Jargon key and context callout** (what this note is for, terms the reader will meet).
2. **TL;DR** — 2–3 sentences a non-expert gets.
3. **Key insights** — non-obvious first, short bullets, each with its number and source.
4. **The data** — concrete numbers/findings in markdown tables + at least one simple
   visual. LTR languages: comparison table, mermaid diagram, or inline ASCII bars like
   `48% ▆▆▆▆▆`. RTL languages: top-down mermaid or a table only — never left-to-right
   flows, ASCII bars or trees (see the RTL rule in SKILL.md).
5. **Bottom line / what to do.**
6. **Decision sections** for decision-shaped questions (see references/decision-questions.md).
7. **What was not found, and limits** — honestly, including any empty community tier.
8. **Sources** — tiered (Authoritative / Academic / Practitioner / Community), each a
   clickable `[title](url)` with publication date and confidence (high/medium/low).
   **Every source named inside the text is also linked at that spot** (link the first
   mention in each paragraph), so the reader never has to scroll to the list to open
   what a sentence rests on.
9. **Do-not-cite table** — the number, why it fell, what to say instead.
Explain every ratio in words with a worked example ("1 to 2,500 means four people in a
10,000-person organization"); readers ask what ratios mean.
Honor every do-not-cite entry and carry flag-check verdicts into the wording (e.g., "per
the company's own disclosure, not independently audited").
**Frontmatter:** `title`, `description`, `created`, `lang`, `source: verified-research`,
`topic`, `tags` (plus whatever schema your notes system uses).
**Location:** the folder the user named; default `NOTES_DIR/<short-kebab-title>.md`.
Write with an absolute path, and afterwards locate the file by glob when editing — the
user may rename it mid-run. Also copy to `ART/research-note.md`.
**Then:** upsert the Source Ledger from the scored table per references/ledger.md (match
by normalized URL, bump Reuse on returning sources, re-sort each touched domain by Score,
update the rollup); fold venue-map candidates into `VENUE_MAP`; append any newly debunked
statistic to references/debunked-statistics.md.
**Finally:** offer the publish step in one line.

## publish  (optional, user opt-in)

Only when the user asks for a shareable or designed version. Follow
references/publish.md: a repo outside the notes folder, a build script that renders the
note, a `DESIGN.md` contract, interactive components where they explain better than
prose, infographics in one consistent style, GitHub Pages, real-browser verification,
the link written back into the note, and cleanup of servers and screenshots.
