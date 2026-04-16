# Session Handoff: Branch Cleanup & Cherry-Picking UI/UX Features

**Date:** April 2026
**Branch:** `main` (all migration work merged)
**Status:** Migration complete and live. Cleanup and feature cherry-pick pending.

---

## Current State

### Live Production
- **URL:** https://insights.housingai.org
- **Platform:** Railway (Docker, python:3.11-slim)
- **Volume:** `/data` (DATA_PATH env var)
- **Cert:** Let's Encrypt (auto-renewed)
- **Source:** `main` branch (auto-deploys on push)

### Recently Merged PRs
| PR | Title | Status |
|----|-------|--------|
| #13 | Migrate from Replit to Railway with Docker containerisation | Merged |
| #14 | Fix LCRA/LCHO dataset mix-up and TP description drift | Merged |
| #15 | Add tsm_measures.py to Dockerfile COPY list | Merged |
| #16 | Harden Docker image (allowlist .dockerignore) + add gitleaks pre-commit | Merged |
| #17 | docs: Update documentation with custom domain URL | Merged |
| #18 | Document pre-commit hook setup in README | Merged |

### Open PRs
| PR | Title | Action Needed |
|----|-------|---------------|
| #12 | Fix critical data bugs, improve UI/UX, add Railway deployment config | Cherry-pick unique features (see Task 2) |

---

## Task 1: Safe Branch Deletions

Run these commands in the cleanup session:

```bash
# Remote branch deletions (all merged, nothing lost)
git push origin --delete migration/railway
git push origin --delete docs/custom-domain-url
git push origin --delete Feature_2025_data

# Replit-agent branch - review first (Replit auto-publishes, likely stale)
# Check: git log origin/replit-agent --not origin/main --oneline
# If all commits are Replit auto-publishes (no unique user work), delete:
git push origin --delete replit-agent

# Local branch cleanup
git branch -D migration/railway
git branch -D fix/data-accuracy-lcra-lcho
git branch -D docs/custom-domain-url
git branch -D security/review-fixes

# Drop stale stash (only adds `import html` — already in main)
git stash drop stash@{0}
```

**Keep these branches:**
- `main` (obviously)
- `feature/ui-ux-improvements` (has open PR #12 with unique features — see Task 2)

---

## Task 2: Cherry-Pick UI/UX Features from PR #12

PR #12 (`feature/ui-ux-improvements` branch, commit `788a079`) contains unique features NOT in main. **The user wants ALL of these — they are positive improvements.**

### Features to Cherry-Pick

1. **Sentry SDK integration**
   - New dependency: `sentry-sdk`
   - Env var gated: `SENTRY_DSN`
   - Add observability for production errors

2. **Dismissible "Recent Updates" changelog toast**
   - Shows on first load for returning users
   - Dismisses on click
   - Tracks which version/date the user has seen

3. **Rename "Raw Data" section → "Score Breakdown"**
   - User-facing UI label change
   - More descriptive, less confusing

4. **Priority formula/threshold fixes**
   - Tooltip-to-code mismatch corrections
   - Ensures tooltips accurately describe the actual calculation logic
   - File: `tooltip_definitions.py` + any priority calc code

5. **Correlation display format**
   - Before: "72.0%"
   - After: "Strong (0.72)"
   - Qualitative label + coefficient, matches statistics conventions

6. **Priority matrix quadrant labels**
   - Fixed labels: "High Priority", "Maintain & Protect", "Lower Impact", "Low Priority"
   - Previously had misleading quadrant names like "Quick Wins"

7. **Dynamic year references**
   - New constant: `CURRENT_DATA_YEAR`
   - Replaces hardcoded "2025" references in user-facing text
   - Simplifies annual updates

8. **Consistent Plotly chart theming**
   - Standardised chart styling across all visualisations
   - Matches app brand colours (#2E5BBA primary)

9. **Remove unused confidence interval checkbox**
   - Dead UI element that did nothing
   - Cleanup for clarity

10. **`validate_etl.py` — data integrity check script**
    - New diagnostic tool (alongside existing `diagnose_duplicates.py`, `db_view_script.py`, `review_pvalues.py`)
    - Validates ETL output before deployment

### Cherry-Pick Strategy (Recommended)

**Option A: One PR per logical group** (recommended for review-ability)
- PR: "Add Sentry observability"
- PR: "UI polish: labels, correlations, quadrants, themes"
- PR: "Add CURRENT_DATA_YEAR constant for dynamic year refs"
- PR: "Add validate_etl.py diagnostic tool"
- PR: "Add dismissible changelog toast"

### Execution Plan

1. **Read PR #12 diff:** `gh pr diff 12` to see full changes
2. **Check each feature against current main** — some may have been partially ported already via PR #14
3. **Create feature branches off main** for each logical group
4. **Apply changes manually** (don't cherry-pick the commit directly — too much conflict potential since main has moved significantly)
5. **Test locally** in Docker before pushing
6. **Open draft PRs** per CLAUDE.md protocol
7. **Close PR #12** with note that features were rescued via new PRs

### Files Likely to Need Edits

- `app.py` — changelog toast, `CURRENT_DATA_YEAR` constant
- `dashboard.py` — "Raw Data" → "Score Breakdown", correlation display, quadrant labels
- `tooltip_definitions.py` — priority formula/threshold fixes
- `styles.py` — Plotly theme consistency
- `pyproject.toml` — `sentry-sdk` dependency
- New file: `validate_etl.py`

### Caution Points

- **Don't just merge PR #12** — it contains old Dockerfile/railway.toml versions that conflict with the migration work
- **Check correlation display code** — current main may already have some of these fixes (from PR #14)
- **Test Sentry integration** with a real DSN before marking PR ready
- **Follow CLAUDE.md guardrails** — draft PRs only, TDD preferred, html.escape() on dynamic UI content

---

## Important Context

### Key Files (Governance)
- `CLAUDE.md` — AI agent constitution, critical guardrails
- `MASTERPLAN.md` — project vision and principles
- `ADRs/ADR-004-migration-replit-to-railway.md` — migration decision record
- `MAINTENANCE.md` — annual update procedures
- `DEPLOYMENT.md` — Railway deployment runbook

### Critical Guardrails (from CLAUDE.md)
- All data access through `data_processor_enhanced.py`
- Analytics in `analytics_refactored.py`, rendering in `dashboard.py`
- Data paths via `config.py` only (no hardcoding)
- `html.escape()` required on all dynamic content in `unsafe_allow_html`
- LCRA vs LCHO peer isolation is non-negotiable
- No PII logging (use provider codes, not names)

### Year Default (Important for Future)
Currently `year=2025` in 10+ places. Next update: November 2026 when new TSM data publishes. Full checklist in `MAINTENANCE.md`.

---

## How to Resume

```bash
cd /Users/teev/Software_Projects/hailie-tsm-insights
git checkout main
git pull origin main
```

Tell Claude Code:
"Read HANDOFF.md for context. Start with Task 1 (safe branch deletions), then proceed with Task 2 (cherry-pick UI/UX features from PR #12). The user wants ALL features from PR #12 — they are positive improvements."
