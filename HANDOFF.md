# Session Handoff: PR #12 Cherry-Pick In Review, Group G Pending

**Date:** April 2026
**Branch:** `main` (clean; 6 draft feature branches open for review)
**Status:** 6 of 7 rescue PRs open as drafts, awaiting manual browser verification and merge. Group G (dynamic ETL) deferred.

---

## Current State

### Live Production
- **URL:** https://insights.housingai.org
- **Platform:** Railway (Docker, python:3.11-slim)
- **Volume:** `/data` (DATA_PATH env var)
- **Cert:** Let's Encrypt (auto-renewed)
- **Source:** `main` branch (auto-deploys on push)

### Recently Merged PRs (chronological)
| PR | Title | Status |
|----|-------|--------|
| #13 | Migrate from Replit to Railway with Docker containerisation | Merged |
| #14 | Fix LCRA/LCHO dataset mix-up and TP description drift | Merged |
| #15 | Add tsm_measures.py to Dockerfile COPY list | Merged |
| #16 | Harden Docker image (allowlist .dockerignore) + add gitleaks pre-commit | Merged |
| #17 | Update documentation with custom domain URL | Merged |
| #18 | Document pre-commit hook setup in README | Merged |
| #19 | Update HANDOFF for branch cleanup and PR #12 cherry-pick | Merged |

### Open draft PRs — PR #12 cherry-pick rescue
Review in this order (small → big, dependencies last):

| PR | Title | Size | Merge notes |
|----|-------|------|-------------|
| [#21](https://github.com/Teev-dev/HAILIE_Insights_Engine/pull/21) | fix(tooltips): align priority formula/thresholds with code | +6/-6 | Fixes a real accuracy bug — tooltip described thresholds (>60) and formula that no longer matched code (>70). Safe to merge first. |
| [#22](https://github.com/Teev-dev/HAILIE_Insights_Engine/pull/22) | feat(config): CURRENT_DATA_YEAR constant | +9/-4 | Adds single module-level constant in `app.py` for user-facing year labels. Fixes a bug in PR #12's own diff (missing f-string prefix). |
| [#23](https://github.com/Teev-dev/HAILIE_Insights_Engine/pull/23) | feat(tools): add validate_etl.py ETL spot-check | +168 | New diagnostic script. Excluded from Docker image (dev/CI tool, not runtime). Uses `config.DB_PATH`. |
| [#24](https://github.com/Teev-dev/HAILIE_Insights_Engine/pull/24) | feat(obs): env-gated Sentry SDK | +14 | No-op unless `SENTRY_DSN` is set. Added `send_default_pii=False` as hardening beyond PR #12's version. |
| [#25](https://github.com/Teev-dev/HAILIE_Insights_Engine/pull/25) | feat(ui): polish labels, correlation format, quadrants, Plotly theming | +78/-35 | Biggest change. "Raw Data" → "Score Breakdown"; correlation shown as "Strong (0.72)"; Quick Wins → Maintain & Protect; consistent Plotly theme; momentum dict now carries `latest_year`/`prior_year`. `html.escape()` preserved throughout. |
| [#26](https://github.com/Teev-dev/HAILIE_Insights_Engine/pull/26) | feat(ui): dismissible changelog toast | +18 | Merge last — toast copy announces changes from #21 and #25. Leads with the open-source/licensing bullet for housing orgs evaluating adoption. |

### Still open
| PR | Title | Action |
|----|-------|--------|
| #12 | Fix critical data bugs, improve UI/UX, add Railway deployment config | Close after #21–#26 (and future Group G) are all merged, with a note linking to the rescue PRs. |

### Deferred
- **Group G — dynamic Excel header detection in `build_analytics_db_v2.py`** (349-line refactor). Replaces fragile hardcoded column positions with dynamic header detection. Biggest and riskiest remaining cherry-pick. Deferred until #21–#26 merge so it lands against a clean base. See "Task 3" below.

---

## Task 1: Browser-verify each draft PR ⚠️

All 6 draft PRs are code-reviewed, DCO-signed, and pre-commit-checked, but **none have been run in a browser**. Each has its own worktree already set up, so reviewing is just `cd` and `streamlit run`:

```bash
# One-time per session — make sure deps are installed in the shared venv:
source /Users/teev/Software_Projects/hailie-tsm-insights/.venv/bin/activate
pip install -e /Users/teev/Software_Projects/hailie-tsm-insights

# Then for each PR, cd into its worktree and run:
cd /Users/teev/Software_Projects/hailie-worktrees/group-a-tooltips       # PR #21
streamlit run app.py
# Browser opens http://localhost:8501 — verify per checklist below, then Ctrl-C.

cd /Users/teev/Software_Projects/hailie-worktrees/group-b-data-year      # PR #22
streamlit run app.py
# ...etc for group-f-validate-etl, group-e-sentry, group-c-ui-polish, group-d-changelog
```

### Per-PR verification checklist

- **#21:** Select any provider → open "How Priority Works" expander → confirm thresholds show `>70 / 50-70 / 30-50 / <30` and formula shows `(Improvement Potential × 0.6) + (Correlation Strength × 100 × 0.4)`. Open momentum expander → confirm note reflects 2024→2025 comparison.
- **#22:** Confirm sidebar "Enhanced Analytics Engine" info block shows `Data source: 2025 TSM Dataset` (NOT the literal string `{CURRENT_DATA_YEAR}`). Footer shows `Data: 2025 TSM`.
- **#23:** `python3 validate_etl.py` against a built `data/hailie_analytics_v2.duckdb` — all 6 checks should pass, exit 0. Also `docker build -t hailie-insights . && docker run --rm hailie-insights find /app -name validate_etl.py` should return nothing (script must stay out of image).
- **#24:** Start with `SENTRY_DSN` unset → no Sentry output in console. Set `SENTRY_DSN=<test dsn>` and raise a test exception → event should reach Sentry.
- **#25:** Priority card shows `"Strong (0.72)"` format; Priority Matrix quadrants show `Maintain & Protect` / `Lower Impact`; matrix y-axis reads `Relationship with Overall Satisfaction`; sidebar expander reads `📋 Score Breakdown`.
- **#26:** Load a provider → blue "What's new" info box appears. Dismiss → disappears for session. Read aloud as if you were a housing officer — does every line make sense?

---

## Task 2: Merge order

After each PR passes browser verification:

```
#21 → #22 → #23 → #24 → #25 → #26
```

Rationale:
- #21 and #22 are tiny and independent — land first.
- #23 and #24 are pure additions, no dashboard impact.
- #25 is the biggest UI change — review carefully.
- #26 (toast) references #21 and #25 content, so it must merge last or the toast announces changes that aren't live.

After each merge, clean up the worktree:
```bash
git worktree remove /Users/teev/Software_Projects/hailie-worktrees/<slug>
```
Worktree slugs: `group-a-tooltips`, `group-b-data-year`, `group-c-ui-polish`, `group-d-changelog`, `group-e-sentry`, `group-f-validate-etl`.

---

## Task 3: Group G — Dynamic ETL Header Detection (deferred)

**Scope:** Port PR #12's `build_analytics_db_v2.py` refactor (+349/-0 lines) that replaces hardcoded Excel column positions with dynamic header detection. Matters because the Regulator of Social Housing sometimes shifts columns between annual releases — the current hardcoded-position parser is fragile.

**Why deferred:** Biggest and riskiest remaining change. The ETL produces the DuckDB that drives the entire app; a subtle porting error would silently corrupt analytics.

**Approach when ready:**
1. Fresh worktree off latest `main` (post #21–#26 merges):
   ```bash
   git worktree add /Users/teev/Software_Projects/hailie-worktrees/group-g-dynamic-etl -b feat/etl-dynamic-headers origin/main
   ```
2. Port `build_analytics_db_v2.py` from `origin/feature/ui-ux-improvements` (the PR #12 branch), preserving main's current path/import conventions (`config.py`, `tsm_measures.py`).
3. **End-to-end ETL run required before marking ready:**
   ```bash
   python3 build_analytics_db_v2.py
   python3 validate_etl.py    # all 6 checks must pass
   ```
4. **Diff the new DuckDB against the current production one** to confirm no regressions in provider scores, percentiles, correlations. Spot-check at least 5 providers (including 1 LCHO, 1 COMBINED) against the source Excel files by hand.
5. Draft PR only after steps 3 and 4 pass.

---

## Task 4: Pre-existing issues found during cherry-pick (follow-ups)

Not introduced by any rescue PR — noticed during the port but out of scope to fix:

1. **`dashboard.py:859` KeyError risk** — `f"1. **Focus on {priority['measure_name']}** - ..."` directly subscripts `measure_name`, but `identify_priority` in `analytics_refactored.py:310+` returns `priority_description` (no `measure_name` key). Would throw if it ever fires.
2. **`analytics_refactored.py:265` nonexistent method** — `self.data_processor.get_percentile_for_score(tp_measure, score)` is called in a fallback branch. Method doesn't exist in `data_processor_enhanced.py`. Only fires if a provider has scores for a measure with no pre-calculated percentile, but would `AttributeError` when it does.
3. **5 hardcoded "2025 vs 2024" momentum labels in `dashboard.py`** use the `.get('latest_year', 2025)` fallback introduced by #25. Infrastructure is in place; wiring to actual data years is a follow-up.

Recommend filing each as a GitHub issue labelled `bug` or `good-first-issue` so they don't get lost.

---

## Task 5: Close PR #12

After #21–#26 and Group G all merge:
1. Comment on PR #12 linking each rescue PR.
2. Close without merging (its Dockerfile/railway.toml versions are stale and would regress the migration).
3. `git push origin --delete feature/ui-ux-improvements`.

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
- LCRA vs LCHO peer isolation is non-negotiable
- No PII logging (use provider codes, not names)

### Year Default
`year=2025` is still the default in 10+ query-layer places. #22 added `CURRENT_DATA_YEAR` only for user-facing text. Query-layer defaults remain maintained via `MAINTENANCE.md` for the annual update (next: November 2026 when new TSM data publishes).

---

## How to Resume

```bash
cd /Users/teev/Software_Projects/hailie-tsm-insights
git checkout main
git pull origin main
gh pr list --state open
```

Tell Claude Code:
*"Read HANDOFF.md. Pick up from wherever we are: if #21–#26 still open, help with browser verification and review feedback. If merged, start Group G per Task 3."*
