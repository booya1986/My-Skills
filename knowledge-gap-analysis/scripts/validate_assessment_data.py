#!/usr/bin/env python3
"""
validate_assessment_data.py — Sanity-check an assessment responses CSV before analysis.

Catches the silent killers: missing required columns, inconsistent encodings,
whitespace-only category splits, duplicate (employee, question) pairs, and
underpowered population segments.

USAGE
    python validate_assessment_data.py responses.csv

EXIT CODES
    0 — passed all checks (warnings may still print)
    1 — one or more critical errors found; fix before analyzing
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"employee_id", "question_id", "is_correct", "business_line", "category", "importance"}
RECOMMENDED_COLUMNS = {"subcategory", "gap_description", "region", "team", "manager_id"}

VALID_IS_CORRECT = {0, 1, 0.0, 1.0, True, False, "0", "1"}
KNOWN_IMPORTANCE = {"high", "medium", "low"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path, help="Path to responses CSV")
    args = parser.parse_args()

    if not args.input.exists():
        sys.exit(f"ERROR: file not found: {args.input}")

    df = pd.read_csv(args.input)
    print(f"Loaded {len(df):,} rows, {len(df.columns)} columns from {args.input}\n")

    errors: list[str] = []
    warnings: list[str] = []

    # --- Required columns ---
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        errors.append(f"Missing required columns: {sorted(missing)}")
        print_summary(errors, warnings)
        return 1

    print("Required columns: OK")

    # --- Recommended columns ---
    missing_recommended = RECOMMENDED_COLUMNS - set(df.columns)
    if missing_recommended:
        warnings.append(
            f"Missing recommended columns (some analyses unavailable): {sorted(missing_recommended)}"
        )

    # --- is_correct values ---
    distinct = set(df["is_correct"].dropna().unique())
    bad = distinct - VALID_IS_CORRECT
    if bad:
        errors.append(
            f"is_correct contains non-binary values: {sorted(map(str, bad))[:5]}... "
            f"Normalize to 0/1 (e.g., map 'Correct'->1, 'Y'->1)."
        )
    null_correct = df["is_correct"].isna().sum()
    if null_correct:
        warnings.append(
            f"{null_correct:,} rows have null is_correct (these will be excluded from error_rate)"
        )

    # --- importance values ---
    importance_normalized = df["importance"].astype(str).str.strip().str.lower()
    unknown_importance = set(importance_normalized.dropna().unique()) - KNOWN_IMPORTANCE
    if unknown_importance:
        warnings.append(
            f"Unknown importance values: {sorted(unknown_importance)}\n"
            f"  Map them to 'high'/'medium'/'low' or extend IMPORTANCE_ALIASES "
            f"in calculate_priority_score.py"
        )
    importance_dist = importance_normalized.value_counts(normalize=True) * 100
    high_pct = importance_dist.get("high", 0)
    if high_pct > 70:
        warnings.append(
            f"{high_pct:.0f}% of questions are 'high' importance — this skews priorities. "
            f"Re-examine the importance rubric (most questions should be 'medium')."
        )

    # --- Duplicate (employee, question) pairs ---
    dup_mask = df.duplicated(subset=["employee_id", "question_id"], keep=False)
    n_dup_rows = int(dup_mask.sum())
    if n_dup_rows:
        n_unique_pairs = df.loc[dup_mask, ["employee_id", "question_id"]].drop_duplicates().shape[0]
        errors.append(
            f"{n_dup_rows} rows are duplicate (employee_id, question_id) pairs "
            f"({n_unique_pairs} distinct pairs). This usually means a join went wrong; "
            f"deduplicate before analysis."
        )

    # --- Whitespace-only differences in categorical columns ---
    for col in ["business_line", "category", "importance"]:
        if col in df.columns:
            stripped = df[col].astype(str).str.strip()
            if (stripped != df[col]).any():
                n = (stripped != df[col]).sum()
                warnings.append(
                    f"{col}: {n} values have leading/trailing whitespace. "
                    f"This silently splits your data — strip during ingestion."
                )

    # --- Population sizes ---
    print("\nPopulation breakdown:")
    print(f"  Unique employees:  {df['employee_id'].nunique():,}")
    print(f"  Unique questions:  {df['question_id'].nunique():,}")
    print(f"  Total responses:   {len(df):,}")
    print(f"  Business lines:    {sorted(df['business_line'].dropna().unique())}")

    if "region" in df.columns:
        regions = df.groupby(["business_line", "region"])["employee_id"].nunique()
        small_regions = regions[regions < 5]
        if len(small_regions):
            warnings.append(
                f"{len(small_regions)} (business_line, region) combinations have < 5 employees. "
                f"Tier 2 priorities for these will be unreliable."
            )

    if "team" in df.columns:
        teams = df.groupby(["business_line", "team"])["employee_id"].nunique()
        tiny_teams = teams[teams < 3]
        if len(tiny_teams):
            warnings.append(
                f"{len(tiny_teams)} (business_line, team) combinations have < 3 employees. "
                f"Tier 3 priorities for these are not statistically meaningful."
            )

    # --- Per-business-line summary ---
    print("\nPer business line:")
    summary = (
        df.groupby("business_line").agg(
            employees=("employee_id", "nunique"),
            questions=("question_id", "nunique"),
            responses=("is_correct", "size"),
            error_rate=("is_correct", lambda s: round((1 - pd.to_numeric(s, errors="coerce").mean()) * 100, 1)),
        )
    )
    print(summary.to_string())

    print()
    print_summary(errors, warnings)
    return 1 if errors else 0


def print_summary(errors: list[str], warnings: list[str]) -> None:
    if not errors and not warnings:
        print("All checks passed. Data is ready for analysis.")
        return

    if errors:
        print(f"\n{len(errors)} ERROR(S) — must fix before analysis:")
        for i, msg in enumerate(errors, 1):
            print(f"  {i}. {msg}")

    if warnings:
        print(f"\n{len(warnings)} WARNING(S) — review these:")
        for i, msg in enumerate(warnings, 1):
            print(f"  {i}. {msg}")


if __name__ == "__main__":
    raise SystemExit(main())
