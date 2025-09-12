import streamlit as st
import pandas as pd
import numpy as np
from data_processor import TSMDataProcessor
from analytics import TSMAnalytics
from dashboard import ExecutiveDashboard
import traceback
from contextlib import contextmanager

# Page configuration
st.set_page_config(page_title="HAILIE TSM Insights Engine",
                   page_icon="🏠",
                   layout="wide",
                   initial_sidebar_state="expanded")

# Custom CSS for executive styling and landing page
st.markdown("""
<style>
    /* Landing Page Styles */
    .hero-section {
        background: linear-gradient(135deg, #2E5BBA 0%, #1E40AF 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .hero-tagline {
        font-size: 1.4rem;
        margin-bottom: 1.5rem;
        opacity: 0.95;
        font-weight: 400;
    }
    
    .hero-description {
        font-size: 1.1rem;
        margin-bottom: 0;
        opacity: 0.9;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-top: 4px solid #2E5BBA;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.75rem;
    }
    
    .feature-description {
        color: #64748B;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .cta-section {
        background: #F8FAFC;
        padding: 2rem;
        border-radius: 12px;
        border: 2px solid #E2E8F0;
        margin: 2rem 0;
        text-align: center;
    }
    
    .cta-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 1rem;
    }
    
    .trust-indicators {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin: 1rem 0;
    }
    
    .trust-badge {
        display: inline-block;
        background: #EEF2FF;
        color: #2E5BBA;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    /* How It Works Section */
    .workflow-container {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .workflow-steps {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .workflow-step {
        text-align: center;
        padding: 1.5rem;
        background: #F8FAFC;
        border-radius: 8px;
        border: 2px solid #E2E8F0;
        position: relative;
    }
    
    .workflow-step::before {
        content: attr(data-step);
        position: absolute;
        top: -15px;
        left: 50%;
        transform: translateX(-50%);
        background: #2E5BBA;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1rem;
    }
    
    .workflow-step-icon {
        font-size: 2.5rem;
        margin: 1rem 0 0.75rem 0;
        display: block;
    }
    
    .workflow-step-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.5rem;
    }
    
    .workflow-step-description {
        color: #64748B;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .results-preview {
        background: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 100%);
        border: 2px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .results-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .result-item {
        background: white;
        padding: 1rem;
        border-radius: 6px;
        border-left: 3px solid #2E5BBA;
        text-align: center;
    }
    
    .result-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .result-label {
        font-size: 0.9rem;
        font-weight: 600;
        color: #1E293B;
        margin-bottom: 0.25rem;
    }
    
    .result-description {
        font-size: 0.8rem;
        color: #64748B;
    }
    
    /* Enhanced existing styles */
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #2E5BBA;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        color: #1E293B;
    }
    
    .metric-label {
        font-size: 1.1rem;
        color: #64748B;
        margin: 0;
        font-weight: 500;
    }
    
    .quartile-top {
        border-left-color: #22C55E !important;
    }
    
    .quartile-high {
        border-left-color: #84CC16 !important;
    }
    
    .quartile-mid {
        border-left-color: #F59E0B !important;
    }
    
    .quartile-low {
        border-left-color: #EF4444 !important;
    }
    
    .momentum-up {
        color: #22C55E;
    }
    
    .momentum-down {
        color: #EF4444;
    }
    
    .momentum-stable {
        color: #64748B;
    }
    
    .priority-high {
        background: #FEF2F2;
        border-left-color: #EF4444 !important;
    }
    
    .main-title {
        color: #1E293B;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #64748B;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
</style>
""",
            unsafe_allow_html=True)


def render_landing_hero():
    """Render the professional hero section"""
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🏠 HAILIE TSM Insights Engine</h1>
        <p class="hero-tagline">Transform Your Housing Performance Data Into Executive Intelligence</p>
        <p class="hero-description">
            Turn complex UK government TSM data into clear, actionable insights. 
            Get your performance ranking, track momentum, and identify priority improvement areas 
            with executive-level clarity.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_features_overview():
    """Render the key features overview section"""
    st.markdown("""
    <div class="features-grid">
        <div class="feature-card">
            <span class="feature-icon">🏆</span>
            <h3 class="feature-title">Your Rank</h3>
            <p class="feature-description">
                See exactly how your housing provider compares to peers with quartile-based scoring. 
                Get clear visual indicators showing your competitive position.
            </p>
        </div>
        
        <div class="feature-card">
            <span class="feature-icon">📈</span>
            <h3 class="feature-title">Your Momentum</h3>
            <p class="feature-description">
                Track your 12-month performance trajectory. Understand if you're improving, 
                stable, or declining across key satisfaction measures.
            </p>
        </div>
        
        <div class="feature-card">
            <span class="feature-icon">🎯</span>
            <h3 class="feature-title">Your Priority</h3>
            <p class="feature-description">
                Identify the single most critical area for improvement based on data-driven 
                correlation analysis with overall tenant satisfaction.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_trust_indicators():
    """Render trust and credibility indicators"""
    st.markdown("""
    <div class="trust-indicators">
        <span class="trust-badge">✅ UK Government TSM Data</span>
        <span class="trust-badge">🔒 Secure & Compliant</span>
        <span class="trust-badge">📊 TP01-TP12 Measures</span>
        <span class="trust-badge">🏛️ All England Providers</span>
        <span class="trust-badge">⚡ Instant Analysis</span>
        <span class="trust-badge">📈 Real-Time Insights</span>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Landing page hero section
    render_landing_hero()
    
    # Key features overview
    render_features_overview()
    
    # Trust indicators
    render_trust_indicators()

    # Initialize variables
    show_advanced_logging = False

    # Initialize data processor to get provider options
    data_processor_for_options = TSMDataProcessor(silent_mode=True)
    provider_options = data_processor_for_options.get_provider_options()
    
    provider_code = None

    # Sidebar for analysis options and optional file upload
    with st.sidebar:

        # Analysis options
        st.header("⚙️ Analysis Options")
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
        st.header("📊 Custom Data (Optional)")
        st.info(
            "💡 Using default 2024 TSM data. Upload your own file only if you have custom data."
        )
        uploaded_file = st.file_uploader(
            "Upload Custom TSM Data",
            type=['xlsx', 'xls'],
            help=
            "Optional: Upload your own TSM data file to override the default 2024 dataset"
        )

        if uploaded_file is not None:
            st.success(
                "✅ Custom file uploaded - using your data instead of default")

    # Call-to-action section for provider selection
    st.markdown("""
    <div class="cta-section">
        <h2 class="cta-title">🚀 Get Your Performance Insights Now</h2>
        <p>Choose your housing provider below to view your executive dashboard with key performance insights.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## 🏢 Select Your Provider")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if provider_options:
            # Provider search dropdown with autocomplete
            st.subheader("🔍 Search by Provider Name")
            selected_provider = st.selectbox(
                "Select your provider",
                options=["Select a provider..."] + list(provider_options.keys()),
                index=0,
                help="Search and select your housing provider from the dropdown"
            )
            
            if selected_provider != "Select a provider...":
                provider_code = provider_options[selected_provider]
                st.success(f"✅ Selected: {provider_code}")
            
            st.markdown("**OR**")
        
        # Fallback text input for provider code
        text_provider_code = st.text_input(
            "Enter Provider Code Directly",
            placeholder="e.g., H1234",
            help="Enter your housing provider's unique identifier if not found above"
        )
        
        # Use text input if provided, otherwise use dropdown selection
        if text_provider_code:
            provider_code = text_provider_code
            if provider_options:
                st.info("💡 Using manually entered provider code")
    
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
            # Initialize processors with silent mode based on checkbox
            with st.spinner("🔄 Processing TSM data..."):
                data_processor = TSMDataProcessor(
                    silent_mode=not show_advanced_logging)
                analytics = TSMAnalytics()
                dashboard = ExecutiveDashboard()

                # Load data - either uploaded file or default
                if uploaded_file is not None:
                    # Process the uploaded file
                    df = data_processor.load_excel_file(uploaded_file)
                    data_source = "custom uploaded file"
                else:
                    # Load default data with provider-specific sheet selection
                    df = data_processor.load_default_data(provider_code)
                    data_source = "default 2024 TSM dataset"

                if df is None or df.empty:
                    st.error(
                        f"❌ Failed to load data from the {data_source}. Please check the file format."
                    )
                    return

                # Clean and validate data
                cleaned_data = data_processor.clean_and_validate(df)

                if cleaned_data is None or cleaned_data.empty:
                    st.error(
                        f"❌ No valid TSM data found in the {data_source}. Please ensure the data contains TP01-TP12 measures."
                    )
                    return

                # Check if provider exists
                if provider_code not in cleaned_data['provider_code'].values:
                    st.error(
                        f"❌ Provider code '{provider_code}' not found in the dataset. Please check the code and try again."
                    )
                    return

            # Generate analytics
            with st.spinner("📈 Calculating performance metrics..."):
                # Calculate rankings
                rankings = analytics.calculate_rankings(
                    cleaned_data, peer_group_filter)

                # Calculate momentum
                momentum = analytics.calculate_momentum(
                    cleaned_data, provider_code)

                # Identify priority
                priority = analytics.identify_priority(cleaned_data,
                                                       provider_code)

            # Display executive dashboard at the top
            dashboard.render_executive_summary(provider_code, rankings,
                                               momentum, priority,
                                               include_confidence)

            # Additional insights section
            st.markdown("---")
            with st.expander("📋 Detailed Analysis", expanded=False):
                dashboard.render_detailed_analysis(cleaned_data, provider_code,
                                                   analytics)

            # Data quality metrics
            with st.expander("🔍 Data Quality Report", expanded=False):
                dashboard.render_data_quality(cleaned_data, data_processor)

        except Exception as e:
            st.error(f"❌ Error processing data: {str(e)}")

            # Show detailed error for debugging only if advanced logging is enabled
            if show_advanced_logging:
                with st.expander("🔧 Technical Details", expanded=False):
                    st.code(traceback.format_exc())

    else:
        # Welcome screen - no provider code entered yet

        # Professional How It Works Section
        with st.expander("📋 How It Works - Get Insights in 3 Simple Steps",
                         expanded=True):
            st.markdown("""
            <div class="workflow-container">
                <div class="workflow-steps">
                    <div class="workflow-step" data-step="1">
                        <span class="workflow-step-icon">🏢</span>
                        <h4 class="workflow-step-title">Select Your Provider</h4>
                        <p class="workflow-step-description">
                            Choose your housing provider from the dropdown or enter your provider code directly. 
                            Our system recognizes all UK housing providers.
                        </p>
                    </div>
                    
                    <div class="workflow-step" data-step="2">
                        <span class="workflow-step-icon">⚡</span>
                        <h4 class="workflow-step-title">Instant Analysis</h4>
                        <p class="workflow-step-description">
                            Our AI engine processes your TSM data in seconds, calculating rankings, 
                            momentum trends, and priority insights automatically.
                        </p>
                    </div>
                    
                    <div class="workflow-step" data-step="3">
                        <span class="workflow-step-icon">📊</span>
                        <h4 class="workflow-step-title">Executive Dashboard</h4>
                        <p class="workflow-step-description">
                            Get clear, actionable insights with visual indicators showing your 
                            performance position and improvement opportunities.
                        </p>
                    </div>
                </div>
                
                <div class="results-preview">
                    <h4 style="text-align: center; margin-bottom: 1rem; color: #1E293B;">What You'll Get</h4>
                    <div class="results-grid">
                        <div class="result-item">
                            <div class="result-icon">🏆</div>
                            <div class="result-label">Your Rank</div>
                            <div class="result-description">Quartile position vs peers</div>
                        </div>
                        <div class="result-item">
                            <div class="result-icon">📈</div>
                            <div class="result-label">Your Momentum</div>
                            <div class="result-description">12-month trend direction</div>
                        </div>
                        <div class="result-item">
                            <div class="result-icon">🎯</div>
                            <div class="result-label">Your Priority</div>
                            <div class="result-description">Top improvement area</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            **💡 Understanding Your Dashboard:**
            
            **🏆 Performance Ranking** - Color-coded quartile system:
            - **🟢 Green**: Top performers (1st quartile) - Leading the sector
            - **🟡 Yellow**: Above average (2nd quartile) - Strong performance  
            - **🟠 Orange**: Below average (3rd quartile) - Room for improvement
            - **🔴 Red**: Needs attention (4th quartile) - Priority focus area
            
            **📈 Momentum Tracking** - 12-month performance trajectory:
            - **↗️ Improving**: Positive trend - keep up the good work
            - **→ Stable**: Consistent performance - maintain standards
            - **↘️ Declining**: Negative trend - requires attention
            
            **🎯 Priority Focus** - Data-driven improvement recommendations:
            - Identifies which satisfaction measure has the strongest correlation with overall performance
            - Focuses your improvement efforts where they'll have maximum impact
            - Based on statistical analysis of TP01-TP12 measures
            """)

        # Additional Information Section
        st.markdown("""
        <div class="workflow-container">
            <h3 style="color: #1E293B; margin-bottom: 1rem;">📊 About Your Data</h3>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
                <div style="background: #F8FAFC; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2E5BBA;">
                    <h4 style="color: #1E293B; margin-bottom: 0.5rem;">🏛️ Official Government Data</h4>
                    <p style="color: #64748B; margin: 0; font-size: 0.95rem;">
                        All analysis based on official UK government TSM (Tenant Satisfaction Measures) 
                        surveys covering TP01-TP12 satisfaction measures.
                    </p>
                </div>
                
                <div style="background: #F8FAFC; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #22C55E;">
                    <h4 style="color: #1E293B; margin-bottom: 0.5rem;">🔒 Secure & Compliant</h4>
                    <p style="color: #64748B; margin: 0; font-size: 0.95rem;">
                        Your data is processed securely with UK data protection compliance. 
                        No sensitive information is stored or shared.
                    </p>
                </div>
                
                <div style="background: #F8FAFC; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #F59E0B;">
                    <h4 style="color: #1E293B; margin-bottom: 0.5rem;">📈 Real-Time Analysis</h4>
                    <p style="color: #64748B; margin: 0; font-size: 0.95rem;">
                        Get instant insights from the latest 2024 dataset covering all 
                        registered housing providers across England.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
