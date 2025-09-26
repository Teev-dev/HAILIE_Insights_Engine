import streamlit as st
import pandas as pd
import numpy as np
from data_processor import TSMDataProcessor
from analytics import TSMAnalytics
from dashboard import ExecutiveDashboard
from styles import apply_css
import traceback
from contextlib import contextmanager

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


def main():
    # Landing page hero section
    render_landing_hero()

    # Key features overview
    render_features_overview()

    # Initialize variables
    show_advanced_logging = False

    # Initialize data processor to get provider options with progress indicator
    with st.spinner("🏠 Loading provider options..."):
        data_processor_for_options = TSMDataProcessor(silent_mode=True)
        provider_options = data_processor_for_options.get_provider_options()

    provider_code = None

    # Sidebar for analysis options and optional file upload
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

        st.markdown("---")

        # Optional custom data upload
        st.header("Custom Data (Optional)")
        st.info(
            "Using default 2024 TSM data. Upload your own file only if you have custom data."
        )
        uploaded_file = st.file_uploader(
            "Upload Custom TSM Data",
            type=['xlsx', 'xls'],
            help=
            "Optional: Upload your own TSM data file to override the default 2024 dataset"
        )

        if uploaded_file is not None:
            st.success(
                "Custom file uploaded - using your data instead of default")

    st.markdown("## Select Your Provider")

    col1, col2 = st.columns([3, 1], gap="large")

    with col1:
        if provider_options:
            # Provider search dropdown with autocomplete
            st.subheader("Search by Provider Name")
            selected_provider = st.selectbox(
                "Select your provider",
                options=["Select a provider..."] +
                list(provider_options.keys()),
                index=0,
                help="Search and select your housing provider from the dropdown"
            )

            if selected_provider != "Select a provider...":
                provider_code = provider_options[selected_provider]
                st.success(f"Selected: {provider_code}")

            st.markdown("**OR**")

        # Fallback text input for provider code
        text_provider_code = st.text_input(
            "Enter Provider Code Directly",
            placeholder="e.g., H1234",
            help=
            "Enter your housing provider's unique identifier if not found above"
        )

        # Use text input if provided, otherwise use dropdown selection
        if text_provider_code:
            provider_code = text_provider_code
            if provider_options:
                st.info("Using manually entered provider code")

    with col2:
        st.markdown("### Quick Help")
        st.markdown("""
        **Need your provider code?**
        - Check with your housing team
        - Look for codes like H1234, H0001
        - Use the search dropdown if unsure
        
        **Can't find your provider?**
        - Try entering the code directly
        - Check if it's in the dropdown list
        """)

    st.markdown("---")

    # Main content area
    if provider_code:
        try:
            # Initialize processors with enhanced progress tracking
            progress_placeholder = st.empty()
            
            with progress_placeholder.container():
                st.info("🔄 Initializing analysis engine...")
            
            data_processor = TSMDataProcessor(silent_mode=not show_advanced_logging)
            analytics = TSMAnalytics()
            dashboard = ExecutiveDashboard()

            # Load data with detailed progress indicators
            with progress_placeholder.container():
                if uploaded_file is not None:
                    st.info("📄 Processing your custom TSM data file...")
                    df = data_processor.load_excel_file(uploaded_file)
                    data_source = "custom uploaded file"
                else:
                    st.info(f"📊 Loading TSM data for provider {provider_code}...")
                    df = data_processor.load_default_data(provider_code)
                    data_source = "default 2024 TSM dataset"

                if df is None or df.empty:
                    st.error(
                        f"Failed to load data from the {data_source}. Please check the file format."
                    )
                    return

                # Clean and validate data
                cleaned_data = data_processor.clean_and_validate(df)

                if cleaned_data is None or cleaned_data.empty:
                    st.error(
                        f"No valid TSM data found in the {data_source}. Please ensure the data contains TP01-TP12 measures."
                    )
                    return

                # Check if provider exists
                if provider_code not in cleaned_data['provider_code'].values:
                    st.error(
                        f"Provider code '{provider_code}' not found in the dataset. Please check the code and try again."
                    )
                    return

            # Generate analytics with detailed progress
            with progress_placeholder.container():
                st.info("🧮 Calculating performance rankings...")
                rankings = analytics.calculate_rankings(
                    cleaned_data, peer_group_filter)

            with progress_placeholder.container():
                st.info("📈 Analyzing 12-month momentum trends...")
                momentum = analytics.calculate_momentum(
                    cleaned_data, provider_code)

            with progress_placeholder.container():
                st.info("🎯 Identifying priority improvement areas...")
                priority = analytics.identify_priority(cleaned_data,
                                                       provider_code)
            
            # Clear progress indicator
            progress_placeholder.empty()

            # Display executive dashboard at the top
            dashboard.render_executive_summary(provider_code, rankings,
                                               momentum, priority,
                                               include_confidence)

            # Additional insights section
            st.markdown("---")
            with st.expander("Detailed Analysis", expanded=False):
                dashboard.render_detailed_analysis(cleaned_data, provider_code,
                                                   analytics)

            # Data quality metrics
            with st.expander("Data Quality Report", expanded=False):
                dashboard.render_data_quality(cleaned_data, data_processor)

        except Exception as e:
            st.error(f"Error processing data: {str(e)}")

            # Show detailed error for debugging only if advanced logging is enabled
            if show_advanced_logging:
                with st.expander("Technical Details", expanded=False):
                    st.code(traceback.format_exc())

    else:
        # Welcome screen - no provider code entered yet

        # Professional How It Works Section
        with st.expander("How It Works - Get Insights in 3 Simple Steps",
                         expanded=True):

            # Workflow steps

            # Step 1
            st.markdown("""
            **1. Select Your Provider**
            
            Choose your housing provider from the dropdown or enter your provider code directly. 
            Our system recognizes all UK housing providers.
            """,
                        unsafe_allow_html=True)

            # Step 2
            st.markdown("""
            **2. Instant Analysis**
            
            Our AI engine processes your TSM data in seconds, calculating rankings, 
            momentum trends, and priority insights automatically.
            """,
                        unsafe_allow_html=True)

            # Step 3
            st.markdown("""
            **3. Executive Dashboard**
            
            Get clear, actionable insights with visual indicators showing your 
            performance position and improvement opportunities.
            """,
                        unsafe_allow_html=True)

            st.markdown("#### What You'll Get")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Your Rank**")
                st.markdown("Quartile position vs peers")
            with col2:
                st.markdown("**Your Momentum**")
                st.markdown("12-month trend direction")
            with col3:
                st.markdown("**Your Priority**")
                st.markdown("Top improvement area")

            st.markdown("""
            **Understanding Your Dashboard:**
            
            **Performance Ranking** - Color-coded quartile system:
            - **Green**: Top performers (1st quartile) - Leading the sector
            - **Yellow**: Above average (2nd quartile) - Strong performance  
            - **Orange**: Below average (3rd quartile) - Room for improvement
            - **Red**: Needs attention (4th quartile) - Priority focus area
            
            **Momentum Tracking** - 12-month performance trajectory:
            - **Improving**: Positive trend - keep up the good work
            - **Stable**: Consistent performance - maintain standards
            - **Declining**: Negative trend - requires attention
            
            **Priority Focus** - Data-driven improvement recommendations:
            - Identifies which satisfaction measure has the strongest correlation with overall performance
            - Focuses your improvement efforts where they'll have maximum impact
            - Based on statistical analysis of TP01-TP12 measures
            """)

        # Additional Information Section
        st.markdown("### About the Data")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Official Government Data**")
            st.markdown(
                "All analysis based on official UK government TSM (Tenant Satisfaction Measures) surveys covering TP01-TP12 satisfaction measures."
            )

        with col2:
            st.markdown("**Secure & Compliant**")
            st.markdown(
                "Your data is processed securely with UK data protection compliance. No sensitive information is stored or shared."
            )

        with col3:
            st.markdown("**Built-In Analysis**")
            st.markdown(
                "Get instant insights from the latest 2024 dataset covering all registered housing providers across England."
            )


if __name__ == "__main__":
    main()
