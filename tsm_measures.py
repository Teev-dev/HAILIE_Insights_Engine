# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Tom Stephenson (Teev-dev)

"""
TSM measure constants.

Single source of truth for the twelve Tenant Satisfaction Measures (TP01-TP12)
published by the UK Regulator of Social Housing. Descriptions here are taken
verbatim (shortened) from the regulator's 2025 column headers in
TSM25_LCRA_Perception / TSM25_LCHO_Perception.

LCHO providers do not report TP02-TP04 (repairs and home-maintenance measures
that do not apply to low-cost home ownership).
"""

from typing import Dict, List, Set


TP_CODES: List[str] = [f"TP{i:02d}" for i in range(1, 13)]

TP_DESCRIPTIONS: Dict[str, str] = {
    "TP01": "Overall satisfaction with the service",
    "TP02": "Satisfaction with the overall repairs service",
    "TP03": "Satisfaction with the time taken to complete most recent repair",
    "TP04": "Satisfaction that the home is well maintained",
    "TP05": "Satisfaction that the home is safe",
    "TP06": "Satisfaction that the landlord listens to tenant views and acts upon them",
    "TP07": "Satisfaction that the landlord keeps tenants informed",
    "TP08": "Agreement that the landlord treats tenants fairly and with respect",
    "TP09": "Satisfaction with the landlord's approach to complaints handling",
    "TP10": "Satisfaction that communal areas are kept clean and well maintained",
    "TP11": "Satisfaction that the landlord makes a positive contribution to the neighbourhood",
    "TP12": "Satisfaction with the landlord's approach to handling anti-social behaviour",
}

LCHO_EXCLUDED: Set[str] = {"TP02", "TP03", "TP04"}


def applicable_measures(dataset_type: str) -> List[str]:
    """Return TP codes that apply to the given dataset type (LCRA or LCHO)."""
    if dataset_type == "LCHO":
        return [tp for tp in TP_CODES if tp not in LCHO_EXCLUDED]
    return list(TP_CODES)
