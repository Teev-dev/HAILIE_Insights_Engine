# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Tom Stephenson (Teev-dev)

from enum import Enum
import html
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from typing import Dict, Any
from tooltip_definitions import (
    TooltipDefinitions,
    comparison_unavailable_notice,
    former_names_caption,
    prior_year_dialog_title,
    prior_year_notice,
)
from mobile_utils import detect_mobile, mobile_friendly_columns, should_show_component

class Direction(Enum):
    """Enum for storing possible directions for labels in
    the priority matrix scatterplot. The order given here
    is from most preferred placement to least."""
    TOP_MIDDLE = 1
    BOTTOM_MIDDLE = 2
    TOP_RIGHT = 3
    TOP_LEFT = 4
    MIDDLE_RIGHT = 5
    MIDDLE_LEFT = 6
    BOTTOM_RIGHT = 7
    BOTTOM_LEFT = 8


def _report_internal_error(context: str, payload: Any = None) -> None:
    """Route error details to Sentry/stdout only — never to the UI."""
    if payload is not None:
        print(f"[ERROR] {context}: {payload!r}")
    else:
        print(f"[ERROR] {context}")
    if os.environ.get("SENTRY_DSN") and isinstance(payload, BaseException):
        import sentry_sdk
        sentry_sdk.capture_exception(payload)


def _corr_label(strength: float) -> str:
    """Qualitative label for a correlation coefficient (absolute value)."""
    s = abs(strength)
    if s >= 0.70:
        return "Strong"
    if s >= 0.40:
        return "Moderate"
    if s >= 0.20:
        return "Weak"
    return "Negligible"


def _ordinal(value: float) -> str:
    """Whole-number ordinal for display, e.g. 21.4 -> '21st'."""
    n = int(round(value))
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _add_point_labels(fig: go.Figure, xs: list[float], ys: list[float], labels: list[str]):
    """ Add labels to the priority matrix scatterplot points. 
    Collision avoidance is implemented by defining bounding boxes around each point,
    the quadrant labels, and each text label as they are generated. If a potential label's
    box overlaps any of the other boxes, we reject that placement and consider the next possibility.
    Boxes are given as 2D lists where the first element is the coordinates of the bottom left
    corner, and the second the coordinates of the top right corner"""
    point_boxes = [[[x-0.5, y-1], [x+0.5, y+1]] for x, y in zip(xs, ys)] +\
                  [[[70, 73], [80, 77]], [[20, 73], [30, 77]], [[70, 23], [80, 27]], [[20, 23], [30, 27]]] # quadrant labels


    def dir_to_coord(p: list[float], direction: Direction) -> list[float]:
        """
        Given a point and a direction for the label, returns the label's coordinates
        """
        if direction == Direction.TOP_MIDDLE:
            return [p[0], p[1] + 3]
        elif direction == Direction.TOP_RIGHT:
            return [p[0] + 2, p[1] + 3]
        elif direction == Direction.MIDDLE_RIGHT:
            return [p[0] + 2, p[1]]
        elif direction == Direction.BOTTOM_RIGHT:
            return [p[0] + 2, p[1] - 3]
        elif direction == Direction.BOTTOM_MIDDLE:
            return [p[0], p[1] - 3]
        elif direction == Direction.BOTTOM_LEFT:
            return [p[0] - 2, p[1] - 3]
        elif direction == Direction.MIDDLE_LEFT:
            return [p[0] - 2, p[1]]
        elif direction == Direction.TOP_LEFT:
            return [p[0] - 2, p[1] + 3]


    def draw_label(p, priority:list, boxes: list, label: str):
        """
        Recursive function for drawing labels
        priority is a list of Direction (TOP_MIDDLE, MIDDLE_RIGHT, etc.) we pop the first item from this list,
        and try to draw the label in that position. If that causes a collision with another label or point,
        we call this function again, trying a different position.
        If priority is empty, there is nowhere for the label to be drawn so we give up and draw the label
        above the point (TOP_MIDDLE). This is an arbitrary choice.
        Given that we only have 12 points, and 8 possible directions, it is unlikely that we will ever encounter an issue.
        """
        if priority == []:
            # This branch is entered only if all possible label placements result in collisions
            # Default to drawing the label in the top middle
            fig.add_annotation(x=p[0], y=p[1]+3, text=label, showarrow=False, font=dict(size=11, color="#1F2933"))
            return

        label_location = dir_to_coord(p, priority.pop(0))
        # Create a 3x3 bounding box around this label
        new_label_box = [[label_location[0]-1.5, label_location[1]-1.5], [label_location[0]+1.5, label_location[1]+1.5]]
        for box in boxes:
            # Check if the new label box overlaps this box OR if the new label would overlap one of the quadrant separating lines
            if (box[0][0] < new_label_box[1][0] and box[1][0] > new_label_box[0][0] and \
                box[1][1] > new_label_box[0][1] and box[0][1] < new_label_box[1][1]) or \
                new_label_box[0][0] <= 50 <= new_label_box[1][0] or \
                new_label_box[0][1] <= 50 <= new_label_box[1][1]:
                draw_label(p, priority, boxes, label)
                return
        # Draw label
        fig.add_annotation(x=label_location[0], y=label_location[1], text=label, showarrow=False, font=dict(size=11, color="#1F2933"))
        # Add this label's bounding box to the box list
        boxes.append(new_label_box)


    # Iteratively create labels
    for label, point in zip(labels, zip(xs, ys)):
        priority = [d for d in Direction]
        draw_label(point, priority, point_boxes, label)
    

PLOTLY_LAYOUT = dict(
    font=dict(
        family='-apple-system, BlinkMacSystemFont, Inter, Segoe UI, sans-serif',
        size=12,
        color='#1F2933',
    ),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(250,250,250,1)',
    margin=dict(l=60, r=20, t=50, b=60),
)


def _prior_year_dialog_body(message: str, button_label: str):
    """Contents of the notice for a provider with no results for the latest year."""
    st.write(message)
    if st.button(button_label, type="primary"):
        st.rerun()


class ExecutiveDashboard:
    """
    Renders the executive dashboard with key metrics
    """

    # ------------------------------------------------------------------
    # Providers with no results for the latest year
    # ------------------------------------------------------------------

    PRIOR_YEAR_DIALOG_STATE_KEY = "prior_year_notice_shown_for"

    @staticmethod
    def should_open_prior_year_dialog(state, selection_key: str, is_prior_year: bool) -> bool:
        """
        Decide whether to open the prior-year notice on this run.

        It opens once each time a provider without latest-year results is
        selected, not on every rerun (changing a peer filter reruns the page).
        Selecting a provider that has latest-year results resets it, so going
        back to the earlier provider shows the notice again. state is
        st.session_state, or any dict in tests.
        """
        key = ExecutiveDashboard.PRIOR_YEAR_DIALOG_STATE_KEY
        if not is_prior_year:
            if key in state:
                del state[key]
            return False
        if state.get(key) == selection_key:
            return False
        state[key] = selection_key
        return True

    def render_prior_year_dialog(self, provider_name: str, data_year: int, current_year: int,
                                 provider_code: str | None = None):
        """Open the dialog telling the user this provider has no latest-year results."""
        message = prior_year_notice(
            self._strip_dataset_suffix(provider_name), data_year, current_year, provider_code)
        dialog = st.dialog(prior_year_dialog_title(current_year))(_prior_year_dialog_body)
        dialog(message, f"Show {data_year} results")

    def render_prior_year_notice(self, provider_name: str, data_year: int, current_year: int,
                                 provider_code: str | None = None):
        """Persistent on-page version of the prior-year notice (stays after the dialog closes)."""
        st.warning(prior_year_notice(
            self._strip_dataset_suffix(provider_name), data_year, current_year, provider_code))

    def render_former_names(self, names: list | None):
        """Caption naming a renamed provider's earlier names; nothing if it was never renamed."""
        caption = former_names_caption(names or [])
        if caption:
            st.caption(caption)

    @staticmethod
    def build_provider_option_labels(options: list, history: Dict) -> Dict[str, str]:
        """
        Display label for each provider dropdown option.

        Options look like "Name - LCRA (CODE)" and are returned unchanged as
        the keys, so everything that parses them keeps working. A provider the
        regulator kept under one code through a rename gets its earlier names
        appended to the label, so searching for the old name still finds it.
        history is EnhancedTSMDataProcessor.get_provider_history().
        """
        labels = {}
        for option in options:
            label = option
            if option.endswith(")") and " (" in option:
                name_part, code = option[:-1].rsplit(" (", 1)
                for suffix in ("LCRA", "LCHO", "COMBINED"):
                    if name_part.endswith(f" - {suffix}"):
                        names = history.get((code, suffix), {}).get('names', [])
                        former = [n['name'] for n in reversed(names[:-1])]
                        if former:
                            label = f"{option}, formerly {', '.join(former)}"
                        break
            labels[option] = label
        return labels

    def render_executive_summary(self, provider_code: str, rankings: Dict, momentum: Dict, priority: Dict, include_confidence: bool = True, provider_name: str | None = None):
        """
        Render the main executive summary with three key metrics
        """
        # Get tooltip definitions
        tooltips = TooltipDefinitions()
        metric_tooltips = tooltips.get_metric_tooltips()
        technical_tooltips = tooltips.get_technical_tooltips()

        # Check if mobile
        is_mobile = detect_mobile()

        # Human-readable provider label: "Name (CODE)" when the name is known,
        # falling back to the bare code. provider_code stays the key for all
        # data lookups below — only the heading text changes.
        provider_display = f"{provider_name} ({provider_code})" if provider_name else provider_code

        st.markdown("## Executive Summary")
        st.markdown(f"**Provider:** {provider_display}")

        if not is_mobile:
            # Overall help for the executive summary. Full width so it lines
            # up with the outer edges of the three-card grid below.
            with st.expander("Understanding Your Dashboard", expanded=False):
                st.markdown(tooltips.get_dashboard_overview())
        else:
            st.markdown("---")

        # Check for errors
        if "error" in rankings:
            _report_internal_error("rankings error", rankings.get("error"))
            st.error("We couldn't calculate your rank right now. Try another provider or refresh.")
            return

        if "error" in momentum:
            _report_internal_error("momentum error", momentum.get("error"))
            st.error("Momentum data is unavailable right now. Please try again later.")
            return

        if "error" in priority:
            _report_internal_error("priority error", priority.get("error"))
            st.error("We couldn't identify a priority measure. Try another provider or refresh.")
            return

        # Get provider data
        if provider_code not in rankings:
            st.error(f"No ranking data found for provider {provider_code}")
            return

        provider_ranking = rankings[provider_code]

        # Lay the key metrics out on a three-column grid: one row of cards,
        # then one row of "how it works" expanders, so the expanders line up
        # whatever the height of the card above them.
        if is_mobile:
            # Mobile: single column, each card followed by its own expander
            cols = [st.container(), st.container(), st.container()]
            help_cols = cols
        else:
            cols = st.columns(3, gap="medium")
            help_cols = st.columns(3, gap="medium")

        # YOUR RANK
        with cols[0]:
            if is_mobile:
                # Mobile: Use native Streamlit components
                st.markdown("### YOUR RANK")
                st.metric(
                    label="Position",
                    value=f"#{provider_ranking['rank']}",
                    delta=f"of {provider_ranking['total_providers']} providers"
                )
                st.markdown(f"**{provider_ranking['quartile']} Quartile**")
                st.markdown(f"{provider_ranking['percentile']:.1f}th percentile")
                st.caption(f"Based on {provider_ranking['measures_count']} satisfaction measures")
            else:
                # Desktop: Use custom HTML
                quartile_class = f"quartile-{html.escape(provider_ranking['quartile'].lower())}"
                quartile_color = html.escape(str(provider_ranking['quartile_color']))
                quartile_name = html.escape(provider_ranking['quartile'])
                st.markdown(f"""
                <div class="metric-card {quartile_class}">
                    <p class="metric-label">YOUR RANK</p>
                    <p class="metric-value">#{provider_ranking['rank']}</p>
                    <p style="font-size: 1.1rem; margin: 0.5rem 0; color: #6C7A89;">
                        of {provider_ranking['total_providers']} providers
                    </p>
                    <p style="font-size: 1rem; font-weight: 600; color: {quartile_color};">
                        {quartile_name} Quartile ({provider_ranking['percentile']:.1f}th percentile)
                    </p>
                    <p style="font-size: 0.9rem; color: #6C7A89; margin-top: 0.5rem;">
                        Based on {provider_ranking['measures_count']} satisfaction measures
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # Expandable help, in the grid row beneath the cards
            with help_cols[0].expander("How Your Rank Works", expanded=False):
                st.markdown(metric_tooltips['ranking']['content'])
                st.markdown(f"""
                **Your specific ranking details:**
                - **Your composite score**: {provider_ranking['score']:.1f}
                - **Your percentile**: {provider_ranking['percentile']:.1f}% (better than {provider_ranking['percentile']:.1f}% of providers)
                - **Quartile color coding**: {provider_ranking['quartile']} performance level
                - **Measures included**: {provider_ranking['measures_count']} out of 12 possible TSM measures
                """)

        # YOUR MOMENTUM
        with cols[1]:
            if is_mobile:
                # Mobile: Use native Streamlit components
                st.markdown("### YOUR MOMENTUM")
                if momentum.get('disabled', False):
                    st.metric(
                        label="Trend",
                        value=momentum['momentum_text'],
                        delta=None
                    )
                    st.caption("Insufficient multi-year data")
                else:
                    st.metric(
                        label="Trend",
                        value=momentum['momentum_text'],
                        delta=f"{momentum['year_over_year_change']:+.1f} pts avg"
                    )
            else:
                # Desktop: Use custom HTML
                if momentum.get('disabled', False):
                    mom_color = html.escape(str(momentum['momentum_color']))
                    mom_icon = html.escape(str(momentum['momentum_icon']))
                    mom_text = html.escape(str(momentum['momentum_text']))
                    st.markdown(f"""
                    <div class="metric-card">
                        <p class="metric-label">YOUR MOMENTUM</p>
                        <p class="metric-value" style="color: {mom_color};">
                            {mom_icon}
                        </p>
                        <p style="font-size: 1.5rem; font-weight: 600; color: {mom_color}; margin: 0.5rem 0;">
                            {mom_text}
                        </p>
                        <p style="font-size: 0.9rem; color: #6C7A89;">
                            Insufficient multi-year data
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Build the performance comparison sections
                    improved = momentum.get('improved_measures', [])
                    declined = momentum.get('declined_measures', [])
                    
                    # Start building the HTML
                    mom_color = html.escape(str(momentum['momentum_color']))
                    mom_icon = html.escape(str(momentum['momentum_icon']))
                    mom_text = html.escape(str(momentum['momentum_text']))
                    card_html = f"""
                    <div class="metric-card">
                        <p class="metric-label">YOUR MOMENTUM</p>
                        <p class="metric-value" style="color: {mom_color};">
                            {mom_icon}
                        </p>
                        <p style="font-size: 1.5rem; font-weight: 600; color: {mom_color}; margin: 0.5rem 0;">
                            {mom_text}
                        </p>
                        <p style="font-size: 0.9rem; color: #6C7A89; margin-bottom: 0.25rem;">
                            <strong>{momentum.get('latest_year', 2026)} vs {momentum.get('prior_year', 2025)}:</strong> {momentum['year_over_year_change']:+.1f} points average
                        </p>
                        <p style="font-size: 0.8rem; color: #6C7A89; margin-bottom: 0.5rem;">
                            {momentum.get('total_measures_compared', 0)} measures compared
                        </p>
                        <p style="font-size: 0.9rem; font-weight: 600; color: #1F2933; margin-top: 0.5rem; margin-bottom: 0.5rem;">
                            Your {momentum.get('latest_year', 2026)} vs {momentum.get('prior_year', 2025)} performance:
                        </p>
                    """

                    # Add improvements section if available
                    if improved:
                        card_html += '<p style="font-size: 0.85rem; font-weight: 600; color: #1F94A3; margin-bottom: 0.25rem;">Top Improvements:</p>'
                        for measure in improved[:3]:
                            desc = html.escape(str(measure["description"]))
                            card_html += f'<p style="font-size: 0.8rem; color: #475569; margin: 0.1rem 0; padding-left: 0.5rem;">&bull; {desc}: +{measure["change"]:.1f} pts</p>'

                    # Add declined section if available
                    if declined:
                        card_html += '<p style="font-size: 0.85rem; font-weight: 600; color: #C85C4A; margin-bottom: 0.25rem; margin-top: 0.5rem;">Areas Needing Attention:</p>'
                        for measure in declined[:3]:
                            desc = html.escape(str(measure["description"]))
                            card_html += f'<p style="font-size: 0.8rem; color: #475569; margin: 0.1rem 0; padding-left: 0.5rem;">&bull; {desc}: {measure["change"]:.1f} pts</p>'
                    
                    # Close the card
                    card_html += "</div>"
                    
                    st.markdown(card_html, unsafe_allow_html=True)

            # Expandable help, in the grid row beneath the cards
            with help_cols[1].expander("How Momentum Works", expanded=False):
                st.markdown(metric_tooltips['momentum']['content'])
                if momentum.get('disabled', False):
                    st.markdown("""
                    **Current status**: Insufficient multi-year data for this provider.

                    **What momentum shows when available**:
                    - Year-over-year performance changes
                    - Which measures improved or declined
                    - Overall trajectory (improving, stable, or declining)
                    """)
                else:
                    st.markdown(f"""
                    **Your {momentum.get('latest_year', 2026)} vs {momentum.get('prior_year', 2025)} performance:**
                    - **Overall change**: {momentum['year_over_year_change']:+.1f} points average
                    - **Measures compared**: {momentum.get('total_measures_compared', 0)} satisfaction measures
                    """)
                    
                    # Show improved measures
                    improved = momentum.get('improved_measures', [])
                    if improved:
                        st.markdown("**Top improvements:**")
                        for measure in improved:
                            st.markdown(f"- {measure['description']}: **+{measure['change']:.1f}** points")
                    
                    # Show declined measures
                    declined = momentum.get('declined_measures', [])
                    if declined:
                        st.markdown("**Areas needing attention:**")
                        for measure in declined:
                            st.markdown(f"- {measure['description']}: **{measure['change']:.1f}** points")

        # YOUR PRIORITY
        with cols[2]:
            # Correlation shown as qualitative label + raw coefficient, e.g. "Strong (0.72)"
            raw_corr = abs(priority.get('correlation_with_tp01', 0))
            corr_text = _corr_label(raw_corr)

            measure_code = priority.get('priority_measure', priority.get('measure', 'N/A'))
            measure_desc = priority.get('priority_description', priority.get('measure_name', 'No priority identified'))
            current_percentile = priority.get('percentile', priority.get('current_percentile', 0))
            improvement = priority.get('improvement_potential', 0)
            
            if is_mobile:
                # Mobile: Use native Streamlit components
                st.markdown("### YOUR PRIORITY")
                st.metric(
                    label=measure_code,
                    value=priority.get('priority_level', 'Medium'),
                    delta=f"{improvement:.1f}% improvement potential"
                )
                st.markdown(f"**{measure_desc}**")
                st.caption(f"Current: {current_percentile:.1f}th percentile")
            else:
                # Desktop: Use custom HTML
                priority_class = "priority-high" if priority.get('priority_level', '') in ['Critical', 'High'] else ""
                priority_color = html.escape(str(priority.get('priority_color', '#0B5C70')))
                priority_level = html.escape(str(priority.get('priority_level', 'Medium')))
                safe_measure_code = html.escape(str(measure_code))
                safe_measure_desc = html.escape(str(measure_desc))
                safe_corr_text = html.escape(str(corr_text))
                st.markdown(f"""
                <div class="metric-card {priority_class}">
                    <p class="metric-label">YOUR PRIORITY</p>
                    <p class="metric-value" style="font-size: 1.8rem; color: {priority_color};">
                        {priority_level}
                    </p>
                    <p style="font-size: 1.3rem; font-weight: 700; margin: 0.3rem 0; color: #0B5C70;">
                        {safe_measure_code}
                    </p>
                    <p style="font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0; color: #1F2933;">
                        {safe_measure_desc}
                    </p>
                    <p style="font-size: 0.9rem; color: #6C7A89;">
                        Current: {current_percentile:.1f}th percentile
                    </p>
                    <p style="font-size: 0.9rem; color: {priority_color}; font-weight: 500;">
                        Improvement potential: {improvement:.1f}%
                    </p>
                    <p style="font-size: 0.85rem; color: #475569; margin-top: 0.3rem;">
                        TP01 correlation: {safe_corr_text} ({raw_corr:.2f})
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # Expandable help, in the grid row beneath the cards
            with help_cols[2].expander("How Priority Works", expanded=False):
                st.markdown(metric_tooltips['priority']['content'])
                st.markdown(f"""
                **Your priority details:**
                - **Focus area**: {measure_desc} ({measure_code})
                - **Current performance**: {current_percentile:.1f}th percentile
                - **Improvement potential**: {improvement:.1f}% (room to improve)
                - **TP01 correlation**: {corr_text} ({raw_corr:.2f})
                - **Weighted priority score**: {priority.get('priority_score', priority.get('weighted_priority_score', 0)):.1f}
                - **Current score**: {priority.get('current_score', 'N/A')}

                **Why this is your priority**: This area combines high improvement potential with strong impact on overall satisfaction.
                """)

    def render_detailed_analysis(self, df: pd.DataFrame, provider_code: str, analytics):
        """
        Render detailed analysis section with correlation insights
        """
        # Get tooltip definitions
        tooltips = TooltipDefinitions()
        technical_tooltips = tooltips.get_technical_tooltips()

        st.markdown("### Detailed Performance Analysis")

        # Get detailed analysis and priority data
        detailed_analysis = analytics.get_detailed_performance_analysis(df, provider_code)
        priority_data = analytics.identify_priority(df, provider_code)

        if "error" in detailed_analysis:
            _report_internal_error("detailed analysis error", detailed_analysis.get("error"))
            st.error("Detailed analysis is unavailable right now. Try another provider or refresh.")
            return

        # Add help information for the detailed analysis section
        with st.expander("Understanding Detailed Analysis", expanded=False):
            st.markdown("""
            **This section provides three detailed views:**

            **Performance Comparison**: See how you score on each satisfaction measure compared to peer averages

            **Correlation Analysis**: Understand which measures have the strongest relationship with overall satisfaction

            **Priority Matrix**: Visual guide to help prioritize which areas to focus on for maximum impact

            **Tip**: Hover over charts for detailed information about each data point.
            """)

        # Performance Comparison Section
        with st.expander("Performance Comparison", expanded=True):
            # Create performance comparison chart
            if detailed_analysis:
                measures = []
                provider_scores = []
                peer_averages = []
                percentiles = []

                for tp_code, data in detailed_analysis.items():
                    measures.append(f"{tp_code}\n{data['description'][:30]}...")
                    provider_scores.append(data['score'])
                    peer_averages.append(data['peer_avg'])
                    percentiles.append(data['percentile'])

                # Create comparison chart with enhanced tooltips
                fig = go.Figure()

                # Prepare detailed data for tooltips
                hover_data_your = []
                hover_data_peer = []
                for tp_code, data in detailed_analysis.items():
                    hover_data_your.append(f"{data['description']}<br>Your Score: {data['score']:.1f}<br>Percentile: {data['percentile']:.1f}%<br>Gap from Peer Avg: {data['score'] - data['peer_avg']:+.1f}")
                    hover_data_peer.append(f"{data['description']}<br>Peer Average: {data['peer_avg']:.1f}<br>Peer Median: {data['peer_median']:.1f}<br>Top Quartile: {data['top_quartile_threshold']:.1f}")

                fig.add_trace(go.Bar(
                    name='Your Score',
                    x=measures,
                    y=provider_scores,
                    marker_color='#0B5C70',
                    hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>",
                    customdata=hover_data_your
                ))

                fig.add_trace(go.Bar(
                    name='Peer Average',
                    x=measures,
                    y=peer_averages,
                    marker_color='#6C7A89',
                    opacity=0.7,
                    hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>",
                    customdata=hover_data_peer
                ))

                fig.update_layout(
                    title="Performance Comparison by Measure - Hover for Details",
                    xaxis_title="Satisfaction Measures",
                    yaxis_title="Score",
                    barmode='group',
                    height=500,
                    showlegend=True,
                    xaxis={'tickangle': -45}
                )

                st.plotly_chart(fig, width='stretch')

                # Performance table with help
                col_table1, col_table2 = st.columns([4, 1])
                with col_table1:
                    st.markdown("#### Detailed Breakdown")
                with col_table2:
                    with st.expander("Table Help", expanded=False):
                        st.markdown("""
                        **Understanding the table:**

                        **Your Score**: Your actual satisfaction score for this measure

                        **Percentile**: What % of providers you perform better than

                        **Peer Average**: Average score of all providers for this measure

                        **Gap**: Difference between your score and peer average
                        - Positive (+) = Above average
                        - Negative (-) = Below average
                        """)

                table_data = []
                for tp_code, data in detailed_analysis.items():
                    table_data.append({
                        'Measure': tp_code,
                        'Description': data['description'],
                        'Your Score': f"{data['score']:.1f}",
                        'Percentile': f"{data['percentile']:.1f}%",
                        'Peer Average': f"{data['peer_avg']:.1f}",
                        'Gap': f"{data['score'] - data['peer_avg']:+.1f}"
                    })

                table_df = pd.DataFrame(table_data)
                st.table(table_df)

        # Correlation Analysis Section
        with st.expander("Correlation Analysis", expanded=False):
            # Add header with tooltip help
            col_header1, col_header2 = st.columns([4, 1])
            with col_header1:
                st.markdown("#### Correlation with Overall Satisfaction (TP01)")
            with col_header2:
                # Help tooltip for correlation
                with st.expander("What is Correlation?", expanded=False):
                    st.markdown(tooltips.get_streamlit_help_text('correlation', technical_tooltips))

            if not "error" in priority_data and 'all_correlations' in priority_data:
                correlations = priority_data['all_correlations']

                if correlations:
                    # Create correlation data for visualization
                    corr_data = []
                    for tp_code, corr_info in correlations.items():
                        corr_data.append({
                            'Measure': tp_code,
                            'Description': analytics.tp_descriptions.get(tp_code, tp_code),
                            'Correlation': corr_info['correlation'],
                            'Strength': corr_info['strength'],
                            'P-Value': corr_info['p_value'],
                            'Sample Size': corr_info['sample_size']
                        })

                    corr_df = pd.DataFrame(corr_data)
                    corr_df = corr_df.sort_values('Strength', ascending=False)

                    # Create correlation bar chart
                    fig_corr = go.Figure()

                    colors = ['#1F94A3' if c > 0 else '#C85C4A' for c in corr_df['Correlation']]

                    # Prepare enhanced hover data for correlation chart
                    correlation_hover_data = []
                    for _, row in corr_df.iterrows():
                        strength_text = "Strong" if row['Strength'] > 0.7 else "Moderate" if row['Strength'] > 0.4 else "Weak"
                        significance = "Significant" if row['P-Value'] < 0.05 else "Not significant"
                        correlation_hover_data.append(
                            f"{row['Description']}<br>"
                            f"Correlation: {row['Correlation']:.3f}<br>"
                            f"Strength: {strength_text} ({row['Strength']:.1%})<br>"
                            f"P-Value: {row['P-Value']:.4f} ({significance})<br>"
                            f"Sample Size: {row['Sample Size']} providers"
                        )

                    fig_corr.add_trace(go.Bar(
                        x=corr_df['Correlation'],
                        y=[f"{row['Measure']}\n{row['Description'][:25]}..." for _, row in corr_df.iterrows()],
                        orientation='h',
                        marker_color=colors,
                        text=[f"{c:.3f}" for c in corr_df['Correlation']],
                        textposition='outside',
                        hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                        customdata=correlation_hover_data
                    ))

                    fig_corr.update_layout(
                        title="Correlation of Each Measure with Overall Satisfaction (TP01) - Hover for Details",
                        xaxis_title="Correlation Coefficient (-1 to +1)",
                        yaxis_title="Measures",
                        height=500,
                        xaxis=dict(range=[-1, 1]),
                        showlegend=False
                    )

                    st.plotly_chart(fig_corr, width='stretch')

                    # Correlation insights with help
                    col_insights1, col_insights2 = st.columns([4, 1])
                    with col_insights1:
                        st.markdown("##### Key Correlation Insights")
                    with col_insights2:
                        with st.expander("Insights Help", expanded=False):
                            st.markdown("""
                            **Understanding correlations:**

                            **Strong correlations (>0.7)**: These measures have major impact on overall satisfaction. Focus here for maximum effect.

                            **Moderate correlations (0.4-0.7)**: Important but secondary impact areas.

                            **Weak correlations (<0.4)**: These may be important for other reasons but have limited impact on overall satisfaction.

                            **Strategy**: Prioritize strong correlation areas when resources are limited.
                            """)

                    strong_correlations = corr_df[corr_df['Strength'] > 0.7]
                    if not strong_correlations.empty:
                        st.success(f"**Strong correlations:** {', '.join(strong_correlations['Measure'].tolist())} show strong relationships with overall satisfaction")

                    weak_correlations = corr_df[corr_df['Strength'] < 0.3]
                    if not weak_correlations.empty:
                        st.info(f"**Weak correlations:** {', '.join(weak_correlations['Measure'].tolist())} have minimal impact on overall satisfaction")

                    # Detailed correlation table with help
                    col_stats1, col_stats2 = st.columns([4, 1])
                    with col_stats1:
                        st.markdown("##### Correlation Statistics")
                    with col_stats2:
                        with st.expander("Statistics Help", expanded=False):
                            st.markdown("""
                            **Statistical terms explained:**

                            **Correlation**: Strength of relationship (-1 to +1)
                            - Closer to +1 = stronger positive relationship
                            - Closer to 0 = weaker relationship

                            **P-Value**: Statistical significance
                            - <0.05 = statistically significant result
                            - >0.05 = result could be due to chance

                            **Sample Size**: Number of providers with data for this measure
                            - Larger samples = more reliable results
                            """)

                    # Create display dataframe with formatted values
                    display_data = []
                    for _, row in corr_df.iterrows():
                        display_data.append({
                            'Measure': row['Measure'],
                            'Description': row['Description'],
                            'Correlation': f"{row['Correlation']:.3f}",
                            'P-Value': f"{row['P-Value']:.4f}",
                            'Sample Size': row['Sample Size']
                        })
                    display_df = pd.DataFrame(display_data)

                    st.table(display_df)
                else:
                    st.warning("Insufficient data to calculate correlations with TP01")
            else:
                st.warning("Correlation analysis not available")

        # Priority Matrix Section
        with st.expander("Priority Matrix", expanded=False):
            # Add header with tooltip help
            col_header1, col_header2 = st.columns([4, 1])
            with col_header1:
                st.markdown("#### Priority Matrix")
            with col_header2:
                # Help tooltip for priority matrix
                with st.expander("Priority Matrix Guide", expanded=False):
                    st.markdown("""
                    **How to read the Priority Matrix:**

                    **Position on chart**:
                    - **X-axis**: Improvement potential (how much you can improve)
                    - **Y-axis**: Correlation with overall satisfaction (impact)
                    - **Bubble size**: Combined priority score

                    **Quadrants**:
                    - **Top-Right (High Priority)**: High impact + High potential — focus here first
                    - **Top-Left (Maintain & Protect)**: High impact + Already strong — protect these strengths
                    - **Bottom-Right (Lower Impact)**: High potential + Lower impact on overall satisfaction
                    - **Bottom-Left (Low Priority)**: Lower impact + Already performing well

                    **Focus on measures in the top-right quadrant for maximum impact.**
                    """)

            if not "error" in priority_data and 'all_weighted_priorities' in priority_data:
                # Get weighted priorities and improvement potentials
                weighted_priorities = priority_data['all_weighted_priorities']
                improvement_potentials = priority_data['all_potentials']
                correlations = priority_data.get('all_correlations', {})

                if weighted_priorities:
                    # Create scatter plot: Improvement Potential vs Correlation
                    scatter_data = []
                    for tp_code in weighted_priorities:
                        scatter_data.append({
                            'Measure': tp_code,
                            'Description': analytics.tp_descriptions.get(tp_code, tp_code),
                            'Improvement Potential': improvement_potentials.get(tp_code, 0),
                            'Correlation': correlations.get(tp_code, {}).get('strength', 0) * 100 if tp_code in correlations else 50,
                            'Weighted Priority': weighted_priorities[tp_code]
                        })

                    scatter_df = pd.DataFrame(scatter_data)

                    # Create priority matrix scatter plot with enhanced tooltips
                    fig_matrix = go.Figure()

                    # Prepare detailed hover data
                    matrix_hover_data = []
                    for _, row in scatter_df.iterrows():
                        priority_score = row['Weighted Priority']
                        if priority_score > 60:
                            priority_level = "Critical"
                        elif priority_score > 40:
                            priority_level = "High"
                        elif priority_score > 20:
                            priority_level = "Medium"
                        else:
                            priority_level = "Low"

                        corr_raw = row['Correlation'] / 100
                        hover_text = (
                            f"{row['Description']}<br>"
                            f"Priority Level: {priority_level}<br>"
                            f"Improvement Potential: {row['Improvement Potential']:.1f}%<br>"
                            f"TP01 Correlation: {_corr_label(corr_raw)} ({corr_raw:.2f})<br>"
                            f"Weighted Priority Score: {priority_score:.1f}<br>"
                            f"Focus Area Ranking: {'Top 3' if priority_score >= sorted(scatter_df['Weighted Priority'], reverse=True)[2] else 'Lower Priority'}"
                        )
                        matrix_hover_data.append(hover_text)

                    # Color based on weighted priority
                    fig_matrix.add_trace(go.Scatter(
                        x=scatter_df['Improvement Potential'],
                        y=scatter_df['Correlation'],
                        mode='markers',
                        marker=dict(
                            size=scatter_df['Weighted Priority']*0.8+10,  # Better size scaling
                            color=scatter_df['Weighted Priority'],
                            # HAILIE ramp: Bright Teal (low) -> Civic Gold (mid) -> Brick Coral (high)
                            colorscale=[[0.0, '#1F94A3'], [0.5, '#D8A62A'], [1.0, '#C85C4A']],
                            showscale=True,
                            colorbar=dict(title="Priority Score"),
                            line=dict(width=1, color='white')  # Add border for better visibility
                        ),
                        text=scatter_df['Measure'],
                        hovertemplate="<b>%{text}</b><br>%{customdata}<extra></extra>",
                        customdata=matrix_hover_data
                    ))

                    # Add quadrant lines
                    fig_matrix.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
                    fig_matrix.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5)

                    # Add quadrant labels
                    fig_matrix.add_annotation(x=75, y=75, text="High Priority", showarrow=False, font=dict(size=12, color="#C85C4A"))
                    fig_matrix.add_annotation(x=25, y=75, text="Maintain & Protect", showarrow=False, font=dict(size=12, color="#1F94A3"))
                    fig_matrix.add_annotation(x=75, y=25, text="Lower Impact", showarrow=False, font=dict(size=12, color="#D8A62A"))
                    fig_matrix.add_annotation(x=25, y=25, text="Low Priority", showarrow=False, font=dict(size=12, color="#6C7A89"))

                    # Add point labels
                    _add_point_labels(
                        fig_matrix,
                        list(scatter_df['Improvement Potential']),
                        list(scatter_df['Correlation']),
                        list(scatter_df['Measure'])
                    )

                    fig_matrix.update_layout(
                        title="Priority Matrix: Improvement Potential vs TP01 Correlation - Hover for Details",
                        xaxis_title="Improvement Potential (%)",
                        yaxis_title="Relationship with Overall Satisfaction",
                        height=600,
                        xaxis=dict(
                            range=[0, 100],
                            title_font=dict(size=12)
                        ),
                        yaxis=dict(
                            range=[0, 100],
                            title_font=dict(size=12)
                        ),
                        font=dict(size=11)
                    )

                    st.plotly_chart(fig_matrix, width='stretch')

                    # Top 3 priorities with help
                    if 'top_3_priorities' in priority_data:
                        col_top3_1, col_top3_2 = st.columns([4, 1])
                        with col_top3_1:
                            st.markdown("##### Top 3 Priority Areas")
                        with col_top3_2:
                            with st.expander("Priority Help", expanded=False):
                                st.markdown("""
                                **Your top 3 priorities are ranked by:**

                                **Weighted priority score**: Combines improvement potential with correlation strength

                                **Improvement potential**: How much you could realistically improve

                                **TP01 correlation**: How much impact improvement would have on overall satisfaction

                                **Action**: Start with #1 priority for maximum impact, then work down the list.
                                """)

                        for i, priority in enumerate(priority_data['top_3_priorities'], 1):
                            col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                            with col1:
                                st.markdown(f"**#{i}**")
                            with col2:
                                st.markdown(f"**{priority['measure']}:** {priority['name']}")
                            with col3:
                                st.markdown(f"Improvement: {priority['improvement_potential']:.1f}%")
                            with col4:
                                st.markdown(f"TP01 Corr: {priority['correlation']:.3f}")
                else:
                    st.warning("Insufficient data to create priority matrix")
            else:
                st.warning("Priority analysis not available")


    def render_data_quality(self, df: pd.DataFrame, data_processor):
        """
        Render data quality report
        """
        # Add header with help
        col_header1, col_header2 = st.columns([4, 1])
        with col_header1:
            st.markdown("### Data Quality Report")
        with col_header2:
            with st.expander("About Data Quality", expanded=False):
                st.markdown("""
                **Data Quality Metrics Explained:**

                **Total Providers**: Number of housing providers in the dataset

                **Providers with Data**: How many providers have valid TSM data

                **TP Measures Found**: Which of the 12 official measures (TP01-TP12) are available

                **Completeness**: Percentage of providers with data for each measure

                **Why this matters**: Higher completeness means more reliable peer comparisons and benchmarking.
                """)

        quality_report = data_processor.get_data_quality_report(df)

        if not quality_report:
            st.warning("No data quality information available")
            return

        # Summary metrics with enhanced tooltips
        st.markdown("""
        **Quick data overview** - hover over metric names for explanations:
        """)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Providers", quality_report.get('total_providers', 0))

        with col2:
            st.metric("Providers with Data", quality_report.get('providers_with_data', 0))

        with col3:
            st.metric("TP Measures Found", quality_report.get('tp_measures_found', 0))

        with col4:
            completeness_avg = 0
            if quality_report.get('completeness_by_measure'):
                completeness_values = [data['percentage'] for data in quality_report['completeness_by_measure'].values()]
                completeness_avg = np.mean(completeness_values)
            st.metric("Avg Completeness", f"{completeness_avg:.1f}%")

        # Completeness by measure
        if quality_report.get('completeness_by_measure'):
            st.markdown("#### Data Completeness by Measure")

            completeness_data = []
            for measure, data in quality_report['completeness_by_measure'].items():
                completeness_data.append({
                    'Measure': measure,
                    'Complete Records': data['count'],
                    'Completeness %': f"{data['percentage']:.1f}%"
                })

            completeness_df = pd.DataFrame(completeness_data)
            st.table(completeness_df)

        # Data ranges
        if quality_report.get('data_ranges'):
            st.markdown("#### Score Ranges by Measure")

            ranges_data = []
            for measure, data in quality_report['data_ranges'].items():
                ranges_data.append({
                    'Measure': measure,
                    'Minimum': f"{data['min']:.1f}",
                    'Maximum': f"{data['max']:.1f}",
                    'Average': f"{data['mean']:.1f}"
                })

            ranges_df = pd.DataFrame(ranges_data)
            st.table(ranges_df)

    def render_performance_analysis(self, detailed_analysis: Dict):
        """
        Render performance analysis visualization
        """
        if not detailed_analysis:
            st.warning("No performance analysis data available")
            return

        if "error" in detailed_analysis:
            _report_internal_error("performance analysis error", detailed_analysis.get("error"))
            st.error("Performance analysis is unavailable right now. Try another provider or refresh.")
            return

        if detailed_analysis and len(detailed_analysis) > 0:
            st.markdown("### Performance Analysis")

            # Create performance comparison chart
            measures = []
            provider_scores = []
            peer_averages = []
            percentiles = []

            for tp_code, data in detailed_analysis.items():
                measures.append(f"{tp_code}")
                provider_scores.append(data['score'])
                peer_averages.append(data['peer_avg'])
                percentiles.append(data['percentile'])

            # Create comparison chart
            fig = go.Figure()

            fig.add_trace(go.Bar(
                name='Your Score',
                x=measures,
                y=provider_scores,
                marker_color='#0B5C70',
                text=[f"{s:.1f}" for s in provider_scores],
                textposition='outside'
            ))

            fig.add_trace(go.Bar(
                name='Peer Average',
                x=measures,
                y=peer_averages,
                marker_color='#6C7A89',
                opacity=0.7
            ))

            fig.update_layout(
                title="Performance Comparison by Measure",
                xaxis_title="TSM Measures",
                yaxis_title="Score",
                barmode='group',
                height=400,
                **PLOTLY_LAYOUT,
            )

            st.plotly_chart(fig, width='stretch')

            # Performance table
            st.markdown("#### Detailed Scores")
            table_data = []
            for tp_code, data in detailed_analysis.items():
                table_data.append({
                    'Measure': tp_code,
                    'Description': data['description'],
                    'Your Score': f"{data['score']:.1f}",
                    'Percentile': f"{data['percentile']:.1f}%",
                    'Peer Avg': f"{data['peer_avg']:.1f}"
                })

            table_df = pd.DataFrame(table_data)
            st.table(table_df)

    def render_correlation_analysis(self, correlations: pd.DataFrame, priority: Dict):
        """
        Render correlation analysis visualization
        """
        st.markdown("### Correlation Analysis")

        if correlations.empty:
            st.info("No correlation data available")
            return

        # Create correlation bar chart
        fig = go.Figure()

        # Sort by absolute correlation value
        correlations['abs_corr'] = correlations['correlation_with_tp01'].abs()
        correlations = correlations.sort_values('abs_corr', ascending=False)

        colors = ['#1F94A3' if c > 0 else '#C85C4A' for c in correlations['correlation_with_tp01']]

        fig.add_trace(go.Bar(
            x=correlations['correlation_with_tp01'],
            y=correlations['tp_measure'],
            orientation='h',
            marker_color=colors,
            text=[f"{c:.3f}" for c in correlations['correlation_with_tp01']],
            textposition='outside'
        ))

        fig.update_layout(
            title="Correlation with Overall Satisfaction (TP01)",
            xaxis_title="Correlation Coefficient",
            yaxis_title="TSM Measure",
            height=400,
            **PLOTLY_LAYOUT,
        )

        st.plotly_chart(fig, width='stretch')

        # Correlation table
        st.markdown("#### Correlation Details")
        table_data = correlations[['tp_measure', 'correlation_with_tp01', 'p_value']].copy()
        table_data.columns = ['Measure', 'Correlation', 'P-Value']
        
        # Ensure we're working with a DataFrame
        if isinstance(table_data, pd.DataFrame):
            table_data['Correlation'] = table_data['Correlation'].apply(lambda x: f"{x:.3f}")
            # Display p<0.05 for statistically significant values (smaller than 4 decimal places)
            table_data['P-Value'] = table_data['P-Value'].apply(
                lambda x: "p<0.05 (statistically significant)" if x < 0.0001 else f"{x:.4f}"
            )

        st.table(table_data)

    def render_priority_matrix(self, priority: Dict, detailed_analysis: Dict):
        """
        Render priority matrix visualization
        """
        st.markdown("### Priority Matrix")

        if "error" in priority:
            _report_internal_error("priority matrix error", priority.get("error"))
            st.error("Priority matrix is unavailable right now. Try another provider or refresh.")
            return

        # Extract priorities if available
        if 'all_priorities' in priority:
            priorities = priority['all_priorities']

            # Create scatter plot
            fig = go.Figure()

            x_values = []  # Improvement potential
            y_values = []  # Correlation strength
            labels = []
            colors = []

            for measure, data in priorities.items():
                x_values.append(data['improvement_potential'])
                y_values.append(data['correlation_strength'] * 100)
                labels.append(measure)

                # Colour ramp by priority score (HAILIE palette).
                if data['priority_score'] > 70:
                    colors.append('#C85C4A')  # Brick Coral - Critical
                elif data['priority_score'] > 50:
                    colors.append('#D8A62A')  # Civic Gold - High
                elif data['priority_score'] > 30:
                    colors.append('#E8C96B')  # Soft Gold - Medium
                else:
                    colors.append('#1F94A3')  # Bright Teal - Low

            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode='markers',
                text=labels,
                marker=dict(
                    size=12,
                    color=colors,
                    line=dict(width=2, color='white')
                ),
                hovertemplate="<b>%{text}</b><br>Improvement: %{x:.1f}%<br>Correlation Strength: %{y:.0f}/100<extra></extra>"
            ))

            fig.update_layout(
                title="Priority Matrix: Improvement Potential vs Impact",
                xaxis_title="Improvement Potential (%)",
                yaxis_title="Relationship with Overall Satisfaction",
                height=500,
                showlegend=False,
                **PLOTLY_LAYOUT,
            )

            # Add quadrant lines
            fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.3)
            fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.3)

            # Add quadrant labels
            fig.add_annotation(x=75, y=75, text="High Priority", showarrow=False, font=dict(size=11, color="#C85C4A"))
            fig.add_annotation(x=25, y=75, text="Maintain & Protect", showarrow=False, font=dict(size=11, color="#1F94A3"))
            fig.add_annotation(x=75, y=25, text="Lower Impact", showarrow=False, font=dict(size=11, color="#D8A62A"))
            fig.add_annotation(x=25, y=25, text="Low Priority", showarrow=False, font=dict(size=11, color="#6C7A89"))

            # Add point labels
            _add_point_labels(fig, x_values, y_values, labels)

            st.plotly_chart(fig, width='stretch')

            # Priority table
            st.markdown("#### Priority Ranking")
            priority_list = sorted(priorities.items(), 
                                  key=lambda x: x[1]['priority_score'], 
                                  reverse=True)

            table_data = []
            for i, (measure, data) in enumerate(priority_list, 1):
                cs = data['correlation_strength']
                table_data.append({
                    'Rank': i,
                    'Measure': measure,
                    'Priority Score': f"{data['priority_score']:.1f}",
                    'Improvement Potential': f"{data['improvement_potential']:.1f}%",
                    'Correlation': f"{_corr_label(cs)} ({cs:.2f})"
                })

            table_df = pd.DataFrame(table_data)
            st.table(table_df)
        else:
            st.info("Priority matrix data not available")


    def render_comparisons(self, selected_provider_code, priority_measure, comparison_df: pd.DataFrame):
        """
        Render the comparison section.
        Currently, there is only a table. More views will be
        added in the future in separate tabs.

        The table is for all providers. 
        The selected provider's row is anchored above the table so it
        can be referenced no matter the scroll position of the table.

        By default, comparisons will be with respect to the priority
        metric for the selected provider, but there will be a drop down
        menu for selecting the other metrics.

        The dataframe passed to this function contains records of
        providers, pulled from our DuckDB database. Thus, we know
        the dataframe will never be empty, and such checks are not
        needed.
        """
        # table_tab, map_tab = st.tabs(["Table View", "Map View"])
        #
        # with table_tab:
        st.markdown(f"### Comparison table - Your priority: {priority_measure}")

        target_row = comparison_df[comparison_df["provider_code"] == selected_provider_code]

        # Display the selected provider's row at the top of the table so it can always be referenced
        st.dataframe(
            target_row.style.apply(
                lambda row: ["background-color: #ffeaa7; font-weight: bold"] * len(row),
                axis=1
            ),
            height=75,
            hide_index=True
        )
        # Small horizontal spacer
        st.markdown(
            """<hr style="margin-top: 0.25rem; margin-bottom: 0.25rem; border: none; border-top: 1px solid #00000000;" />""",
            unsafe_allow_html=True
        )
        # Display the full table, with the selected provider's row highlighted
        st.dataframe(
            comparison_df.style.apply(
                lambda row: ["background-color: #ffeaa7; font-weight: bold" if row["provider_code"] == selected_provider_code else "" for _ in row],
                axis=1
            ),
            hide_index=True
        )


    def render_feedback_form(self, provider_code: str = None, dataset_type: str = None):
        """Render the "report a data issue / feature request" form.

        Lives on the main page as an expander, available with or without a
        provider selected. When one is selected, its code and dataset are
        attached to the report so maintainers know what the reporter was
        looking at. Email transport is delegated to feedback_service; this
        method only collects input, validates lightly, and shows the result.
        """
        import time

        from feedback_service import looks_like_email, send_feedback

        # Categories mirror the real signals we want to capture: source-data
        # problems, calculation/ranking errors, stale data, misinterpretation
        # risk, and open feature requests.
        categories = [
            "Source data looks wrong",
            "A calculation or ranking looks off",
            "The data looks out of date",
            "A result could be misread or is misleading",
            "Feature request or something else",
        ]

        with st.expander("Spotted a data issue or want to suggest a feature? Tell us here", expanded=False):
            # Intro callout — left-border house style, matching the dataset
            # indicator so it reads as part of the app, not a bolt-on.
            st.markdown(
                '<div class="feedback-intro">'
                '<strong>Spotted something off in the data?</strong><br/>'
                'These figures feed board reports and regulatory returns, so getting '
                'them right matters to us. Flag a wrong number, a ranking that looks '
                'off, data that seems out of date, a result that could be misread — '
                'or tell us what you wish the tool did. It comes straight to the team.'
                '</div>',
                unsafe_allow_html=True,
            )

            with st.form("feedback_form", clear_on_submit=False):
                category = st.selectbox("What's this about?", categories)
                area = st.text_input(
                    "Which measure or section? (optional)",
                    max_chars=200,
                    placeholder="e.g. the repairs satisfaction score, or the priority matrix",
                )
                message = st.text_area(
                    "Tell us what you noticed",
                    max_chars=5000,
                    placeholder="What did you expect to see, and what did you see instead?",
                    height=140,
                )
                reporter_email = st.text_input(
                    "Your email (optional — only used to reply)",
                    max_chars=200,
                    placeholder="you@yourorganisation.org",
                )
                submitted = st.form_submit_button("Send report")

            if not submitted:
                return

            # Lightweight per-session guards against accidental floods.
            sent_count = st.session_state.get("_feedback_count", 0)
            last_sent = st.session_state.get("_feedback_last_sent", 0.0)
            now = time.time()
            if sent_count >= 5:
                st.warning(
                    "Thanks for all the reports — that's the limit for this session. "
                    "Please come back later if you spot more."
                )
                return
            if now - last_sent < 15:
                st.warning("Just a moment — please wait a few seconds before sending another report.")
                return

            if reporter_email.strip() and not looks_like_email(reporter_email):
                st.warning(
                    "That email address doesn't look right. Correct it, or clear the "
                    "field to send without one."
                )
                return

            result = send_feedback(
                category=category,
                message=message,
                area=area,
                reporter_email=reporter_email,
                provider_code=provider_code,
                dataset_type=dataset_type,
            )
            if result.ok:
                st.session_state["_feedback_count"] = sent_count + 1
                st.session_state["_feedback_last_sent"] = now
                st.success(result.user_message)
            else:
                st.error(result.user_message)

    # ------------------------------------------------------------------
    # Peer group filtering (size band / region)
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_dataset_suffix(provider_name: str) -> str:
        """Drop the ' - LCRA' style suffix the ETL appends to provider names."""
        for suffix in (" - LCRA", " - LCHO", " - COMBINED"):
            if provider_name.endswith(suffix):
                return provider_name[: -len(suffix)]
        return provider_name

    @staticmethod
    def describe_peer_group(dataset_type: str, size_band: str | None = None, region: str | None = None) -> str:
        """Plain-text description of a peer group, e.g.
        'LCRA providers, 5,000-40,000 homes, predominant region East Midlands'."""
        parts = [f"{dataset_type} providers"]
        if size_band:
            parts.append(f"{size_band} homes")
        if region:
            parts.append(f"predominant region {region}")
        return ", ".join(parts)

    def render_peer_group_filter(self, filter_options: Dict, own_metadata: Dict | None = None,
                                 key_prefix: str = "peer") -> tuple:
        """
        Render the size-band and region selectors.

        Returns (size_band, region); each is None when "all" is chosen. When
        own_metadata is given, the provider's own band and region are marked
        so "landlords like me" is one click away.
        """
        tooltips = TooltipDefinitions()
        own_metadata = own_metadata or {}
        bands = {o['value']: o['provider_count'] for o in filter_options.get('size_bands', [])}
        regions = {o['value']: o['provider_count'] for o in filter_options.get('regions', [])}

        if not bands and not regions:
            return None, None

        st.markdown("#### Peer group")
        st.caption(tooltips.get_peer_group_intro())

        def band_label(value):
            if value is None:
                return "All sizes"
            label = f"{value} homes ({bands[value]} providers)"
            return f"{label} - your size band" if value == own_metadata.get('size_band') else label

        def region_label(value):
            if value is None:
                return "All regions"
            label = f"{value} ({regions[value]} providers)"
            return f"{label} - your region" if value == own_metadata.get('region') else label

        if detect_mobile():
            cols = [st.container(), st.container()]
        else:
            cols = st.columns(2, gap="medium")

        with cols[0]:
            size_band = st.selectbox(
                "Landlord size",
                options=[None] + list(bands),
                format_func=band_label,
                key=f"{key_prefix}_size_band",
                help="Size band published by the regulator: homes owned across the landlord group.",
            )
        with cols[1]:
            region = st.selectbox(
                "Region",
                options=[None] + list(regions),
                format_func=region_label,
                key=f"{key_prefix}_region",
                help="The landlord's predominant region as published by the regulator. "
                     "Landlords spread across several regions are recorded as Mixed.",
            )

        with st.expander("How peer groups work", expanded=False):
            st.markdown(tooltips.get_peer_group_help())

        return size_band, region

    def render_peer_group_notice(self, peer_group: Dict, dataset_type: str, selected_count: int = 1):
        """Tell the user which peer group is in force, and why if a filter was not applied."""
        if not peer_group:
            return

        subject = "you" if selected_count == 1 else "the providers you selected"

        if peer_group.get('fallback'):
            requested = self.describe_peer_group(
                dataset_type, peer_group.get('requested_size_band'), peer_group.get('requested_region'))
            matched = peer_group.get('filtered_group_size', 0)
            noun = "provider falls" if matched == 1 else "providers fall"
            st.warning(
                f"Only {matched} {noun} in the group \"{requested}\" (including {subject}). "
                f"Groups smaller than {peer_group.get('min_peer_group_size')} "
                f"are not used, because one landlord's result would move every position sharply. "
                f"Showing all {peer_group.get('peer_group_size', 0)} {dataset_type} providers instead."
            )
            return

        if peer_group.get('is_filtered'):
            description = html.escape(self.describe_peer_group(
                dataset_type, peer_group.get('size_band'), peer_group.get('region')))
            size = html.escape(str(peer_group.get('peer_group_size', 0)))
            st.markdown(
                f'<div class="peer-group-banner"><strong>Peer group:</strong> {description} '
                f'&mdash; {size} providers including {html.escape(subject)}. '
                f'Rank, percentiles and peer averages below use this group only.</div>',
                unsafe_allow_html=True,
            )

    # ------------------------------------------------------------------
    # Multi-provider (group executive) comparison
    # ------------------------------------------------------------------

    COMPARE_COLORS = ['#0B5C70', '#D8A62A', '#6C7A89']

    COMPARE_ERROR_MESSAGES = {
        'too_few_providers': "Select at least two providers to compare.",
        'too_many_providers': "You can compare up to three providers at a time.",
        'duplicate_providers': "The same provider has been selected more than once.",
        'mixed_dataset_types': (
            "These providers cannot be placed side by side: some of the results you selected are for "
            "rented housing (LCRA) and some for shared ownership (LCHO). The two are measured on "
            "different questions against different peer groups. Choose providers of the same type."
        ),
    }

    def _render_unavailable_compare_card(self, provider: Dict, label: str, comparison_year: int):
        """Greyed-out card, with the reason above it, for a provider that has no
        results for the comparison year."""
        code = str(provider['provider_code'])
        latest_year = provider.get('latest_year')
        st.warning(comparison_unavailable_notice(label, latest_year, comparison_year, code))

        safe_name = html.escape(label)
        safe_code = html.escape(code)
        safe_year = html.escape(str(comparison_year))
        latest_line = (f"Most recent results: {html.escape(str(latest_year))}"
                       if latest_year else "No results available")
        st.markdown(f"""
        <div class="metric-card compare-card compare-card-unavailable">
            <p class="compare-name">{safe_name}</p>
            <p class="compare-code">{safe_code}</p>
            <div class="compare-section">
                <p class="compare-section-label">Rank</p>
                <p class="compare-headline" style="font-size: 1.15rem;">No {safe_year} results</p>
                <p class="compare-detail">{latest_line}</p>
            </div>
            <div class="compare-section">
                <p class="compare-section-label">Momentum</p>
                <p class="compare-headline" style="font-size: 1.15rem;">Not available</p>
            </div>
            <div class="compare-section">
                <p class="compare-section-label">Priority</p>
                <p class="compare-headline" style="font-size: 1.15rem;">Not available</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def render_provider_comparison(self, comparison: Dict):
        """Render two or three providers side by side."""
        tooltips = TooltipDefinitions()

        if not comparison:
            st.warning("No comparison data available.")
            return

        if "error" in comparison:
            message = self.COMPARE_ERROR_MESSAGES.get(comparison["error"])
            if message:
                st.warning(message)
            else:
                _report_internal_error("provider comparison error", comparison.get("error"))
                st.error("We couldn't build this comparison right now. Try different providers or refresh.")
            return

        providers = comparison['providers']
        dataset_type = comparison['dataset_type']
        peer_group = comparison.get('peer_group', {})
        is_mobile = detect_mobile()
        # Providers with no results for the comparison year keep their place in
        # the row of cards, greyed out, and are left out of everything else.
        unavailable = {u['provider_code']: u for u in comparison.get('unavailable', [])}
        comparison_year = comparison.get('comparison_year')
        by_code = {p['provider_code']: p for p in providers}
        card_order = comparison.get('selection_order') or list(by_code)
        labels = {
            p['provider_code']: self._strip_dataset_suffix(str(p['provider_name']))
            for p in list(providers) + list(unavailable.values())
        }

        st.markdown("## Group Comparison")
        self.render_peer_group_notice(peer_group, dataset_type, selected_count=len(providers))
        if providers and not peer_group.get('is_filtered'):
            st.caption(
                f"Each provider is ranked among all {peer_group.get('peer_group_size', 0)} "
                f"{dataset_type} providers."
            )

        with st.expander("Understanding the comparison", expanded=False):
            st.markdown(tooltips.get_comparison_overview())

        # --- One summary card per provider ---
        if is_mobile:
            cols = [st.container() for _ in card_order]
        else:
            cols = st.columns(len(card_order), gap="medium")

        compared_codes = [p['provider_code'] for p in providers]
        for col, code in zip(cols, card_order):
            if code in unavailable:
                with col:
                    self._render_unavailable_compare_card(unavailable[code], labels[code], comparison_year)
                continue

            provider = by_code[code]
            # Accent follows the provider's position among those compared, so
            # the card matches its bars in the chart below.
            i = compared_codes.index(code)
            ranking = provider['ranking']
            momentum = provider['momentum']
            priority = provider['priority']
            accent = self.COMPARE_COLORS[i % len(self.COMPARE_COLORS)]

            safe_name = html.escape(labels[provider['provider_code']])
            safe_code = html.escape(str(provider['provider_code']))
            quartile_color = html.escape(str(ranking['quartile_color']))
            quartile_name = html.escape(str(ranking['quartile']))

            mom_color = html.escape(str(momentum.get('momentum_color', '#64748B')))
            mom_text = html.escape(str(momentum.get('momentum_text', 'Unavailable')))
            if momentum.get('disabled', False):
                mom_detail = "No prior-year results to compare"
            else:
                mom_detail = (f"{momentum.get('latest_year', 2026)} vs {momentum.get('prior_year', 2025)}, "
                              f"{momentum.get('total_measures_compared', 0)} measures")

            if "error" in priority:
                _report_internal_error("comparison priority error", priority.get("error"))
                priority_headline = "Unavailable"
                priority_detail = ""
                priority_color = "#64748B"
            else:
                priority_headline = html.escape(str(priority.get('priority_measure', 'N/A')))
                priority_detail = (f"{html.escape(str(priority.get('priority_description', '')))} "
                                   f"({html.escape(str(priority.get('priority_level', '')))} priority, "
                                   f"{_ordinal(priority.get('percentile', 0))} percentile)")
                priority_color = html.escape(str(priority.get('priority_color', '#0B5C70')))

            with col:
                st.markdown(f"""
                <div class="metric-card compare-card" style="--compare-accent: {accent};">
                    <p class="compare-name">{safe_name}</p>
                    <p class="compare-code">{safe_code}</p>
                    <div class="compare-section">
                        <p class="compare-section-label">Rank</p>
                        <p class="compare-headline">#{ranking['rank']} <span style="font-size: 0.95rem; font-weight: 500; color: #6C7A89;">of {ranking['total_providers']}</span></p>
                        <p class="compare-detail" style="color: {quartile_color}; font-weight: 600;">{quartile_name} quartile ({_ordinal(ranking['percentile'])} percentile)</p>
                        <p class="compare-detail">Average score {ranking['score']:.1f} across {ranking['measures_count']} measures</p>
                    </div>
                    <div class="compare-section">
                        <p class="compare-section-label">Momentum</p>
                        <p class="compare-headline" style="font-size: 1.15rem; color: {mom_color};">{mom_text}</p>
                        <p class="compare-detail">{html.escape(mom_detail)}</p>
                    </div>
                    <div class="compare-section">
                        <p class="compare-section-label">Priority</p>
                        <p class="compare-headline" style="font-size: 1.15rem; color: {priority_color};">{priority_headline}</p>
                        <p class="compare-detail">{priority_detail}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        if not providers:
            return

        # --- What the group has in common, and where it diverges ---
        measures = comparison.get('measures', [])
        insights = []
        widest = comparison.get('widest_gap')
        if widest and widest.get('spread'):
            high = ", ".join(labels[c] for c in widest['highest'])
            low = ", ".join(labels[c] for c in widest['lowest'])
            insights.append(
                f"**Widest gap:** {widest['description']} ({widest['measure']}) - "
                f"{widest['spread']:.1f} points between {high} and {low}."
            )
        descriptions = {m['measure']: m['description'] for m in measures}
        below = comparison.get('shared_below_median', [])
        if below:
            listed = "; ".join(f"{descriptions[tp]} ({tp})" for tp in below)
            insights.append(f"**Below the peer median for every provider:** {listed}.")
        above = comparison.get('shared_above_median', [])
        if above:
            listed = "; ".join(f"{descriptions[tp]} ({tp})" for tp in above)
            insights.append(f"**At or above the peer median for every provider:** {listed}.")

        if insights:
            st.markdown("### Across the group")
            for line in insights:
                st.markdown(f"- {line}")

        if not measures:
            st.warning("No measure-level results are available for these providers.")
            return

        # --- Measure-by-measure chart ---
        st.markdown("### Measure by measure")
        measure_codes = [m['measure'] for m in measures]
        fig = go.Figure()
        for i, provider in enumerate(providers):
            code = provider['provider_code']
            scores = [m['values'][code]['score'] for m in measures]
            fig.add_trace(go.Bar(
                name=labels[code],
                x=measure_codes,
                y=scores,
                marker_color=self.COMPARE_COLORS[i % len(self.COMPARE_COLORS)],
                customdata=[m['description'] for m in measures],
                hovertemplate="%{customdata}<br>%{y:.1f}%<extra>%{fullData.name}</extra>",
            ))
        fig.update_layout(
            title="Scores by measure",
            xaxis_title="TSM Measures",
            yaxis_title="Score (%)",
            barmode='group',
            height=420,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
            **PLOTLY_LAYOUT,
        )
        fig.update_layout(margin=dict(l=60, r=20, t=90, b=60))
        st.plotly_chart(fig, width='stretch')

        # --- Tables: scores, and position within the peer group ---
        def build_table(field: str, suffix: str) -> pd.DataFrame:
            rows = []
            for m in measures:
                row = {'Measure': m['measure'], 'Description': m['description']}
                for provider in providers:
                    code = provider['provider_code']
                    value = m['values'][code][field]
                    row[labels[code]] = f"{value:.1f}{suffix}" if value is not None else "N/A"
                if field == 'score' and len(providers) > 1:
                    row['Highest'] = ", ".join(labels[c] for c in m['highest']) or "-"
                    row['Gap (pts)'] = f"{m['spread']:.1f}" if m['spread'] is not None else "-"
                rows.append(row)
            return pd.DataFrame(rows)

        # Tall enough to show every measure without an inner scrollbar.
        table_height = 35 * (len(measures) + 1) + 3

        scores_tab, percentiles_tab = st.tabs(["Scores", "Position in peer group"])
        with scores_tab:
            if len(providers) > 1:
                st.caption("Published satisfaction scores (%). Gap is the difference between the highest and lowest of the providers shown.")
            else:
                st.caption("Published satisfaction scores (%).")
            st.dataframe(build_table('score', ''), hide_index=True, width='stretch', height=table_height)
        with percentiles_tab:
            st.caption("Percentile within the peer group for each measure. Higher is better.")
            st.dataframe(build_table('percentile', ''), hide_index=True, width='stretch', height=table_height)
