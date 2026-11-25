# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Tom Stephenson (Teev-dev)

"""Tests for size-band / region peer-group filtering.

Stdlib unittest, run against the baked-in analytics database:

    python -m unittest tests.test_peer_groups
"""

import unittest

from analytics_refactored import MIN_PEER_GROUP_SIZE, TSMAnalytics
from data_processor_enhanced import SIZE_BAND_ORDER, EnhancedTSMDataProcessor

LCRA_CODE = "L4229"   # Acis Group: LCRA only, 5,000-40,000, East Midlands
LCRA_BAND = "5,000-40,000"
LCRA_REGION = "East Midlands"
DUAL_CODE = "L4240"   # A2Dominion: reports in both LCRA and LCHO


class PeerGroupDataTests(unittest.TestCase):
    def setUp(self):
        self.dp = EnhancedTSMDataProcessor()

    def tearDown(self):
        self.dp.close()

    def test_provider_metadata(self):
        meta = self.dp.get_provider_metadata(LCRA_CODE, "LCRA")
        self.assertEqual(meta["size_band"], LCRA_BAND)
        self.assertEqual(meta["region"], LCRA_REGION)
        self.assertEqual(meta["landlord_type"], "PRP")

    def test_unknown_provider_metadata_is_empty(self):
        self.assertEqual(self.dp.get_provider_metadata("NOPE", "LCRA"), {})

    def test_filter_options_cover_every_scored_provider_with_a_band(self):
        for dataset_type in ("LCRA", "LCHO"):
            options = self.dp.get_peer_filter_options(dataset_type)
            bands = [o["value"] for o in options["size_bands"]]
            self.assertEqual(bands, [b for b in SIZE_BAND_ORDER if b in bands])
            total = self.dp.get_dataset_summary_stats(dataset_type)["provider_count"]
            banded = sum(o["provider_count"] for o in options["size_bands"])
            # At most a couple of providers have no band recorded by the regulator.
            self.assertLessEqual(banded, total)
            self.assertGreaterEqual(banded, total - 2)
            self.assertEqual(options["regions"][-1]["value"], "Mixed")

    def test_no_filter_returns_whole_dataset(self):
        everyone = self.dp.get_peer_group_scores("LCRA")
        self.assertEqual(
            everyone["provider_code"].nunique(),
            self.dp.get_dataset_summary_stats("LCRA")["provider_count"],
        )

    def test_filter_matches_option_count(self):
        options = self.dp.get_peer_filter_options("LCRA")
        expected = {o["value"]: o["provider_count"] for o in options["regions"]}
        scores = self.dp.get_peer_group_scores("LCRA", region=LCRA_REGION)
        self.assertEqual(scores["provider_code"].nunique(), expected[LCRA_REGION])

    def test_filtered_group_never_leaves_the_dataset(self):
        """A size filter on LCHO must not pull in LCRA-only providers."""
        lcho_all = set(self.dp.get_peer_group_scores("LCHO")["provider_code"])
        for band in SIZE_BAND_ORDER:
            group = set(self.dp.get_peer_group_scores("LCHO", size_band=band)["provider_code"])
            self.assertTrue(group <= lcho_all)
        lcho = self.dp.get_peer_group_scores("LCHO", size_band=LCRA_BAND)
        self.assertFalse(set(lcho["tp_measure"]) & {"TP02", "TP03", "TP04"})

    def test_selected_provider_is_kept_when_outside_the_filter(self):
        outside = self.dp.get_peer_group_scores("LCRA", region="London")
        self.assertNotIn(LCRA_CODE, set(outside["provider_code"]))
        kept = self.dp.get_peer_group_scores("LCRA", region="London", include_provider_codes=[LCRA_CODE])
        self.assertIn(LCRA_CODE, set(kept["provider_code"]))
        self.assertEqual(kept["provider_code"].nunique(), outside["provider_code"].nunique() + 1)

    def test_wide_scores_respect_filter(self):
        wide = self.dp.get_all_providers_with_scores("LCRA", size_band=LCRA_BAND, region=LCRA_REGION)
        long = self.dp.get_peer_group_scores("LCRA", size_band=LCRA_BAND, region=LCRA_REGION)
        self.assertEqual(set(wide["provider_code"]), set(long["provider_code"]))
        self.assertEqual(wide["provider_code"].nunique(), len(wide))

    def test_measure_statistics_respect_filter(self):
        long = self.dp.get_peer_group_scores("LCRA", region=LCRA_REGION)
        tp01 = long[long["tp_measure"] == "TP01"]["score"]
        stats = self.dp.get_measure_statistics("TP01", "LCRA", region=LCRA_REGION)
        self.assertEqual(stats["sample_size"], len(tp01))
        self.assertAlmostEqual(stats["mean_score"], tp01.mean(), places=6)
        self.assertAlmostEqual(stats["median_score"], tp01.median(), places=6)


class PeerGroupAnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.dp = EnhancedTSMDataProcessor()
        self.analytics = TSMAnalytics(self.dp)

    def tearDown(self):
        self.dp.close()

    def test_recalculated_percentiles_match_etl_on_the_full_dataset(self):
        """The on-the-fly method must reproduce the ETL's stored percentiles."""
        for code, dataset_type in ((LCRA_CODE, "LCRA"), (DUAL_CODE, "LCRA"), (DUAL_CODE, "LCHO")):
            stored = self.analytics._peer_percentiles(code, dataset_type)
            scores = self.dp.get_peer_group_scores(dataset_type)
            self.assertTrue(stored)
            from scipy.stats import percentileofscore
            for tp, expected in stored.items():
                measure = scores[scores["tp_measure"] == tp]
                own = measure.loc[measure["provider_code"] == code, "score"].iloc[0]
                self.assertAlmostEqual(percentileofscore(measure["score"].values, own), expected, places=9)

    def test_filtered_percentiles_use_only_the_peer_group(self):
        pct = self.analytics._peer_percentiles(LCRA_CODE, "LCRA", region=LCRA_REGION)
        scores = self.dp.get_peer_group_scores("LCRA", region=LCRA_REGION)
        tp01 = scores[scores["tp_measure"] == "TP01"]
        own = tp01.loc[tp01["provider_code"] == LCRA_CODE, "score"].iloc[0]
        at_or_below = (tp01["score"] <= own).sum()
        below = (tp01["score"] < own).sum()
        # scipy's default 'rank' method: the average rank of the score, as a percentage.
        self.assertAlmostEqual(pct["TP01"], (at_or_below + below + 1) / 2 / len(tp01) * 100, places=9)
        self.assertTrue(all(0 <= v <= 100 for v in pct.values()))

    def test_rankings_are_restricted_to_the_peer_group(self):
        full = self.analytics.calculate_rankings(None, dataset_type="LCRA")
        filtered = self.analytics.calculate_rankings(
            None, dataset_type="LCRA", region=LCRA_REGION, include_provider_codes=[LCRA_CODE])
        group = set(self.dp.get_peer_group_scores("LCRA", region=LCRA_REGION)["provider_code"])
        self.assertEqual(set(filtered), group)
        self.assertEqual(filtered[LCRA_CODE]["total_providers"], len(group))
        self.assertLess(len(filtered), len(full))
        # Composite score is the provider's own and must not move with the peer group.
        self.assertAlmostEqual(filtered[LCRA_CODE]["score"], full[LCRA_CODE]["score"], places=9)
        self.assertEqual(sorted(r["rank"] for r in filtered.values()), list(range(1, len(group) + 1)))

    def test_resolve_peer_group_applies_a_large_enough_filter(self):
        group = self.analytics.resolve_peer_group([LCRA_CODE], "LCRA", region=LCRA_REGION)
        self.assertTrue(group["is_filtered"])
        self.assertFalse(group["fallback"])
        self.assertEqual(group["region"], LCRA_REGION)
        self.assertGreaterEqual(group["peer_group_size"], MIN_PEER_GROUP_SIZE)

    def test_resolve_peer_group_falls_back_when_too_small(self):
        # LCHO has only a handful of providers per region.
        group = self.analytics.resolve_peer_group([DUAL_CODE], "LCHO", region="North East")
        self.assertTrue(group["fallback"])
        self.assertFalse(group["is_filtered"])
        self.assertIsNone(group["region"])
        self.assertEqual(group["requested_region"], "North East")
        self.assertLess(group["filtered_group_size"], MIN_PEER_GROUP_SIZE)
        self.assertEqual(
            group["peer_group_size"], self.dp.get_dataset_summary_stats("LCHO")["provider_count"])

    def test_no_filter_leaves_existing_results_unchanged(self):
        plain = self.analytics.identify_priority(None, LCRA_CODE, dataset_type="LCRA")
        explicit = self.analytics.identify_priority(
            None, LCRA_CODE, dataset_type="LCRA", size_band=None, region=None)
        self.assertEqual(plain, explicit)
        self.assertNotIn("error", plain)

    def test_priority_and_detail_use_filtered_percentiles(self):
        pct = self.analytics._peer_percentiles(LCRA_CODE, "LCRA", region=LCRA_REGION)
        priority = self.analytics.identify_priority(
            None, LCRA_CODE, dataset_type="LCRA", region=LCRA_REGION)
        self.assertNotIn("error", priority)
        measure = priority["priority_measure"]
        self.assertAlmostEqual(priority["percentile"], pct[measure], places=9)

        detail = self.analytics.get_detailed_performance_analysis(
            None, LCRA_CODE, dataset_type="LCRA", region=LCRA_REGION)
        self.assertNotIn("error", detail)
        for tp, row in detail.items():
            self.assertAlmostEqual(row["percentile"], pct[tp], places=9)
        stats = self.dp.get_measure_statistics("TP01", "LCRA", region=LCRA_REGION)
        self.assertAlmostEqual(detail["TP01"]["peer_avg"], stats["mean_score"], places=9)

    def test_lcho_filter_keeps_repairs_measures_out(self):
        detail = self.analytics.get_detailed_performance_analysis(
            None, DUAL_CODE, dataset_type="LCHO", size_band="5,000-40,000")
        self.assertNotIn("error", detail)
        self.assertFalse(set(detail) & {"TP02", "TP03", "TP04"})


if __name__ == "__main__":
    unittest.main()
