# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Tom Stephenson (Teev-dev)

"""Unit tests for feedback_service.

Stdlib unittest only — no pytest dependency. Run from the repo root with:

    python -m unittest tests.test_feedback_service

The real Resend SDK is never imported: a fake module is injected into
sys.modules so ``import resend`` inside send_feedback() resolves to the stub.
"""

import sys
import types
import unittest
from unittest import mock

import feedback_service
from feedback_service import looks_like_email, send_feedback


def _install_fake_resend(send_impl):
    """Register a stub ``resend`` module whose Emails.send calls send_impl."""
    module = types.ModuleType("resend")
    module.api_key = None

    class _Emails:
        @staticmethod
        def send(params):
            return send_impl(params)

    module.Emails = _Emails
    sys.modules["resend"] = module
    return module


class LooksLikeEmailTests(unittest.TestCase):
    def test_accepts_plausible_addresses(self):
        self.assertTrue(looks_like_email("guy@housingai.org"))
        self.assertTrue(looks_like_email("  a.b-c@sub.example.co.uk  "))

    def test_rejects_broken_addresses(self):
        for bad in ["", "nope", "a@b", "a b@c.d", "@x.y", "x@y."]:
            self.assertFalse(looks_like_email(bad), bad)


class SendFeedbackValidationTests(unittest.TestCase):
    def test_blank_message_is_rejected_without_sending(self):
        result = send_feedback(category="Source data looks wrong", message="   ")
        self.assertFalse(result.ok)
        self.assertIn("more detail", result.user_message)

    def test_overlong_message_is_rejected(self):
        result = send_feedback(
            category="Feature request or something else",
            message="x" * (feedback_service.MAX_MESSAGE_LEN + 1),
        )
        self.assertFalse(result.ok)
        self.assertIn("shorten", result.user_message)


class SendFeedbackConfigTests(unittest.TestCase):
    def test_missing_api_key_returns_friendly_message(self):
        with mock.patch.object(feedback_service, "RESEND_API_KEY", ""), \
                mock.patch.object(feedback_service, "FEEDBACK_TO_EMAIL", "guy@housingai.org"):
            result = send_feedback(
                category="Source data looks wrong",
                message="The repairs number looks far too high for us.",
            )
        self.assertFalse(result.ok)
        self.assertIn("guy@housingai.org", result.user_message)


class SendFeedbackSendTests(unittest.TestCase):
    def tearDown(self):
        sys.modules.pop("resend", None)

    def test_successful_send_builds_expected_params(self):
        captured = {}
        _install_fake_resend(lambda params: captured.update(params) or {"id": "abc"})

        with mock.patch.object(feedback_service, "RESEND_API_KEY", "re_test"), \
                mock.patch.object(feedback_service, "FEEDBACK_FROM_EMAIL", "from@x.org"), \
                mock.patch.object(feedback_service, "FEEDBACK_TO_EMAIL", "to@x.org"):
            result = send_feedback(
                category="A calculation or ranking looks off",
                message="Our rank dropped but the scores are identical.",
                reporter_email="reporter@org.uk",
                provider_code="LH3827",
                dataset_type="LCRA",
            )

        self.assertTrue(result.ok)
        self.assertEqual(captured["from"], "from@x.org")
        self.assertEqual(captured["to"], ["to@x.org"])
        self.assertEqual(captured["reply_to"], "reporter@org.uk")
        self.assertIn("LH3827", captured["subject"])
        # Provider context and message both reach the body.
        self.assertIn("LH3827", captured["text"])
        self.assertIn("LCRA", captured["text"])
        self.assertIn("identical", captured["text"])

    def test_invalid_reporter_email_omits_reply_to(self):
        captured = {}
        _install_fake_resend(lambda params: captured.update(params) or {"id": "abc"})

        with mock.patch.object(feedback_service, "RESEND_API_KEY", "re_test"):
            result = send_feedback(
                category="The data looks out of date",
                message="This still shows last year's figures.",
                reporter_email="not-an-email",
            )

        self.assertTrue(result.ok)
        self.assertNotIn("reply_to", captured)

    def test_html_body_escapes_user_input(self):
        captured = {}
        _install_fake_resend(lambda params: captured.update(params) or {"id": "abc"})

        with mock.patch.object(feedback_service, "RESEND_API_KEY", "re_test"):
            send_feedback(
                category="Feature request or something else",
                message="<script>alert('x')</script> please fix",
            )

        self.assertNotIn("<script>", captured["html"])
        self.assertIn("&lt;script&gt;", captured["html"])

    def test_transport_error_returns_friendly_message(self):
        def _boom(params):
            raise RuntimeError("network down")

        _install_fake_resend(_boom)

        with mock.patch.object(feedback_service, "RESEND_API_KEY", "re_test"):
            result = send_feedback(
                category="Source data looks wrong",
                message="Something is clearly wrong with this figure.",
            )

        self.assertFalse(result.ok)
        self.assertIn("couldn't send", result.user_message)


if __name__ == "__main__":
    unittest.main()
