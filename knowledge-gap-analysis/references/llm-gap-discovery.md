# LLM-Assisted Gap Discovery — Phase 2 Deep Dive

This document explains how to use a large language model to derive a knowledge-gap taxonomy from raw assessment questions, and how to validate the result with subject-matter experts. Read this when starting a new assessment cycle, when adding new questions to an existing taxonomy, or when the user asks "how do we know what each question is testing?"

## The problem this phase solves

A multiple-choice question is just a string of text. To aggregate "60% of staff failed anti-fraud questions", every question must first be tagged with the gap it measures, plus a category, subcategory, and importance level.

Manual tagging by an expert is the gold standard for accuracy but takes 30–60 minutes per question. For a 100-question assessment, that is 50–100 expert-hours. Most organizations cannot afford that.

The compromise: have an LLM produce a draft taxonomy in minutes, then use experts to *validate* (and correct) rather than *create from scratch*. Expert time drops by 5–10×.

## When this phase is needed

- **First assessment cycle** — no taxonomy exists yet
- **New questions added** — only the new ones need tagging
- **Re-validating an old taxonomy** — when business priorities shift and importance levels need updating

You do **not** need to re-run this phase between assessments if the question set and taxonomy are unchanged.

## The 3-step workflow

### Step 1 — Prepare the input

Gather every question with the following fields:

| Field | Required | Notes |
|---|---|---|
| `question_id` | yes | Unique stable identifier |
| `question_text` | yes | The full question prompt |
| `correct_answer` | yes | The text of the correct option |
| `distractors` | yes | The text of the wrong options |
| `business_line` | yes if applicable | Sales / operations / compliance / etc. |
| `existing_category` | optional | If you already have a rough category |

Save as a single CSV or JSON file. Strip any PII or proprietary names from the question text — the LLM will see the full content.

### Step 2 — Run the LLM with a structured prompt

Use the prompt template in `assets/llm_prompt_template.md`. Key principles:

- **Demand structured JSON output** (or use function calling). Free-form text in any language produces inconsistent shapes that break downstream code.
- **Process in batches** (10–25 questions per call) so the model sees enough context to be consistent across questions, but not so many that token limits or context drift become problems.
- **Run twice with low temperature** (e.g., 0.2) and compare. Disagreements between runs are exactly the questions experts should look at first.

Output schema for each question:

```json
{
  "question_id": "Q042",
  "gap_description": "Inability to identify the correct procedure when X occurs",
  "category": "Risk Management",
  "subcategory": "Incident Response",
  "importance_level": "high",
  "rationale": "This is a regulatory requirement; failure exposes the organization to fines."
}
```

### Step 3 — Run the expert validation loop (Phase 3)

For each business line, route the LLM-drafted taxonomy to 1–3 subject-matter experts. They should review three things per question:

1. **Is the gap_description accurate?** Often the LLM picks up on the wrong dimension of a question. The rationale field helps surface this.
2. **Is the importance_level correct?** Experts know which gaps map to regulatory or financial risk; the LLM is guessing.
3. **Is the category placement right?** Experts often see structural patterns the LLM misses.

**Practical workflow:**
- Put the LLM output in a spreadsheet with columns for expert comments and corrections.
- Track who reviewed what and when.
- Run 2–3 review rounds — early rounds find big errors, later rounds smooth out edge cases.
- When experts disagree, escalate to a senior expert or the L&D lead. Document the resolution.

**When you can declare the taxonomy "locked":**
- All questions reviewed by ≥ 1 expert
- Disagreements resolved or marked as "escalated, pending"
- Importance distribution looks plausible (typically 20–40% high, 40–60% medium, 20–30% low; if it skews dramatically, re-examine)

## Lessons from production use

### Insist on structured output

The single biggest mistake is asking the LLM for "free-form" tags in natural language. The result will be:
- Different category names for what should be the same category ("Risk Mgmt", "Risk Management", "Risk-Mgmt")
- Importance levels expressed as words sometimes and numbers other times
- Mixed-language outputs even with English-only prompts

Use JSON schema enforcement, function calling, or a strict prompt with output examples. Validate the output programmatically before handing to experts.

### Document the prompt as a source artifact

Treat the LLM prompt the same way you treat code: version control it, write a CHANGELOG, and require approval to change it. Six months from now, when you re-tag a new question, using a different prompt will introduce inconsistencies you cannot debug.

### Start small with the "edge case" questions first

Pick 5–10 questions you know are tricky (regulatory + nuanced answers, two-correct-answers-in-context, technical jargon) and run them through the prompt first. Iterate the prompt until those produce sensible output. Only then do the bulk tagging.

### Run a second pass with a different LLM

If budget and time allow, run the same prompt through two different LLM providers (e.g., one from each major vendor) and have a script highlight disagreements. The disagreements concentrate the questions where expert judgment matters most.

### Keep importance distribution honest

If your LLM output says "92% of questions are high importance", something is wrong with the prompt — either the bar for "high" is too low or the LLM is being sycophantic. Push back in the prompt: "Reserve 'high' for questions where a wrong answer creates direct regulatory, financial, or safety risk. Most questions should be 'medium'."

## Common failure modes

### The LLM invents categories

If the prompt does not constrain the category vocabulary, the LLM will invent a slightly different category name for nearly every question. Fix: provide a closed list of allowed categories in the prompt, and use a tool/JSON schema to enforce it.

### Inconsistent importance levels across batches

If question 47 is rated "high" in one batch and "medium" in another, the model is being influenced by the surrounding questions in each batch. Fix: include a brief importance rubric in every prompt call, with examples.

### Hallucinated rationale

Sometimes the model produces a plausible-sounding rationale that is factually wrong about the domain. The expert validation phase catches these — that is its main purpose. Do not skip Phase 3.

### Language drift in non-English assessments

If the source content is in language X but the prompt is in English, the model may translate-and-summarize the question rather than analyzing it directly, losing nuance. Fix: write the prompt in the same language as the source content (or use few-shot examples in that language).

## Output handoff to Phase 4

The validated taxonomy is the input to Phase 4 priority scoring. Specifically:
- Each question's `importance_level` becomes the `importance` column in the responses CSV
- Each question's `category` and `subcategory` become the grouping fields
- The `gap_description` is human-readable text for the final reports

Once the taxonomy is locked, Phase 4 (priority scoring) can run automatically as new assessment data arrives.

## See also

- `assets/llm_prompt_template.md` — the actual prompt to start from
- `references/data-schema-template.md` — how the validated taxonomy joins back to response data
- `references/priority-formula.md` — what the importance level feeds into
