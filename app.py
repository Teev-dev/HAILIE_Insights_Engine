import streamlit as st
import pandas as pd
import numpy as np
from data_processor import TSMDataProcessor
from analytics import TSMAnalytics
from dashboard import ExecutiveDashboard
import traceback

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
    
    # Sidebar for file upload and settings
    with st.sidebar:
        st.header("📊 Data Upload")
        uploaded_file = st.file_uploader(
            "Upload TSM Data (Excel file)", 
            type=['xlsx', 'xls'],
            help="Upload your UK government TSM data file containing TP01-TP12 satisfaction measures"
        )
        
        if uploaded_file is not None:
            st.success("✅ File uploaded successfully")
            
            # Provider selection
            st.header("🏢 Provider Settings")
            provider_code = st.text_input(
                "Your Provider Code", 
                placeholder="e.g., H1234",
                help="Enter your housing provider's unique identifier"
            )
            
            # Analysis options
            st.header("⚙️ Analysis Options")
            include_confidence = st.checkbox("Include confidence intervals", value=True)
            peer_group_filter = st.selectbox(
                "Peer Group Filter",
                ["All Providers", "Similar Size", "Same Region", "Same Type"],
                help="Filter comparison providers for more relevant benchmarking"
            )
    
    # Main content area
    if uploaded_file is not None and provider_code:
        try:
            # Initialize processors
            with st.spinner("🔄 Processing TSM data..."):
                data_processor = TSMDataProcessor()
                analytics = TSMAnalytics()
                dashboard = ExecutiveDashboard()
                
                # Process the uploaded file
                df = data_processor.load_excel_file(uploaded_file)
                
                if df is None or df.empty:
                    st.error("❌ Failed to load data from the uploaded file. Please check the file format.")
                    return
                
                # Clean and validate data
                cleaned_data = data_processor.clean_and_validate(df)
                
                if cleaned_data is None or cleaned_data.empty:
                    st.error("❌ No valid TSM data found in the uploaded file. Please ensure the file contains TP01-TP12 measures.")
                    return
                
                # Check if provider exists
                if provider_code not in cleaned_data.get('provider_code', []):
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
            
            # Display executive dashboard
            st.markdown("---")
            dashboard.render_executive_summary(
                provider_code, 
                rankings, 
                momentum, 
                priority,
                include_confidence
            )
            
            # Additional insights section
            with st.expander("📋 Detailed Analysis", expanded=False):
                dashboard.render_detailed_analysis(cleaned_data, provider_code, analytics)
            
            # Data quality metrics
            with st.expander("🔍 Data Quality Report", expanded=False):
                dashboard.render_data_quality(cleaned_data, data_processor)
                
        except Exception as e:
            st.error(f"❌ Error processing data: {str(e)}")
            
            # Show detailed error for debugging
            with st.expander("🔧 Technical Details", expanded=False):
                st.code(traceback.format_exc())
                
    elif uploaded_file is not None:
        st.info("👆 Please enter your provider code in the sidebar to continue")
        
    else:
        # Welcome screen
        st.markdown("""
        ### Welcome to HAILIE Insights Engine
        
        This executive dashboard provides key insights from UK government TSM (Tenant Satisfaction Measures) data:
        
        **📊 Your Rank** - See how you compare to similar housing providers with quartile-based scoring
        
        **📈 Your Momentum** - Track your 12-month performance trajectory 
        
        **🎯 Your Priority** - Identify the single most critical area for improvement
        
        ---
        
        **To get started:**
        1. Upload your TSM Excel data file using the sidebar
        2. Enter your provider code
        3. View your executive dashboard with key performance insights
        
        ---
        
        **Supported Data Format:**
        - UK government TSM datasets (Excel format)
        - TP01-TP12 satisfaction measure codes
        - Multi-sheet workbooks with provider data
        """)

if __name__ == "__main__":
    main()
