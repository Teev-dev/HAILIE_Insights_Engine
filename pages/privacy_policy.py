import streamlit as st

st.set_page_config(
    page_title="Privacy Policy | HAILIE TSM Insights",
    page_icon="🔒",
    layout="centered"
)

st.title("🔒 Privacy Policy")

st.markdown("""
**Last Updated:** January 2026

---

## Introduction

Welcome to HAILIE TSM Insights Engine. We are committed to protecting your privacy and ensuring the security of any information you provide while using our service. This Privacy Policy explains how we collect, use, and safeguard your information. HAILIE is an independent, vendor-neutral initiative. There are no sales pitches or hidden agendas.

---

## Information We Collect

### Automatically Collected Information
When you use our analytics platform, we may automatically collect:
- Browser type and version
- Device type (mobile/desktop)
- Session duration and interaction patterns
- Anonymized usage statistics for service improvement

### Information You Provide
- Provider selection preferences
- Search queries within the application
- Any feedback or communications you submit

---

## How We Use Your Information

We use the collected information to:
- Provide and improve our analytics services
- Enhance user experience and platform performance
- Generate aggregated, anonymized insights about service usage
- Respond to your inquiries and support requests

---

## Data Security

We implement appropriate technical and organizational measures to protect your information, including:
- Secure data transmission protocols
- Access controls and authentication measures
- Regular security assessments and updates

---

## Data Retention

We retain usage data only for as long as necessary to provide our services and fulfill the purposes outlined in this policy. Anonymized aggregate data may be retained indefinitely for analytical purposes.

---

## Third-Party Services

Our platform may utilize third-party services for:
- Hosting and infrastructure
- Analytics and performance monitoring

These providers are bound by their own privacy policies and data protection obligations.

---

## Your Rights

You have the right to:
- Request information about data we hold about you
- Request correction of inaccurate information
- Request deletion of your data where applicable
- Withdraw consent for data processing

---

## Cookies and Tracking

Our application may use session cookies to:
- Maintain your session state
- Remember your preferences during a session
- Improve service performance

---

## Changes to This Policy

We may update this Privacy Policy from time to time. Any changes will be posted on this page with an updated revision date.

---

## Contact Us

If you have questions or concerns about this Privacy Policy or our data practices, please contact the HAILIE TSM Insights team.

---

""")

st.markdown("---")
st.caption("HAILIE TSM Insights Engine | Privacy Policy")

if st.button("← Back to Dashboard"):
    st.switch_page("app.py")
