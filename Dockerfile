FROM python:3.11-slim

# Security: run as non-root user
RUN groupadd -r hailie && useradd -r -g hailie -m hailie

WORKDIR /app

# Install dependencies first (layer caching)
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir . && rm -rf /root/.cache

# Copy application code
COPY app.py dashboard.py analytics_refactored.py data_processor_enhanced.py \
     styles.py tooltip_definitions.py mobile_utils.py config.py ./
COPY pages/ pages/
COPY .streamlit/ .streamlit/

# Copy pre-built analytics database (open-source default)
# Production deployments can override with DATA_PATH env var pointing to a persistent volume
COPY data/hailie_analytics_v2.duckdb data/

# Own the app directory
RUN chown -R hailie:hailie /app

USER hailie

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8501}/_stcore/health')"

# Railway injects $PORT; default to 8501 for local development
EXPOSE ${PORT:-8501}

CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true"]
