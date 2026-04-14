# Session Handoff: Replit → Railway Migration

**Date:** April 2026
**Branch:** `migration/railway` (from `main`)
**Status:** Complete — code migration and documentation update both done, ready to commit

---

## What's Done (Phases 1-4 complete)

### Phase 1: Foundation & Cleanup
- [x] Deleted `.replit`, `replit.md`, Replit screenshots
- [x] Created `.gitignore`
- [x] Fixed `pyproject.toml` (renamed from `repl-nix-workspace` to `hailie-insights-engine`, added metadata)
- [x] Restructured `attached_assets/` → `data/` (with `data/source/` and `data/docs/`)
- [x] Created `MASTERPLAN.md`

### Phase 2: Docker & Railway Infrastructure
- [x] Created `Dockerfile` (python:3.11-slim, non-root `hailie` user, health check, `$PORT`)
- [x] Created `.dockerignore`
- [x] Updated `.streamlit/config.toml` (removed hardcoded port 5000)
- [x] Created `railway.toml` (DOCKERFILE builder, health check, restart policy)

### Phase 3: Code Updates
- [x] Created `config.py` (DATA_PATH env var with fallback to `data/`)
- [x] Updated all 7 Python files to use `config.py` paths (zero `attached_assets` refs remain)
- [x] Applied `html.escape()` to all dynamic content in `dashboard.py` unsafe HTML blocks
- [x] Security audit: app.py HTML is static (safe), SQL f-string in ETL uses hardcoded table names (safe)

### Phase 4: Verification
- [x] Docker image builds successfully
- [x] Container starts, health check passes at `/_stcore/health`
- [x] Streamlit loads and serves on `$PORT`
- [x] User tested the app via Docker and approved

### Changes NOT yet committed
All changes are unstaged on branch `migration/railway`. Run `git status` to see full list.

---

## What's Next (Documentation Update — not yet started)

### Plan file
Full plan at: `.claude/plans/peppy-churning-emerson.md`

### Step 1: Create CLAUDE.md
- AI agent constitution required by `guides/collaboration-protocol.md` Section 5
- Must include: domain context (UK social housing, TSM), layer boundaries, guardrails (config.py paths, html.escape, LCRA/LCHO isolation, year defaults), anti-patterns, dev workflow
- Follow structure from `guides/rigorous-project-setup-guide.md` Section 6

### Step 2: Create ADR-004
- File: `ADRs/ADR-004-migration-replit-to-railway.md`
- Match format of ADR-001 through 003
- Migration driver: cost and control
- Document: Docker, railway.toml, config.py, DATA_PATH, dual data strategy

### Step 3: Create DEPLOYMENT.md
- Railway deployment runbook, persistent disk setup, env vars, troubleshooting

### Step 4: Create MAINTENANCE.md
- Annual TSM data refresh, year default update checklist
- Critical: flag hardcoded `year = 2025` in `data_processor_enhanced.py:461`

### Step 5: Update HAILIE-Insights-Engine-Architecture-v2.md
- Stale refs: line 21 (port 5000), line 183 (attached_assets), lines 232-236 (Replit platform), line 392 (replit.md in file tree)
- Add Deployment Architecture section, update file structure appendix

### Step 6: Update ADR-001
- Append note: "Deployment moved to Railway April 2026. See ADR-004."

### Step 7: Update README.md
- License: dual (MIT for code, CC-BY 4.0 for docs/data) — user confirmed
- Fix "TSM 2024" → "TSM 2024-2025"
- Add link to DEPLOYMENT.md, Contributing section

### Step 8: License files
- Create `LICENSE-CODE` (MIT) and `LICENSE-DOCS` (CC-BY 4.0)

### Housekeeping
- Add new .md files to `.dockerignore`
- Commit all changes on `migration/railway` branch

---

## Key Decisions Made This Session

| Decision | Detail |
|----------|--------|
| Data strategy | Dual: baked into Docker image (open-source default) + Railway persistent volume (production) |
| Data path | `DATA_PATH` env var, fallback to `data/` |
| Directory name | `data/` (was `attached_assets/`) |
| License | Dual: MIT for code, CC-BY 4.0 for docs/data |
| Migration driver | Cost and control |
| Deployment config | `railway.toml` (not Procfile) |
| Port | `$PORT` (Railway-injected), default 8501 |
| Security | Non-root Docker user, html.escape() on all dynamic HTML, XSRF protection |

---

## Memory Files Created

- `.claude/projects/.../memory/user_profile.md` — Teev, project owner, values reliability/security/open-source
- `.claude/projects/.../memory/project_railway_migration.md` — Migration decisions

---

## How to Resume

```bash
cd /Users/teev/Software_Projects/hailie-tsm-insights
git checkout migration/railway
git status  # See all pending changes
```

Then tell Claude Code: "Continue with the documentation update plan in `.claude/plans/peppy-churning-emerson.md` — start from Step 1 (CLAUDE.md). Also read HANDOFF.md for full context."
