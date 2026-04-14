# Architecture Decision Record: Migration from Replit to Railway

**ADR Number:** 004
**Date:** April 2026
**Status:** Implemented
**Authors:** TS

## Title

Migration of Deployment Platform from Replit to Railway with Docker Containerisation

## Context

HAILIE Insights Engine was initially deployed on Replit (see ADR-001), which served well during prototyping and early development. As the project matured toward production use and open-source release, several limitations became apparent:

- **Cost escalation:** Replit's pricing model became increasingly expensive relative to the value provided for a single-application deployment.
- **Limited infrastructure control:** Replit abstracts away container configuration, port management, health checks, and persistent storage — making it difficult to implement production-grade reliability patterns.
- **Platform lock-in:** Replit-specific files (`.replit`, `replit.md`, Nix module configurations) created dependencies that complicated portability and open-source contribution.
- **Data persistence:** Replit's storage model did not cleanly support separating the application from its data, which is important for both production reliability and the open-source distribution model.

The project needed a deployment platform that offered full infrastructure control at predictable cost, while maintaining simplicity for a solo maintainer.

## Decision

Migrate from Replit to Railway with Docker containerisation, implementing a dual data strategy:

1. **Docker containerisation** using `python:3.11-slim` base image with a non-root user (`hailie`)
2. **Railway as deployment platform** with `railway.toml` configuration
3. **Dynamic port binding** via Railway's injected `$PORT` environment variable (default 8501)
4. **`DATA_PATH` environment variable** for configurable data directory, enabling persistent volume support
5. **Dual data strategy:**
   - Open-source default: DuckDB database baked into the Docker image (works out of the box)
   - Production override: `DATA_PATH` points to a Railway persistent volume (data survives container restarts)
6. **Health checks** on Streamlit's built-in `/_stcore/health` endpoint
7. **Restart policy** of `ON_FAILURE` with 3 maximum retries

## Rationale

### 1. Cost and Control
Railway provides predictable, usage-based pricing with full control over the deployment pipeline. Docker gives reproducible builds that work identically in local development and production, eliminating platform-specific behaviour.

### 2. Production Readiness
Health checks, restart policies, and non-root containers are standard production patterns that Replit did not support natively. These patterns improve reliability without adding operational complexity.

### 3. Open-Source Friendliness
The dual data strategy means anyone can `docker build && docker run` and immediately have a working application with real TSM data — no external database setup required. Production deployments override `DATA_PATH` to use persistent storage, keeping the database independent of the container lifecycle.

### 4. Elimination of Platform Lock-in
Removing Replit-specific files (`.replit`, `replit.md`, Nix configurations) and replacing them with standard Docker and Railway configuration means the application can be deployed to any Docker-compatible platform with minimal changes.

### 5. Data Directory Standardisation
Renaming `attached_assets/` (a Replit convention) to `data/` with clear subdirectories (`data/source/` for raw Excel files, `data/docs/` for reference PDFs) improves clarity and follows standard project conventions.

## Alternatives Considered

### Alternative 1: Remain on Replit

**Approach:** Continue using Replit with its built-in deployment and storage.

**Pros:**
- Zero migration effort
- Familiar workflow

**Cons:**
- Increasing cost with limited pricing control
- No Docker support for reproducible builds
- Platform-specific lock-in (.replit, Nix modules)
- Limited health check and restart policy options
- Persistent storage not cleanly separable from application

**Verdict:** ❌ Rejected — cost and control limitations were the primary drivers for migration.

### Alternative 2: Fly.io

**Approach:** Deploy Docker containers on Fly.io's edge infrastructure.

**Pros:**
- Docker-native deployment
- Global edge deployment for low latency
- Persistent volumes supported

**Cons:**
- More complex persistent storage configuration
- Less straightforward pricing model
- Global distribution unnecessary for a UK-focused application

**Verdict:** ❌ Rejected — Railway is simpler for single-region deployment, which is all this application needs.

### Alternative 3: Self-Hosted VPS (e.g., Hetzner, DigitalOcean)

**Approach:** Run Docker on a managed VPS with manual infrastructure management.

**Pros:**
- Maximum control over infrastructure
- Lowest ongoing cost
- No platform dependency

**Cons:**
- Significant operational overhead (OS updates, TLS certificates, monitoring, backups)
- Single point of failure without additional infrastructure
- Too much maintenance burden for a solo maintainer

**Verdict:** ❌ Rejected — operational overhead outweighs cost savings for a solo-maintained project.

## Consequences

### Positive Consequences
✅ Full control over infrastructure, deployment pipeline, and container configuration
✅ Reproducible builds via Docker — works identically locally and on Railway
✅ Health checks and restart policies improve production reliability
✅ Non-root container user reduces security attack surface
✅ Open-source users can run the application with `docker build && docker run` — zero external setup
✅ `DATA_PATH` env var enables clean separation of application and data in production
✅ All Replit-specific lock-in eliminated

### Negative Consequences
❌ Railway has a learning curve for contributors unfamiliar with the platform
❌ Persistent volume setup is an extra configuration step vs Replit's built-in storage
❌ Docker image includes the full DuckDB database (~8MB), increasing image size

### Neutral Consequences
➖ Port changed from hardcoded 5000 to dynamic `$PORT` (defaulting to 8501)
➖ Data directory renamed from `attached_assets/` to `data/`
➖ All Python files updated to use `config.py` for path resolution
➖ `.streamlit/config.toml` no longer specifies port (handled by Dockerfile CMD)

## Implementation Details

### Files Created
- `Dockerfile` — python:3.11-slim, non-root `hailie` user, layer-cached pip install, health check, `$PORT` binding
- `railway.toml` — DOCKERFILE builder, health check on `/_stcore/health`, ON_FAILURE restart with 3 retries
- `config.py` — `DATA_DIR = os.environ.get("DATA_PATH", ...)` with `DB_PATH` and `SOURCE_DIR` exports
- `.dockerignore` — excludes source data, documentation, development tools, ADRs from image
- `.gitignore` — Python artifacts, env files, DuckDB WAL, OS files, IDE files

### Files Deleted
- `.replit` — Nix configuration, workflows, port binding
- `replit.md` — Replit agent context documentation
- Replit-named screenshots (picard.replit.dev filenames)

### Files Modified
- All 7 Python files with hardcoded `attached_assets/` paths updated to use `config.py`
- `.streamlit/config.toml` — removed hardcoded port 5000 and browser server address
- `pyproject.toml` — renamed from `repl-nix-workspace` to `hailie-insights-engine`, added metadata
- `dashboard.py` — added `html.escape()` to all dynamic content in unsafe HTML blocks

### Directory Restructure
```
attached_assets/           →  data/
  hailie_analytics_v2.duckdb    data/hailie_analytics_v2.duckdb
  hailie_analytics.duckdb       data/hailie_analytics.duckdb
  *.xlsx                        data/source/*.xlsx
  *.pdf                         data/docs/*.pdf
```

### Migration Path
1. Delete Replit artifacts
2. Create `.gitignore`, fix `pyproject.toml`
3. Restructure `attached_assets/` → `data/`
4. Create Docker and Railway infrastructure
5. Create `config.py` and update all path references
6. Apply security fixes (`html.escape()`)
7. Docker build and test verification

## Validation

- ✅ Docker image builds successfully from `python:3.11-slim`
- ✅ Container starts and serves Streamlit on `$PORT`
- ✅ Health check responds 200 at `/_stcore/health`
- ✅ `DATA_PATH` override correctly resolves to external directory
- ✅ Without `DATA_PATH`, baked-in database loads correctly
- ✅ All existing functionality preserved (provider selection, dashboard rendering, LCRA/LCHO detection)
- ✅ Zero references to `attached_assets` remain in Python code
- ✅ User acceptance testing completed via Docker

## References

- ADR-001: Pivot to Streamlit/DuckDB (original Replit deployment decision)
- `Dockerfile`, `railway.toml`, `config.py` in repository root
- `DEPLOYMENT.md` for step-by-step Railway deployment guide
