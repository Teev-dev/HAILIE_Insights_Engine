import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
from tooltip_definitions import TooltipDefinitions
from mobile_utils import detect_mobile, mobile_friendly_columns, should_show_component


def _corr_label(strength: float) -> str:
    """Qualitative label for correlation strength (absolute value)."""
    s = abs(strength)
    if s >= 0.70:
        return "Strong"
    if s >= 0.40:
        return "Moderate"
    if s >= 0.20:
        return "Weak"
    return "Negligible"


# Consistent Plotly layout defaults for editorial aesthetic
PLOTLY_LAYOUT = dict(
    font=dict(
        family='-apple-system, BlinkMacSystemFont, Inter, Segoe UI, sans-serif',
        size=12,
        color='#1E293B'
    ),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(250,250,250,1)',
    margin=dict(l=60, r=20, t=50, b=60),
)


class ExecutiveDashboard:
    """
    Renders the executive dashboard with key metrics
    """

    def render_executive_summary(self, provider_code: str, rankings: Dict, momentum: Dict, priority: Dict, include_confidence: bool = True):
        """
        Render the main executive summary with three key metrics
        """
        # Get tooltip definitions
        tooltips = TooltipDefinitions()
        metric_tooltips = tooltips.get_metric_tooltips()
        technical_tooltips = tooltips.get_technical_tooltips()
        
        # Check if mobile
        is_mobile = detect_mobile()

        if not is_mobile:
            col_header1, col_header2 = st.columns([4, 1], gap="medium")
            with col_header1:
                st.markdown("## Executive Summary")
                st.markdown(f"**Provider:** {provider_code}")
            with col_header2:
                # Add overall help for the executive summary
                with st.expander("Understanding Your Dashboard", expanded=False):
                    st.markdown("""
                    **Your dashboard shows three key insights:**

                    **Your Rank**: How you compare to other housing providers
                    **Your Momentum**: Your performance trend over time  
                    **Your Priority**: Most important area to focus on

                    Click the help icons (?) next to each metric for detailed explanations.
                    """)
        else:
            # Mobile: Simpler header
            st.markdown("## Executive Summary")
            st.markdown(f"**Provider:** {provider_code}")

        st.markdown("---")

        # Check for errors
        if "error" in rankings:
            st.error(f"Rankings Error: {rankings['error']}")
            return

        if "error" in momentum:
            st.error(f"Momentum Error: {momentum['error']}")
            return

        if "error" in priority:
            st.error(f"Priority Error: {priority['error']}")
            return

        # Get provider data
        if provider_code not in rankings:
            st.error(f"No ranking data found for provider {provider_code}")
            return

        provider_ranking = rankings[provider_code]

        # Create responsive columns for the key metrics - mobile-friendly
        if is_mobile:
            # Mobile: Single column layout with native components
            cols = [st.container(), st.container(), st.container()]
        else:
            cols = st.columns([1, 1, 1], gap="medium")

        # YOUR RANK
        with cols[0]:
            if is_mobile:
                # Mobile: Use native Streamlit components
                st.markdown("### 📊 YOUR RANK")
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
                quartile_class = f"quartile-{provider_ranking['quartile'].lower()}"
                st.markdown(f"""
                <div class="metric-card {quartile_class}">
                    <p class="metric-label">YOUR RANK</p>
                    <p class="metric-value">#{provider_ranking['rank']}</p>
                    <p style="font-size: 1.1rem; margin: 0.5rem 0; color: #64748B;">
                        of {provider_ranking['total_providers']} providers
                    </p>
                    <p style="font-size: 1rem; font-weight: 600; color: {provider_ranking['quartile_color']};">
                        {provider_ranking['quartile']} Quartile ({provider_ranking['percentile']:.1f}th percentile)
                    </p>
                    <p style="font-size: 0.9rem; color: #64748B; margin-top: 0.5rem;">
                        Based on {provider_ranking['measures_count']} satisfaction measures
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # Add expandable help section
            with st.expander("How Your Rank Works", expanded=False):
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
                st.markdown("### 📈 YOUR MOMENTUM")
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
                    st.markdown(f"""
                    <div class="metric-card">
                        <p class="metric-label">YOUR MOMENTUM</p>
                        <p class="metric-value" style="color: {momentum['momentum_color']};">
                            {momentum['momentum_icon']}
                        </p>
                        <p style="font-size: 1.5rem; font-weight: 600; color: {momentum['momentum_color']}; margin: 0.5rem 0;">
                            {momentum['momentum_text']}
                        </p>
                        <p style="font-size: 0.9rem; color: #64748B;">
                            Insufficient multi-year data
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Build the performance comparison sections
                    improved = momentum.get('improved_measures', [])
                    declined = momentum.get('declined_measures', [])
                    
                    # Start building the HTML
                    card_html = f"""
                    <div class="metric-card">
                        <p class="metric-label">YOUR MOMENTUM</p>
                        <p class="metric-value" style="color: {momentum['momentum_color']};">
                            {momentum['momentum_icon']}
                        </p>
                        <p style="font-size: 1.5rem; font-weight: 600; color: {momentum['momentum_color']}; margin: 0.5rem 0;">
                            {momentum['momentum_text']}
                        </p>
                        <p style="font-size: 0.9rem; color: #64748B; margin-bottom: 0.25rem;">
                            <strong>{momentum.get('latest_year', 2025)} vs {momentum.get('prior_year', 2024)}:</strong> {momentum['year_over_year_change']:+.1f} points average
                        </p>
                        <p style="font-size: 0.8rem; color: #64748B; margin-bottom: 0.5rem;">
                            {momentum.get('total_measures_compared', 0)} measures compared
                        </p>
                        <p style="font-size: 0.9rem; font-weight: 600; color: #1E293B; margin-top: 0.5rem; margin-bottom: 0.5rem;">
                            Your {momentum.get('latest_year', 2025)} vs {momentum.get('prior_year', 2024)} performance:
                        </p>
                    """
                    
                    # Add improvements section if available
                    if improved:
                        card_html += '<p style="font-size: 0.85rem; font-weight: 600; color: #22C55E; margin-bottom: 0.25rem;">Top Improvements:</p>'
                        for measure in improved[:3]:
                            card_html += f'<p style="font-size: 0.8rem; color: #475569; margin: 0.1rem 0; padding-left: 0.5rem;">• {measure["description"]}: +{measure["change"]:.1f} pts</p>'
                    
                    # Add declined section if available
                    if declined:
                        card_html += '<p style="font-size: 0.85rem; font-weight: 600; color: #EF4444; margin-bottom: 0.25rem; margin-top: 0.5rem;">Areas Needing Attention:</p>'
                        for measure in declined[:3]:
                            card_html += f'<p style="font-size: 0.8rem; color: #475569; margin: 0.1rem 0; padding-left: 0.5rem;">• {measure["description"]}: {measure["change"]:.1f} pts</p>'
                    
                    # Close the card
                    card_html += "</div>"
                    
                    st.markdown(card_html, unsafe_allow_html=True)

            # Add expandable help section for momentum
            with st.expander("How Momentum Works", expanded=False):
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
                    **Your {momentum.get('latest_year', 2025)} vs {momentum.get('prior_year', 2024)} performance:**
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
            # Format data for display — use raw coefficient (0-1) with qualitative label
            raw_corr = abs(priority.get('correlation_with_tp01', 0))
            corr_text = _corr_label(raw_corr)

            measure_code = priority.get('priority_measure', priority.get('measure', 'N/A'))
            measure_desc = priority.get('priority_description', priority.get('measure_name', 'No priority identified'))
            current_percentile = priority.get('percentile', priority.get('current_percentile', 0))
            improvement = priority.get('improvement_potential', 0)
            
            if is_mobile:
                # Mobile: Use native Streamlit components
                st.markdown("### 🎯 YOUR PRIORITY")
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
                st.markdown(f"""
                <div class="metric-card {priority_class}">
                    <p class="metric-label">YOUR PRIORITY</p>
                    <p class="metric-value" style="font-size: 1.8rem; color: {priority.get('priority_color', '#2E5BBA')};">
                        {priority.get('priority_level', 'Medium')}
                    </p>
                    <p style="font-size: 1.3rem; font-weight: 700; margin: 0.3rem 0; color: #2E5BBA;">
                        {measure_code}
                    </p>
                    <p style="font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0; color: #1E293B;">
                        {measure_desc}
                    </p>
                    <p style="font-size: 0.9rem; color: #64748B;">
                        Current: {current_percentile:.1f}th percentile
                    </p>
                    <p style="font-size: 0.9rem; color: {priority.get('priority_color', '#2E5BBA')}; font-weight: 500;">
                        Improvement potential: {improvement:.1f}%
                    </p>
                    <p style="font-size: 0.85rem; color: #475569; margin-top: 0.3rem;">
                        TP01 correlation: {corr_text} ({raw_corr:.2f})
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # Add expandable help section for priority
            with st.expander("How Priority Works", expanded=False):
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
            st.error(detailed_analysis["error"])
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
        with st.expander("📊 Performance Comparison", expanded=True):
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
                    marker_color='#2E5BBA',
                    hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>",
                    customdata=hover_data_your
                ))

                fig.add_trace(go.Bar(
                    name='Peer Average',
                    x=measures,
                    y=peer_averages,
                    marker_color='#64748B',
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
        with st.expander("📈 Correlation Analysis", expanded=False):
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

                    colors = ['#22C55E' if c > 0 else '#EF4444' for c in corr_df['Correlation']]

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
        with st.expander("🎯 Priority Matrix", expanded=False):
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

                        corr_raw = row['Correlation'] / 100  # Convert back to coefficient for display
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
                        mode='markers+text',
                        marker=dict(
                            size=scatter_df['Weighted Priority']*0.8+10,  # Better size scaling
                            color=scatter_df['Weighted Priority'],
                            colorscale='RdYlGn_r',
                            showscale=True,
                            colorbar=dict(title="Priority Score"),
                            line=dict(width=1, color='white')  # Add border for better visibility
                        ),
                        text=scatter_df['Measure'],
                        textposition="top center",
                        hovertemplate="<b>%{text}</b><br>%{customdata}<extra></extra>",
                        customdata=matrix_hover_data
                    ))

                    # Add quadrant lines
                    fig_matrix.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
                    fig_matrix.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5)

                    # Add quadrant labels
                    fig_matrix.add_annotation(x=75, y=75, text="High Priority", showarrow=False, font=dict(size=12, color="red"))
                    fig_matrix.add_annotation(x=25, y=75, text="Maintain & Protect", showarrow=False, font=dict(size=12, color="green"))
                    fig_matrix.add_annotation(x=75, y=25, text="Lower Impact", showarrow=False, font=dict(size=12, color="orange"))
                    fig_matrix.add_annotation(x=25, y=25, text="Low Priority", showarrow=False, font=dict(size=12, color="gray"))

                    fig_matrix.update_layout(
                        title="Priority Matrix: Improvement Potential vs TP01 Correlation - Hover for Details",
                        xaxis_title="Improvement Potential (%) →",
                        yaxis_title="Relationship with Overall Satisfaction ↑",
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

    def render_insights_summary(self, rankings: Dict, momentum: Dict, priority: Dict, provider_code: str):
        """
        Render actionable insights summary
        """
        st.markdown("### Key Insights & Recommendations")

        if provider_code not in rankings:
            st.warning("No ranking data available for insights")
            return

        provider_ranking = rankings[provider_code]

        insights = []

        # Ranking insights
        if provider_ranking['quartile'] == 'Top':
            insights.append("**Excellent performance** - You're in the top quartile of providers!")
        elif provider_ranking['quartile'] == 'Low':
            insights.append("**Performance attention needed** - You're in the bottom quartile.")

        # Momentum insights
        if momentum.get('disabled', False):
            insights.append("**Momentum analysis** - Insufficient data for year-over-year comparison.")
        elif momentum['direction'] == 'up':
            improved_count = len(momentum.get('improved_measures', []))
            insights.append(f"**Positive momentum** - {momentum['momentum_text']} with {improved_count} measures showing significant improvement.")
        elif momentum['direction'] == 'down':
            declined_count = len(momentum.get('declined_measures', []))
            insights.append(f"**Declining trend** - {momentum['momentum_text']} with {declined_count} measures needing immediate attention.")
        elif momentum['direction'] == 'stable':
            insights.append(f"**Stable performance** - {momentum['momentum_text']} year-over-year.")

        # Priority insights with correlation context
        if priority.get('priority_level', '') in ['Critical', 'High']:
            raw_corr_insight = abs(priority.get('correlation_with_tp01', 0))
            corr_text_insight = _corr_label(raw_corr_insight).lower()
            measure_name = priority.get('priority_description', priority.get('measure_name', 'this area'))
            insights.append(f"**Priority action required** - Focus on {measure_name} for maximum impact ({corr_text_insight} correlation with overall satisfaction).")

        # Display insights
        for insight in insights:
            st.markdown(insight)

        # Recommendations
        st.markdown("#### Recommended Actions")

        # Enhanced recommendations with correlation insights
        raw_corr_rec = abs(priority.get('correlation_with_tp01', 0))
        impact_text = "high impact on overall satisfaction" if raw_corr_rec >= 0.70 else "moderate impact on overall satisfaction" if raw_corr_rec >= 0.40 else "some impact on overall satisfaction"

        recommendations = [
            f"1. **Focus on {priority['measure_name']}** - This has the highest improvement potential ({priority['improvement_potential']:.1f}%) with {impact_text}",
            f"2. **Benchmark against top quartile** - Learn from providers scoring above {provider_ranking.get('top_quartile_threshold', 'N/A')}"
        ]

        # Add momentum recommendation only if not disabled
        if not momentum.get('disabled', False):
            if momentum['direction'] == 'up':
                recommendations.append(f"3. **Sustain improvements** - Continue focus areas that drove {len(momentum.get('improved_measures', []))} measure improvements")
            elif momentum['direction'] == 'down':
                declined = momentum.get('declined_measures', [])
                if declined:
                    recommendations.append(f"3. **Address decline** - Prioritize {declined[0]['description']} which declined {declined[0]['change']:.1f} points")
            else:
                recommendations.append("3. **Build on stability** - Identify breakthrough opportunities to move from stable to improving")
        else:
            recommendations.append("3. **Establish baseline** - Ensure 2025 data collection for future year-over-year tracking")

        # Add top 3 priorities if available
        if 'top_3_priorities' in priority and len(priority['top_3_priorities']) > 1:
            recommendations.append(f"4. **Secondary priorities** - Also consider {priority['top_3_priorities'][1]['name']} and {priority['top_3_priorities'][2]['name'] if len(priority['top_3_priorities']) > 2 else 'other measures'}")

        for rec in recommendations:
            st.markdown(rec)

    def render_performance_analysis(self, detailed_analysis: Dict):
        """
        Render performance analysis visualization
        """
        if not detailed_analysis:
            st.warning("No performance analysis data available")
            return

        if "error" in detailed_analysis:
            st.error(detailed_analysis["error"])
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
                marker_color='#2E5BBA',
                text=[f"{s:.1f}" for s in provider_scores],
                textposition='outside'
            ))

            fig.add_trace(go.Bar(
                name='Peer Average',
                x=measures,
                y=peer_averages,
                marker_color='#64748B',
                opacity=0.7
            ))

            fig.update_layout(
                title="Performance Comparison by Measure",
                xaxis_title="TSM Measures",
                yaxis_title="Score",
                barmode='group',
                height=400,
                **PLOTLY_LAYOUT
            )

            st.plotly_chart(fig, width='stretch')

            # Performance table
            st.markdown("#### Detailed Scores")
            table_data = []
            for tp_code, data in detailed_analysis.items():
                table_data.append({
                    'Measure': tp_code,
                    'Description': data['description'][:40] + '...' if len(data['description']) > 40 else data['description'],
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

        colors = ['#22C55E' if c > 0 else '#EF4444' for c in correlations['correlation_with_tp01']]

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
            **PLOTLY_LAYOUT
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
            st.error(priority["error"])
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

                # Color based on priority score
                if data['priority_score'] > 70:
                    colors.append('#EF4444')  # Red - Critical
                elif data['priority_score'] > 50:
                    colors.append('#F59E0B')  # Orange - High
                elif data['priority_score'] > 30:
                    colors.append('#EAB308')  # Yellow - Medium
                else:
                    colors.append('#22C55E')  # Green - Low

            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode='markers+text',
                text=labels,
                textposition='top center',
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
                showlegend=False
            )

            # Add quadrant lines
            fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.3)
            fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.3)

            # Add quadrant labels
            fig.add_annotation(x=75, y=75, text="High Priority", showarrow=False, font=dict(size=11, color="red"))
            fig.add_annotation(x=25, y=75, text="Maintain & Protect", showarrow=False, font=dict(size=11, color="green"))
            fig.add_annotation(x=75, y=25, text="Lower Impact", showarrow=False, font=dict(size=11, color="orange"))
            fig.add_annotation(x=25, y=25, text="Low Priority", showarrow=False, font=dict(size=11, color="gray"))

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