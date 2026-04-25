# Knowledge Gap Analysis — A Portable Skill for L&D Teams

A reusable, AI-friendly methodology for turning raw assessment data (test results, competency surveys, certifications) into a prioritized, actionable training plan.

This is a **Claude Code Skill** — a self-contained package that teaches Claude how to guide you through the full process. Drop it into your Claude Code setup and Claude will help you analyze your own assessment data using a proven 5-phase framework.

The methodology is **domain-agnostic**, **industry-agnostic**, and **language-agnostic**. It works for any workforce assessment in any organization.

---

## What you get

```
knowledge-gap-analysis/
├── SKILL.md                          The main playbook (Claude reads this first)
├── README.md                         You are here
├── references/
│   ├── priority-formula.md           Why and how the priority score works
│   ├── llm-gap-discovery.md          How to use an LLM to tag your questions
│   ├── three-tier-hierarchy.md       How to produce reports for 3 audiences
│   └── data-schema-template.md       The canonical CSV schema
├── scripts/
│   ├── calculate_priority_score.py   Standalone Python — compute priorities
│   └── validate_assessment_data.py   Standalone Python — sanity-check your CSV
└── assets/
    └── llm_prompt_template.md        Ready-to-use prompt for tagging questions
```

Total: 8 files, ~1,400 lines. Self-contained — no external dependencies on any organization, codebase, or proprietary system.

---

## Who this is for

- L&D managers who run periodic assessments and need to decide what to train
- HR analytics teams who want a defensible training prioritization framework
- Compliance officers who need to translate test failures into training programs
- Anyone with an Excel/CSV of assessment responses asking "what should we train first?"

---

## Installation — three options

### Option 1: Use as a Claude Code Skill (recommended)

If you have Claude Code installed:

```bash
# Copy the entire folder into your Claude Code skills directory
cp -r knowledge-gap-analysis ~/.claude/skills/
```

Restart Claude Code. The skill will activate automatically when you ask Claude about training priorities, knowledge gaps, or assessment analysis.

To verify it loaded, ask Claude: *"Do you have a skill for knowledge gap analysis?"*

### Option 2: Use the methodology directly (no Claude Code needed)

You don't need any AI tool to use the methodology. Read the files in this order:

1. `SKILL.md` — get the big picture (5-phase framework, core principles)
2. `references/data-schema-template.md` — shape your data into the canonical CSV
3. `references/priority-formula.md` — understand the priority score
4. `references/llm-gap-discovery.md` — if you don't yet have a knowledge-gap taxonomy
5. `references/three-tier-hierarchy.md` — when you're ready to produce reports

Run the Python scripts directly (see "Quick start" below).

### Option 3: Project-scoped skill

Drop the folder into a specific project's `.claude/skills/`:

```bash
cp -r knowledge-gap-analysis your-project/.claude/skills/
```

Now the skill is available only in that project, not globally.

---

## Quick start — 5 minutes to your first prioritized list

### Prerequisites

- Python 3.9+ with `pandas` installed: `pip install pandas`
- A CSV of assessment responses (see required schema below)

### Step 1 — Prepare your CSV

Your CSV needs at minimum these columns:

| Column | Type | Example |
|---|---|---|
| `employee_id` | string or int | `E001` |
| `question_id` | string or int | `Q42` |
| `is_correct` | 0 or 1 | `1` |
| `business_line` | string | `Sales` |
| `category` | string | `Compliance` |
| `importance` | high / medium / low | `high` |

Optional but recommended: `subcategory`, `region`, `team`, `manager_id`, `gap_description`.

See `references/data-schema-template.md` for full guidance.

### Step 2 — Validate your data

```bash
python scripts/validate_assessment_data.py your_responses.csv
```

This catches the silent killers: missing columns, inconsistent encodings, whitespace-only category splits, duplicate rows. Fix any reported errors before continuing.

### Step 3 — Calculate priorities

```bash
python scripts/calculate_priority_score.py \
  --input your_responses.csv \
  --output priorities.csv
```

Open `priorities.csv` — your knowledge gaps are now sorted by priority. Review the top 10 with your team.

### Step 4 — Produce per-audience reports

For executives (organization-wide top 10):

```bash
python scripts/calculate_priority_score.py \
  --input your_responses.csv \
  --output exec_top10.csv \
  --top 10
```

For a regional manager:

```bash
python scripts/calculate_priority_score.py \
  --input your_responses.csv \
  --output region_north.csv \
  --filter region=North \
  --level region
```

For a specific team lead:

```bash
python scripts/calculate_priority_score.py \
  --input your_responses.csv \
  --output team_a.csv \
  --filter team=Team-A \
  --level team
```

See `references/three-tier-hierarchy.md` for the full reasoning behind the three audience tiers.

---

## What if I don't have a `category` or `importance` column yet?

That's the most common starting point. Use Phase 2 of the methodology — tag your questions with an LLM, then validate with subject-matter experts.

1. Open `assets/llm_prompt_template.md`
2. Adapt the placeholders to your domain
3. Send batches of your questions to your preferred LLM (Claude, GPT, etc.)
4. Hand the resulting taxonomy to your subject-matter experts for validation
5. Join the validated taxonomy back to your responses CSV
6. Now you can run the priority script

The full process (with lessons learned) is in `references/llm-gap-discovery.md`.

---

## The 5-phase framework — TL;DR

1. **Ingest and validate** — get your data into the canonical CSV shape
2. **LLM-assisted gap tagging** — use an LLM to draft a knowledge-gap taxonomy
3. **Expert validation** — subject-matter experts review and refine the taxonomy
4. **Priority scoring** — `(importance × error_rate × coverage) / 1000`
5. **Three-tier delivery** — organization-wide / regional / team-level reports

The full framework is in `SKILL.md`.

---

## Core principles

Four guardrails. Violating them produces analyses that look right but mislead stakeholders.

1. **Always separate business lines.** Different lines have different domains, regulations, and customers. Combined averages hide actionable patterns.
2. **Deduplicate by employee where it matters.** A row is a *response*, not a *person*.
3. **Document your LLM prompt and taxonomy version.** Six months from now you will need to re-run; without the artifacts, comparisons break.
4. **Show distributions, not just averages.** Averages hide the tails. The tails are usually the story.

---

## What this skill does NOT include

To keep it portable and shareable, this package deliberately leaves out:

- **No employee data.** Zero rows of real responses. You bring your own data.
- **No organization-specific logic.** No bank, hospital, retailer, or vendor terminology. The methodology applies to all of them.
- **No dashboard code.** The methodology is independent of how you visualize it. Use Excel, Tableau, Power BI, a custom React app — whatever fits your workflow.
- **No language-specific text.** Examples and code are in English; the methodology works for assessments in any language.

If you want a dashboard, you can build one in any framework. The CSV outputs of `calculate_priority_score.py` plug into anything.

---

## Frequently asked

**Q: Do I need an LLM to use this?**
A: Only for Phase 2 (tagging questions with knowledge gaps). If your assessment already has a category column and importance levels, skip Phase 2 and go straight to the priority script.

**Q: Can I use a different priority formula?**
A: Yes. The formula in `references/priority-formula.md` is a defensible default that balances importance, severity, and coverage. If your stakeholders prefer RICE, AHP, or a custom weighting, edit `calculate_priority_score.py`. The structure (separate-by-business-line, three-tier reporting) still applies.

**Q: What if my organization has only one business line?**
A: Populate the `business_line` column with a single value (e.g., `"All"`). The schema stays consistent and the script still works.

**Q: How big can the dataset be?**
A: The script handles tens of thousands of rows easily on a laptop. For millions, swap pandas for DuckDB or run inside a database.

**Q: Can I use this with non-English assessments?**
A: Yes. The methodology is language-agnostic. The scripts accept any string in the categorical columns. For Phase 2 (LLM tagging), translate the prompt template into your source language for best results.

**Q: Is the data I run through the scripts sent anywhere?**
A: No. The scripts are standalone Python — everything runs locally. Nothing is uploaded.

---

## Contributing improvements

This is a methodology document as much as a tool. If you find:

- A clearer way to explain a phase
- An additional pitfall worth warning about
- A better default for a parameter
- A useful extension (e.g., longitudinal comparison, manager-level heatmaps)

— edit the relevant file and share back. The methodology gets stronger with use.

---

## License

Use it, adapt it, share it. No warranty. Test on a small sample before relying on outputs for budget decisions.

---

## Where to start

If you're new: read `SKILL.md` first. It's the playbook.

If you have data ready and want to see results immediately: run the validation script, then the priority script.

If you're skeptical: read `references/priority-formula.md`. The reasoning behind every component is explained.
