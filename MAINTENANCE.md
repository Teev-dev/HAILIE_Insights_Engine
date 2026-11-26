# Maintenance Guide

## Annual TSM Data Refresh

### When

The UK Government publishes new TSM data annually, typically around November. Monitor the [Regulator of Social Housing](https://www.gov.uk/government/organisations/regulator-of-social-housing) for publication dates.

### Procedure

1. **Download** the new TSM Excel file from the government source
2. **Place** it in `data/source/`
3. **Run ETL:**
   ```bash
   python build_analytics_db_v2.py --excel-path data/source/NEW_FILE.xlsx --year YYYY
   ```
4. **Verify** record counts:
   ```bash
   python db_view_script.py
   ```
5. **Check for duplicates:**
   ```bash
   python diagnose_duplicates.py
   ```
   The ETL also loads `provider_metadata` (landlord type, size band, predominant region) from the same workbook; peer-group filtering reads it. To reload only that table for a year, without recalculating scores or percentiles, add `--metadata-only`.
6. **Update year defaults** (see checklist below)
7. **Test locally:**
   ```bash
   streamlit run app.py
   ```
8. **Deploy** (rebuild Docker image or copy database to Railway volume)

   **Note:** when `DATA_PATH` points at a persistent volume, the baked-in database is only copied there if no database exists yet (`config.py` auto-seed). A rebuilt image does **not** replace the volume's database. After any change to the database (new year, new table such as `provider_metadata`), copy the new file to the volume. Until then the app keeps working on the old database, but features that need the new data are unavailable: without `provider_metadata` the peer group size/region selectors are hidden.

## Year Default Update Checklist

When ingesting a new year of data, update all year defaults from the previous year (N-1) to the new year (N). Line numbers drift as the file evolves — grep is the source of truth. Example from the 2026 refresh:

### data_processor_enhanced.py

| Method | Change |
|--------|--------|
| `get_provider_percentiles` | `year: int = N-1` → `year: int = N` |
| `get_dataset_correlations` | `year: int = N-1` → `year: int = N` |
| `get_provider_scores` | `year: int = N-1` → `year: int = N` |
| `get_peer_comparison_data` | `year: int = N-1` → `year: int = N` |
| `get_dataset_summary_stats` | `year: int = N-1` → `year: int = N` |
| `get_measure_distribution` | `year: int = N-1` → `year: int = N` |
| `get_all_providers_with_scores` | `year: int = N-1` → `year: int = N` |
| `load_default_data` | `year: int = N-1` → `year: int = N` |
| `get_measure_statistics` | `year: int = N-1` → `year: int = N` |
| `get_provider_metadata` | `year: int = N-1` → `year: int = N` |
| `get_peer_filter_options` | `year: int = N-1` → `year: int = N` |
| `get_peer_group_scores` | `year: int = N-1` → `year: int = N` |

Also update the `Defaults to year YYYY (latest data)` docstrings.

### analytics_refactored.py

`LATEST_DATA_YEAR = N` constant (near the top of the file). `calculate_momentum()` and the multi-provider comparison take their year from it; nothing else in the file names a year.

### app.py

`CURRENT_DATA_YEAR = N` constant (near the top of the file).

### dashboard.py

Two `.get()` fallback literals: `.get('latest_year', N)` and `.get('prior_year', N-1)`. Grep catches both.

### tooltip_definitions.py

Review `PROVIDER_SUCCESSION_NOTES` (see "Providers missing from the new year" below).

### validate_etl.py

Extend `TEST_PROVIDERS` with new-year entries, the LCHO count loop, and the multi-year assertion.

### Quick search command

```bash
grep -rn "year.*=.*2025\|year = 2025" *.py
```

This should return zero results after the update is complete.

## Providers missing from the new year

Each year some landlords drop out of the regulator's dataset, usually because they merged into another landlord. They stay in the provider dropdown. Selecting one shows a notice and its most recent results, compared with the peers of that same year; the app works this out from the data (`get_latest_year` against `CURRENT_DATA_YEAR`), so no code change is needed for them to keep working.

What does need a human each year is the merger wording in `PROVIDER_SUCCESSION_NOTES` (`tooltip_definitions.py`): one sourced sentence per lapsed provider, naming the landlord that now reports. After ingesting the new year, run:

```bash
python -m unittest tests.test_prior_year_providers
```

- `test_every_lapsed_dropdown_provider_is_accounted_for` fails if a provider has newly lapsed. Find out what happened to it (trade press, the regulator's register), then either add a note with the successor's provider code, or add the provider to the test's list of lapsed providers with no known successor.
- `test_succession_notes_point_from_lapsed_to_current_providers` fails if a provider with a note is back in the data, or its successor has itself left the data. Remove or update the note.

Providers the regulator keeps under the same code through a rename need nothing: the dropdown shows the new name with "formerly ..." appended, and year-over-year comparisons carry on across the rename.

## Database Rebuild from Source

If the database becomes corrupted or you need a clean rebuild from all available years:

```bash
# Remove existing database
rm data/hailie_analytics_v2.duckdb

# Rebuild from each year's source data
python build_analytics_db_v2.py --excel-path data/source/2024_TSM_Full_Data_v1.1_FINAL_1756577982265.xlsx --year 2024
python build_analytics_db_v2.py --excel-path data/source/2025_TSM_Full_Data_v1.0_FINAL.xlsx --year 2025
python build_analytics_db_v2.py --excel-path data/source/2026_TSM_Full_Dataset_FINAL.xlsx --year 2026
```

Repeat for each year of data available in `data/source/`.

## Dependency Updates

### When

Check quarterly, or when security advisories are published for key dependencies.

### Key dependencies to watch

| Package | Risk | Notes |
|---------|------|-------|
| `streamlit` | Breaking changes between majors | Test UI thoroughly after updates |
| `duckdb` | Database format changes | May require database rebuild |
| `pandas` | API deprecations | Check for warnings in test output |
| `scipy` | Minimal risk | Statistical functions are stable |
| `plotly` | Chart rendering changes | Visual regression check needed |

### Update procedure

1. Update versions in `pyproject.toml`
2. Rebuild locally: `pip install .`
3. Test: `streamlit run app.py` — verify all three insights render correctly
4. Rebuild Docker: `docker build -t hailie-insights . && docker run -p 8501:8501 -e PORT=8501 hailie-insights`
5. If all passes, commit and deploy

## Docker Image Maintenance

### Rebuild triggers

- New TSM data ingested (database changed)
- Dependency versions updated
- Application code changed
- Base image security update (`python:3.11-slim`)

### Base image updates

Periodically check for security updates to `python:3.11-slim`:

```bash
docker pull python:3.11-slim
docker build --no-cache -t hailie-insights .
```
