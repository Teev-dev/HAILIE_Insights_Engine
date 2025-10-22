import streamlit as st
import pandas as pd
import numpy as np
from data_processor_refactored import TSMDataProcessor
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
    """Check if the analytics database exists"""
    db_path = "attached_assets/hailie_analytics.duckdb"
    return os.path.exists(db_path)


def main():
    # Landing page hero section
    render_landing_hero()

    # Key features overview
    render_features_overview()

    # Check if database exists
    if not check_database_exists():
        st.error("""
        ❌ **Analytics Database Not Found**
        
        The pre-calculated analytics database has not been generated yet.
        Please run the ETL pipeline first:
        
        ```bash
        python build_analytics_db.py
        ```
        
        This will process the TSM data and create the analytics database required for the application.
        """)
        return

    # Initialize variables
    show_advanced_logging = False

    # Initialize data processor to get provider options
    data_processor_for_options = TSMDataProcessor(silent_mode=True)
    provider_options = data_processor_for_options.get_provider_options()

    provider_code = None

    # Sidebar for analysis options
    with st.sidebar:
        # Analysis options
        st.header("Analysis Options")
        include_confidence = st.checkbox("Include confidence intervals",
                                         value=True)
        peer_group_filter = st.selectbox(
            "Peer Group Filter",
            ["All Providers", "Similar Size", "Same Region", "Same Type"],
            help="Filter comparison providers for more relevant benchmarking")

        # Advanced options
        st.markdown("---")
        show_advanced_logging = st.checkbox(
            "Show advanced logging view",
            value=False,
            help="Display detailed processing logs and debugging information")
        
        # Note about the new architecture
        st.markdown("---")
        st.info("""
        📊 **Pre-Calculated Analytics**
        
        This application now uses a pre-calculated analytics database for 
        instant performance. All percentiles and correlations are pre-computed 
        for optimal speed.
        
        Data source: 2024 TSM Dataset
        """)

    st.markdown("## Select Your Provider")

    # Single column layout for provider selection
    if provider_options:
        # Provider search dropdown with autocomplete
        st.subheader("Search by Provider Name")
        selected_provider = st.selectbox(
            "Type or select your provider:",
            options=[""] + provider_options,
            help="Start typing to search for your provider",
            format_func=lambda x: "Select a provider..." if x == "" else x)

        # Extract provider code from selection
        if selected_provider and selected_provider != "":
            # Format is "Provider Name (CODE)"
            if "(" in selected_provider and ")" in selected_provider:
                provider_code = selected_provider.split("(")[-1].replace(")", "")
            else:
                provider_code = None
    else:
        st.error("❌ Unable to load provider list. Please try refreshing the page.")
        provider_code = None

    # Process the selected provider
    if provider_code:
        st.markdown("---")

        # Initialize data processor and analytics with database connection
        data_processor = TSMDataProcessor(silent_mode=not show_advanced_logging)
        analytics = TSMAnalytics(data_processor)

        # Check if provider exists in database
        if not data_processor.get_provider_exists(provider_code):
            st.error(f"❌ Provider '{provider_code}' not found. Please check the code and try again.")
            return

        # Load data (for backward compatibility with dashboard)
        df = data_processor.load_default_data()
        
        if df is None or df.empty:
            st.error("❌ Unable to load provider data. Please try again later.")
            return

        st.success(f"✅ Loaded pre-calculated analytics for provider: {provider_code}")

        # Calculate key metrics using pre-calculated data
        rankings = analytics.calculate_rankings(df, peer_group_filter)
        momentum = analytics.calculate_momentum(df, provider_code)
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
            detailed_analysis = analytics.get_detailed_performance_analysis(
                df, provider_code)
            dashboard.render_performance_analysis(detailed_analysis)

        with tab2:
            # Get pre-calculated correlations
            correlations = data_processor.get_all_correlations()
            dashboard.render_correlation_analysis(correlations, priority)

        with tab3:
            dashboard.render_priority_matrix(priority, detailed_analysis)

        with tab4:
            # Show provider's raw scores
            provider_scores = data_processor.get_provider_scores(provider_code)
            if provider_scores:
                scores_df = pd.DataFrame([provider_scores])
                st.dataframe(scores_df, use_container_width=True)
            else:
                st.info("No raw data available for this provider")

        # Footer
        st.markdown("---")
        st.caption(
            "HAILIE TSM Insights Engine v2.0 | Using Pre-Calculated Analytics Database | Data: 2024 TSM Dataset"
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