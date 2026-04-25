# LLM Prompt Template — Knowledge Gap Tagging

This is the structured prompt used in Phase 2 to convert raw assessment questions into a tagged knowledge-gap taxonomy. Adapt the placeholders to your domain, validate the output with experts (Phase 3), and version-control this file alongside your analysis code.

---

## How to use this template

1. Fill in the `{{PLACEHOLDERS}}` with your domain-specific values.
2. Send to your LLM of choice (Claude, GPT, or any model that supports structured output / function calling).
3. Process the response as JSON. Reject any non-conforming output.
4. Hand the resulting taxonomy to subject-matter experts for Phase 3 validation.

**Critical:** demand structured JSON output. Free-form text is the #1 cause of downstream pipeline failures.

---

## The prompt (English version)

```
You are an expert in workforce assessment design and competency frameworks for the {{INDUSTRY}} domain.

I will give you a batch of assessment questions, each with its correct answer and the wrong-answer options (distractors). Your task is to analyze each question and produce a structured tag describing the knowledge gap it measures.

For each question, return a JSON object with these exact fields:

- "question_id": the identifier I provided
- "gap_description": one or two sentences describing the underlying knowledge gap if an employee answers incorrectly. Phrase as the GAP, not the question. Example: "Inability to identify the correct escalation procedure when X happens" — not "What is the escalation procedure?"
- "category": pick exactly one from this closed list: {{CATEGORY_LIST}}
- "subcategory": pick exactly one from this closed list: {{SUBCATEGORY_LIST}} (or use "general" if no subcategory fits)
- "importance_level": exactly one of "high", "medium", or "low" — see the rubric below
- "rationale": one sentence explaining your importance choice

IMPORTANCE RUBRIC (use this strictly — most questions should be "medium"):
- "high" — incorrect answer creates direct regulatory, financial, safety, or reputational risk to the organization. Reserve this for must-know knowledge.
- "medium" — incorrect answer reduces employee effectiveness or customer experience but does not create direct risk. Most questions fall here.
- "low" — incorrect answer is a minor productivity or efficiency loss. Nice-to-know knowledge.

CONSTRAINTS:
- Do not invent new categories or subcategories. Use only the lists I provided.
- Do not exceed two sentences for gap_description.
- Output a single JSON array, one object per question, in the same order I provided them.
- No prose before or after the JSON. No markdown code fences.

QUESTIONS:
{{BATCH_OF_QUESTIONS_AS_JSON}}
```

---

## Example input batch

```json
[
  {
    "question_id": "Q001",
    "question_text": "When event E occurs in system S, what is the first action the operator should take?",
    "correct_answer": "Acknowledge the alert and run the diagnostic checklist",
    "distractors": [
      "Restart the system",
      "Wait for the next shift to handle it",
      "Open a support ticket without diagnosing"
    ]
  },
  {
    "question_id": "Q002",
    "question_text": "Which of the following is the mandatory step before activating workflow W?",
    "correct_answer": "Confirm prerequisite condition X is met",
    "distractors": [
      "Activate the workflow first, then check",
      "Skip the check if the previous workflow ran successfully",
      "The check is optional"
    ]
  }
]
```

## Example output

```json
[
  {
    "question_id": "Q001",
    "gap_description": "Inability to recognize that event E requires acknowledgment plus a diagnostic checklist as the mandatory first response.",
    "category": "Operational Procedures",
    "subcategory": "Incident Response",
    "importance_level": "high",
    "rationale": "Skipping the diagnostic step risks masking root causes and prolongs downtime."
  },
  {
    "question_id": "Q002",
    "gap_description": "Lack of awareness that workflow W has a hard prerequisite check that must run before activation.",
    "category": "Process Compliance",
    "subcategory": "Prerequisites",
    "importance_level": "high",
    "rationale": "Skipping the prerequisite leads to predictable failure modes downstream."
  }
]
```

---

## Tuning notes

### Setting the closed category list

Before running this prompt at scale, decide on the category and subcategory taxonomy. Two options:

1. **Top-down:** the L&D team predefines categories aligned to your competency framework. This produces consistent output but may miss patterns the data reveals.
2. **Bottom-up:** run an exploratory pass with a small sample (10–20 questions) and "open" categorization. Cluster the LLM-suggested categories. Lock the resulting list. Then run the full batch with that list as the closed vocabulary.

Bottom-up usually wins for new assessments because it surfaces categories that match the actual content rather than the abstract framework.

### Batch size

Start with 10 questions per call. If the model is consistent and within token limits, raise to 25. Above 25 the model often loses consistency.

### Temperature

Use low temperature (0.1–0.3). You want consistency, not creativity.

### Running twice and comparing

Run the same batch twice with the same prompt. Where the two runs disagree (different importance level, different category), those are the questions to escalate to experts first. They are usually the genuinely hard cases.

### Localization

If your assessment content is in a non-English language, translate the prompt itself into that language. Mixed-language prompts (English instructions, source-language content) often produce translated-and-summarized output rather than direct analysis.

---

## Common failure patterns and fixes

| Failure | Fix |
|---|---|
| Model invents new categories | Add stronger constraint: "If no category matches, set category=='UNKNOWN'. Do not invent new ones." Then review UNKNOWNs manually. |
| Importance distribution skews high | Strengthen the rubric: add explicit examples of what "medium" looks like. Pre-state: "Most questions in this batch should be medium." |
| Inconsistent gap_description style | Add 2–3 example outputs to the prompt (few-shot pattern). |
| Output includes markdown fences | Add: "Output raw JSON only. No backticks, no prose." If the model still wraps it, strip programmatically. |
| Model hallucinates regulations | Add: "If you are uncertain whether something is a regulatory requirement, set importance to medium and note the uncertainty in rationale." |

---

## After tagging — Phase 3 handoff

Save the LLM output as a CSV with columns:

```csv
question_id,gap_description,category,subcategory,importance_level,llm_rationale,expert_reviewed,expert_changes,reviewer
```

The right four columns are for experts to fill in during Phase 3:
- `expert_reviewed` — date / yes flag when the expert checked the row
- `expert_changes` — what they changed (if anything)
- `reviewer` — who reviewed it

This becomes your audit trail. Lock the file when all rows are reviewed and store it as the canonical taxonomy for this assessment cycle.
