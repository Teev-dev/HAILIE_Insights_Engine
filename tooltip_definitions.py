"""
Tooltip definitions for complex data metrics in the HAILIE TSM Dashboard
"""


class TooltipDefinitions:
    """
    Centralized tooltip definitions for all complex metrics and technical terms
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
                
                **Color coding**: Green (top) → Light Green → Orange → Red (bottom)
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
                • **TP02**: Satisfaction with repairs
                • **TP03**: Time taken for recent repair
                • **TP04**: Satisfaction with repair time
                • **TP05**: Home is well-maintained
                • **TP06**: Home is safe
                • **TP07**: Satisfaction with neighbourhood
                • **TP08**: Landlord's neighbourhood contribution
                • **TP09**: Complaint handling approach
                • **TP10**: Landlord treats residents fairly
                • **TP11**: Landlord listens to residents
                • **TP12**: Anti-social behaviour handling
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
