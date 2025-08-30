import streamlit as st
import pandas as pd
import numpy as np
from data_processor import TSMDataProcessor
from analytics import TSMAnalytics
from dashboard import ExecutiveDashboard
import traceback
from contextlib import contextmanager

# Page configuration
st.set_page_config(
    page_title="HAILIE Insights Engine",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive styling
st.markdown("""
<style>
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
""", unsafe_allow_html=True)

def main():
    # Title and description
    st.markdown('<h1 class="main-title">🏠 HAILIE Insights Engine</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Executive Dashboard for Social Housing Performance Analysis</p>', unsafe_allow_html=True)
    
    # Sidebar for settings and optional file upload
    with st.sidebar:
        st.header("🏢 Provider Settings")
        
        # Initialize data processor to get provider options
        data_processor = TSMDataProcessor()
        provider_options = data_processor.get_provider_options()
        
        provider_code = None
        
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
        
        # Analysis options
        st.header("⚙️ Analysis Options")
        include_confidence = st.checkbox("Include confidence intervals", value=True)
        peer_group_filter = st.selectbox(
            "Peer Group Filter",
            ["All Providers", "Similar Size", "Same Region", "Same Type"],
            help="Filter comparison providers for more relevant benchmarking"
        )
        
        st.markdown("---")
        
        # Optional custom data upload
        st.header("📊 Custom Data (Optional)")
        st.info("💡 Using default 2024 TSM data. Upload your own file only if you have custom data.")
        uploaded_file = st.file_uploader(
            "Upload Custom TSM Data", 
            type=['xlsx', 'xls'],
            help="Optional: Upload your own TSM data file to override the default 2024 dataset"
        )
        
        if uploaded_file is not None:
            st.success("✅ Custom file uploaded - using your data instead of default")
    
    # Main content area
    if provider_code:
        try:
            # Create a placeholder for the log container that we'll fill at the bottom
            log_messages = []
            
            # Store the original st functions
            original_info = st.info
            original_warning = st.warning
            original_success = st.success
            original_error = st.error
            
            # Override st functions to capture messages
            def wrapped_info(msg):
                log_messages.append(('info', msg))
                    
            def wrapped_warning(msg):
                log_messages.append(('warning', msg))
                    
            def wrapped_success(msg):
                log_messages.append(('success', msg))
                    
            def wrapped_error(msg):
                # Show error in main area immediately
                original_error(msg)
                log_messages.append(('error', msg))
                return
            
            # Temporarily replace st functions
            st.info = wrapped_info
            st.warning = wrapped_warning
            st.success = wrapped_success
            st.error = wrapped_error
            
            try:
                # Initialize processors (data_processor already initialized for provider options)
                with st.spinner("🔄 Processing TSM data..."):
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
                        st.error(f"❌ Failed to load data from the {data_source}. Please check the file format.")
                        return
                    
                    # Clean and validate data
                    cleaned_data = data_processor.clean_and_validate(df)
                    
                    if cleaned_data is None or cleaned_data.empty:
                        st.error(f"❌ No valid TSM data found in the {data_source}. Please ensure the data contains TP01-TP12 measures.")
                        return
                    
                    # Check if provider exists
                    if provider_code not in cleaned_data['provider_code'].values:
                        st.error(f"❌ Provider code '{provider_code}' not found in the dataset. Please check the code and try again.")
                        return
                
                # Generate analytics
                with st.spinner("📈 Calculating performance metrics..."):
                    # Calculate rankings
                    rankings = analytics.calculate_rankings(cleaned_data, peer_group_filter)
                    
                    # Calculate momentum
                    momentum = analytics.calculate_momentum(cleaned_data, provider_code)
                    
                    # Identify priority
                    priority = analytics.identify_priority(cleaned_data, provider_code)
                    
            finally:
                # Restore original st functions
                st.info = original_info
                st.warning = original_warning
                st.success = original_success
                st.error = original_error
            
            # Display executive dashboard at the top
            dashboard.render_executive_summary(
                provider_code, 
                rankings, 
                momentum, 
                priority,
                include_confidence
            )
            
            # Additional insights section
            st.markdown("---")
            with st.expander("📋 Detailed Analysis", expanded=False):
                dashboard.render_detailed_analysis(cleaned_data, provider_code, analytics)
            
            # Data quality metrics
            with st.expander("🔍 Data Quality Report", expanded=False):
                dashboard.render_data_quality(cleaned_data, data_processor)
            
            # Processing details at the bottom
            with st.expander("📋 Processing Details", expanded=False):
                for msg_type, msg in log_messages:
                    if msg_type == 'info':
                        original_info(msg)
                    elif msg_type == 'warning':
                        original_warning(msg)
                    elif msg_type == 'success':
                        original_success(msg)
                    elif msg_type == 'error':
                        original_error(msg)
                
        except Exception as e:
            st.error(f"❌ Error processing data: {str(e)}")
            
            # Show detailed error for debugging
            with st.expander("🔧 Technical Details", expanded=False):
                st.code(traceback.format_exc())
                
    else:
        # Welcome screen - no provider code entered yet
        st.markdown("""
        ### Welcome to HAILIE Insights Engine
        
        This executive dashboard provides key insights from UK government TSM (Tenant Satisfaction Measures) data:
        
        **📊 Your Rank** - See how you compare to similar housing providers with quartile-based scoring
        
        **📈 Your Momentum** - Track your 12-month performance trajectory 
        
        **🎯 Your Priority** - Identify the single most critical area for improvement
        
        ---
        
        **To get started:**
        1. Enter your provider code in the sidebar (e.g., H1234)
        2. View your executive dashboard with key performance insights
        3. Optionally upload custom TSM data if needed
        
        ---
        
        **📊 Data Ready to Use:**
        - Default 2024 TSM dataset already loaded
        - UK government TSM datasets with TP01-TP12 satisfaction measures
        - All housing providers across England included
        
        👆 **Simply enter your provider code in the sidebar to begin!**
        """)

if __name__ == "__main__":
    main()
