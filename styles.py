"""
CSS Styles Module for HAILIE TSM Insights Engine
Contains all custom CSS styling for the Streamlit application
"""

def get_main_css():
    """
    Returns the main CSS stylesheet for the application
    """
    return """
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
"""

def apply_css(st):
    """
    Apply the main CSS styles to a Streamlit app
    
    Args:
        st: Streamlit module
    """
    st.markdown(get_main_css(), unsafe_allow_html=True)