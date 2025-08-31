import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

class ExecutiveDashboard:
    """
    Renders the executive dashboard with key metrics
    """
    
    def render_executive_summary(self, provider_code: str, rankings: Dict, momentum: Dict, priority: Dict, include_confidence: bool = True):
        """
        Render the main executive summary with three key metrics
        """
        st.markdown("## 📊 Executive Summary")
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
        
        # Create three columns for the key metrics
        col1, col2, col3 = st.columns(3)
        
        # YOUR RANK
        with col1:
            quartile_class = f"quartile-{provider_ranking['quartile'].lower()}"
            
            st.markdown(f"""
            <div class="metric-card {quartile_class}">
                <p class="metric-label">🏆 YOUR RANK</p>
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
        
        # YOUR MOMENTUM
        with col2:
            if momentum.get('disabled', False):
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-label">📈 YOUR MOMENTUM</p>
                    <p class="metric-value" style="color: {momentum['momentum_color']};">
                        {momentum['momentum_icon']}
                    </p>
                    <p style="font-size: 1.5rem; font-weight: 600; color: {momentum['momentum_color']}; margin: 0.5rem 0;">
                        {momentum['momentum_text']}
                    </p>
                    <p style="font-size: 0.9rem; color: #64748B;">
                        Requires multi-year TSM data for true momentum analysis
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-label">📈 YOUR MOMENTUM</p>
                    <p class="metric-value" style="color: {momentum['momentum_color']};">
                        {momentum['momentum_icon']}
                    </p>
                    <p style="font-size: 1.5rem; font-weight: 600; color: {momentum['momentum_color']}; margin: 0.5rem 0;">
                        {momentum['momentum_text']}
                    </p>
                    <p style="font-size: 0.9rem; color: #64748B;">
                        Relative to peer average: {momentum['relative_performance']:+.1f} points
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # YOUR PRIORITY
        with col3:
            priority_class = "priority-high" if priority['priority_level'] in ['Critical', 'High'] else ""
            
            # Format correlation strength for display
            corr_strength = priority.get('correlation_strength', 0)
            corr_text = "Strong" if corr_strength > 70 else "Moderate" if corr_strength > 40 else "Weak"
            
            st.markdown(f"""
            <div class="metric-card {priority_class}">
                <p class="metric-label">🎯 YOUR PRIORITY</p>
                <p class="metric-value" style="font-size: 1.8rem; color: {priority['priority_color']};">
                    {priority['priority_level']}
                </p>
                <p style="font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0; color: #1E293B;">
                    {priority['measure_name']}
                </p>
                <p style="font-size: 0.9rem; color: #64748B;">
                    Current: {priority['current_percentile']:.1f}th percentile
                </p>
                <p style="font-size: 0.9rem; color: {priority['priority_color']}; font-weight: 500;">
                    Improvement potential: {priority['improvement_potential']:.1f}%
                </p>
                <p style="font-size: 0.85rem; color: #475569; margin-top: 0.3rem;">
                    TP01 correlation: {corr_text} ({corr_strength:.1f}%)
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_detailed_analysis(self, df: pd.DataFrame, provider_code: str, analytics):
        """
        Render detailed analysis section with correlation insights
        """
        st.markdown("### 🔍 Detailed Performance Analysis")
        
        # Get detailed analysis and priority data
        detailed_analysis = analytics.get_detailed_performance_analysis(df, provider_code)
        priority_data = analytics.identify_priority(df, provider_code)
        
        if "error" in detailed_analysis:
            st.error(detailed_analysis["error"])
            return
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Performance Comparison", "🔗 Correlation Analysis", "🎯 Priority Matrix"])
        
        with tab1:
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
                
                # Create comparison chart
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='Your Score',
                    x=measures,
                    y=provider_scores,
                    marker_color='#2E5BBA'
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
                    xaxis_title="Satisfaction Measures",
                    yaxis_title="Score",
                    barmode='group',
                    height=500,
                    showlegend=True,
                    xaxis={'tickangle': -45}
                )
                
                st.plotly_chart(fig, width='stretch')
                
                # Performance table
                st.markdown("#### 📋 Detailed Breakdown")
                
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
                st.dataframe(table_df, width='stretch')
        
        with tab2:
            st.markdown("#### 🔗 Correlation with Overall Satisfaction (TP01)")
            
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
                    
                    fig_corr.add_trace(go.Bar(
                        x=corr_df['Correlation'],
                        y=[f"{row['Measure']}\n{row['Description'][:25]}..." for _, row in corr_df.iterrows()],
                        orientation='h',
                        marker_color=colors,
                        text=[f"{c:.3f}" for c in corr_df['Correlation']],
                        textposition='outside'
                    ))
                    
                    fig_corr.update_layout(
                        title="Correlation of Each Measure with Overall Satisfaction (TP01)",
                        xaxis_title="Correlation Coefficient",
                        yaxis_title="Measures",
                        height=500,
                        xaxis=dict(range=[-1, 1]),
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_corr, width='stretch')
                    
                    # Correlation insights
                    st.markdown("##### 📈 Key Correlation Insights")
                    
                    strong_correlations = corr_df[corr_df['Strength'] > 0.7]
                    if not strong_correlations.empty:
                        st.success(f"**Strong correlations:** {', '.join(strong_correlations['Measure'].tolist())} show strong relationships with overall satisfaction")
                    
                    weak_correlations = corr_df[corr_df['Strength'] < 0.3]
                    if not weak_correlations.empty:
                        st.info(f"**Weak correlations:** {', '.join(weak_correlations['Measure'].tolist())} have minimal impact on overall satisfaction")
                    
                    # Detailed correlation table
                    st.markdown("##### 📊 Correlation Statistics")
                    
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
                    
                    st.dataframe(display_df, width='stretch')
                else:
                    st.warning("Insufficient data to calculate correlations with TP01")
            else:
                st.warning("Correlation analysis not available")
        
        with tab3:
            st.markdown("#### 🎯 Priority Matrix")
            
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
                    
                    # Create priority matrix scatter plot
                    fig_matrix = go.Figure()
                    
                    # Color based on weighted priority
                    fig_matrix.add_trace(go.Scatter(
                        x=scatter_df['Improvement Potential'],
                        y=scatter_df['Correlation'],
                        mode='markers+text',
                        marker=dict(
                            size=scatter_df['Weighted Priority'],
                            color=scatter_df['Weighted Priority'],
                            colorscale='RdYlGn_r',
                            showscale=True,
                            colorbar=dict(title="Priority Score")
                        ),
                        text=scatter_df['Measure'],
                        textposition="top center",
                        hovertemplate="<b>%{text}</b><br>" +
                                      "Improvement Potential: %{x:.1f}%<br>" +
                                      "TP01 Correlation: %{y:.1f}%<br>" +
                                      "<extra></extra>"
                    ))
                    
                    # Add quadrant lines
                    fig_matrix.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
                    fig_matrix.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5)
                    
                    # Add quadrant labels
                    fig_matrix.add_annotation(x=75, y=75, text="High Priority", showarrow=False, font=dict(size=12, color="red"))
                    fig_matrix.add_annotation(x=25, y=75, text="Quick Wins", showarrow=False, font=dict(size=12, color="green"))
                    fig_matrix.add_annotation(x=75, y=25, text="Monitor", showarrow=False, font=dict(size=12, color="orange"))
                    fig_matrix.add_annotation(x=25, y=25, text="Low Priority", showarrow=False, font=dict(size=12, color="gray"))
                    
                    fig_matrix.update_layout(
                        title="Priority Matrix: Improvement Potential vs TP01 Correlation",
                        xaxis_title="Improvement Potential (%)",
                        yaxis_title="Correlation with Overall Satisfaction (%)",
                        height=600,
                        xaxis=dict(range=[0, 100]),
                        yaxis=dict(range=[0, 100])
                    )
                    
                    st.plotly_chart(fig_matrix, width='stretch')
                    
                    # Top 3 priorities
                    if 'top_3_priorities' in priority_data:
                        st.markdown("##### 🏆 Top 3 Priority Areas")
                        
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
        st.markdown("### 📊 Data Quality Report")
        
        quality_report = data_processor.get_data_quality_report(df)
        
        if not quality_report:
            st.warning("No data quality information available")
            return
        
        # Summary metrics
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
            st.dataframe(completeness_df, width='stretch')
        
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
            st.dataframe(ranges_df, width='stretch')
    
    def render_insights_summary(self, rankings: Dict, momentum: Dict, priority: Dict, provider_code: str):
        """
        Render actionable insights summary
        """
        st.markdown("### 💡 Key Insights & Recommendations")
        
        if provider_code not in rankings:
            st.warning("No ranking data available for insights")
            return
        
        provider_ranking = rankings[provider_code]
        
        insights = []
        
        # Ranking insights
        if provider_ranking['quartile'] == 'Top':
            insights.append("🎉 **Excellent performance** - You're in the top quartile of providers!")
        elif provider_ranking['quartile'] == 'Low':
            insights.append("⚠️ **Performance attention needed** - You're in the bottom quartile.")
        
        # Momentum insights
        if momentum.get('disabled', False):
            insights.append("⏳ **Momentum analysis** - Will be available in 2026 with multi-year TSM data.")
        elif momentum['direction'] == 'up':
            insights.append(f"📈 **Positive momentum** - {momentum['momentum_text']} trajectory detected.")
        elif momentum['direction'] == 'down':
            insights.append(f"📉 **Declining trend** - {momentum['momentum_text']} requires immediate attention.")
        
        # Priority insights with correlation context
        if priority['priority_level'] in ['Critical', 'High']:
            corr_strength = priority.get('correlation_strength', 0)
            corr_text = "strong" if corr_strength > 70 else "moderate" if corr_strength > 40 else "weak"
            insights.append(f"🚨 **Priority action required** - Focus on {priority['measure_name']} for maximum impact (has {corr_text} correlation with overall satisfaction).")
        
        # Display insights
        for insight in insights:
            st.markdown(insight)
        
        # Recommendations
        st.markdown("#### 🎯 Recommended Actions")
        
        # Enhanced recommendations with correlation insights
        corr_strength = priority.get('correlation_strength', 0)
        impact_text = "high impact on overall satisfaction" if corr_strength > 70 else "moderate impact on overall satisfaction" if corr_strength > 40 else "some impact on overall satisfaction"
        
        recommendations = [
            f"1. **Focus on {priority['measure_name']}** - This has the highest improvement potential ({priority['improvement_potential']:.1f}%) with {impact_text}",
            f"2. **Benchmark against top quartile** - Learn from providers scoring above {provider_ranking.get('top_quartile_threshold', 'N/A')}"
        ]
        
        # Add momentum recommendation only if not disabled
        if not momentum.get('disabled', False):
            recommendations.append(f"3. **Monitor momentum** - Track monthly progress to maintain {momentum['momentum_text'].lower()} trend")
        else:
            recommendations.append("3. **Prepare for momentum tracking** - Set up data collection processes for 2025 TSM analysis")
        
        # Add top 3 priorities if available
        if 'top_3_priorities' in priority and len(priority['top_3_priorities']) > 1:
            recommendations.append(f"4. **Secondary priorities** - Also consider {priority['top_3_priorities'][1]['name']} and {priority['top_3_priorities'][2]['name'] if len(priority['top_3_priorities']) > 2 else 'other measures'}")
        
        for rec in recommendations:
            st.markdown(rec)
