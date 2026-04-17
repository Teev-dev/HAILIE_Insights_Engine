# Session Handoff: PR #12 Rescue Done, Group G + Follow-ups Pending

**Date:** April 2026
**Branch:** `main` (clean; only remaining PR #12 work is Group G)
**Status:** PR #12 rescue complete — 6/7 cherry-pick PRs merged, PR #12 closed. Group G (dynamic ETL) deferred. Three pre-existing bugs filed as follow-up issues.

---

## Current State

### Live Production
- **URL:** https://insights.housingai.org
- **Platform:** Railway (Docker, python:3.11-slim)
- **Volume:** `/data` (DATA_PATH env var)
- **Cert:** Let's Encrypt (auto-renewed)
- **Source:** `main` branch (auto-deploys on push)

### Recently Merged PRs (PR #12 rescue + supporting changes)
| PR | Title | Notes |
|----|-------|-------|
| #21 | fix(tooltips): align priority formula/thresholds with code | Group A |
| #22 | feat(config): CURRENT_DATA_YEAR constant | Group B; lives in `app.py` |
| #23 | feat(tools): add validate_etl.py ETL spot-check | Group F; excluded from Docker image |
| #24 | feat(obs): env-gated Sentry SDK | Group E; `send_default_pii=False`; no `[streamlit]` extra (doesn't exist in sentry-sdk 2.x) |
| #25 | feat(ui): polish labels, correlation format, quadrants, Plotly theming | Group C |
| #26 | feat(ui): dismissible 'What's new' changelog toast | Group D; copy in plain English for housing domain users |
| #27 | docs(handoff): mid-rescue state | superseded by this update |
| #28 | fix(build): configure setuptools py-modules | unblocks `pip install -e .` |

### Closed without merging
- **#12** (`feature/ui-ux-improvements`) — original PR. Its Dockerfile/railway.toml/data-path versions would have regressed the migration. Unique features rescued via PRs #21–#26. Branch deleted.

### Branch state
Only `main` exists locally and on origin. All rescue branches and worktrees have been cleaned up.

---

## Task 1: Group G — Dynamic ETL Header Detection

**Scope:** Port PR #12's `build_analytics_db_v2.py` refactor (+349 lines) that replaces hardcoded Excel column positions with dynamic header detection. Matters because the Regulator of Social Housing sometimes shifts columns between annual releases — the current hardcoded-position parser is fragile and likely to break on the November 2026 data release.

**Why deferred:** Biggest and riskiest remaining change. The ETL produces the DuckDB that drives the entire app; a subtle porting error would silently corrupt analytics across all providers.

**Approach when ready:**

1. Fresh worktree off latest `main`:
   ```bash
   git worktree add /Users/teev/Software_Projects/hailie-worktrees/group-g-dynamic-etl -b feat/etl-dynamic-headers origin/main
   ```
2. Port `build_analytics_db_v2.py` from the now-closed `feature/ui-ux-improvements` branch (git has it even though the branch is deleted — see `git log --all`). Preserve main's current path/import conventions (`config.py`, `tsm_measures.py`).
3. **End-to-end ETL run required before marking ready:**
   ```bash
   python3 build_analytics_db_v2.py
   python3 validate_etl.py    # all 6 checks must pass
   ```
4. **Diff the new DuckDB against the current production one** to confirm no regressions in provider scores, percentiles, correlations. Spot-check at least 5 providers (including 1 LCHO, 1 COMBINED) against the source Excel files by hand.
5. Open draft PR only after steps 3 and 4 pass.

---

## Task 2: Follow-up issues (filed 2026-04-17)

Three pre-existing bugs found during the rescue — none introduced by rescue PRs, all in main pre-rescue:

- **[#29](https://github.com/Teev-dev/HAILIE_Insights_Engine/issues/29)** `bug` `good first issue` — `dashboard.py:859` subscripts `priority['measure_name']` but `identify_priority` returns `priority_description`. Latent `KeyError`. One-line fix.
- **[#30](https://github.com/Teev-dev/HAILIE_Insights_Engine/issues/30)** `bug` — `analytics_refactored.py:265` calls `data_processor.get_percentile_for_score(...)`, which doesn't exist. Fallback branch; recommend removing in favour of an ETL-integrity check (validate_etl.py check 5 already enforces this).
- **[#31](https://github.com/Teev-dev/HAILIE_Insights_Engine/issues/31)** `enhancement` `good first issue` — `dashboard.py` momentum labels are still effectively hardcoded `2025 vs 2024`. Infrastructure from PR #25 is in place; need `data_processor.get_provider_years` + `CURRENT_DATA_YEAR` moved to `config.py`.

Priority: **#29 first** (simple one-liner, prevents a real crash if hit). Then #30 (correctness). Then #31 (enhancement; ship before November 2026 TSM data release so annual update is lower-touch).

---

## Important Context

### Key Files (Governance)
- `CLAUDE.md` — AI agent constitution, critical guardrails
- `MASTERPLAN.md` — project vision and principles
- `ADRs/ADR-004-migration-replit-to-railway.md` — migration decision record
- `MAINTENANCE.md` — annual update procedures
- `DEPLOYMENT.md` — Railway deployment runbook
- `guides/collaboration-protocol.md` §5 — AI autonomous session protocol (worktree isolation, draft PRs, DCO)

### Critical Guardrails (from CLAUDE.md)
- All data access through `data_processor_enhanced.py`
- Analytics in `analytics_refactored.py`, rendering in `dashboard.py`
- Data paths via `config.py` only (no hardcoding)
- `html.escape()` required on all dynamic content in `unsafe_allow_html`
- LCRA vs LCHO peer isolation is non-negotiable — always pass `dataset_type` explicitly
- No PII logging (use provider codes, not names)

### Year Default
`year=2025` is still the default in ~10 query-layer places (see MAINTENANCE.md). PR #22 added `CURRENT_DATA_YEAR` only for user-facing text. Query-layer defaults remain maintained manually. Next annual update: November 2026.

### Local dev environment
- Python 3.11 required. `.venv` must be created with `python3.11 -m venv .venv`.
- Core deps: `pip install duckdb streamlit pandas plotly scipy numpy openpyxl 'sentry-sdk>=2.0.0' pre-commit`
- Since PR #28, `pip install -e .` also works.
- Pre-commit hooks require `pre-commit install` once per clone.

---

## How to Resume

```bash
cd /Users/teev/Software_Projects/hailie-tsm-insights
git checkout main
git pull origin main
gh issue list --label bug
```

Tell Claude Code:
*"Read HANDOFF.md. Pick up either Group G (dynamic ETL, Task 1) or one of the follow-up issues (#29, #30, #31 in Task 2) — whichever I indicate."*

Recommend starting with **#29** if you want a quick win — it's a 5-minute fix that resolves a real crash risk. Group G is a half-day at minimum with careful verification.
