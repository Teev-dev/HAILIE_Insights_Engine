# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Tom Stephenson (Teev-dev)

"""
Application configuration.

Data path resolution:
- Production (Railway): Set DATA_PATH env var to persistent volume mount (e.g. /data)
- Open-source default: Uses local data/ directory (baked into Docker image)
"""

import os
import shutil

_APP_DIR = os.path.dirname(__file__)
_BAKED_IN_DATA = os.path.join(_APP_DIR, "data")

DATA_DIR = os.environ.get("DATA_PATH", _BAKED_IN_DATA)

DB_PATH = os.path.join(DATA_DIR, "hailie_analytics_v2.duckdb")

SOURCE_DIR = os.path.join(DATA_DIR, "source")

# --- Feedback / contact form (Resend email delivery) ---
# Powers the in-app "report a data issue / feature request" form. All optional:
# when RESEND_API_KEY is unset the form degrades to a "not configured yet"
# message instead of failing, so the app runs without any mail setup.
# See feedback_service.py for how these are used.
#   RESEND_API_KEY      — Resend API key (https://resend.com). Unset => form off.
#   FEEDBACK_FROM_EMAIL — verified Resend sender. The sandbox default works the
#                         moment a key is added; swap to a verified domain later.
#   FEEDBACK_TO_EMAIL   — maintainer inbox that receives reports.
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
FEEDBACK_FROM_EMAIL = os.environ.get(
    "FEEDBACK_FROM_EMAIL", "HAILIE Insights <onboarding@resend.dev>"
)
FEEDBACK_TO_EMAIL = os.environ.get("FEEDBACK_TO_EMAIL", "guy@housingai.org")

# Auto-seed: if DATA_PATH is set (persistent volume) but the database isn't there yet,
# copy it from the baked-in image so the app works on first deploy. Failures are
# logged to stdout only — never raised at import, so the app can still start and
# surface a controlled "database unavailable" message to the user.
if DATA_DIR != _BAKED_IN_DATA and not os.path.exists(DB_PATH):
    _baked_db = os.path.join(_BAKED_IN_DATA, "hailie_analytics_v2.duckdb")
    if os.path.exists(_baked_db):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            shutil.copy2(_baked_db, DB_PATH)
        except OSError as _seed_exc:
            print(f"[ERROR] config auto-seed failed: {type(_seed_exc).__name__}")
