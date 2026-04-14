# Session Handoff: Replit → Railway Migration

**Date:** April 2026
**Branch:** `migration/railway` (deployed to Railway for testing)
**Status:** Migration complete, deployed, testing in progress

---

## What's Done

### Code Migration (complete)
- [x] Deleted Replit artifacts (.replit, replit.md, screenshots)
- [x] Restructured `attached_assets/` → `data/` (with `source/` and `docs/`)
- [x] Created Dockerfile (python:3.11-slim, non-root user via gosu, health checks)
- [x] Created railway.toml, .dockerignore, .gitignore
- [x] Created config.py with DATA_PATH env var + auto-seed from baked-in DB
- [x] Updated all Python files to use config.py paths
- [x] Applied html.escape() security fix to dashboard.py
- [x] Fixed pyproject.toml metadata
- [x] Added SPDX license identifiers to all main code files
- [x] Added copyright footer: Tom Stephenson (Teev-dev), MIT/CC-BY 4.0
- [x] Fixed Railway volume permissions (entrypoint.sh + gosu)
- [x] Fixed sidebar "double_arrow_right" text rendering glitch

### Documentation (complete)
- [x] Created CLAUDE.md (AI agent constitution)
- [x] Created ADR-004 (Replit → Railway migration decision)
- [x] Created MASTERPLAN.md, DEPLOYMENT.md, MAINTENANCE.md
- [x] Created LICENSE-CODE (MIT) and LICENSE-DOCS (CC-BY 4.0)
- [x] Updated Architecture doc, ADR-001, README
- [x] Added collaboration protocol and setup guides

### Railway Deployment (live, testing)
- [x] Railway project: extraordinary-trust
- [x] Branch: migration/railway (temporary, for testing before merge to main)
- [x] Volume mounted at /data with DATA_PATH=/data
- [x] Public URL: https://insights.housingai.org
- [x] Auto-seed working (config.py copies baked-in DB to volume on first deploy)
- [x] App loads and functions correctly

---

## What's Next

### 1. Verify sidebar fix deployed
Check the public URL — the "double_arrow_right" text at top should be gone.

### 2. Investigate data accuracy reports
**Users have reported inaccuracies in the data the app produces.** This needs investigation in a fresh session. Areas to check:
- `build_analytics_db_v2.py` — ETL pipeline, data ingestion from xlsx
- `data_processor_enhanced.py` — query logic, percentile calculations, peer isolation
- `analytics_refactored.py` — ranking, momentum, priority calculations
- Year defaults (currently 2025) — are queries hitting the right year?
- LCRA/LCHO isolation — are peer comparisons correctly separated?
- Hardcoded `year = 2025` on `data_processor_enhanced.py:461` — potential issue
- Source data integrity — compare raw xlsx values against what the DB returns
- Diagnostic tools available: `python diagnose_duplicates.py`, `python db_view_script.py`, `python review_pvalues.py`

### 3. After testing is confirmed good
- Switch Railway back to `main` branch (Settings > Source)
- Create PR from `migration/railway` → `main`
- Merge
- Railway auto-redeploys from main
- Delete stale branches: `replit-agent`, `security/review-fixes`

---

## Key Context

| Item | Value |
|------|-------|
| Owner | Tom Stephenson (Teev-dev) |
| License | Dual: MIT (code), CC-BY 4.0 (docs/data) |
| Railway project | extraordinary-trust |
| Public URL | insights.housingai.org |
| Volume mount | /data (DATA_PATH=/data) |
| Current branch on Railway | migration/railway |
| Production branch | main (switch back after merge) |

---

## How to Resume

```bash
cd /Users/teev/Software_Projects/hailie-tsm-insights
git checkout migration/railway
```

For data accuracy investigation, tell Claude Code:
"Read HANDOFF.md for context. Users are reporting data inaccuracies in the app. Investigate the ETL pipeline, query logic, and calculations to find the source of the problem."
