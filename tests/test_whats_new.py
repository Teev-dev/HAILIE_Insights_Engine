# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Tom Stephenson (Teev-dev)

"""Unit tests for the "What's new" notice.

Stdlib unittest only - no pytest dependency. Run from the repo root with:

    python -m unittest tests.test_whats_new

app.py is read as text only (it runs Streamlit at import time).
"""

import os
import re
import unittest

from tooltip_definitions import WHATS_NEW_MESSAGE


class WhatsNewMessageTests(unittest.TestCase):
    def test_mentions_2026(self):
        self.assertIn("2026", WHATS_NEW_MESSAGE)

    def test_contains_no_emoji(self):
        self.assertTrue(all(ord(c) < 0x2600 for c in WHATS_NEW_MESSAGE))
        self.assertNotIn("\ufe0f", WHATS_NEW_MESSAGE)

    def test_contains_no_measure_codes(self):
        self.assertIsNone(
            re.search(r"\bTP\s?\d{1,2}\b", WHATS_NEW_MESSAGE, re.IGNORECASE)
        )

    def test_does_not_mention_dataset_type_jargon(self):
        self.assertNotIn("LCRA", WHATS_NEW_MESSAGE)
        self.assertNotIn("LCHO", WHATS_NEW_MESSAGE)

    def test_has_between_one_and_four_bullets(self):
        bullets = [
            line for line in WHATS_NEW_MESSAGE.splitlines() if line.startswith("- ")
        ]
        self.assertGreaterEqual(len(bullets), 1)
        self.assertLessEqual(len(bullets), 4)


class AppSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.path.join(os.path.dirname(__file__), "..", "app.py")
        with open(path, encoding="utf-8") as f:
            cls.source = f.read()

    def test_loaded_banner_removed(self):
        self.assertNotIn("analytics for provider", self.source)

    def test_no_st_success_loaded(self):
        self.assertNotIn('st.success(f"Loaded', self.source)

    def test_notice_wired_to_constant(self):
        self.assertIn("WHATS_NEW_MESSAGE", self.source)


if __name__ == "__main__":
    unittest.main()
