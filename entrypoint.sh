#!/bin/sh
# Fix volume mount permissions (Railway mounts as root)
if [ -d "/data" ] && [ "$(id -u)" = "0" ]; then
    chown -R hailie:hailie /data
fi
exec gosu hailie streamlit run app.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true
