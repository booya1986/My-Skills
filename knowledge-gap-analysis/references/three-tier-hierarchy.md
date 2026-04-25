# Three-Tier Output Hierarchy — Phase 5 Deep Dive

This document explains how to take a single set of assessment responses and produce three audience-specific reports, each with priorities scoped to that audience's level. Read this when planning the deliverables, when the user asks "what should each stakeholder see?", or when explaining why a gap is priority #1 for one team but priority #15 for the organization.

## The core insight

The same priority formula `(importance × error_rate × coverage) / 1000` produces different rankings depending on what population you compute it over.

- Compute it over **everyone** → tier 1 organizational priorities
- Compute it over **employees in one region** → tier 2 regional priorities (different per region)
- Compute it over **employees on one team** → tier 3 team priorities (different per team)

The same gap can rank #15 organization-wide because most teams handle it well, while ranking #1 in a specific team where everyone failed it. Without tier 3 reports, that team's crisis is invisible to the people who need to act on it.

## Why three tiers, not one

Each tier maps to a distinct decision and a distinct decision-maker.

### Tier 1 — Organization-wide

| | |
|---|---|
| **Audience** | Executive sponsor, head of L&D, board |
| **Decision** | Approve overall training themes and budget envelope |
| **Time horizon** | Annual or quarterly |
| **Format** | Single dashboard or 1-page PDF |
| **Granularity** | Top 10 priorities, business line totals, key metrics |

Computed by:
- `error_rate` over all responses
- `coverage_percentage` over the entire workforce
- One report per business line (never combined)

### Tier 2 — Regional / Department

| | |
|---|---|
| **Audience** | Regional managers, department heads |
| **Decision** | Allocate regional training resources, decide which teams need more support |
| **Time horizon** | Quarterly |
| **Format** | Excel workbook, one tab per region × business line |
| **Granularity** | Top 20–30 priorities per region, comparison to organization-wide |

Computed by:
- `error_rate` filtered to responses from this region
- `coverage_percentage` filtered to employees in this region
- Side-by-side with the organization-wide score so the reader sees the gap (literally) between regional and overall

### Tier 3 — Team / Unit

| | |
|---|---|
| **Audience** | Team leads, unit managers |
| **Decision** | "Who on my team needs which course this week?" |
| **Time horizon** | Weekly to monthly |
| **Format** | Per-team Excel file, one row per gap, with employee-level heatmap |
| **Granularity** | All gaps applicable to the team, with individual employee performance |

Computed by:
- `error_rate` filtered to this team's responses
- `coverage_percentage` filtered to this team's members
- Direct links to relevant courses for each gap, so the manager can act in one click

## Worked example — same gap, three tiers

Suppose a gap "X" has these stats:

| Scope | Responses | Error rate | Coverage | Importance | Priority |
|---|---|---|---|---|---|
| Organization-wide | 500 | 30% | 50% | High (100) | (100 × 30 × 50)/1000 = **150** |
| Region North | 80 | 65% | 80% | High (100) | (100 × 65 × 80)/1000 = **520** |
| Team A (in North) | 6 | 100% | 100% | High (100) | (100 × 100 × 100)/1000 = **1000** |

**Same gap. Three different priorities. Three different recommendations.**

- Tier 1 report: "Gap X is a moderate concern. Will address in our Q3 plan."
- Tier 2 report (North): "Gap X is a major concern in your region. Flag it now."
- Tier 3 report (Team A): "Every member of this team failed Gap X. Enroll all 6 in the relevant course this week."

Without all three reports, only the team lead would know to act, and they would not have the framework to escalate to the regional manager.

## Sample size thresholds per tier

The smaller the population, the noisier the error rate. Set minimum thresholds:

| Tier | Minimum responses per gap | Rationale |
|---|---|---|
| Organization | 10 | Standard statistical floor |
| Region | 5 | Regions can be small; tolerate slightly noisier signals |
| Team | 3 | Teams are tiny; below 3 the signal is too weak to act on |

**What to do with under-threshold gaps:**
- Do not include them in the priority list
- Show them in a separate "needs more data" section
- Flag for inclusion in the next assessment cycle

## Output formats — practical recommendations

### Tier 1 — One dashboard or one PDF page

Show:
- Top 10 organization priorities (table with importance, error rate, coverage, score)
- Side-by-side bar charts: business line A vs business line B priorities
- Total estimated training hours / cost
- One-line recommendation per top-3 gap

Avoid: 30-page PDFs that no executive will read, dashboards with 12 panels that hide the headlines.

### Tier 2 — Excel workbook with one tab per region

Each tab includes:
- Top 20 gaps for that region
- A "delta vs organization" column so the reader sees which gaps are worse here than elsewhere
- A summary section: how this region compares overall

If you have 5 regions × 2 business lines, that is 10 tabs in one workbook. Use clear tab names and a table of contents tab.

### Tier 3 — One file per team, with two sheets

**Sheet 1 — Gap summary:**
- All gaps applicable to this team, sorted by team-level priority
- Direct hyperlinks to the relevant training course
- Employee count per gap

**Sheet 2 — Employee × Category heatmap:**
- Rows: each employee (anonymized or by ID)
- Columns: each category
- Cells: the employee's success rate in that category, color-coded
- This is the most actionable view: a manager can scan it and see exactly who needs help with what

## How to scope the calculations correctly

The formula is the same. Only the "scope" changes — the WHERE clause when you query the data.

```
-- Tier 1 (org-wide)
SELECT category, AVG(is_correct=0) * 100 AS error_rate
FROM responses
WHERE business_line = ?
GROUP BY category;

-- Tier 2 (regional)
SELECT category, AVG(is_correct=0) * 100 AS error_rate
FROM responses
WHERE business_line = ? AND region = ?
GROUP BY category;

-- Tier 3 (team)
SELECT category, AVG(is_correct=0) * 100 AS error_rate
FROM responses
WHERE business_line = ? AND team = ?
GROUP BY category;
```

Coverage works the same way — denominator is the population in scope.

`scripts/calculate_priority_score.py` accepts a `--level` flag to switch between scopes.

## Common mistakes

### Reusing the org-wide priority list at the team level

Tempting and wrong. The whole point of tier 3 is that team-level priorities differ from organizational ones. If you give every team the same list, you lose the methodology's main value.

### Skipping tier 2 because "we have tier 1 and tier 3"

Tier 2 is what enables regional managers to coordinate across their teams. Without it, regional patterns (e.g., "this region has consistently lower scores on X") are hidden.

### Showing all three tiers to all audiences

Each audience gets their tier. An executive does not need a per-team breakdown; a team lead does not need org-wide totals. Mixing tiers creates noise and dilutes the call to action.

### Forgetting to anonymize or lock down team-level data

Tier 3 reports contain individual employee performance. Treat them as confidential. Distribute only to the relevant team lead and follow your organization's data-handling rules.

## Process for producing all three tiers

1. Lock the validated taxonomy (output of Phase 3).
2. Run `scripts/calculate_priority_score.py --level org` once, save tier 1 outputs.
3. Loop over regions: run `--level region --filter region=<name>` for each, save tier 2 outputs.
4. Loop over teams: run `--level team --filter team=<name>` for each, save tier 3 outputs.
5. Distribute according to your communication plan: tier 1 to execs, tier 2 to regionals, tier 3 to team leads.
6. Schedule a review session per tier — these are decisions that benefit from real-time discussion, not just file attachments.

## See also

- `references/priority-formula.md` — the underlying formula
- `scripts/calculate_priority_score.py` — the executable that supports all three levels
- `references/data-schema-template.md` — the schema fields that define region and team
