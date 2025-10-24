import streamlit as st
import pandas as pd
import numpy as np
from data_processor_enhanced import EnhancedTSMDataProcessor
from analytics_refactored import TSMAnalytics
from dashboard import ExecutiveDashboard
from styles import apply_css
import traceback
from contextlib import contextmanager
import os

# Page configuration
st.set_page_config(page_title="HAILIE TSM Insights Engine",
                   page_icon="✓",
                   layout="wide",
                   initial_sidebar_state="expanded")

# Apply custom CSS styles from styles module
apply_css(st)


def render_landing_hero():
    """Render the professional hero section"""
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">TSM Insights by HAILIE</h1>
        <p class="hero-tagline">Transform Your TSM Performance Into Executive Intelligence</p>
    </div>
    """,
                unsafe_allow_html=True)


def render_features_overview():
    """Render the key features overview section"""
    st.markdown("""
    <div class="features-grid">
        <div class="feature-card">
            <div class="feature-icon-professional rank-icon"></div>
            <h3 class="feature-title">Your Rank</h3>
            <p class="feature-description">
                See exactly how your housing provider compares to peers with quartile-based scoring. 
                Get clear visual indicators showing your competitive position.
            </p>
        </div>
        <div class="feature-card">
            <div class="feature-icon-professional momentum-icon"></div>
            <h3 class="feature-title">Your Momentum</h3>
            <p class="feature-description">
                Track your 12-month performance trajectory. Understand if you're improving, 
                stable, or declining across key satisfaction measures.
            </p>
        </div>
        <div class="feature-card">
            <div class="feature-icon-professional priority-icon"></div>
            <h3 class="feature-title">Your Priority</h3>
            <p class="feature-description">
                Identify the single most critical area for improvement based on data-driven 
                correlation analysis with overall tenant satisfaction.
            </p>
        </div>
    </div>
    """,
                unsafe_allow_html=True)


def check_database_exists():
    """Check if the enhanced analytics database exists"""
    db_path = "attached_assets/hailie_analytics_v2.duckdb"
    return os.path.exists(db_path)


def render_dataset_indicator(dataset_type: str, peer_count: int):
    """Render a visual indicator showing which dataset is being used"""
    if dataset_type == 'LCRA':
        color = "#2E7D32"  # Green
        description = "Large-scale Council & Registered Providers"
        note = "Full TSM metrics including repairs satisfaction"
    elif dataset_type == 'LCHO':
        color = "#1565C0"  # Blue
        description = "Large-scale Voluntary Transfer Organizations"
        note = "Core TSM metrics (repairs metrics not applicable)"
    else:
        color = "#757575"  # Grey
        description = "Combined Dataset"
        note = "Providers with combined reporting"
    
    st.markdown(f"""
    <div style="background-color: {color}15; border-left: 4px solid {color}; padding: 10px; margin: 10px 0; border-radius: 4px;">
        <strong style="color: {color};">Dataset: {dataset_type}</strong><br/>
        <small>{description}</small><br/>
        <small style="opacity: 0.8;">{note}</small><br/>
        <small style="opacity: 0.8;">📊 Comparing with {peer_count} peer providers in {dataset_type} group</small>
    </div>
    """, unsafe_allow_html=True)


def main():
    # Landing page hero section
    render_landing_hero()

    # Key features overview
    render_features_overview()

    # Check if database exists
    if not check_database_exists():
        st.error("""
        ❌ **Enhanced Analytics Database Not Found**
        
        The enhanced analytics database with LCRA/LCHO separation has not been generated yet.
        Please run the enhanced ETL pipeline first:
        
        ```bash
        python build_analytics_db_v2.py
        ```
        
        This will process both LCRA and LCHO datasets and create the enhanced analytics database.
        """)
        return

    # Initialize variables
    show_advanced_logging = False

    # Initialize enhanced data processor to get provider options
    data_processor_for_options = EnhancedTSMDataProcessor(silent_mode=True)
    provider_options = data_processor_for_options.get_provider_options()

    provider_code = None
    selected_dataset_type = None

    # Sidebar for analysis options
    with st.sidebar:
        # Analysis options
        st.header("Analysis Options")
        include_confidence = st.checkbox("Include confidence intervals",
                                         value=True)
        
        # Note about dataset separation
        st.info("""
        🔄 **Automatic Dataset Detection**
        
        The system automatically detects whether your selected provider 
        belongs to the LCRA or LCHO dataset and compares only with 
        appropriate peers.
        
        • **LCRA**: Full TP01-TP12 metrics
        • **LCHO**: TP01, TP05-TP12 (repairs metrics N/A)
        """)

        # Advanced options
        st.markdown("---")
        show_advanced_logging = st.checkbox(
            "Show advanced logging view",
            value=False,
            help="Display detailed processing logs and debugging information")
        
        # Note about the enhanced architecture
        st.markdown("---")
        st.info("""
        📊 **Enhanced Analytics Engine**
        
        This application uses an enhanced analytics database with:
        • Separate LCRA and LCHO datasets
        • Dataset-specific percentiles
        • Peer group isolation
        • Automatic metric adaptation
        
        Data source: 2024 TSM Dataset
        """)

    st.markdown("## Select Your Provider")

    # Single column layout for provider selection
    if provider_options:
        # Provider search dropdown with autocomplete - includes all providers
        st.subheader("Search by Provider Name")
        st.markdown("<small>All LCRA and LCHO providers available</small>", unsafe_allow_html=True)
        
        selected_provider = st.selectbox(
            "Type or select your provider:",
            options=[""] + provider_options,
            help="Start typing to search for your provider - includes both LCRA and LCHO providers",
            format_func=lambda x: "Select a provider..." if x == "" else x)

        # Extract provider code and name from selection
        if selected_provider and selected_provider != "":
            # Format is "Provider Name (CODE)"
            if "(" in selected_provider and ")" in selected_provider:
                provider_code = selected_provider.split("(")[-1].replace(")", "")
                # Extract just the provider name without the code part for dataset detection
                provider_name_only = selected_provider.rsplit("(", 1)[0].strip()
            else:
                provider_code = None
                provider_name_only = selected_provider
        else:
            provider_code = None
            selected_provider = None
            provider_name_only = None
    else:
        st.error("❌ Unable to load provider list. Please try refreshing the page.")
        provider_code = None
        selected_provider = None
        provider_name_only = None

    # Process the selected provider
    if provider_code:
        st.markdown("---")

        # Initialize enhanced data processor and analytics with database connection
        data_processor = EnhancedTSMDataProcessor(silent_mode=not show_advanced_logging)
        
        # Check if provider exists in database
        if not data_processor.get_provider_exists(provider_code):
            st.error(f"❌ Provider '{provider_code}' not found. Please check the code and try again.")
            return

        # Get the dataset type for this provider (use the name without the code part)
        dataset_type = data_processor.get_provider_dataset_type(provider_code, provider_name_only)
        if not dataset_type:
            st.error(f"❌ Could not determine dataset type for provider '{provider_code}'")
            return

        # Get dataset summary stats for context
        dataset_stats = data_processor.get_dataset_summary_stats(dataset_type)
        peer_count = dataset_stats.get('provider_count', 0) - 1  # Exclude the current provider
        
        # Display dataset indicator
        render_dataset_indicator(dataset_type, peer_count)
        
        # Load provider data with automatic dataset detection (pass provider name without code)
        df = data_processor.load_default_data(provider_code, provider_name_only)
        
        if df is None or df.empty:
            st.error("❌ Unable to load provider data. Please try again later.")
            return

        st.success(f"✅ Loaded {dataset_type} analytics for provider: {provider_code}")
        
        # Get applicable measures for this dataset type
        applicable_measures = data_processor.get_applicable_measures(dataset_type)
        
        # Initialize analytics (it will work with the loaded data)
        analytics = TSMAnalytics(data_processor)

        # Calculate key metrics using pre-calculated data within the correct peer group
        rankings = analytics.calculate_rankings(df, "All Providers", dataset_type)
        momentum = analytics.calculate_momentum(df, provider_code)
        
        # Get dataset-specific correlations for priority calculation
        if dataset_type == 'LCHO':
            correlations_df = data_processor.get_dataset_correlations('LCHO')
        else:
            correlations_df = data_processor.get_dataset_correlations('LCRA')
        priority = analytics.identify_priority(df, provider_code)

        # Initialize and render dashboard
        dashboard = ExecutiveDashboard()

        # Executive Summary
        dashboard.render_executive_summary(provider_code, rankings, momentum,
                                          priority)

        # Detailed Analysis Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Performance Analysis",
            "📈 Measure Correlations",
            "🎯 Priority Matrix",
            "📋 Raw Data"
        ])

        with tab1:
            st.markdown(f"### Performance Analysis - {dataset_type} Peer Group")
            
            # Show note for LCHO providers about missing metrics
            if dataset_type == 'LCHO':
                st.info("""
                ℹ️ **Note for LCHO Providers**: 
                Repairs metrics (TP02-TP04) are not applicable to LCHO providers 
                and are excluded from this analysis. All comparisons are made 
                within your LCHO peer group only.
                """)
            
            detailed_analysis = analytics.get_detailed_performance_analysis(
                df, provider_code)
            
            # Filter out N/A metrics for LCHO
            if dataset_type == 'LCHO' and detailed_analysis and not "error" in detailed_analysis:
                detailed_analysis = {
                    k: v for k, v in detailed_analysis.items() 
                    if k not in ['TP02', 'TP03', 'TP04']
                }
            
            dashboard.render_performance_analysis(detailed_analysis)

        with tab2:
            st.markdown(f"### Correlation Analysis - {dataset_type} Dataset")
            
            # Get dataset-specific correlations
            correlations = data_processor.get_dataset_correlations(dataset_type)
            
            if dataset_type == 'LCHO':
                st.info("Correlations calculated using LCHO providers only (excluding repairs metrics)")
            else:
                st.info("Correlations calculated using LCRA providers with all metrics")
            
            dashboard.render_correlation_analysis(correlations, priority)

        with tab3:
            st.markdown(f"### Priority Matrix - {dataset_type} Context")
            
            # Filter priority matrix for LCHO if needed
            if dataset_type == 'LCHO' and priority:
                # Ensure repairs metrics aren't in the priority recommendations
                if 'measure' in priority and priority['measure'] in ['TP02', 'TP03', 'TP04']:
                    st.warning("Priority calculation adjusted for LCHO dataset")
            
            dashboard.render_priority_matrix(priority, detailed_analysis)

        with tab4:
            st.markdown(f"### Raw Data - {dataset_type} Provider")
            
            # Show provider's raw scores
            scores_df = data_processor.get_provider_scores(provider_code)
            if not scores_df.empty:
                # Add descriptions
                scores_df['description'] = scores_df['tp_measure'].apply(lambda x: data_processor.tp_descriptions.get(x, 'Unknown measure'))
                
                # For LCHO, mark repairs metrics as N/A using NaN for numeric compatibility
                if dataset_type == 'LCHO':
                    na_metrics = ['TP02', 'TP03', 'TP04']
                    for metric in na_metrics:
                        if metric in scores_df['tp_measure'].values:
                            scores_df.loc[scores_df['tp_measure'] == metric, 'score'] = np.nan
                            scores_df.loc[scores_df['tp_measure'] == metric, 'description'] += ' (Not Applicable)'
                
                # Format for display
                display_df = scores_df[['tp_measure', 'description', 'score']].copy()
                display_df.columns = ['Measure', 'Description', 'Score (%)']
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Show peer comparison info
                st.markdown(f"""
                **Dataset Information:**
                - Dataset Type: **{dataset_type}**
                - Peer Group Size: **{peer_count} providers**
                - Applicable Measures: **{len(applicable_measures)}**
                """)
            else:
                st.warning("No score data available for this provider")

        # Footer
        st.markdown("---")
        st.caption(
            f"HAILIE TSM Insights Engine v3.0 | Enhanced Analytics with {dataset_type} Dataset | Data: 2024 TSM"
        )
        
        # Close database connection when done
        data_processor.close()

    else:
        # Instructions when no provider is selected
        st.markdown("---")
        st.info("""
        👆 **Getting Started:**
        
        Search for your provider name in the dropdown above.
        Start typing to filter the list and find your provider quickly.
        
        The system will instantly retrieve your pre-calculated analytics.
        """)


if __name__ == "__main__":
    main()