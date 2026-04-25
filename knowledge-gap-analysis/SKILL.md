---
name: knowledge-gap-analysis
description: End-to-end methodology for analyzing assessment data to identify, prioritize, and act on knowledge gaps in any workforce. Use this skill when the user is working with employee test results, L&D assessment data, training needs analysis, competency gaps, or any task involving turning raw assessment scores into prioritized training recommendations. Triggers on phrases like "knowledge gap", "training priorities", "assessment analysis", "skill gap analysis", "competency framework", "L&D analytics", "what should we train", or when the user has Excel/CSV files with test scores and needs to decide what to train. Provides a proven 5-phase framework: (1) data ingestion and validation, (2) LLM-assisted gap tagging, (3) expert validation loop, (4) priority scoring with importance × error_rate × coverage formula, (5) three-tier output hierarchy (organization/region/team). Make sure to invoke this skill whenever the user mentions assessment results, test data, training prioritization, or wants to convert raw scores into actionable training plans, even if they do not use these exact terms.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python:*)
---

# Knowledge Gap Analysis — A Methodology for L&D Teams

A repeatable, evidence-based framework for turning assessment data (test results, competency surveys, certification exams) into a prioritized training plan that stakeholders trust.

This skill encodes a tested end-to-end methodology — from raw assessment data to team-level training recommendations. It is **domain-agnostic, industry-agnostic, and language-agnostic** — apply it to any workforce assessment in any organization.

## When to use this skill

Invoke this skill when the user:

- Has a file (Excel, CSV, database export) with employee test/quiz/assessment results and asks "what should we train?"
- Wants to identify which knowledge gaps are most critical and deserve immediate intervention
- Needs to translate raw assessment scores into a prioritized list for L&D budget decisions
- Is preparing executive recommendations on competency gaps
- Asks about the "priority formula", "acuteness score", or "training prioritization"
- Wants to map test questions to underlying knowledge gaps (taxonomy creation)
- Needs to produce reports at different organizational levels (organization-wide, regional, team)
- Mentions L&D, training needs analysis, or competency frameworks in a data context

## Why a methodology, not just a script

Most L&D teams already know how to compute averages. The hard problems are:

1. **What does each test question really measure?** A multiple-choice question is just text — without explicit tagging, you cannot aggregate "70% of staff fail anti-fraud questions" because no column says "anti-fraud".
2. **How do we decide what is critical?** A 90% error rate on a low-importance question matters less than 50% on a regulatory must-know. Naive ranking by error rate misleads.
3. **How do we make the output actionable for everyone?** An executive needs a single chart. A team lead needs a list of which of *their* people need which course. The same data must be sliced three different ways.
4. **How do we avoid hiding local crises in averages?** A specific team can have 100% error rate on a topic where the organization average is 30%. Aggregate reporting masks this.

This skill addresses all four — see the 5-phase framework below.

## The 5-phase framework

### Phase 1 — Data ingestion and validation

Before any analysis, the data must be in a consistent shape with one row per `(employee, question)` pair, and known categorical fields for importance, business line, and grouping (region/team/manager).

**What to do:**
1. Load the source file with the user.
2. Identify the canonical schema using `references/data-schema-template.md` as a guide.
3. Run `scripts/validate_assessment_data.py <file>` to surface schema issues, duplicates, missing values, and business-line mixing.
4. Deduplicate carefully: rows are *responses*, not *people*. Aggregate to the employee level only when the analysis calls for it.

**Critical gotchas:**
- Whitespace-only differences in category names (`"Compliance"` vs `"Compliance "`) silently split your data. Always strip strings.
- Boolean correctness columns are inconsistently encoded across organizations (`Y/N`, `1/0`, `Correct/Incorrect`, `True/False`, localized strings). Inspect before assuming.
- Test scores and correctness flags are **two different metrics** — do not conflate them.

See `references/data-schema-template.md` for the full schema contract and column-by-column guidance.

### Phase 2 — LLM-assisted gap discovery

Most assessments do not come with a clean knowledge-gap taxonomy. The questions exist; the gaps they measure are implicit in the question text. Manually tagging 50–200 questions takes a domain expert days.

**The shortcut:** use an LLM to propose a draft taxonomy in minutes, then have experts validate it.

**What to do:**
1. Open `assets/llm_prompt_template.md` — this is the structured prompt to start from.
2. Feed in each question with its correct answer and distractors.
3. The LLM returns structured JSON: `{ gap_description, importance_level, category, subcategory }` per question.
4. Iterate the prompt until output is consistent and coherent.
5. Output goes into a spreadsheet that the user can hand to subject-matter experts for the next phase.

**Why structured JSON output is non-negotiable:** free-form responses (especially in non-English languages) produce inconsistent shapes that break every downstream step. Insist on JSON Schema or function-calling.

See `references/llm-gap-discovery.md` for the full process, prompt patterns, and lessons learned.

### Phase 3 — Expert validation loop

The LLM draft is a *starting point*, never a final taxonomy. Subject-matter experts (the people who actually know the domain) must validate every gap before any priority calculation runs.

**What to do:**
1. Hand the LLM-drafted taxonomy to 1–3 domain experts per business line.
2. Have them check three things per question: Is the gap description accurate? Is the importance level correct? Is it in the right category?
3. Run 2–3 review rounds — disagreements between experts often surface the most interesting nuances.
4. Lock the taxonomy version and store it. Future re-tests reuse it; changes require a new version number.

**Why this phase is the difference between a credible report and a rejected one:** stakeholders will challenge any priority that contradicts their intuition. If the underlying taxonomy was validated by *their own* experts, the conversation shifts from "your tool is wrong" to "let's discuss the data".

### Phase 4 — Priority scoring

Once each response is mapped to a validated knowledge gap, compute a single priority score per gap to drive the training plan.

**The formula:**

```
priority_score = (importance_weight × error_rate × coverage_percentage) / 1000
```

Where:
- `importance_weight`: business criticality predetermined by experts. High = 100, Medium = 50, Low = 25.
- `error_rate`: percentage of employees who answered incorrectly (0–100).
- `coverage_percentage`: percentage of the population that was assessed on this gap (0–100).

**Why multiplication, not addition:** a gap that is unimportant, never failed, or never tested should drop to near-zero priority. Multiplication enforces this; averaging would let one strong dimension mask a zero on another.

See `references/priority-formula.md` for worked examples, justification, and alternatives considered (RICE, AHP, simple rank).

**What to do:**
- Run `scripts/calculate_priority_score.py --input responses.csv --output priorities.csv` to compute and rank gaps.
- Review the top 10 with the user before committing to a training plan.

### Phase 5 — Three-tier output hierarchy

The same priority calculation, applied at three different scopes, produces three different reports for three different audiences.

| Tier | Scope | Audience | Decision they make |
|---|---|---|---|
| 1 — Organization | Population-wide error_rate and coverage | Executives, L&D head | Approve overall budget and themes |
| 2 — Region/Department | Region-scoped error_rate and coverage | Regional managers | Allocate regional training |
| 3 — Team/Unit | Team-scoped error_rate and coverage | Team leads | Decide who in *my team* needs *which course* this week |

**Why the same question can have different priorities at each tier:**
The exact same gap might be priority #15 organization-wide but priority #1 in a specific team where every member failed it. Tier 3 reports surface these local crises that Tier 1 averages hide.

See `references/three-tier-hierarchy.md` for the worked example and the precise way to scope each calculation.

## Core principles (non-negotiable)

These are guardrails. Violating them produces analyses that look correct but mislead stakeholders.

### Principle 1 — Always separate business lines

Different business lines (sales vs operations, retail vs corporate, ED vs ICU, frontend vs backend) have different knowledge domains, regulatory requirements, and customer profiles. Aggregating across them masks the patterns that matter.

**Example:** A gap that is critical for retail staff might not even apply to corporate teams. Reporting a combined error rate produces a number that no one can act on.

**How to apply:** every `GROUP BY` should include the business-line column. Every visualization should split by business line (side-by-side or separate views, never combined). Every export should produce one tab per business line.

### Principle 2 — Deduplicate by employee where it matters

A single row in the source file is a single response, not a single person. Distinguish carefully:

- "Number of employees" → `COUNT(DISTINCT employee_id)`
- "Number of responses" → `COUNT(*)`
- "Average score per employee" → average their scores first, then average across employees (not a flat average of all responses)

### Principle 3 — Document the LLM prompt and taxonomy version

Six months from now, when the next assessment runs, you will need to re-tag new questions consistently. If the original prompt and taxonomy are lost, the new tagging will not align with the previous one and longitudinal comparisons become impossible.

**How to apply:** check the LLM prompt and the validated taxonomy into version control alongside the analysis code. Tag releases.

### Principle 4 — Show distributions, not just averages

Averages hide the tails. A 70% average score can come from "everyone scored ~70" or from "half scored 95, half scored 45". The training implications are completely different.

**How to apply:** every summary metric should be paired with its distribution (histogram, percentiles, or at minimum min/max).

## Recommended outputs by audience

| Audience | Format | What they get |
|---|---|---|
| Executives / Board | Single dashboard or 1-page PDF | Top 3–5 organizational gaps, total training spend ask, ROI projection |
| Department / Regional heads | Excel workbook (one tab per region × business line) | Top 20 gaps for their region, with how it compares to org-wide |
| Team leads / Managers | Per-team Excel file | Their team's gap list, employee-level heatmap, direct links to relevant courses |

The Tier 3 (team-level) outputs are the most actionable because they tell a manager exactly which person to enroll in which course. Invest disproportionately in making them clear.

## Common pitfalls

- **Sensitivity-blind heatmaps.** If most error rates fall in 20–50% but the color scale runs 0–100%, every cell looks "yellowish-green" and patterns vanish. Set the scale to the actual data range.
- **Mixing test score and correctness flag.** These are different metrics. Score is `0–100`, correctness is `0/1`. Use the right one for the right calculation.
- **Skipping the expert validation phase.** "The LLM said this is high importance" is not a defensible answer when an executive challenges a priority. Always have a human-validated taxonomy.
- **Single-sheet "everything" reports.** Stakeholders cannot find their part of the story in a 10,000-row spreadsheet. Build one targeted report per audience.
- **Forgetting minimum sample thresholds.** A gap with only 2 responses cannot be reliably ranked. Set a minimum (e.g., n ≥ 5 for team-level, n ≥ 10 for org-level) and flag underpowered gaps separately.

## How the bundled resources fit together

```
SKILL.md                              you are here — methodology overview
├── references/
│   ├── priority-formula.md           deep dive on the priority score
│   ├── llm-gap-discovery.md          how to run Phase 2
│   ├── three-tier-hierarchy.md       how to scope Phase 5
│   └── data-schema-template.md       the canonical schema and column guide
├── scripts/
│   ├── calculate_priority_score.py   compute priorities from a CSV
│   └── validate_assessment_data.py   sanity-check a CSV before analysis
└── assets/
    └── llm_prompt_template.md        ready-to-use prompt for Phase 2
```

Read the relevant reference file when its phase becomes active. Do not load all of them upfront — they are deliberately separated so each one can be loaded only when needed.

## A quick-start workflow

For a user starting from scratch with a new assessment file:

1. Read `references/data-schema-template.md` and shape the user's data into the canonical CSV.
2. Run `scripts/validate_assessment_data.py` and resolve any flagged issues.
3. If the data lacks a knowledge-gap column: open `assets/llm_prompt_template.md`, follow `references/llm-gap-discovery.md` to tag every question, then run a Phase 3 expert validation cycle.
4. Run `scripts/calculate_priority_score.py` to produce the prioritized list.
5. Read `references/three-tier-hierarchy.md` and produce the three audience-specific exports.
6. Walk the user through the top 10 priorities and decide on training actions.

If at any point the user says "but this gap looks wrong" — stop and re-validate the taxonomy. Do not patch the formula to make a single gap rank higher; that breaks the framework for every other gap.
