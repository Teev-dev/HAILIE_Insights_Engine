import streamlit as st
import pandas as pd
import numpy as np
from data_processor_enhanced import EnhancedTSMDataProcessor
from analytics_refactored import TSMAnalytics
from dashboard import ExecutiveDashboard
from styles import apply_css
from mobile_utils import detect_mobile, mobile_friendly_columns, render_mobile_info, should_show_component
import traceback
from contextlib import contextmanager
import os

# Page configuration - MUST be first Streamlit command
# Using 'wide' layout for all devices, content adapts responsively
st.set_page_config(
    page_title="HAILIE TSM Insights Engine",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS styles from styles module
apply_css(st)


def render_landing_hero():
    """Render the professional hero section"""
    is_mobile = detect_mobile()
    
    if is_mobile:
        # Mobile version - styled gradient header
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #2E5BBA 0%, #050B1F 100%);
            color: white;
            padding: 1.5rem 1rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <h1 style="
                font-size: 1.75rem;
                font-weight: 800;
                margin-bottom: 0.5rem;
                line-height: 1.2;
                color: white;
            ">TSM Insights by HAILIE</h1>
            <p style="
                font-size: 1rem;
                margin: 0;
                opacity: 0.95;
                color: white;
                line-height: 1.4;
            ">Transform Your TSM Performance Into Executive Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Desktop version - use custom HTML
        st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">TSM Insights by HAILIE</h1>
            <p class="hero-tagline">Transform Your TSM Performance Into Executive Intelligence</p>
        </div>
        """,
                    unsafe_allow_html=True)


def render_features_overview():
    """Render the key features overview section"""
    is_mobile = detect_mobile()
    
    if is_mobile:
        # Mobile version - use native Streamlit components in single column
        st.markdown("### Key Insights We Provide")
        
        with st.container():
            st.markdown("**📊 Your Rank**")
            st.markdown("See exactly how your housing provider compares to peers with quartile-based scoring.")
            
            st.markdown("**📈 Your Momentum**")
            st.markdown("Track your 12-month performance trajectory across key satisfaction measures.")
            
            st.markdown("**🎯 Your Priority**")
            st.markdown("Identify the single most critical area for improvement based on data-driven analysis.")
    else:
        # Desktop version - use custom HTML grid
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
    """Check if the enhanced analytics database exists and is accessible"""
    db_path = "attached_assets/hailie_analytics_v2.duckdb"

    # Check if file exists
    if not os.path.exists(db_path):
        return False

    # Check if file is readable
    if not os.access(db_path, os.R_OK):
        st.error(f"❌ Database file exists but is not readable: {db_path}")
        return False

    # Check if it's a valid DuckDB file (basic check)
    try:
        import duckdb
        conn = duckdb.connect(db_path, read_only=True)
        conn.execute("SELECT 1").fetchone()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Database file exists but appears corrupted: {str(e)}")
        return False


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
    try:
        data_processor_for_options = EnhancedTSMDataProcessor(silent_mode=True)
        provider_options = data_processor_for_options.get_provider_options()
    except ConnectionError as e:
        st.error(f"""
        ❌ **Database Connection Failed**

        Unable to connect to the analytics database: {str(e)}

        Please ensure the database file exists at:
        `attached_assets/hailie_analytics_v2.duckdb`

        If the database is missing, run:
        ```bash
        python build_analytics_db_v2.py
        ```
        """)
        return
    except Exception as e:
        st.error(f"❌ Unexpected error initializing data processor: {str(e)}")
        return

    provider_code = None
    selected_dataset_type = None

    # Sidebar for analysis options
    with st.sidebar:
        # Device view toggle
        st.header("View Settings")
        force_mobile = st.checkbox(
            "📱 Use Mobile View",
            value=detect_mobile(),
            help="Toggle mobile-optimized layout"
        )
        
        # Override detection if manually toggled
        if force_mobile:
            st.session_state.force_mobile_view = True
        else:
            st.session_state.force_mobile_view = False
        
        st.markdown("---")
        
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

        Data source: 2025 TSM Dataset
        """)

    st.markdown('<div id="provider-search-section"></div>', unsafe_allow_html=True)
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
        try:
            data_processor = EnhancedTSMDataProcessor(silent_mode=not show_advanced_logging)
        except ConnectionError as e:
            st.error(f"""
            ❌ **Database Connection Failed**

            Unable to connect to the analytics database: {str(e)}

            The database file may be corrupted or inaccessible.
            """)
            return
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            return

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

        # Check if mobile
        is_mobile = detect_mobile()
        
        # Show mobile info message if applicable
        if is_mobile:
            st.markdown("---")
            render_mobile_info()
        
        # Detailed Analysis Sections - Only on desktop
        if not is_mobile:
            st.markdown("---")
            st.markdown("## Detailed Analysis")
            
            with st.expander("📊 Performance Analysis", expanded=True):
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

                # Debug logging
                if show_advanced_logging:
                    st.write("Debug - detailed_analysis type:", type(detailed_analysis))
                    st.write("Debug - detailed_analysis value:", detailed_analysis)
                    st.write("Debug - detailed_analysis keys:", list(detailed_analysis.keys()) if detailed_analysis and isinstance(detailed_analysis, dict) else "None or not a dict")
                    st.write("Debug - dataset_type:", dataset_type)

                # Filter out N/A metrics for LCHO
                if dataset_type == 'LCHO' and detailed_analysis and "error" not in detailed_analysis:
                    original_count = len(detailed_analysis)
                    detailed_analysis = {
                        k: v for k, v in detailed_analysis.items() 
                        if k not in ['TP02', 'TP03', 'TP04']
                    }
                    if show_advanced_logging:
                        st.write(f"Debug - Filtered {original_count} measures down to {len(detailed_analysis)} for LCHO")

                # Check if we have any measures to display
                if not detailed_analysis:
                    st.warning("No performance data available to display")
                elif "error" in detailed_analysis:
                    st.error(f"Error loading performance data: {detailed_analysis['error']}")
                else:
                    dashboard.render_performance_analysis(detailed_analysis)

            with st.expander("📈 Measure Correlations", expanded=False):
                st.markdown(f"### Correlation Analysis - {dataset_type} Dataset")

                # Get dataset-specific correlations
                correlations = data_processor.get_dataset_correlations(dataset_type)

                if dataset_type == 'LCHO':
                    st.info("Correlations calculated using LCHO providers only (excluding repairs metrics)")
                else:
                    st.info("Correlations calculated using LCRA providers with all metrics")

                dashboard.render_correlation_analysis(correlations, priority)

            with st.expander("🎯 Priority Matrix", expanded=False):
                st.markdown(f"### Priority Matrix - {dataset_type} Context")

                # Filter priority matrix for LCHO if needed
                if dataset_type == 'LCHO' and priority:
                    # Ensure repairs metrics aren't in the priority recommendations
                    if 'measure' in priority and priority['measure'] in ['TP02', 'TP03', 'TP04']:
                        st.warning("Priority calculation adjusted for LCHO dataset")

                dashboard.render_priority_matrix(priority, detailed_analysis)

            with st.expander("📋 Raw Data", expanded=False):
                st.markdown(f"### Raw Data - {dataset_type} Provider")

                # Show provider's raw scores - FILTERED BY DATASET TYPE
                scores_df = data_processor.get_provider_scores(provider_code)
                
                # Filter to only show the selected dataset type to avoid confusion
                if not scores_df.empty and 'dataset_type' in scores_df.columns:
                    scores_df = scores_df[scores_df['dataset_type'] == dataset_type]
                
                if not scores_df.empty:
                    # Ensure scores_df is a DataFrame, not an array
                    if isinstance(scores_df, pd.DataFrame):
                        # Add descriptions
                        scores_df['description'] = scores_df['tp_measure'].apply(lambda x: data_processor.tp_descriptions.get(x, 'Unknown measure'))

                        # Filter out non-applicable measures based on dataset type
                        if dataset_type == 'LCHO':
                            # Remove repairs metrics (TP02-TP04) for LCHO providers
                            na_metrics = ['TP02', 'TP03', 'TP04']
                            scores_df = scores_df[~scores_df['tp_measure'].isin(na_metrics)]

                            st.info("ℹ️ **Note**: Repairs metrics (TP02-TP04) are not applicable to LCHO providers and are excluded from this view.")

                        # Format for display
                        display_df = scores_df[['tp_measure', 'description', 'score']].copy()
                        display_df.columns = ['Measure', 'Description', 'Score (%)']

                        # Format scores with 1 decimal place
                        display_df['Score (%)'] = display_df['Score (%)'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A")
                        st.table(display_df)
                    else:
                        st.warning("Data format issue - unable to display scores")
                        display_df = pd.DataFrame()  # Empty dataframe for the peer comparison info

                    # Show peer comparison info
                    st.markdown(f"""
                    **Dataset Information:**
                    - Dataset Type: **{dataset_type}**
                    - Peer Group Size: **{peer_count} providers**
                    - Applicable Measures: **{len(applicable_measures)}**
                    - Measures Displayed: **{len(display_df)}**
                    """)
                else:
                    st.warning("No score data available for this provider")

        # Footer
        st.markdown("---")
        st.caption(
            f"HAILIE TSM Insights Engine v3.0 | Enhanced Analytics with {dataset_type} Dataset | Data: 2025 TSM"
        )
        st.markdown(
            '<p style="text-align: center; font-size: 0.85em; color: #666;">'
            '🔒 <a href="/privacy_policy" target="_self">Privacy Policy</a>'
            '</p>',
            unsafe_allow_html=True
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
        
        # Footer with privacy link
        st.markdown("---")
        st.caption("HAILIE TSM Insights Engine v3.0 | Data: 2025 TSM")
        st.markdown(
            '<p style="text-align: center; font-size: 0.85em; color: #666;">'
            '🔒 <a href="/privacy_policy" target="_self">Privacy Policy</a>'
            '</p>',
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()