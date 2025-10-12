# Patch for missing dashboard methods
# These methods should be added to the ExecutiveDashboard class in dashboard.py

def render_performance_analysis(self, detailed_analysis: Dict):
    """
    Render performance analysis visualization
    """
    if "error" in detailed_analysis:
        st.error(detailed_analysis["error"])
        return
        
    if detailed_analysis:
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
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
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
        st.dataframe(table_df, use_container_width=True)

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
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Correlation table
    st.markdown("#### Correlation Details")
    table_data = correlations[['tp_measure', 'correlation_with_tp01', 'p_value']].copy()
    table_data.columns = ['Measure', 'Correlation', 'P-Value']
    table_data['Correlation'] = table_data['Correlation'].apply(lambda x: f"{x:.3f}")
    table_data['P-Value'] = table_data['P-Value'].apply(lambda x: f"{x:.4f}")
    
    st.dataframe(table_data, use_container_width=True)

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
            hovertemplate="<b>%{text}</b><br>Improvement: %{x:.1f}%<br>Correlation: %{y:.1f}%<extra></extra>"
        ))
        
        fig.update_layout(
            title="Priority Matrix: Improvement Potential vs Impact",
            xaxis_title="Improvement Potential (%)",
            yaxis_title="Correlation Strength with TP01 (%)",
            height=500,
            showlegend=False
        )
        
        # Add quadrant lines
        fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.3)
        fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.3)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Priority table
        st.markdown("#### Priority Ranking")
        priority_list = sorted(priorities.items(), 
                              key=lambda x: x[1]['priority_score'], 
                              reverse=True)
        
        table_data = []
        for i, (measure, data) in enumerate(priority_list, 1):
            table_data.append({
                'Rank': i,
                'Measure': measure,
                'Priority Score': f"{data['priority_score']:.1f}",
                'Improvement Potential': f"{data['improvement_potential']:.1f}%",
                'Correlation': f"{data['correlation_strength']:.1f}%"
            })
        
        table_df = pd.DataFrame(table_data)
        st.dataframe(table_df, use_container_width=True)
    else:
        st.info("Priority matrix data not available")