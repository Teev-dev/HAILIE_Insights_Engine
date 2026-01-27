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

## Data Insights Disclaimer

**Important Notice Regarding Analytics and Insights:**

The data, analytics, rankings, and insights provided by HAILIE TSM Insights Engine are intended for informational purposes only and should not be construed as professional advice, recommendations, or endorsements.

**Limitation of Liability:**
- The insights and analytics presented are derived from publicly available TSM (Tenant Satisfaction Measures) data and are subject to the accuracy and completeness of the source data.
- HAILIE TSM Insights Engine, its operators, and affiliates make no warranties, express or implied, regarding the accuracy, reliability, completeness, or suitability of the insights for any particular purpose.
- We are not responsible for any decisions made or actions taken based on the information provided through this platform.
- Rankings, trends, and comparative analyses are statistical interpretations and should be considered alongside other relevant factors and professional judgment.
- Past performance indicators and historical trends do not guarantee future results or outcomes.

**Use at Your Own Risk:**
Users acknowledge that reliance on any insights, data, or analytics provided by this platform is at their own risk. We disclaim all liability for any direct, indirect, incidental, consequential, or special damages arising from the use of or inability to use the insights provided.

**Not Professional Advice:**
The information provided does not constitute legal, financial, regulatory, or professional advice. Users should consult with appropriate qualified professionals before making decisions based on the data presented.

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
