# CLAUDE.md

## Project Overview

HAILIE Insights Engine is a Streamlit web application that transforms UK government TSM (Tenant Satisfaction Measures) data into executive-level insights for social housing providers. It delivers three answers: your rank among peers, your momentum over time, and your single highest-priority improvement area.

**Tech stack:** Python 3.11, Streamlit, DuckDB, Pandas, SciPy, Plotly
**Deployment:** Docker on Railway (`$PORT` env var, `DATA_PATH` for persistent volumes)
**Data:** Public UK Government TSM datasets (annual, no PII)

## Domain Context (UK Social Housing)

This is not generic analytics software. Understand these domain facts before making changes:

- **TSM data** is published annually by the Regulator of Social Housing. It measures tenant satisfaction across 12 standardised measures (TP01-TP12).
- **Two provider types exist:**
  - **LCRA** (Low Cost Rental Accommodation) — 355 providers, all 12 measures
  - **LCHO** (Low Cost Home Ownership) — 56 providers, TP01 + TP05-TP12 only (TP02-TP04 repairs measures do not apply)
- **Peer comparisons must be isolated by type.** Never mix LCRA and LCHO providers in rankings or percentiles.
- **Providers use these insights for board reporting and regulatory compliance.** Accuracy is not optional.
- **The data is public.** No personal data is collected, stored, or processed. However, treat provider performance data with care — it informs real organisational decisions.

## Repository Structure

```
├── app.py                       # Streamlit entry point
├── dashboard.py                 # Executive dashboard rendering (presentation only)
├── analytics_refactored.py      # Analytics engine (business logic)
├── data_processor_enhanced.py   # DuckDB data access layer (all database queries)
├── config.py                    # Data path resolution (DATA_PATH env var)
├── styles.py                    # CSS styling and theme
├── tooltip_definitions.py       # UI help text definitions
├── mobile_utils.py              # Responsive layout detection and utilities
├── build_analytics_db_v2.py     # ETL pipeline (offline, development only)
├── data/
│   ├── hailie_analytics_v2.duckdb  # Pre-built analytics database (runtime)
│   └── source/                     # Source .xlsx files (not in Docker image)
├── config.py                    # DATA_PATH env var resolution
├── Dockerfile                   # Container build (python:3.11-slim, non-root)
├── railway.toml                 # Railway deployment config
├── MASTERPLAN.md                # Project vision and principles
├── ADRs/                        # Architecture Decision Records
└── guides/                      # Collaboration protocol, setup guide
```

## Layer Boundaries

| Adding...                | Put in...                    | Not in...                         |
|--------------------------|------------------------------|-----------------------------------|
| Database query           | `data_processor_enhanced.py` | `dashboard.py`, `app.py`          |
| Analytics / business logic | `analytics_refactored.py`  | `dashboard.py`, `data_processor_enhanced.py` |
| Dashboard rendering / HTML | `dashboard.py`             | `analytics_refactored.py`         |
| Data path resolution     | `config.py`                  | Hardcoded strings anywhere        |
| CSS / styling            | `styles.py`                  | Inline in `dashboard.py`          |
| UI help text             | `tooltip_definitions.py`     | Inline in `dashboard.py`          |

## Critical Guardrails

### Data paths — CRITICAL

Always use `config.py`. Never hardcode paths.

```python
# WRONG
conn = duckdb.connect("data/hailie_analytics_v2.duckdb")

# RIGHT
from config import DB_PATH
conn = duckdb.connect(DB_PATH)
```

### HTML escaping — CRITICAL

All dynamic content rendered via `unsafe_allow_html=True` must be escaped with `html.escape()`.

```python
# WRONG
st.markdown(f"<span>{measure_desc}</span>", unsafe_allow_html=True)

# RIGHT
st.markdown(f"<span>{html.escape(measure_desc)}</span>", unsafe_allow_html=True)
```

### LCRA vs LCHO isolation — CRITICAL

Never mix provider types in peer comparisons. All ranking and percentile methods take `dataset_type` — always pass it.

```python
# WRONG — compares rental providers against home ownership providers
percentiles = processor.get_provider_percentiles(code, year=2025)

# RIGHT — isolated within provider's own peer group
dataset_type = processor.get_provider_dataset_type(code)
percentiles = processor.get_provider_percentiles(code, year=2025)
# dataset_type is determined automatically and used for peer isolation
```

### No PII logging — CRITICAL

The dataset is public, but never log in ways that could be confused with personal data. Use provider codes, not names.

```python
# WRONG
logger.info(f"Loading data for {provider_name}")

# RIGHT
logger.info(f"Loading data for provider {provider_code}")
```

### Year defaults — IMPORTANT

All query methods in `data_processor_enhanced.py` default to `year=2025`. These must be updated when new TSM data is ingested:

- `get_provider_percentiles` (line 123)
- `get_dataset_correlations` (line 156)
- `get_provider_scores` (line 245)
- `get_peer_comparison_data` (line 271)
- `get_dataset_summary_stats` (line 310)
- `get_measure_distribution` (line 341)
- `get_all_providers_with_scores` (line 370)
- `get_measure_statistics` (line 495)
- **Hardcoded SQL** on line 461: `WHERE ... year = 2025` (not a default parameter — must be edited directly)
- `analytics_refactored.py` line 129: `year=2025` in momentum calculation

See `MAINTENANCE.md` for the full annual update procedure.

## Anti-Patterns

| Anti-Pattern | Why It's Wrong | Do This Instead |
|---|---|---|
| Querying DuckDB from `dashboard.py` | Breaks layer separation | Call `data_processor_enhanced.py` |
| Hardcoding `"data/"` in Python files | Breaks Railway persistent volume override | Import from `config.py` |
| Comparing LCRA and LCHO providers | Statistically invalid (different measures available) | Filter by `dataset_type` first |
| Rendering dynamic strings in `unsafe_allow_html` without `html.escape()` | XSS vulnerability | Always escape dynamic content |
| Putting analytics logic in `data_processor_enhanced.py` | Conflates data access and business logic | Keep analytics in `analytics_refactored.py` |
| Adding `port` to `.streamlit/config.toml` | Breaks Railway's `$PORT` injection | Port is set via Dockerfile CMD only |
| Running ETL scripts in production | They rebuild the database from scratch | ETL is offline/development only |

## Edge Cases

- **LCHO missing TP02-04:** Any code iterating TP01-TP12 must handle missing measures for LCHO providers. Check `dataset_type` before assuming all 12 measures exist.
- **Momentum placeholder:** Momentum is fully implemented for 2024→2025 comparison. If only one year of data exists for a provider, momentum returns `disabled: True`.
- **Combined providers:** Some providers appear in both LCRA and LCHO datasets. The system handles this by comparing them within each dataset separately.

## Development Workflow

1. Branch from `main` for all changes
2. Write tests before implementation (TDD preferred)
3. Run locally: `streamlit run app.py`
4. Test Docker build: `docker build -t hailie-insights . && docker run -p 8501:8501 -e PORT=8501 hailie-insights`
5. Open draft PRs for all changes — no direct commits to `main`
6. Architectural changes require an ADR (see `ADRs/` for format)

## Autonomous Session Protocol

When working without real-time human supervision:

1. **Plan** — State what you will change and why, referencing this file
2. **Isolate** — Work in a feature branch or git worktree, never on `main`
3. **Test** — Verify changes work (run the app, check Docker build)
4. **PR** — Open a draft PR with clear description
5. **Handoff** — Document what was done and what remains
6. **Clean up** — Update task status, remove temporary files

## What AI Agents Must Never Do

| Action | Why | Instead |
|--------|-----|---------|
| Edit governance docs (MASTERPLAN.md, ADRs, this file) | Require human consensus | Create handoff plan |
| Deploy to production | Requires human verification | Document in handoff plan |
| Skip tests or hooks | Undermines quality guarantees | Fix the underlying issue |
| Guess at domain logic | Housing rules have regulatory implications | Flag for domain review |
| Commit to `main` | Bypasses review process | Use feature branch + draft PR |

## References

- `MASTERPLAN.md` — Project vision and principles
- `HAILIE-Insights-Engine-Architecture-v2.md` — Full technical architecture
- `ADRs/` — All architectural decisions
- `DEPLOYMENT.md` — Railway deployment runbook
- `MAINTENANCE.md` — Annual update procedures
- `guides/collaboration-protocol.md` — How to contribute
