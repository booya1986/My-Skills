# Data Schema Template

This document defines the canonical schema that the rest of the methodology assumes. Read this when starting with a new data source, when shaping raw data into a usable form, or when the validation script flags schema issues.

## The minimum viable schema

To run any analysis, you need a single table where each row represents one employee's response to one assessment question.

| Column | Type | Required | Description |
|---|---|---|---|
| `employee_id` | string or int | yes | Stable unique identifier per employee. Never use names. |
| `question_id` | string or int | yes | Stable unique identifier per question. |
| `is_correct` | 0 or 1 | yes | Whether the employee answered correctly. |
| `business_line` | string | yes | Top-level business segmentation (sales, ops, etc.). Used for separation. |
| `category` | string | yes | Knowledge category (from validated taxonomy). |
| `importance` | "high" / "medium" / "low" | yes | Question's strategic importance (from validated taxonomy). |

This is the **strict minimum**. Without these six columns, the methodology cannot produce reliable priorities.

## Recommended additional columns

| Column | Type | Description | Why include |
|---|---|---|---|
| `subcategory` | string | Finer-grained taxonomy level | Enables drill-down in dashboards |
| `gap_description` | string | Human-readable description of the knowledge gap | Used in the final reports for non-technical readers |
| `region` | string | Geographic or organizational region | Enables tier 2 reports |
| `team` | string | Team or unit identifier | Enables tier 3 reports |
| `manager_id` | string | Manager identifier | Enables manager-level heatmaps |
| `test_score` | 0–100 | Numeric score on the question (if scored, not just correct/incorrect) | Useful for advanced metrics |
| `assessment_date` | date | When the response was collected | Enables longitudinal analysis |
| `seniority_band` | string | e.g. "0-2y", "2-5y", "5+y" | Enables cohort analysis |

If you have these columns, capture them. If not, you can still run the core analysis with just the minimum schema.

## Column-by-column guidance

### `employee_id`

- Use a stable identifier issued by your HR system or a hash of email/employee number.
- **Never** use names. Names are PII; once they are in the analysis pipeline, they leak everywhere.
- Verify uniqueness: the same employee should not have two different IDs.
- Verify stability: the same employee should not get a new ID between assessment cycles (otherwise longitudinal comparison breaks).

### `question_id`

- Use the question identifier from your assessment platform.
- Stability matters: if you re-tag a question between cycles, the analysis joins by `question_id`, so changing it breaks comparison.

### `is_correct`

- Must be 0 or 1 (or boolean equivalent).
- Watch out for inconsistent encodings in the source: `Y/N`, `Correct/Incorrect`, `True/False`, localized strings, even nulls. Normalize to 0/1 during ingestion.
- A null here means "did not respond" — exclude from error rate calculations, do not treat as incorrect.

### `business_line`

- This is the **separation column** that the methodology will never aggregate across.
- Examples: "Sales" vs "Operations", "Retail" vs "Corporate", "Frontline" vs "Back Office".
- If your organization only has one business line, populate this column with a single value (e.g., "All") so the schema is consistent.
- Whitespace and capitalization matter: "Sales " (trailing space) is treated as a different business line than "Sales". Strip and normalize.

### `category` and `subcategory`

- Come from the validated taxonomy (Phase 3 output).
- Closed vocabularies — categories should be a finite list, not free text.
- If your raw data does not have these columns, run Phase 2 (LLM-assisted gap discovery) first.

### `importance`

- Three values: "high", "medium", "low" (case-insensitive).
- Comes from the validated taxonomy.
- The `calculate_priority_score.py` script accepts both English ("high") and localized values via a configurable mapping (see `IMPORTANCE_ALIASES` in the script) — but normalize to English internally for consistency.

### `region` and `team`

- Optional, but enable tier 2 and tier 3 reports respectively.
- Use stable identifiers (e.g., team codes, not team names) where possible.
- A team can move regions over time; if you need historical accuracy, snapshot the team-region mapping per assessment cycle.

## Common shape transformations

### From "wide" to "long"

Some assessment platforms export a wide format: one row per employee, one column per question.

```
employee_id, q1, q2, q3, q4, ...
E001,        1,  0,  1,  1,  ...
E002,        0,  1,  1,  0,  ...
```

The methodology requires "long" format (one row per response):

```
employee_id, question_id, is_correct
E001,        q1,          1
E001,        q2,          0
E001,        q3,          1
...
```

Use `pandas.melt()` or equivalent to reshape. Do this before validation.

### Joining the taxonomy back to responses

After Phase 3, you have a separate taxonomy table with one row per question:

```
question_id, category, subcategory, importance, gap_description
q1,          A,        A.1,         high,       ...
q2,          B,        B.2,         medium,     ...
```

Join this to the responses table:

```python
df = responses.merge(taxonomy, on='question_id', how='left')
```

After the join, every response row carries its question's taxonomy fields — ready for priority scoring.

## Data quality checks (automated)

`scripts/validate_assessment_data.py` checks for:

- Required columns present
- `is_correct` is 0/1 (and reports the encoding it found)
- `importance` values are in the allowed set (with auto-mapping suggestions for common variants)
- No duplicate `(employee_id, question_id)` pairs (a duplicate means the same employee answered the same question twice, which usually indicates a data join error)
- Whitespace-only differences in categorical columns (the silent killer)
- Population sizes per business line, region, and team
- Missing-value rates per column

Run this script before any analysis. If it reports errors, fix them before proceeding.

## Privacy notes

- `employee_id` is pseudonymous, not anonymous. Treat the dataset as PII-equivalent.
- Never include `employee_name` in the working dataset. If your source includes it, drop it during ingestion.
- Tier 3 (team-level) reports may show individual employee performance. Distribute only to the relevant team lead and follow your data-handling policies.

## Example minimal CSV

```csv
employee_id,question_id,is_correct,business_line,category,importance
E001,Q01,1,Sales,Product Knowledge,high
E001,Q02,0,Sales,Compliance,high
E001,Q03,1,Sales,Customer Service,medium
E002,Q01,0,Operations,Product Knowledge,high
E002,Q02,1,Operations,Compliance,high
...
```

This is the simplest valid input to `scripts/calculate_priority_score.py`.

## Example richer CSV

```csv
employee_id,question_id,is_correct,business_line,category,subcategory,importance,region,team,manager_id,gap_description
E001,Q01,1,Sales,Product Knowledge,Premium Tier,high,North,Team-A,M001,"Knows when to recommend premium tier"
E001,Q02,0,Sales,Compliance,Disclosure,high,North,Team-A,M001,"Identifies required disclosures"
...
```

The richer your schema, the more drill-down dimensions are available in the reports.
