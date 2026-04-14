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

# Auto-seed: if DATA_PATH is set (persistent volume) but the database isn't there yet,
# copy it from the baked-in image so the app works on first deploy.
if DATA_DIR != _BAKED_IN_DATA and not os.path.exists(DB_PATH):
    _baked_db = os.path.join(_BAKED_IN_DATA, "hailie_analytics_v2.duckdb")
    if os.path.exists(_baked_db):
        os.makedirs(DATA_DIR, exist_ok=True)
        shutil.copy2(_baked_db, DB_PATH)
