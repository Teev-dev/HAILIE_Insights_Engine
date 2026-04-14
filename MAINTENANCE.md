# Maintenance Guide

## Annual TSM Data Refresh

### When

The UK Government publishes new TSM data annually, typically around November. Monitor the [Regulator of Social Housing](https://www.gov.uk/government/organisations/regulator-of-social-housing) for publication dates.

### Procedure

1. **Download** the new TSM Excel file from the government source
2. **Place** it in `data/source/`
3. **Run ETL:**
   ```bash
   python build_analytics_db_v2.py --file data/source/NEW_FILE.xlsx --year YYYY
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

When ingesting a new year of data (e.g., 2026 data arriving November 2026), update all year defaults from `2025` to `2026`:

### data_processor_enhanced.py

| Line | Method | Change |
|------|--------|--------|
| 123  | `get_provider_percentiles` | `year: int = 2025` → `year: int = 2026` |
| 156  | `get_dataset_correlations` | `year: int = 2025` → `year: int = 2026` |
| 245  | `get_provider_scores` | `year: int = 2025` → `year: int = 2026` |
| 271  | `get_peer_comparison_data` | `year: int = 2025` → `year: int = 2026` |
| 310  | `get_dataset_summary_stats` | `year: int = 2025` → `year: int = 2026` |
| 341  | `get_measure_distribution` | `year: int = 2025` → `year: int = 2026` |
| 370  | `get_all_providers_with_scores` | `year: int = 2025` → `year: int = 2026` |
| 461  | `get_provider_dataset_type` (SQL) | `year = 2025` → `year = 2026` (hardcoded in SQL string, not a parameter default) |
| 495  | `get_measure_statistics` | `year: int = 2025` → `year: int = 2026` |

### analytics_refactored.py

| Line | Context | Change |
|------|---------|--------|
| 129  | Momentum calculation | `year=2025` → `year=2026` |

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
python build_analytics_db_v2.py --file data/source/2024_TSM_Full_Data_v1.1_FINAL_1756577982265.xlsx --year 2024
python build_analytics_db_v2.py --file data/source/2025_TSM_Full_Data_v1.0_FINAL.xlsx --year 2025
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
