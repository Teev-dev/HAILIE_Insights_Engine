FROM python:3.11-slim

# Security: non-root user for running the app, gosu for permission handoff
RUN groupadd -r hailie && useradd -r -g hailie -m hailie \
    && apt-get update && apt-get install -y --no-install-recommends gosu && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first (layer caching)
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir . && rm -rf /root/.cache

# Copy application code. The build context is filtered by .dockerignore
# (allowlist-shaped: everything excluded unless explicitly re-included), so
# this COPY ships only the files enumerated there.
COPY . .

RUN chmod +x /app/entrypoint.sh && chown -R hailie:hailie /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8501}/_stcore/health')"

# Railway injects $PORT; default to 8501 for local development
EXPOSE ${PORT:-8501}

# Start as root, fix volume permissions, then drop to hailie user via gosu
ENTRYPOINT ["/app/entrypoint.sh"]
