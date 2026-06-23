# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Tom Stephenson (Teev-dev)

"""Feedback delivery service.

Sends user-submitted data-issue reports and feature requests to the project
maintainers via Resend (https://resend.com).

This is a side-effecting *service* layer — not a data-access or analytics
module. The Streamlit UI (dashboard.py) collects the input and calls
``send_feedback``; every transport concern (API key, sender, error handling)
lives here so the presentation layer stays ignorant of how mail is sent.

Configuration — all via environment variables, surfaced through config.py:

- ``RESEND_API_KEY``      Resend API key. When unset the feature is treated as
                          "not configured": ``send_feedback`` returns a controlled
                          error instead of raising, so the app still runs.
- ``FEEDBACK_FROM_EMAIL`` Verified Resend sender. Defaults to Resend's sandbox
                          sender so the form works the moment a key is added;
                          override once a real domain is verified.
- ``FEEDBACK_TO_EMAIL``   Maintainer inbox that receives the reports.

Privacy: a reporter may optionally supply their own email so we can reply. That
address is forwarded to the maintainer inbox (as the email ``reply_to``) but is
NEVER written to logs — CLAUDE.md forbids PII-adjacent logging. Diagnostic log
lines carry only the report category and provider code.
"""

from __future__ import annotations

import html
import os
import re
from dataclasses import dataclass
from typing import Optional

from config import FEEDBACK_FROM_EMAIL, FEEDBACK_TO_EMAIL, RESEND_API_KEY

# Bounds mirror the input limits enforced in the UI; re-checked here so the
# service is safe to call directly (e.g. from tests) without the form.
MIN_MESSAGE_LEN = 10
MAX_MESSAGE_LEN = 5000
MAX_FIELD_LEN = 200

# Deliberately permissive — we only need to avoid mangling a clearly-broken
# Reply-To header, not police valid-but-unusual addresses.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class FeedbackResult:
    """Outcome of a send attempt. ``user_message`` is always safe to render
    directly in the UI (no internal detail, no escaping needed by the caller)."""

    ok: bool
    user_message: str


def looks_like_email(value: str) -> bool:
    """Best-effort sanity check for an optional reply-to address."""
    return bool(_EMAIL_RE.match((value or "").strip()))


def _log(context: str, exc: Optional[BaseException] = None) -> None:
    """Route diagnostics to stdout/Sentry only — never the UI, never PII."""
    if exc is not None:
        print(f"[feedback] {context}: {type(exc).__name__}")
    else:
        print(f"[feedback] {context}")
    if os.environ.get("SENTRY_DSN") and isinstance(exc, BaseException):
        import sentry_sdk

        sentry_sdk.capture_exception(exc)


def _build_bodies(
    category: str,
    message: str,
    area: str,
    reporter_email: str,
    provider_code: Optional[str],
    dataset_type: Optional[str],
) -> tuple[str, str]:
    """Return ``(html_body, text_body)``. All user-supplied values are
    HTML-escaped in the HTML body per the project's XSS guardrail."""
    provider = provider_code or "Not selected"
    dataset = dataset_type or "Not selected"
    area_display = area.strip() or "Not specified"
    reply_display = reporter_email.strip() or "Not provided"

    rows = [
        ("Type", category),
        ("Measure / section", area_display),
        ("Provider in view", provider),
        ("Dataset", dataset),
        ("Reply to", reply_display),
    ]
    rows_html = "".join(
        f'<tr>'
        f'<td style="padding:4px 12px 4px 0;color:#64748B;white-space:nowrap;'
        f'vertical-align:top;">{html.escape(label)}</td>'
        f'<td style="padding:4px 0;color:#1E293B;">{html.escape(str(value))}</td>'
        f'</tr>'
        for label, value in rows
    )
    message_html = html.escape(message).replace("\n", "<br/>")

    html_body = (
        '<div style="font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;'
        'max-width:560px;color:#1E293B;">'
        '<h2 style="color:#0B5C70;font-size:18px;margin:0 0 4px;">'
        'New TSM dashboard feedback</h2>'
        '<p style="color:#64748B;font-size:13px;margin:0 0 16px;">'
        'Submitted from the HAILIE TSM Insights dashboard.</p>'
        f'<table style="font-size:14px;border-collapse:collapse;margin-bottom:16px;">'
        f'{rows_html}</table>'
        '<div style="border-left:4px solid #0B5C70;background:#F4F8F9;'
        'padding:12px 16px;border-radius:4px;font-size:14px;line-height:1.6;">'
        f'{message_html}</div>'
        '</div>'
    )

    text_lines = [f"{label}: {value}" for label, value in rows]
    text_lines += ["", "Message:", message]
    text_body = "\n".join(text_lines)

    return html_body, text_body


def send_feedback(
    *,
    category: str,
    message: str,
    area: str = "",
    reporter_email: str = "",
    provider_code: Optional[str] = None,
    dataset_type: Optional[str] = None,
) -> FeedbackResult:
    """Send a data-issue report or feature request to the maintainer inbox.

    Returns a :class:`FeedbackResult`; never raises for expected failure modes
    (missing config, transport error, validation) — those become a friendly
    ``ok=False`` message the UI can show as-is.
    """
    message = (message or "").strip()
    area = (area or "").strip()[:MAX_FIELD_LEN]
    reporter_email = (reporter_email or "").strip()[:MAX_FIELD_LEN]

    if len(message) < MIN_MESSAGE_LEN:
        return FeedbackResult(
            False, "Please add a bit more detail before sending — a sentence or two helps."
        )
    if len(message) > MAX_MESSAGE_LEN:
        return FeedbackResult(
            False, "That message is longer than we can accept. Please shorten it and try again."
        )

    if not RESEND_API_KEY:
        _log("send attempted but RESEND_API_KEY is not configured")
        return FeedbackResult(
            False,
            f"The in-app feedback channel isn't switched on yet. "
            f"Please email {FEEDBACK_TO_EMAIL} directly for now — sorry about that.",
        )

    try:
        import resend
    except ImportError as exc:
        _log("resend package not installed", exc)
        return FeedbackResult(
            False, "We couldn't send your report just now. Please try again later."
        )

    resend.api_key = RESEND_API_KEY

    html_body, text_body = _build_bodies(
        category, message, area, reporter_email, provider_code, dataset_type
    )

    context_tag = f" — {provider_code}" if provider_code else ""
    params = {
        "from": FEEDBACK_FROM_EMAIL,
        "to": [FEEDBACK_TO_EMAIL],
        "subject": f"TSM feedback: {category}{context_tag}",
        "html": html_body,
        "text": text_body,
    }
    # Only set a Reply-To we're reasonably sure is a real address, so the
    # maintainer can reply straight to the reporter.
    if looks_like_email(reporter_email):
        params["reply_to"] = reporter_email

    try:
        resend.Emails.send(params)
    except Exception as exc:  # noqa: BLE001 — transport errors must not reach the UI
        _log("resend send failed", exc)
        return FeedbackResult(
            False, "We couldn't send your report just now. Please try again in a few minutes."
        )

    # Log the category and provider code only — never the message or email.
    _log(f"report sent: category={category!r} provider={provider_code or '-'}")
    return FeedbackResult(True, "Thanks — your report's on its way. We read every one.")
