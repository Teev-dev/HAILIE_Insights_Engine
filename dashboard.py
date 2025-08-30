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
            </div>
            """, unsafe_allow_html=True)
    
    def render_detailed_analysis(self, df: pd.DataFrame, provider_code: str, analytics):
        """
        Render detailed analysis section
        """
        st.markdown("### 🔍 Detailed Performance Analysis")
        
        # Get detailed analysis
        detailed_analysis = analytics.get_detailed_performance_analysis(df, provider_code)
        
        if "error" in detailed_analysis:
            st.error(detailed_analysis["error"])
            return
        
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
            
            st.plotly_chart(fig, use_container_width=True)
            
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
            st.dataframe(table_df, use_container_width=True)
    
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
            st.dataframe(completeness_df, use_container_width=True)
        
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
            st.dataframe(ranges_df, use_container_width=True)
    
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
        if momentum['direction'] == 'up':
            insights.append(f"📈 **Positive momentum** - {momentum['momentum_text']} trajectory detected.")
        elif momentum['direction'] == 'down':
            insights.append(f"📉 **Declining trend** - {momentum['momentum_text']} requires immediate attention.")
        
        # Priority insights
        if priority['priority_level'] in ['Critical', 'High']:
            insights.append(f"🚨 **Priority action required** - Focus on {priority['measure_name']} for maximum impact.")
        
        # Display insights
        for insight in insights:
            st.markdown(insight)
        
        # Recommendations
        st.markdown("#### 🎯 Recommended Actions")
        
        recommendations = [
            f"1. **Focus on {priority['measure_name']}** - This has the highest improvement potential ({priority['improvement_potential']:.1f}%)",
            f"2. **Benchmark against top quartile** - Learn from providers scoring above {provider_ranking.get('top_quartile_threshold', 'N/A')}",
            f"3. **Monitor momentum** - Track monthly progress to maintain {momentum['momentum_text'].lower()} trend"
        ]
        
        for rec in recommendations:
            st.markdown(rec)
