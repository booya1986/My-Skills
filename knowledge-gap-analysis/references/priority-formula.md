# Priority Formula — Deep Dive

This document explains the priority scoring formula used in Phase 4 of the methodology. Read this when the user asks how priorities are computed, wants to tune the weights, or challenges a specific gap's ranking.

## The formula

```
priority_score = (importance_weight × error_rate × coverage_percentage) / 1000
```

| Component | Definition | Range |
|---|---|---|
| `importance_weight` | Business criticality predetermined by subject-matter experts during Phase 3 validation | 25, 50, or 100 |
| `error_rate` | Percentage of employees who answered incorrectly on this gap | 0–100 |
| `coverage_percentage` | Percentage of the relevant population that was actually assessed on this gap | 0–100 |

The division by 1000 is a cosmetic rescaling so scores fall in roughly the 0–1000 range and are easy to read. It does not change the ranking.

## Why these three components

### Importance — "How much should we care?"

Not all knowledge is equal. A regulatory compliance gap can lead to fines; a "nice to know" gap rarely does. The expert-validated importance weighting injects strategic judgment into what would otherwise be a purely statistical ranking.

**Standard weights:**
- High = 100 — must-know, regulatory, customer-facing critical
- Medium = 50 — important for role effectiveness
- Low = 25 — useful but not essential

**Why these specific numbers (100/50/25):** the absolute values are arbitrary; what matters is the ratio. High is 2× Medium and 4× Low. This means a high-importance gap with a moderate error rate can outrank a low-importance gap that nearly everyone failed — which matches stakeholder intuition.

If the 4× ratio feels too aggressive for your context, you can tune it (e.g., 100/60/30 for a flatter curve, or 100/40/15 for a steeper one). Document the choice and stick with it across analyses for comparability.

### Error rate — "How badly are people doing?"

This is the direct measure of failure. It is computed from the binary correct/incorrect column, not from the test score. Higher = worse.

```
error_rate = (count of incorrect responses / total responses) × 100
```

**Why error rate, not average score:**
- Error rate has a single, interpretable meaning: "X% of people got this wrong"
- Average scores conflate severity (how wrong) with frequency (how many wrong) — harder to reason about
- Error rate cleanly normalizes across questions with different point values

### Coverage — "How widespread is the impact?"

Not every gap is tested in every employee. Some questions only appear for specific roles, levels, or randomized subsets. Coverage measures what fraction of the relevant population was actually assessed on this gap.

```
coverage_percentage = (employees who responded / total employees in scope) × 100
```

**Why coverage matters:** a gap with 80% error rate but tested only on 5 employees is a much weaker signal than a gap with 60% error rate tested on 500 employees. Coverage acts as a confidence multiplier.

**Important nuance:** coverage uses *attempted responses*, not *correct responses*. An employee who answered (correctly or not) counts for coverage; one who skipped does not.

## Why multiplication, not addition or averaging

Multiplication enforces a "must-have all three" property. If any single dimension is zero, the whole score is zero:

| Importance | Error rate | Coverage | Score | Interpretation |
|---|---|---|---|---|
| 100 (high) | 90% | 80% | **7,200/1000 = 7.2** | High-impact, widespread failure — top priority |
| 100 (high) | 90% | 2% | 0.18 | Severe but barely measured — weak signal, deprioritize |
| 100 (high) | 5% | 80% | 0.40 | Important but everyone knows it — no need to train |
| 25 (low) | 90% | 80% | 1.80 | Widespread failure on a low-importance topic — modest priority |

**Why averaging would mislead:**
- Averaging would let one strong dimension hide weakness in another
- A 90% error rate on a low-importance, low-coverage gap would average to "moderate" — but it is actually a low-priority signal
- Multiplication makes the framework *intolerant* of weak inputs, which is what we want

## Worked example — three gaps competing for the top slot

Imagine three knowledge gaps in a workforce assessment:

| Gap | Importance | Error rate | Coverage |
|---|---|---|---|
| A: New regulation introduced 3 months ago | High (100) | 75% | 60% |
| B: Long-standing core procedure | High (100) | 30% | 95% |
| C: Niche advanced topic | Medium (50) | 90% | 12% |

**Scores:**
- A: (100 × 75 × 60) / 1000 = **450** ← highest priority
- B: (100 × 30 × 95) / 1000 = **285**
- C: (50 × 90 × 12) / 1000 = **54**

**Why A wins:** combination of importance, high failure rate, and broad enough sample size. The new regulation explanation is consistent — recent rollouts produce exactly this signature.

**Why B is second despite being well-covered:** error rate is low. Most people know it. Training the 30% who don't is still worthwhile, but it is a smaller crisis than A.

**Why C is small despite 90% error rate:** only 12% of the population was tested on it. The signal is weak, and the importance is medium. A defensible action is "add to the next assessment cycle to get better coverage" rather than "launch training now".

## Tuning thresholds

In practice, set these guardrails:

- **Minimum coverage threshold:** drop gaps with coverage below 5% from the priority list (they cannot be reliably ranked). Flag them as "needs more data".
- **Minimum response count per gap:** at the team level, require ≥ 3 employees responded; at the regional level, ≥ 5; at the org level, ≥ 10. Below these thresholds the error rate is too noisy.
- **Top-N output:** show the top 10 to executives, top 25 to regional managers, all gaps to team leads.

## Alternatives considered (and why this was chosen)

### RICE (Reach × Impact × Confidence × Effort)

RICE is a popular product-prioritization framework. The skill's formula is structurally similar:
- Reach ≈ coverage_percentage
- Impact ≈ importance_weight
- Confidence ≈ implicit in coverage (more coverage = more confidence)
- Effort is intentionally omitted — the framework prioritizes what *should* be trained, separately from what *can* be cheaply trained. Effort enters in the planning step that follows.

### AHP (Analytic Hierarchy Process)

AHP allows multi-criteria pairwise comparisons by experts. More rigorous, but: it requires significantly more expert time, the output is harder to explain to executives, and it does not handle the coverage dimension naturally. Use AHP only if your stakeholders specifically demand it.

### Simple ranking (sort by error rate alone)

Naive but tempting. Fails because it ignores importance (you train people on trivia and miss compliance issues) and ignores coverage (statistically noisy gaps land at the top).

### Inverse score (100 − average_score)

Used in some L&D tools. The problem: it conflates "many people got it slightly wrong" with "few people got it completely wrong". Error rate is a cleaner signal.

## How to defend the formula in stakeholder reviews

When a stakeholder challenges a specific priority:

1. **Show the breakdown.** Walk through the three components for the gap in question.
2. **Compare to a higher-ranked gap.** Show why the other gap scored higher on at least one dimension.
3. **If the dispute is about importance:** route it back to the validating expert for that business line. The formula is downstream of expert judgment, not a substitute for it.
4. **Never patch the formula for a single gap.** If you believe the formula is wrong, change it for everyone and re-rank.

## Implementation reference

See `scripts/calculate_priority_score.py` for the executable implementation. The script accepts a CSV with the canonical schema (`references/data-schema-template.md`) and produces a CSV sorted by priority score in descending order.
