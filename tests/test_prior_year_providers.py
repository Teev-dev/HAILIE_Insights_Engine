# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Tom Stephenson (Teev-dev)

"""Tests for providers that are not in the latest year of TSM data.

Some landlords stop appearing in the regulator's dataset (usually after a
merger). They stay selectable, with a notice, and are shown against the peers
of their own most recent year. Run against the baked-in analytics database:

    python -m unittest tests.test_prior_year_providers
"""

import unittest

from analytics_refactored import LATEST_DATA_YEAR, TSMAnalytics
from dashboard import ExecutiveDashboard
from data_processor_enhanced import EnhancedTSMDataProcessor
from tooltip_definitions import (
    PROVIDER_SUCCESSION_NOTES,
    former_names_caption,
    prior_year_notice,
    succession_note,
)

LONGHURST = "L4277"      # LCRA and LCHO, 2024 only
FLAGSHIP = "4651"        # LCRA and LCHO, 2024 and 2025
THAMES_VALLEY = "L0514"  # LCRA and LCHO, 2024 only
ABBEYFIELD = "H1046"     # COMBINED, 2024 only
WEST_KENT = "LH3827"     # current in both datasets
BE_ONE = "4568"          # renamed: Bolton at Home Limited until 2025
ACIS = "L4229"           # current, LCRA only


def sel(code, name, dataset_type):
    return {"provider_code": code, "provider_name": f"{name} - {dataset_type}", "dataset_type": dataset_type}


class RecordingProcessor:
    """Wraps a processor and records the year each year-aware call received."""

    def __init__(self, inner):
        self._inner = inner
        self.years = []

    def __getattr__(self, name):
        attr = getattr(self._inner, name)
        if not callable(attr):
            return attr

        def wrapper(*args, **kwargs):
            import inspect
            if 'year' in inspect.signature(attr).parameters:
                bound = inspect.signature(attr).bind(*args, **kwargs)
                bound.apply_defaults()
                self.years.append((name, bound.arguments['year']))
            return attr(*args, **kwargs)
        return wrapper


class LatestYearTests(unittest.TestCase):
    def setUp(self):
        self.dp = EnhancedTSMDataProcessor()

    def tearDown(self):
        self.dp.close()

    def test_latest_year_per_provider_and_dataset(self):
        self.assertEqual(self.dp.get_latest_year(LONGHURST, "LCRA"), 2024)
        self.assertEqual(self.dp.get_latest_year(FLAGSHIP, "LCHO"), 2025)
        self.assertEqual(self.dp.get_latest_year(WEST_KENT, "LCRA"), 2026)
        self.assertIsNone(self.dp.get_latest_year("NOPE", "LCRA"))

    def test_latest_year_is_specific_to_the_dataset_type(self):
        # Legal & General stopped reporting LCRA after 2025 but still reports LCHO.
        self.assertEqual(self.dp.get_latest_year("5062", "LCRA"), 2025)
        self.assertEqual(self.dp.get_latest_year("5062", "LCHO"), 2026)

    def test_every_dropdown_option_has_a_latest_year(self):
        history = self.dp.get_provider_history()
        for provider in self.dp.get_all_provider_codes():
            key = (provider["provider_code"], provider["dataset_type"])
            self.assertIn(key, history)
            self.assertEqual(history[key]["latest_year"], self.dp.get_latest_year(*key))

    def test_load_default_data_for_a_prior_year(self):
        self.assertIsNone(self.dp.load_default_data(LONGHURST, "Longhurst Group Limited - LCRA"))
        df = self.dp.load_default_data(LONGHURST, "Longhurst Group Limited - LCRA", year=2024)
        self.assertEqual(len(df), 1)
        self.assertEqual(int(df["year"].iloc[0]), 2024)

    def test_name_history_records_renames(self):
        names = self.dp.get_provider_history()[(BE_ONE, "LCRA")]["names"]
        self.assertEqual([n["name"] for n in names], ["Bolton at Home Limited", "Be One Homes"])
        self.assertEqual((names[0]["first_year"], names[0]["last_year"]), (2024, 2025))
        self.assertEqual((names[1]["first_year"], names[1]["last_year"]), (2026, 2026))

    def test_unrenamed_provider_has_one_name(self):
        names = self.dp.get_provider_history()[(ACIS, "LCRA")]["names"]
        self.assertEqual(len(names), 1)


class PriorYearAnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.dp = EnhancedTSMDataProcessor()

    def tearDown(self):
        self.dp.close()

    def test_rankings_use_that_years_peer_group(self):
        total_2024 = self.dp.get_dataset_summary_stats("LCRA", year=2024)["provider_count"]
        total_2026 = self.dp.get_dataset_summary_stats("LCRA")["provider_count"]
        self.assertNotEqual(total_2024, total_2026)

        rankings = TSMAnalytics(self.dp, year=2024).calculate_rankings(None, dataset_type="LCRA")
        self.assertIn(LONGHURST, rankings)
        self.assertEqual(rankings[LONGHURST]["total_providers"], total_2024)

        self.assertNotIn(LONGHURST, TSMAnalytics(self.dp).calculate_rankings(None, dataset_type="LCRA"))

    def test_peer_group_size_matches_the_ranking_total(self):
        analytics = TSMAnalytics(self.dp, year=2024)
        group = analytics.resolve_peer_group([LONGHURST], "LCRA")
        rankings = analytics.calculate_rankings(None, dataset_type="LCRA")
        self.assertEqual(group["peer_group_size"], rankings[LONGHURST]["total_providers"])

    def test_every_year_aware_call_receives_the_bound_year(self):
        spy = RecordingProcessor(self.dp)
        analytics = TSMAnalytics(spy, year=2024)
        meta = self.dp.get_provider_metadata(LONGHURST, "LCRA", year=2024)
        analytics.resolve_peer_group([LONGHURST], "LCRA", meta["size_band"], meta["region"])
        analytics.calculate_rankings(None, dataset_type="LCRA")
        analytics.identify_priority(None, LONGHURST, dataset_type="LCRA")
        analytics.identify_priority(None, LONGHURST, dataset_type="LCRA", size_band=meta["size_band"])
        analytics.get_detailed_performance_analysis(None, LONGHURST, dataset_type="LCRA")
        analytics.get_detailed_performance_analysis(
            None, LONGHURST, dataset_type="LCRA", size_band=meta["size_band"])
        self.assertTrue(spy.years)
        self.assertEqual({year for _, year in spy.years}, {2024}, spy.years)

    def test_momentum_calls_use_the_bound_year_and_the_one_before(self):
        spy = RecordingProcessor(self.dp)
        TSMAnalytics(spy, year=2025).calculate_momentum(None, FLAGSHIP, dataset_type="LCRA")
        self.assertEqual(sorted(year for _, year in spy.years), [2024, 2025])

    def test_priority_uses_that_years_correlations_and_percentiles(self):
        priority = TSMAnalytics(self.dp, year=2024).identify_priority(None, LONGHURST, dataset_type="LCRA")
        self.assertNotIn("error", priority)
        correlations = self.dp.get_dataset_correlations("LCRA", year=2024)
        expected = dict(zip(correlations["tp_measure"], correlations["correlation_with_tp01"]))
        percentiles = self.dp.get_provider_percentiles(LONGHURST, year=2024, dataset_type="LCRA")
        expected_pct = dict(zip(percentiles["tp_measure"], percentiles["percentile_rank"]))
        for measure, detail in priority["all_priorities"].items():
            self.assertAlmostEqual(detail["correlation"], expected[measure], places=9)
            self.assertAlmostEqual(detail["percentile"], expected_pct[measure], places=9)

    def test_detail_uses_that_years_peer_averages(self):
        detail = TSMAnalytics(self.dp, year=2024).get_detailed_performance_analysis(
            None, LONGHURST, dataset_type="LCRA")
        self.assertNotIn("error", detail)
        self.assertEqual(len(detail), 12)
        stats_2024 = self.dp.get_measure_statistics("TP01", "LCRA", year=2024)
        stats_2026 = self.dp.get_measure_statistics("TP01", "LCRA")
        self.assertNotAlmostEqual(stats_2024["mean_score"], stats_2026["mean_score"], places=6)
        self.assertAlmostEqual(detail["TP01"]["peer_avg"], stats_2024["mean_score"], places=9)

    def test_own_size_band_and_region_give_a_prior_year_peer_group(self):
        meta = self.dp.get_provider_metadata(LONGHURST, "LCRA", year=2024)
        self.assertTrue(meta["size_band"] and meta["region"])
        options = self.dp.get_peer_filter_options("LCRA", year=2024)
        self.assertIn(meta["region"], [o["value"] for o in options["regions"]])
        group = TSMAnalytics(self.dp, year=2024).resolve_peer_group(
            [LONGHURST], "LCRA", meta["size_band"], meta["region"])
        self.assertTrue(group["is_filtered"])
        expected = self.dp.get_peer_group_scores(
            "LCRA", year=2024, size_band=meta["size_band"], region=meta["region"],
            include_provider_codes=[LONGHURST])["provider_code"].nunique()
        self.assertEqual(group["peer_group_size"], expected)

    def test_prior_year_lcho_provider_has_no_repairs_measures(self):
        analytics = TSMAnalytics(self.dp, year=2024)
        detail = analytics.get_detailed_performance_analysis(None, THAMES_VALLEY, dataset_type="LCHO")
        self.assertNotIn("error", detail)
        self.assertFalse(set(detail) & {"TP02", "TP03", "TP04"})
        priority = analytics.identify_priority(None, THAMES_VALLEY, dataset_type="LCHO")
        self.assertNotIn("error", priority)
        self.assertNotIn(priority["priority_measure"], {"TP02", "TP03", "TP04"})
        lcho_2024 = self.dp.get_dataset_summary_stats("LCHO", year=2024)["provider_count"]
        rankings = analytics.calculate_rankings(None, dataset_type="LCHO")
        self.assertEqual(rankings[THAMES_VALLEY]["total_providers"], lcho_2024)

    def test_combined_prior_year_provider_returns_no_error(self):
        analytics = TSMAnalytics(self.dp, year=2024)
        self.assertIn(ABBEYFIELD, analytics.calculate_rankings(None, dataset_type="COMBINED"))
        self.assertNotIn("error", analytics.get_detailed_performance_analysis(
            None, ABBEYFIELD, dataset_type="COMBINED"))
        self.assertNotIn("error", analytics.identify_priority(None, ABBEYFIELD, dataset_type="COMBINED"))

    def test_momentum_compares_latest_year_with_the_one_before(self):
        momentum = TSMAnalytics(self.dp, year=2025).calculate_momentum(None, FLAGSHIP, dataset_type="LCRA")
        self.assertFalse(momentum["disabled"])
        self.assertEqual((momentum["latest_year"], momentum["prior_year"]), (2025, 2024))
        s25 = self.dp.get_provider_scores(FLAGSHIP, year=2025, dataset_type="LCRA")
        s24 = self.dp.get_provider_scores(FLAGSHIP, year=2024, dataset_type="LCRA")
        merged = s25.merge(s24, on="tp_measure", suffixes=("_25", "_24"))
        expected = (merged["score_25"] - merged["score_24"]).mean()
        self.assertAlmostEqual(momentum["year_over_year_change"], expected, places=9)

    def test_momentum_disabled_for_a_single_year_provider(self):
        momentum = TSMAnalytics(self.dp, year=2024).calculate_momentum(None, LONGHURST, dataset_type="LCRA")
        self.assertTrue(momentum["disabled"])
        self.assertEqual((momentum["latest_year"], momentum["prior_year"]), (2024, 2023))

    def test_explicit_latest_year_equals_the_default(self):
        default = TSMAnalytics(self.dp)
        explicit = TSMAnalytics(self.dp, year=LATEST_DATA_YEAR)
        for dataset_type in ("LCRA", "LCHO"):
            self.assertEqual(
                default.calculate_rankings(None, dataset_type=dataset_type)[WEST_KENT],
                explicit.calculate_rankings(None, dataset_type=dataset_type)[WEST_KENT])
            self.assertEqual(
                default.calculate_momentum(None, WEST_KENT, dataset_type=dataset_type),
                explicit.calculate_momentum(None, WEST_KENT, dataset_type=dataset_type))
            self.assertEqual(
                default.identify_priority(None, WEST_KENT, dataset_type=dataset_type),
                explicit.identify_priority(None, WEST_KENT, dataset_type=dataset_type))
            self.assertEqual(
                default.get_detailed_performance_analysis(None, WEST_KENT, dataset_type=dataset_type),
                explicit.get_detailed_performance_analysis(None, WEST_KENT, dataset_type=dataset_type))

    def test_momentum_spans_a_rename(self):
        momentum = TSMAnalytics(self.dp).calculate_momentum(None, BE_ONE, dataset_type="LCRA")
        self.assertFalse(momentum["disabled"])
        self.assertEqual((momentum["latest_year"], momentum["prior_year"]), (2026, 2025))
        self.assertEqual(momentum["total_measures_compared"], 12)


class TiedRankTests(unittest.TestCase):
    """Providers with the same average score share a rank."""

    def setUp(self):
        self.dp = EnhancedTSMDataProcessor()
        self.rankings = TSMAnalytics(self.dp).calculate_rankings(None, dataset_type="LCRA")

    def tearDown(self):
        self.dp.close()

    def test_tied_providers_share_rank_percentile_and_quartile(self):
        home, moat = self.rankings["L3076"], self.rankings["L0386"]  # Home Group, Moat Homes
        self.assertAlmostEqual(home["score"], moat["score"], places=9)
        for field in ("rank", "percentile", "quartile"):
            self.assertEqual(home[field], moat[field], field)

    def test_ranks_either_side_of_a_tie_are_preserved(self):
        ordered = sorted(self.rankings.values(), key=lambda r: (r["rank"], -r["score"]))
        ranks = [r["rank"] for r in ordered]
        self.assertEqual(ranks[0], 1)
        ties = 0
        for position, entry in enumerate(ordered, start=1):
            if position > 1 and round(entry["score"], 9) == round(ordered[position - 2]["score"], 9):
                self.assertEqual(entry["rank"], ordered[position - 2]["rank"])
                ties += 1
            else:
                # Everyone not in a tie keeps the position they hold in the ordering.
                self.assertEqual(entry["rank"], position)
        self.assertGreater(ties, 0)

    def test_ranks_do_not_change_between_calls(self):
        for _ in range(5):
            again = TSMAnalytics(self.dp).calculate_rankings(None, dataset_type="LCRA")
            self.assertEqual({c: r["rank"] for c, r in again.items()},
                             {c: r["rank"] for c, r in self.rankings.items()})


class CompareWithUnavailableProviderTests(unittest.TestCase):
    ACIS = sel(ACIS, "Acis Group Limited", "LCRA")
    A2D = sel("L4240", "A2Dominion Housing Group Limited", "LCRA")
    LONGHURST = sel(LONGHURST, "Longhurst Group Limited", "LCRA")
    FLAGSHIP = sel(FLAGSHIP, "Flagship Housing Limited", "LCRA")

    def setUp(self):
        self.dp = EnhancedTSMDataProcessor()
        self.analytics = TSMAnalytics(self.dp)

    def tearDown(self):
        self.dp.close()

    def test_two_current_and_one_missing_compares_the_two(self):
        comparison = self.analytics.compare_providers([self.ACIS, self.LONGHURST, self.A2D])
        self.assertNotIn("error", comparison)
        self.assertEqual([p["provider_code"] for p in comparison["providers"]], ["L4229", "L4240"])
        self.assertEqual(comparison["selection_order"], ["L4229", LONGHURST, "L4240"])
        self.assertEqual(
            comparison["unavailable"],
            [{"provider_code": LONGHURST, "provider_name": "Longhurst Group Limited - LCRA",
              "latest_year": 2024}])

        without = self.analytics.compare_providers([self.ACIS, self.A2D])
        self.assertEqual(without["unavailable"], [])
        for key in ("providers", "measures", "widest_gap", "shared_below_median",
                    "shared_above_median", "peer_group"):
            self.assertEqual(comparison[key], without[key], key)

    def test_one_current_and_one_missing_shows_the_current_one(self):
        comparison = self.analytics.compare_providers([self.LONGHURST, self.ACIS])
        self.assertNotIn("error", comparison)
        self.assertEqual([p["provider_code"] for p in comparison["providers"]], ["L4229"])
        self.assertEqual([u["provider_code"] for u in comparison["unavailable"]], [LONGHURST])
        single = self.analytics.calculate_rankings(None, dataset_type="LCRA")
        self.assertEqual(comparison["providers"][0]["ranking"], single["L4229"])
        self.assertEqual(len(comparison["measures"]), 12)
        # Nothing is "shared across the group" when only one provider is compared.
        self.assertIsNone(comparison["widest_gap"])
        self.assertEqual(comparison["shared_below_median"], [])
        self.assertEqual(comparison["shared_above_median"], [])
        for measure in comparison["measures"]:
            self.assertEqual(set(measure["values"]), {"L4229"})

    def test_all_missing_returns_no_comparison_and_no_error(self):
        comparison = self.analytics.compare_providers([self.LONGHURST, self.FLAGSHIP])
        self.assertNotIn("error", comparison)
        self.assertEqual(comparison["providers"], [])
        self.assertEqual(comparison["measures"], [])
        self.assertEqual(
            [(u["provider_code"], u["latest_year"]) for u in comparison["unavailable"]],
            [(LONGHURST, 2024), (FLAGSHIP, 2025)])

    def test_selection_rules_still_apply_to_the_whole_selection(self):
        self.assertEqual(
            self.analytics.compare_providers([self.LONGHURST]), {"error": "too_few_providers"})
        mixed = [self.ACIS, sel(LONGHURST, "Longhurst Group Limited", "LCHO")]
        self.assertEqual(self.analytics.compare_providers(mixed), {"error": "mixed_dataset_types"})


class NoticeCopyTests(unittest.TestCase):
    def setUp(self):
        self.dp = EnhancedTSMDataProcessor()

    def tearDown(self):
        self.dp.close()

    def test_succession_notes_point_from_lapsed_to_current_providers(self):
        """Fails at the next data refresh if a note has gone stale."""
        history = self.dp.get_provider_history()
        latest = {}
        for (code, _), entry in history.items():
            latest[code] = max(latest.get(code, 0), entry["latest_year"])
        for code, entry in PROVIDER_SUCCESSION_NOTES.items():
            self.assertIn(code, latest, code)
            self.assertLess(latest[code], LATEST_DATA_YEAR, f"{code} is back in the latest data")
            self.assertEqual(latest.get(entry["successor_code"]), LATEST_DATA_YEAR,
                             f"successor of {code} is not in the latest data")
            self.assertTrue(entry["note"].endswith("."))

    def test_every_lapsed_dropdown_provider_is_accounted_for(self):
        lapsed = {
            p["provider_code"] for p in self.dp.get_all_provider_codes()
            if self.dp.get_latest_year(p["provider_code"], p["dataset_type"]) < LATEST_DATA_YEAR
        }
        self.assertEqual(lapsed - set(PROVIDER_SUCCESSION_NOTES), {ABBEYFIELD})

    def test_notice_wording(self):
        text = prior_year_notice("Longhurst Group Limited", 2024, 2026, LONGHURST)
        self.assertIn("Longhurst Group Limited is not in the regulator's 2026", text)
        self.assertIn("from 2024", text)
        self.assertIn(succession_note(LONGHURST), text)
        self.assertIn("Amplius Living", text)

        generic = prior_year_notice("The Abbeyfield Society", 2024, 2026, ABBEYFIELD)
        self.assertIsNone(succession_note(ABBEYFIELD))
        self.assertIn("from 2024", generic)
        self.assertNotIn("None", generic)

    def test_former_names_caption(self):
        names = self.dp.get_provider_history()[(BE_ONE, "LCRA")]["names"]
        self.assertEqual(former_names_caption(names),
                         "Previously reported as Bolton at Home Limited (2024 to 2025).")
        self.assertIsNone(former_names_caption(self.dp.get_provider_history()[(ACIS, "LCRA")]["names"]))

    def test_shipped_copy_has_no_emojis_or_measure_codes(self):
        import re
        texts = [e["note"] for e in PROVIDER_SUCCESSION_NOTES.values()]
        texts.append(prior_year_notice("X", 2024, 2026, LONGHURST))
        for text in texts:
            self.assertIsNone(re.search(r"TP\d\d", text), text)
            self.assertTrue(all(ord(ch) < 0x2190 for ch in text), text)


class OptionLabelTests(unittest.TestCase):
    def setUp(self):
        self.dp = EnhancedTSMDataProcessor()
        self.options = self.dp.get_provider_options()
        self.labels = ExecutiveDashboard.build_provider_option_labels(
            self.options, self.dp.get_provider_history())

    def tearDown(self):
        self.dp.close()

    def test_option_values_are_untouched_and_all_labelled(self):
        self.assertEqual(list(self.labels), self.options)
        for option, label in self.labels.items():
            self.assertTrue(label.startswith(option))

    def test_renamed_provider_is_searchable_by_its_former_name(self):
        self.assertEqual(
            self.labels["Be One Homes - LCRA (4568)"],
            "Be One Homes - LCRA (4568), formerly Bolton at Home Limited")
        self.assertIn("Paradigm Housing Group Limited",
                      self.labels["Lifestone Homes Limited - LCHO (L4215)"])

    def test_unrenamed_provider_label_is_unchanged(self):
        option = "Acis Group Limited - LCRA (L4229)"
        self.assertEqual(self.labels[option], option)
        changed = [o for o, label in self.labels.items() if o != label]
        self.assertEqual(len(changed), 21)


class DialogGateTests(unittest.TestCase):
    def test_opens_once_per_selection(self):
        state = {}
        gate = ExecutiveDashboard.should_open_prior_year_dialog
        self.assertTrue(gate(state, "Longhurst - LCRA (L4277)", True))
        # A rerun for the same selection (e.g. changing a peer filter) does not reopen it.
        self.assertFalse(gate(state, "Longhurst - LCRA (L4277)", True))
        # A different lapsed provider opens it again.
        self.assertTrue(gate(state, "Flagship - LCRA (4651)", True))

    def test_reopens_after_visiting_a_current_provider(self):
        state = {}
        gate = ExecutiveDashboard.should_open_prior_year_dialog
        self.assertTrue(gate(state, "Longhurst - LCRA (L4277)", True))
        self.assertFalse(gate(state, "Acis - LCRA (L4229)", False))
        self.assertTrue(gate(state, "Longhurst - LCRA (L4277)", True))


if __name__ == "__main__":
    unittest.main()
