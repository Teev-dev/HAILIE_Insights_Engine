# Deployment Guide

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed locally (for testing)
- [Railway](https://railway.app) account (for production deployment)
- GitHub repository connected to Railway

## Local Development

```bash
git clone https://github.com/Teev-dev/HAILIE_Insights_Engine.git
cd HAILIE_Insights_Engine
pip install .
streamlit run app.py
```

Opens at http://localhost:8501.

## Local Docker Testing

```bash
docker build -t hailie-insights .
docker run -p 8501:8501 -e PORT=8501 hailie-insights
```

Opens at http://localhost:8501. This runs the same container that Railway will deploy.

## Railway Deployment (5-Minute Setup)

1. Create a new project in the [Railway dashboard](https://railway.app/dashboard)
2. Select "Deploy from GitHub repo" and connect this repository
3. Railway auto-detects the `Dockerfile` and `railway.toml`
4. Click Deploy — the app starts automatically on Railway's injected `$PORT`
5. Railway provides a public URL (e.g., `https://your-app.up.railway.app`)

No environment variables are required for a basic deployment. The baked-in database works immediately.

## Environment Variables

| Variable    | Required | Default           | Description                                      |
|-------------|----------|-------------------|--------------------------------------------------|
| `PORT`      | Auto     | `8501`            | Injected by Railway automatically. Do not set manually. |
| `DATA_PATH` | No       | `./data` (in image) | Path to directory containing `hailie_analytics_v2.duckdb`. Set this to use a persistent volume. |

## Persistent Disk Setup (Production)

For production deployments, use a Railway persistent volume so the database survives container restarts and redeployments:

1. In Railway dashboard, go to your service settings
2. Click **Volumes** and add a new volume
3. Set the mount path (e.g., `/data`)
4. Add environment variable: `DATA_PATH=/data`
5. On first deploy, the baked-in database is used. To use the volume:
   - SSH into the container or use Railway CLI
   - Copy the database: `cp /app/data/hailie_analytics_v2.duckdb /data/`
6. Subsequent deploys use the volume data, not the baked-in copy

Without `DATA_PATH`, the application uses the database baked into the Docker image. This is fine for demos, testing, and open-source users, but data will reset on each deployment.

## Updating TSM Data

When new government TSM data is published (typically November each year):

1. Download the new TSM Excel file from the government source
2. Place it in `data/source/` locally
3. Run the ETL pipeline:
   ```bash
   python build_analytics_db_v2.py --file data/source/NEW_FILE.xlsx --year YYYY
   ```
4. Verify the data:
   ```bash
   python db_view_script.py
   ```
5. Deploy the updated database:
   - **If using persistent volume:** Copy `data/hailie_analytics_v2.duckdb` to the Railway volume
   - **If using baked-in:** Commit the updated `.duckdb` file and redeploy (Railway rebuilds the Docker image)
6. Update year defaults in code — see `MAINTENANCE.md` for the full checklist

## Health Check

- **Endpoint:** `/_stcore/health` (Streamlit built-in)
- **Railway config:** `railway.toml` sets `healthcheckPath = "/_stcore/health"` with 10s timeout
- **Docker config:** `HEALTHCHECK` in Dockerfile runs every 30s, 3 retries before marking unhealthy
- **Restart policy:** `ON_FAILURE` with 3 maximum retries (configured in `railway.toml`)

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Container exits immediately | `PORT` not set or port conflict | Railway injects `PORT` automatically. For local Docker, pass `-e PORT=8501` |
| "Database not found" error | `DATA_PATH` points to empty directory | Copy database to the volume mount path, or unset `DATA_PATH` to use baked-in data |
| Health check failing | App still starting up | Increase `--start-period` in Dockerfile HEALTHCHECK (currently 5s) |
| Stale data after redeploy | Using baked-in database, not volume | Set `DATA_PATH` to volume mount path and copy database there |
| Provider dropdown is empty | Database file is corrupted or wrong version | Rebuild with `python build_analytics_db_v2.py` |
| Port 5000 references in logs | Old `.streamlit/config.toml` cached | Delete `.streamlit/` cache in container and redeploy |

## Architecture Reference

See `ADRs/ADR-004-migration-replit-to-railway.md` for the full decision record on this deployment architecture.

## Security & Availability

### Internal exceptions are never shown to users

The runtime app (`app.py`, `dashboard.py`, `data_processor_enhanced.py`) follows a strict rule: raw exception messages, stack traces, and internal file paths never reach the browser. User-facing errors are short, generic, and actionable (e.g. "Database is unavailable. Please contact support.", "Try another provider or refresh.").

Diagnostic details are routed through a private `_report_internal_error()` helper in each module, which writes to stdout and — when `SENTRY_DSN` is set — calls `sentry_sdk.capture_exception()`. The data layer never imports `streamlit`; it returns neutral values (`None`, empty `DataFrame`, `{}`) on failure and lets the UI layer decide what the user sees.

If you add new exception handling, follow the same pattern: generic `st.error(...)` string + `_report_internal_error("<context>", exc)` call. Never interpolate `str(e)`, dict `['error']` payloads, or path variables into user-visible markdown.

### Edge protection for public exposure

Railway does not provide a Web Application Firewall. If the app is exposed to the public internet, front it with an edge layer that provides:

- **Authentication / access control** — SSO, IP allowlist, or basic-auth gateway. Cloudflare Access, a reverse proxy with OAuth, or similar.
- **TLS termination** — Railway provides TLS for the `*.railway.app` hostname, but custom domains must be configured correctly.
- **Bot mitigation** — Cloudflare's managed challenge, or equivalent, to block scraping of the provider dropdown.

If the app is intended for authenticated internal use only, put it behind a VPN or organisation-SSO gateway rather than relying on obscurity.

### Rate limiting & bot mitigation

Streamlit has no built-in rate limiting. Apply ingress-level controls at whichever layer fronts Railway:

- **Cloudflare rate-limiting rules** — 100 requests/min/IP is a sensible starting point for a dashboard of this shape.
- **Bot Fight Mode** (Cloudflare) or equivalent to reduce automated traffic.
- Consider per-endpoint caps on `/_stcore/` health and websocket endpoints if you see abnormal traffic.

### Replica guidance

`railway.toml` sets `numReplicas = 2` as the baseline. This gives:

- **Zero-downtime deploys** — one replica serves traffic while the other is rolling.
- **Crash tolerance** — a single-replica crash (segfault, OOM, hung event loop) takes the service fully offline; two replicas buy you time to auto-restart.

Scale above `2` if traffic justifies it (>50 concurrent users, noticeable latency). Above `4` consider a proper load-balancer health strategy and sticky sessions, since Streamlit websocket state is per-replica and not shared.
