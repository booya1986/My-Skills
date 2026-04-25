#!/usr/bin/env python3
"""
calculate_priority_score.py — Compute knowledge-gap priorities from assessment responses.

Implements the priority formula:
    priority_score = (importance_weight × error_rate × coverage_percentage) / 1000

The same calculation can be scoped to three levels (organization, region, team)
to support the three-tier reporting hierarchy.

USAGE
    python calculate_priority_score.py --input responses.csv --output priorities.csv
    python calculate_priority_score.py --input responses.csv --output priorities.csv --level region
    python calculate_priority_score.py --input responses.csv --output priorities.csv --level team --filter team=Team-A
    python calculate_priority_score.py --input responses.csv --output priorities.csv --business-line Sales

INPUT CSV (minimum required columns)
    employee_id, question_id, is_correct (0/1), business_line, category, importance (high/medium/low)

INPUT CSV (recommended additional columns)
    subcategory, gap_description, region, team

OUTPUT CSV
    Sorted by priority_score descending. One row per (business_line, scope, gap).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"employee_id", "question_id", "is_correct", "business_line", "category", "importance"}

IMPORTANCE_WEIGHTS = {"high": 100, "medium": 50, "low": 25}

# Common importance synonyms across languages and styles. Extend as needed.
IMPORTANCE_ALIASES = {
    "h": "high", "hi": "high", "high importance": "high", "critical": "high",
    "m": "medium", "med": "medium", "moderate": "medium",
    "l": "low", "lo": "low", "low importance": "low", "minor": "low",
}

# Minimum response counts per gap for the priority to be considered reliable.
MIN_RESPONSES = {"org": 10, "region": 5, "team": 3}


def load_responses(path: Path) -> pd.DataFrame:
    """Load the responses CSV and validate required columns."""
    if not path.exists():
        sys.exit(f"ERROR: input file not found: {path}")

    df = pd.read_csv(path)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        sys.exit(f"ERROR: missing required columns: {sorted(missing)}")

    # Strip whitespace on string columns to avoid silent splits.
    for col in ["business_line", "category", "importance"]:
        df[col] = df[col].astype(str).str.strip()

    # Normalize importance to lowercase canonical values.
    df["importance_normalized"] = df["importance"].str.lower().map(
        lambda v: IMPORTANCE_ALIASES.get(v, v)
    )

    unknown = set(df["importance_normalized"].unique()) - set(IMPORTANCE_WEIGHTS)
    if unknown:
        sys.exit(
            f"ERROR: unrecognized importance values: {sorted(unknown)}\n"
            f"Expected one of: {sorted(IMPORTANCE_WEIGHTS)} (or known aliases).\n"
            f"To accept your custom value, add it to IMPORTANCE_ALIASES in this script."
        )

    df["importance_weight"] = df["importance_normalized"].map(IMPORTANCE_WEIGHTS)

    # is_correct should be 0 or 1.
    df["is_correct"] = pd.to_numeric(df["is_correct"], errors="coerce")
    bad = df["is_correct"].isna().sum()
    if bad:
        sys.exit(f"ERROR: {bad} rows have non-numeric is_correct values. Normalize to 0/1 first.")

    return df


def apply_filter(df: pd.DataFrame, filter_expr: str | None) -> pd.DataFrame:
    """Apply a key=value filter, e.g. 'region=North' or 'team=Team-A'."""
    if not filter_expr:
        return df
    if "=" not in filter_expr:
        sys.exit(f"ERROR: --filter must be 'column=value', got: {filter_expr}")
    col, value = filter_expr.split("=", 1)
    col, value = col.strip(), value.strip()
    if col not in df.columns:
        sys.exit(f"ERROR: filter column '{col}' not in data")
    return df[df[col] == value]


def calculate_priorities(
    df: pd.DataFrame,
    level: str,
    business_line: str | None,
) -> pd.DataFrame:
    """
    Compute priority scores at the chosen scope.

    The scope determines:
      - what subset of responses contributes to error_rate and coverage
      - what counts as "the population" for coverage denominator
    """
    scope = df.copy()

    # Restrict to one business line at a time — never aggregate across them.
    if business_line:
        scope = scope[scope["business_line"] == business_line]
        if scope.empty:
            sys.exit(f"ERROR: no rows for business_line='{business_line}'")
        business_lines = [business_line]
    else:
        business_lines = scope["business_line"].dropna().unique().tolist()

    results = []
    min_responses = MIN_RESPONSES[level]

    for bl in business_lines:
        bl_data = scope[scope["business_line"] == bl]
        bl_population = bl_data["employee_id"].nunique()

        # group_cols defines the gap's identity. Extend with subcategory if available.
        group_cols = ["category"]
        if "subcategory" in bl_data.columns:
            group_cols.append("subcategory")

        agg = (
            bl_data.groupby(group_cols, dropna=False)
            .agg(
                response_count=("is_correct", "size"),
                unique_responders=("employee_id", "nunique"),
                error_rate=("is_correct", lambda s: (1 - s.mean()) * 100),
                importance_weight=("importance_weight", "max"),
            )
            .reset_index()
        )

        agg["business_line"] = bl
        agg["coverage_percentage"] = (agg["unique_responders"] / bl_population) * 100

        # The formula.
        agg["priority_score"] = (
            agg["importance_weight"] * agg["error_rate"] * agg["coverage_percentage"]
        ) / 1000

        # Flag underpowered gaps but keep them in the output for transparency.
        agg["reliable"] = agg["response_count"] >= min_responses

        results.append(agg)

    if not results:
        return pd.DataFrame()

    out = pd.concat(results, ignore_index=True)

    # Order columns for readability; sort highest priority first.
    leading = ["business_line"] + group_cols + [
        "priority_score", "importance_weight", "error_rate",
        "coverage_percentage", "response_count", "unique_responders", "reliable",
    ]
    other = [c for c in out.columns if c not in leading]
    out = out[leading + other]
    out = out.sort_values(
        ["business_line", "reliable", "priority_score"],
        ascending=[True, False, False],
    ).reset_index(drop=True)

    # Round numerics for human-readable output.
    out["priority_score"] = out["priority_score"].round(2)
    out["error_rate"] = out["error_rate"].round(1)
    out["coverage_percentage"] = out["coverage_percentage"].round(1)

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", required=True, type=Path, help="Path to responses CSV")
    parser.add_argument("--output", required=True, type=Path, help="Path to write priorities CSV")
    parser.add_argument(
        "--level",
        choices=["org", "region", "team"],
        default="org",
        help="Scope for the priority calculation (controls minimum-response threshold). "
             "Use --filter to restrict to a specific region or team.",
    )
    parser.add_argument(
        "--filter",
        dest="filter_expr",
        help="Restrict to a subset, e.g. 'region=North' or 'team=Team-A'",
    )
    parser.add_argument(
        "--business-line",
        help="If set, only compute priorities for this business line. "
             "If omitted, computes per business_line and writes them all to one file.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="If set, keep only the top N priorities per business line in the output.",
    )

    args = parser.parse_args()

    df = load_responses(args.input)
    df = apply_filter(df, args.filter_expr)

    if df.empty:
        sys.exit("ERROR: no rows after applying filter")

    priorities = calculate_priorities(df, args.level, args.business_line)

    if priorities.empty:
        sys.exit("ERROR: no priorities computed (check input data)")

    if args.top:
        priorities = (
            priorities.groupby("business_line", group_keys=False)
            .head(args.top)
            .reset_index(drop=True)
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    priorities.to_csv(args.output, index=False)

    n_business_lines = priorities["business_line"].nunique()
    n_reliable = int(priorities["reliable"].sum())
    n_total = len(priorities)

    print(
        f"Wrote {n_total} priorities ({n_reliable} reliable, "
        f"{n_total - n_reliable} flagged as low-sample) "
        f"across {n_business_lines} business line(s) to {args.output}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
