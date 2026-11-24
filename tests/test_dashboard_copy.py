# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Tom Stephenson (Teev-dev)

"""Unit tests for executive-summary help copy and card markup.

Stdlib unittest only - no pytest dependency. Run from the repo root with:

    python -m unittest tests.test_dashboard_copy

app.py, dashboard.py and styles.py are read as text only.
"""

import os
import unittest

from tooltip_definitions import TooltipDefinitions

ROOT = os.path.join(os.path.dirname(__file__), "..")


def _read(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return f.read()


class DashboardOverviewTests(unittest.TestCase):
    def setUp(self):
        self.text = TooltipDefinitions.get_dashboard_overview()

    def test_points_to_dropdown_under_each_card(self):
        self.assertIn("dropdown underneath each card", self.text)

    def test_no_longer_mentions_help_icons(self):
        self.assertNotIn("help icons", self.text)
        self.assertNotIn("(?)", self.text)
        self.assertNotIn("help icons", _read("dashboard.py"))

    def test_names_all_three_insights(self):
        for name in ("Your Rank", "Your Momentum", "Your Priority"):
            self.assertIn(name, self.text)


class CardMarkupTests(unittest.TestCase):
    def test_feature_card_titles_are_not_headings(self):
        # Streamlit attaches an anchor-link icon to every heading element.
        self.assertNotIn('<h3 class="feature-title">', _read("app.py"))

    def test_cards_have_no_hover_effect(self):
        css = _read("styles.py")
        self.assertNotIn(".metric-card:hover", css)
        self.assertNotIn(".feature-card:hover", css)


if __name__ == "__main__":
    unittest.main()
