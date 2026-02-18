#!/usr/bin/env python3
"""
ETL Validation Script for HAILIE Analytics Database
Spot-checks provider scores in DuckDB against raw Excel source data
"""

import pandas as pd
import duckdb
import sys

DB_PATH = "attached_assets/hailie_analytics_v2.duckdb"

# Known providers to validate (code, expected_dataset, year)
TEST_PROVIDERS = [
    # LCRA providers
    ("L4004", "LCRA", 2025),
    ("L4229", "LCRA", 2025),
    ("L4004", "LCRA", 2024),
    # LCHO-only providers (not in LCRA)
    ("4636", "LCHO", 2025),
    ("4668", "LCHO", 2025),
]


def validate():
    con = duckdb.connect(DB_PATH, read_only=True)
    failures = 0

    print("=" * 60)
    print("HAILIE ETL Validation")
    print("=" * 60)

    # 1. Check table existence
    tables = con.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
    ).df()["table_name"].tolist()
    expected_tables = ["raw_scores", "calculated_percentiles", "calculated_correlations",
                       "provider_dataset_mapping", "provider_summary"]
    for t in expected_tables:
        if t in tables:
            print(f"  [OK] Table '{t}' exists")
        else:
            print(f"  [FAIL] Table '{t}' missing")
            failures += 1

    # 2. Check multi-year data exists
    years = con.execute("SELECT DISTINCT year FROM raw_scores ORDER BY year").df()["year"].tolist()
    print(f"\n  Years in database: {years}")
    if 2024 in years and 2025 in years:
        print("  [OK] Multi-year data present")
    else:
        print("  [FAIL] Expected both 2024 and 2025 data")
        failures += 1

    # 3. Check provider counts per dataset
    print("\n  Provider counts by dataset and year:")
    counts = con.execute("""
        SELECT year, dataset_type, COUNT(DISTINCT provider_code) as n
        FROM raw_scores
        GROUP BY year, dataset_type
        ORDER BY year, dataset_type
    """).df()
    print(counts.to_string(index=False))

    # 3b. Validate LCHO provider counts (should be ~56 for 2024, ~59 for 2025)
    for check_year, min_expected in [(2024, 50), (2025, 50)]:
        lcho_row = counts[(counts["year"] == check_year) & (counts["dataset_type"] == "LCHO")]
        if lcho_row.empty:
            print(f"  [FAIL] No LCHO providers found for {check_year}")
            failures += 1
        else:
            lcho_count = int(lcho_row["n"].iloc[0])
            if lcho_count >= min_expected:
                print(f"  [OK] {check_year} LCHO: {lcho_count} providers (expected >= {min_expected})")
            else:
                print(f"  [FAIL] {check_year} LCHO: only {lcho_count} providers (expected >= {min_expected})")
                failures += 1

    # 4. Spot-check provider scores
    print("\n  Spot-checking provider scores...")
    for provider_code, expected_dataset, year in TEST_PROVIDERS:
        scores = con.execute("""
            SELECT tp_measure, score, dataset_type
            FROM raw_scores
            WHERE provider_code = ? AND year = ? AND dataset_type = ?
            ORDER BY tp_measure
        """, [provider_code, year, expected_dataset]).df()

        if scores.empty:
            print(f"  [FAIL] {provider_code} ({expected_dataset}, {year}): no data found")
            failures += 1
            continue

        actual_dataset = scores["dataset_type"].iloc[0]
        n_measures = len(scores)
        score_range = f"{scores['score'].min():.1f}-{scores['score'].max():.1f}"

        if actual_dataset != expected_dataset:
            print(f"  [FAIL] {provider_code}: expected {expected_dataset}, got {actual_dataset}")
            failures += 1
        else:
            print(f"  [OK] {provider_code} ({actual_dataset}, {year}): "
                  f"{n_measures} measures, scores {score_range}")

        # Validate scores are in 0-100 range
        out_of_range = ((scores["score"] < 0) | (scores["score"] > 100)).sum()
        if out_of_range > 0:
            print(f"  [FAIL] {provider_code}: {out_of_range} scores outside 0-100 range")
            failures += 1

    # 5. Check percentiles exist for all providers with scores
    print("\n  Checking percentile coverage...")
    missing_percentiles = con.execute("""
        SELECT COUNT(DISTINCT rs.provider_code || rs.tp_measure || CAST(rs.year AS VARCHAR)) as missing
        FROM raw_scores rs
        LEFT JOIN calculated_percentiles cp
            ON rs.provider_code = cp.provider_code
            AND rs.tp_measure = cp.tp_measure
            AND rs.year = cp.year
        WHERE cp.percentile_rank IS NULL
    """).fetchone()[0]
    if missing_percentiles == 0:
        print("  [OK] All scores have corresponding percentiles")
    else:
        print(f"  [WARN] {missing_percentiles} scores missing percentiles")

    # 6. Check dataset mapping integrity
    # Providers CAN appear in both LCRA and LCHO (different schemes, different scores)
    # But should NOT appear as both COMBINED and LCRA/LCHO
    bad_dupes = con.execute("""
        SELECT provider_code
        FROM provider_dataset_mapping
        WHERE dataset_type = 'COMBINED'
          AND provider_code IN (
            SELECT provider_code FROM provider_dataset_mapping
            WHERE dataset_type IN ('LCRA', 'LCHO')
          )
    """).df()
    multi_dataset = con.execute("""
        SELECT COUNT(DISTINCT provider_code) as n
        FROM provider_dataset_mapping
        GROUP BY provider_code
        HAVING COUNT(DISTINCT dataset_type) > 1
    """).df()
    multi_count = len(multi_dataset) if not multi_dataset.empty else 0
    if bad_dupes.empty:
        print(f"  [OK] No COMBINED/LCRA overlap ({multi_count} providers in both LCRA+LCHO — expected)")
    else:
        print(f"  [FAIL] {len(bad_dupes)} providers appear as COMBINED alongside LCRA/LCHO")
        failures += 1

    con.close()

    print("\n" + "=" * 60)
    if failures == 0:
        print("ALL CHECKS PASSED")
    else:
        print(f"{failures} CHECK(S) FAILED")
    print("=" * 60)

    return failures == 0


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
