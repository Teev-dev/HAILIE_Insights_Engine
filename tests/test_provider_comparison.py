# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Tom Stephenson (Teev-dev)

"""Tests for the multi-provider (group executive) comparison.

    python -m unittest tests.test_provider_comparison
"""

import unittest

from analytics_refactored import TSMAnalytics
from data_processor_enhanced import EnhancedTSMDataProcessor


def sel(code, name, dataset_type):
    return {"provider_code": code, "provider_name": f"{name} - {dataset_type}", "dataset_type": dataset_type}


ACIS = sel("L4229", "Acis Group Limited", "LCRA")
A2D = sel("L4240", "A2Dominion Housing Group Limited", "LCRA")
ABRI = sel("L4172", "Abri Group Limited", "LCRA")
A2D_LCHO = sel("L4240", "A2Dominion Housing Group Limited", "LCHO")
ABRI_LCHO = sel("L4172", "Abri Group Limited", "LCHO")


class CompareProvidersTests(unittest.TestCase):
    def setUp(self):
        self.dp = EnhancedTSMDataProcessor()
        self.analytics = TSMAnalytics(self.dp)

    def tearDown(self):
        self.dp.close()

    def test_rejects_fewer_than_two(self):
        self.assertEqual(self.analytics.compare_providers([ACIS]), {"error": "too_few_providers"})

    def test_rejects_more_than_three(self):
        four = [ACIS, A2D, ABRI, sel("L4511", "Accent Group Limited", "LCRA")]
        self.assertEqual(self.analytics.compare_providers(four), {"error": "too_many_providers"})

    def test_rejects_mixed_dataset_types(self):
        """LCRA and LCHO results must never be placed in one comparison."""
        self.assertEqual(
            self.analytics.compare_providers([ACIS, A2D_LCHO]), {"error": "mixed_dataset_types"})

    def test_rejects_duplicates(self):
        self.assertEqual(
            self.analytics.compare_providers([ACIS, dict(ACIS)]), {"error": "duplicate_providers"})

    def test_three_lcra_providers_match_single_provider_results(self):
        comparison = self.analytics.compare_providers([ACIS, A2D, ABRI])
        self.assertNotIn("error", comparison)
        self.assertEqual(comparison["dataset_type"], "LCRA")
        self.assertEqual([p["provider_code"] for p in comparison["providers"]], ["L4229", "L4240", "L4172"])

        single_rankings = self.analytics.calculate_rankings(None, dataset_type="LCRA")
        for provider in comparison["providers"]:
            code = provider["provider_code"]
            self.assertEqual(provider["ranking"], single_rankings[code])
            self.assertEqual(
                provider["priority"],
                self.analytics.identify_priority(None, code, dataset_type="LCRA"))

        self.assertEqual(len(comparison["measures"]), 12)
        tp01 = comparison["measures"][0]
        stored = self.analytics._peer_percentiles("L4229", "LCRA")
        self.assertAlmostEqual(tp01["values"]["L4229"]["percentile"], stored["TP01"], places=9)
        scores = {c: v["score"] for c, v in tp01["values"].items()}
        self.assertEqual(tp01["highest"], [max(scores, key=scores.get)])
        self.assertEqual(tp01["lowest"], [min(scores, key=scores.get)])
        self.assertAlmostEqual(tp01["spread"], max(scores.values()) - min(scores.values()), places=9)
        self.assertEqual(
            comparison["widest_gap"]["spread"], max(m["spread"] for m in comparison["measures"]))

    def test_lcho_comparison_has_no_repairs_measures(self):
        comparison = self.analytics.compare_providers([A2D_LCHO, ABRI_LCHO])
        self.assertNotIn("error", comparison)
        codes = [m["measure"] for m in comparison["measures"]]
        self.assertFalse(set(codes) & {"TP02", "TP03", "TP04"})
        lcho_total = self.dp.get_dataset_summary_stats("LCHO")["provider_count"]
        for provider in comparison["providers"]:
            self.assertEqual(provider["ranking"]["total_providers"], lcho_total)

    def test_filter_ranks_everyone_in_one_shared_group(self):
        # Acis is East Midlands; the other two are South East. All three must
        # still be ranked in the same group.
        comparison = self.analytics.compare_providers([ACIS, A2D, ABRI], region="South East")
        self.assertTrue(comparison["peer_group"]["is_filtered"])
        totals = {p["ranking"]["total_providers"] for p in comparison["providers"]}
        self.assertEqual(totals, {comparison["peer_group"]["peer_group_size"]})
        south_east = self.dp.get_peer_group_scores("LCRA", region="South East")["provider_code"].nunique()
        self.assertEqual(comparison["peer_group"]["peer_group_size"], south_east + 1)

    def test_too_small_filter_falls_back_to_full_dataset(self):
        comparison = self.analytics.compare_providers([A2D_LCHO, ABRI_LCHO], region="North East")
        self.assertTrue(comparison["peer_group"]["fallback"])
        unfiltered = self.analytics.compare_providers([A2D_LCHO, ABRI_LCHO])
        self.assertEqual(
            [p["ranking"] for p in comparison["providers"]],
            [p["ranking"] for p in unfiltered["providers"]])


if __name__ == "__main__":
    unittest.main()
