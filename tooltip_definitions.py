# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Tom Stephenson (Teev-dev)

"""
Tooltip definitions for complex data metrics in the HAILIE TSM Dashboard
"""

# Dismissible "What's new" notice shown above the executive summary (app.py).
WHATS_NEW_MESSAGE = """\
**What's new**: the 2026 results are here.
- Your dashboard now uses the 2026 tenant satisfaction results, so your ranking, scores and top priority all reflect the latest data.
- Momentum now shows how your 2026 results compare with 2025, where results are available for both years.
- Labels on the Priority Matrix chart are now placed so they no longer overlap each other, the points or the quadrant labels.
- You can now narrow your peer group to landlords of a similar size or region, and compare up to three providers side by side.
"""

# ---------------------------------------------------------------------------
# Providers that are no longer in the latest year of data
# ---------------------------------------------------------------------------
#
# Landlords that have left the regulator's dataset stay selectable and are
# shown with their most recent results. Where the reason is a merger, the
# notice says so and names the landlord that now reports. Keyed by provider
# code; successor_code is the provider code the combined landlord reports
# under, which must be present in the latest year of data.
#
# Hand-maintained. tests/test_prior_year_providers.py fails at the next data
# refresh if an entry has gone stale or a newly lapsed provider has no entry
# (see MAINTENANCE.md). Each sentence was checked against the trade press or
# the regulator's register in November 2026; sources are in the comments.
PROVIDER_SUCCESSION_NOTES = {
    # insidehousing.co.uk/news/essex-based-landlords-make-merger-official-96536
    'L3535': {
        'successor_code': 'L4331',
        'note': "Estuary Housing Association merged with Chelmer Housing Partnership in spring 2026 "
                "to form Delta Housing. The combined landlord is listed as Delta Housing Limited.",
    },
    # insidehousing.co.uk/news/bromford-and-flagship-complete-merger-90757
    # insidehousing.co.uk/news/bromford-flagship-and-livewest-confirm-merger-completion-95463
    '4651': {
        'successor_code': 'L4449',
        'note': "Flagship merged with Bromford in February 2025, and the group merged with LiveWest "
                "in January 2026. The combined landlord is listed as Bromford Flagship LiveWest Limited.",
    },
    # insidehousing.co.uk/news/merger-to-create-37000-home-landlord-completes-89811
    'L4277': {
        'successor_code': '5060',
        'note': "Longhurst Group merged with Grand Union Housing Group in December 2024. "
                "The combined landlord is listed as Amplius Living.",
    },
    # abri.co.uk/media-hub/abri-completes-partnership-with-octavia
    'L0717': {
        'successor_code': 'L4172',
        'note': "Octavia Housing joined Abri Group in December 2024. "
                "The group is listed as Abri Group Limited.",
    },
    # placesforpeople.co.uk/news/all-news/origin-housing-now-fully-integrated-into-places-for-people
    'L0871': {
        'successor_code': 'L4236',
        'note': "Origin Housing joined Places for People in April 2024 and was fully integrated "
                "in April 2026. The group is listed as Places for People Group Limited.",
    },
    # insidehousing.co.uk/news/new-27000-home-group-created-as-landlords-complete-merger-94424
    # gov.uk/government/publications/paradigm-housing-group-limited (renamed Lifestone Homes Limited)
    'L4370': {
        'successor_code': 'L4215',
        'note': "Settle merged with Paradigm Housing Group in October 2025. "
                "The combined landlord is listed as Lifestone Homes Limited.",
    },
    # housingtoday.co.uk/news/shepherds-bush-folded-into-guinness-as-full-merger-completes/5135253.article
    'LH0050': {
        'successor_code': '4729',
        'note': "Shepherds Bush Housing Association joined The Guinness Partnership in December 2023 "
                "and transferred to it fully in March 2025. "
                "The group is listed as The Guinness Partnership Limited.",
    },
    # abri.co.uk/media-hub/abri-and-silva-complete-partnership
    'L4513': {
        'successor_code': 'L4172',
        'note': "Silva Homes joined Abri Group in October 2023. "
                "The group is listed as Abri Group Limited.",
    },
    # housingtoday.co.uk/news/mtvh-changes-parent-company-in-move-to-simplify-structure/5133641.article
    'L0514': {
        'successor_code': 'L0726',
        'note': "Thames Valley Housing Association is part of Metropolitan Thames Valley Housing. "
                "Following a structural change on 31 December 2024, the charitable Metropolitan "
                "Housing Trust became the parent company, with Thames Valley Housing Association "
                "operating as a subsidiary. The group is listed as Metropolitan Housing Trust Limited.",
    },
    # insidehousing.co.uk/news/housing-associations-complete-merger-to-form-33000-home-landlord-89927
    'LH4220': {
        'successor_code': 'L4491',
        'note': "The Wrekin Housing Group merged with Housing Plus Group in January 2025. "
                "The combined landlord is listed as The Housing Plus Group Limited.",
    },
    # hyde-housing.co.uk/news/corporate-and-financial/tower-hamlets-community-housing-thch-joins-the-hyde-group
    'L4260': {
        'successor_code': 'LH0032',
        'note': "Tower Hamlets Community Housing joined the Hyde Group in April 2025. "
                "The group is listed as Hyde Housing Association Limited.",
    },
}


def succession_note(provider_code):
    """The merger sentence for a provider that has left the data, or None."""
    entry = PROVIDER_SUCCESSION_NOTES.get(provider_code)
    return entry['note'] if entry else None


def prior_year_dialog_title(current_year):
    """Title of the notice shown when a provider has no results for the latest year."""
    return f"No {current_year} results for this provider"


def prior_year_notice(provider_name, data_year, current_year, provider_code=None):
    """Notice shown when a provider's most recent results are from an earlier year."""
    text = (
        f"{provider_name} is not in the regulator's {current_year} tenant satisfaction data. "
        f"You are seeing its most recent results, from {data_year}. "
        f"Its rank and comparisons use other landlords' {data_year} results."
    )
    note = succession_note(provider_code)
    return f"{text}\n\n{note}" if note else text


def comparison_unavailable_notice(provider_name, latest_year, current_year, provider_code=None):
    """Message above a comparison card for a provider with no results for the latest year."""
    text = f"{provider_name} has no {current_year} results, so it is not part of this comparison."
    if latest_year:
        text += (f" Its most recent results are from {latest_year}: "
                 "choose Single provider to see them.")
    note = succession_note(provider_code)
    return f"{text} {note}" if note else text


def former_names_caption(names):
    """
    Caption naming the earlier names of a renamed provider, or None.

    names: oldest first, each {'name', 'first_year', 'last_year'}; the last
    entry is the current name.
    """
    former = names[:-1] if names else []
    if not former:
        return None

    def describe(entry):
        if entry['first_year'] == entry['last_year']:
            return f"{entry['name']} ({entry['first_year']})"
        return f"{entry['name']} ({entry['first_year']} to {entry['last_year']})"

    parts = [describe(entry) for entry in former]
    listed = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
    return f"Previously reported as {listed}."


class TooltipDefinitions:
    """
    Centralized tooltip definitions for all complex metrics and technical terms
    """

    @staticmethod
    def get_dashboard_overview():
        """Text for the "Understanding Your Dashboard" expander."""
        return """
**Your dashboard shows three key insights:**

- **Your Rank**: how you compare with other housing providers
- **Your Momentum**: how your results have changed since last year
- **Your Priority**: the most important area to focus on

For a fuller explanation, open the dropdown underneath each card.
"""

    @staticmethod
    def get_peer_group_intro():
        """Caption above the peer group size / region selectors."""
        return ("By default the comparison is with every provider that reports the same "
                "measures. Narrow it to landlords of a similar size or region if that is a "
                "fairer benchmark.")

    @staticmethod
    def get_peer_group_help():
        """Text for the "How peer groups work" expander."""
        return """
**Where size and region come from**

Both are published by the Regulator of Social Housing alongside each landlord's results:

- **Size** is the landlord group's size band, by number of homes owned.
- **Region** is the landlord's predominant region. Landlords spread across several regions are recorded as **Mixed**.

**What changes when you narrow the peer group**

- **Your Rank**, your percentiles and the peer averages are recalculated using only the landlords in the group you chose, plus you.
- **Your Priority** uses your position within that group to judge where you have most room to improve.
- **Your Momentum** does not change. It compares your own results with last year's.
- The link between each measure and overall satisfaction is still measured across all landlords, because a small group is not enough to measure it reliably.

**Small groups**

If a group would contain too few landlords, a single result could move everyone's position sharply. In that case the full peer group is used instead and the dashboard tells you so.
"""

    @staticmethod
    def get_comparison_overview():
        """Text for the "Understanding the comparison" expander."""
        return """
**Compare two or three providers side by side**

This view is for executives responsible for more than one registered provider.

- Every provider is ranked within the **same peer group**, so positions can be read across the columns.
- **Scores** are each provider's published results. **Percentiles** show where each provider sits within the peer group.
- Providers must report the same set of measures to be compared. Rented-housing results and shared-ownership results are measured differently, so they cannot be placed side by side.
- For the full analysis of any one provider, switch back to the single provider view.
"""

    @staticmethod
    def get_metric_tooltips():
        """Get tooltips for main dashboard metrics"""
        return {
            'ranking': {
                'title':
                'Your Rank Explained',
                'content':
                """
                **How ranking works:**
                • Based on your average score across all TSM satisfaction measures (TP01-TP12)
                • Compares you against all other housing providers in the dataset
                • Higher satisfaction scores = better ranking
                
                **Quartile meanings:**
                • **Top Quartile (Green)**: Top 25% of providers - excellent performance
                • **High Quartile (Light Green)**: 50-75% range - above average performance  
                • **Mid Quartile (Orange)**: 25-50% range - below average performance
                • **Low Quartile (Red)**: Bottom 25% - needs immediate improvement
                
                **Percentile**: Shows exactly where you rank - 90th percentile means you perform better than 90% of providers
                """
            },
            'momentum': {
                'title':
                'Your Momentum Explained',
                'content':
                """
                **What momentum shows:**
                • Tracks your performance trajectory over the past 12 months
                • Compares your trend against peer averages
                • Identifies if you're improving, stable, or declining
                
                **Status meanings:**
                • **↗️ Improving**: Your scores are trending upward consistently
                • **→ Stable**: Performance remains consistent with minimal change
                • **↘️ Declining**: Scores show a downward trend requiring attention
                
                **Note**: Momentum compares your latest year against the prior year. Providers with data in both years will see full trajectory analysis.
                """
            },
            'priority': {
                'title':
                'Your Priority Explained',
                'content':
                """
                **How priority is calculated:**
                • Combines improvement potential with correlation to overall satisfaction (TP01)
                • Higher potential + stronger correlation = higher priority
                • Identifies where effort will have maximum impact
                
                **Priority levels:**
                • **Critical**: >70 weighted score - immediate action needed
                • **High**: 50-70 score - high impact improvement area
                • **Medium**: 30-50 score - moderate impact area
                • **Low**: <30 score - lower impact area
                
                **Improvement potential**: How much you could improve based on peer performance (100% - your percentile)
                **TP01 correlation**: How strongly this measure relates to overall satisfaction
                """
            }
        }

    @staticmethod
    def get_technical_tooltips():
        """Get tooltips for technical terms"""
        return {
            'percentile': {
                'title':
                'Percentile Ranking',
                'content':
                """
                **What percentile means:**
                • Shows what percentage of providers you perform better than
                • 75th percentile = you perform better than 75% of providers
                • Higher percentiles = better relative performance
                
                **Example**: If you're at the 80th percentile for repairs satisfaction, you perform better than 80% of all housing providers for repairs.
                """
            },
            'correlation': {
                'title':
                'Correlation with Overall Satisfaction',
                'content':
                """
                **What correlation shows:**
                • Measures how strongly each satisfaction area relates to overall satisfaction (TP01)
                • Ranges from -1 to +1 (stronger correlations closer to +1 or -1)
                • Helps identify which areas have biggest impact on tenant satisfaction
                
                **Correlation strength:**
                • **Strong (>0.7)**: Major impact on overall satisfaction
                • **Moderate (0.4-0.7)**: Noticeable impact
                • **Weak (<0.4)**: Limited impact
                
                **Why it matters**: Focus on areas with strong correlations for maximum impact on tenant satisfaction.
                """
            },
            'improvement_potential': {
                'title':
                'Improvement Potential',
                'content':
                """
                **How improvement potential is calculated:**
                • Based on the gap between your performance and top-performing providers
                • Higher percentages = more room for improvement
                • Calculated as: 100% - your current percentile
                
                **Example**: If you're at 40th percentile, your improvement potential is 60%
                
                **Why it matters**: Shows realistic improvement targets based on what other providers achieve.
                """
            },
            'weighted_priority': {
                'title':
                'Weighted Priority Score',
                'content':
                """
                **How weighted priority works:**
                • Combines improvement potential × correlation strength with overall satisfaction
                • Identifies areas where improvement will have maximum impact
                • Higher scores = higher priority for action
                
                **Formula**: (Improvement Potential × 0.6) + (Correlation Strength × 100 × 0.4)
                
                **Why this matters**: Helps you focus limited resources on areas that will improve overall tenant satisfaction most effectively.
                """
            },
            'quartile': {
                'title':
                'Quartile Performance Bands',
                'content':
                """
                **Quartile system:**
                • Divides all providers into 4 equal groups based on performance
                • Each quartile represents 25% of providers
                
                **Performance bands:**
                • **1st Quartile (Top)**: Best 25% of providers
                • **2nd Quartile (High)**: Next 25% (above average)
                • **3rd Quartile (Mid)**: Next 25% (below average)  
                • **4th Quartile (Low)**: Bottom 25% of providers
                
                **Color coding**: Green (top), Light Green, Orange, Red (bottom)
                """
            },
            'tp_measures': {
                'title':
                'TSM Satisfaction Measures (TP01-TP12)',
                'content':
                """
                **What TSM measures are:**
                • Official UK government Tenant Satisfaction Measures
                • 12 key areas of housing provider performance
                • Based on annual tenant surveys
                
                **The 12 measures:**
                • **TP01**: Overall satisfaction (primary measure)
                • **TP02**: Satisfaction with the overall repairs service
                • **TP03**: Satisfaction with the time taken to complete most recent repair
                • **TP04**: Satisfaction that the home is well maintained
                • **TP05**: Satisfaction that the home is safe
                • **TP06**: Landlord listens to tenant views and acts upon them
                • **TP07**: Landlord keeps tenants informed
                • **TP08**: Landlord treats tenants fairly and with respect
                • **TP09**: Landlord's approach to complaints handling
                • **TP10**: Communal areas kept clean and well maintained
                • **TP11**: Landlord makes a positive contribution to the neighbourhood
                • **TP12**: Landlord's approach to handling anti-social behaviour
                """
            },
            'peer_comparison': {
                'title':
                'Peer Comparison',
                'content':
                """
                **How peer comparison works:**
                • Compares your performance against similar housing providers
                • Can be filtered by provider size, region, or type
                • Shows where you stand relative to your peer group
                
                **Peer average**: The average score of all providers in your comparison group
                **Gap**: The difference between your score and the peer average
                • Positive gap = above peer average
                • Negative gap = below peer average
                
                **Why peer comparison matters**: More relevant than comparing against all providers - focuses on achievable benchmarks.
                """
            }
        }

    @staticmethod
    def get_chart_tooltips():
        """Get enhanced tooltip templates for charts"""
        return {
            'performance_comparison':
            """
            <b>%{fullData.name}</b><br>
            <b>%{x}</b><br>
            Score: %{y:.1f}<br>
            <extra></extra>
            """,
            'correlation_chart':
            """
            <b>%{y}</b><br>
            Correlation: %{x:.3f}<br>
            Strength: %{customdata[0]}<br>
            Sample Size: %{customdata[1]} providers<br>
            P-Value: %{customdata[2]:.4f}<br>
            <extra></extra>
            """,
            'priority_matrix':
            """
            <b>%{text}</b><br>
            <b>%{customdata[0]}</b><br>
            Improvement Potential: %{x:.1f}%<br>
            TP01 Correlation: %{y:.1f}%<br>
            Weighted Priority: %{customdata[1]:.1f}<br>
            Current Percentile: %{customdata[2]:.1f}%<br>
            <extra></extra>
            """
        }

    @staticmethod
    def get_help_icon_html(tooltip_key: str, definitions_dict: dict) -> str:
        """Generate HTML for help icon with tooltip"""
        if tooltip_key not in definitions_dict:
            return ""

        tooltip_data = definitions_dict[tooltip_key]

        # Clean up the tooltip content for HTML
        clean_content = tooltip_data['content'].replace('"', '&quot;').replace(
            '\n', '&#10;')

        html_template = f"""
        <span style="position: relative; display: inline-block; margin-left: 5px;">
            <span style="
                display: inline-block;
                width: 16px;
                height: 16px;
                background-color: #64748B;
                color: white;
                border-radius: 50%;
                text-align: center;
                font-size: 12px;
                line-height: 16px;
                cursor: help;
                font-weight: bold;
                vertical-align: middle;
            " title="{clean_content}">?</span>
        </span>
        """
        return html_template

    @staticmethod
    def get_streamlit_help_text(tooltip_key: str,
                                definitions_dict: dict) -> str:
        """Get formatted help text for Streamlit help parameter"""
        if tooltip_key not in definitions_dict:
            return ""

        tooltip_data = definitions_dict[tooltip_key]
        return tooltip_data['content'].strip()
