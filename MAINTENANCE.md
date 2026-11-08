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
6. **Update year defaults** (see checklist below)
7. **Test locally:**
   ```bash
   streamlit run app.py
   ```
8. **Deploy** (rebuild Docker image or copy database to Railway volume)

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
| `get_provider_dataset_type` (SQL) | `year = N-1` → `year = N` (hardcoded in SQL string, not a parameter default — grep for `AND year =`) |
| `get_measure_statistics` | `year: int = N-1` → `year: int = N` |

Also update the five `Defaults to year YYYY (latest data)` docstrings and the `# Get provider summary data for the specific dataset (default to YYYY)` comment.

### analytics_refactored.py

`calculate_momentum()` has ~18 literal year references across four return branches (success / insufficient_data / no_comparison / error). Update together:

- Docstring: `compare N vs N-1 performance`
- Call sites: `get_provider_scores(..., year=N-1, ...)` + `get_provider_scores(..., year=N, ...)`
- Local variables: `provider_N-1`/`provider_N` and `scores_N-1`/`scores_N`
- Dict keys returned per measure: `score_N-1`/`score_N`
- `latest_year: N` and `prior_year: N-1` in all four return branches

### app.py

`CURRENT_DATA_YEAR = N` constant (near the top of the file).

### dashboard.py

Two `.get()` fallback literals: `.get('latest_year', N)` and `.get('prior_year', N-1)`. Grep catches both.

### validate_etl.py

Extend `TEST_PROVIDERS` with new-year entries, the LCHO count loop, and the multi-year assertion.

### Quick search command

```bash
grep -rn "year.*=.*2025\|year = 2025" *.py
```

This should return zero results after the update is complete.

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
