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
    /* Global Responsive Variables */
    :root {
        --primary-color: #2E5BBA;
        --primary-dark: #1E40AF;
        --secondary-color: #22C55E;
        --warning-color: #F59E0B;
        --danger-color: #EF4444;
        --text-primary: #1E293B;
        --text-secondary: #64748B;
        --text-light: #94A3B8;
        --bg-primary: #FFFFFF;
        --bg-secondary: #F8FAFC;
        --bg-tertiary: #F1F5F9;
        --border-color: #E2E8F0;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        --border-radius-sm: 6px;
        --border-radius-md: 8px;
        --border-radius-lg: 12px;
        --border-radius-xl: 16px;
        --spacing-xs: 0.5rem;
        --spacing-sm: 0.75rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
        --spacing-xl: 2rem;
        --spacing-2xl: 3rem;
    }

    /* Base font sizing - keep consistent baseline */
    html {
        font-size: 16px;
    }
    
    /* Accessibility: Respect user motion preferences */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
    }

    /* Landing Page Styles */
    .hero-section {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
        color: white;
        padding: var(--spacing-2xl) var(--spacing-xl);
        border-radius: var(--border-radius-xl);
        margin-bottom: var(--spacing-xl);
        text-align: center;
        box-shadow: var(--shadow-xl);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 50%);
        pointer-events: none;
    }
    
    @media (max-width: 768px) {
        .hero-section {
            padding: var(--spacing-xl) var(--spacing-lg);
            margin-bottom: var(--spacing-lg);
        }
    }
    
    @media (max-width: 480px) {
        .hero-section {
            padding: var(--spacing-lg) var(--spacing-md);
        }
    }
    
    .hero-title {
        font-size: clamp(2rem, 5vw, 3.5rem);
        font-weight: 800;
        margin-bottom: var(--spacing-md);
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        line-height: 1.1;
        letter-spacing: -0.025em;
    }
    
    .hero-tagline {
        font-size: clamp(1rem, 3vw, 1.5rem);
        margin-bottom: var(--spacing-lg);
        opacity: 0.95;
        font-weight: 400;
        line-height: 1.4;
    }
    
    .hero-description {
        font-size: clamp(0.9rem, 2.5vw, 1.1rem);
        margin-bottom: 0;
        opacity: 0.9;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.6;
    }
    
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--spacing-lg);
        margin: var(--spacing-xl) 0;
    }
    
    @media (max-width: 768px) {
        .features-grid {
            grid-template-columns: 1fr;
            gap: var(--spacing-md);
            margin: var(--spacing-lg) 0;
        }
    }
    
    .feature-card {
        background: var(--bg-primary);
        padding: var(--spacing-xl);
        border-radius: var(--border-radius-lg);
        box-shadow: var(--shadow-md);
        border-top: 4px solid var(--primary-color);
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(46, 91, 186, 0.03), transparent);
        transition: left 0.5s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: var(--shadow-xl);
    }
    
    .feature-card:hover::before {
        left: 100%;
    }
    
    @media (max-width: 768px) {
        .feature-card {
            padding: var(--spacing-lg);
        }
        
        .feature-card:hover {
            transform: translateY(-2px) scale(1.01);
        }
    }
    
    .feature-icon {
        font-size: clamp(2.5rem, 5vw, 3.5rem);
        margin-bottom: var(--spacing-md);
        display: block;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover .feature-icon {
        transform: scale(1.1);
    }
    
    .feature-title {
        font-size: clamp(1.1rem, 3vw, 1.4rem);
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: var(--spacing-sm);
        line-height: 1.3;
    }
    
    .feature-description {
        color: var(--text-secondary);
        font-size: clamp(0.9rem, 2.5vw, 1rem);
        line-height: 1.6;
    }
    
    .cta-section {
        background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
        padding: var(--spacing-xl);
        border-radius: var(--border-radius-lg);
        border: 2px solid var(--border-color);
        margin: var(--spacing-xl) 0;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .cta-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--primary-color));
    }
    
    @media (max-width: 768px) {
        .cta-section {
            padding: var(--spacing-lg);
        }
    }
    
    .cta-title {
        font-size: clamp(1.3rem, 3vw, 1.8rem);
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: var(--spacing-md);
        line-height: 1.3;
    }
    
    .trust-indicators {
        background: var(--bg-primary);
        padding: var(--spacing-lg);
        border-radius: var(--border-radius-md);
        border: 1px solid var(--border-color);
        margin: var(--spacing-md) 0;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }
    
    .trust-indicators:hover {
        box-shadow: var(--shadow-md);
    }
    
    @media (max-width: 768px) {
        .trust-indicators {
            padding: var(--spacing-md);
        }
    }
    
    .trust-badge {
        display: inline-block;
        background: linear-gradient(135deg, #EEF2FF, #F0F7FF);
        color: var(--primary-color);
        padding: var(--spacing-xs) var(--spacing-md);
        border-radius: 20px;
        font-size: clamp(0.8rem, 2vw, 0.9rem);
        font-weight: 600;
        margin: calc(var(--spacing-xs) / 2);
        border: 1px solid rgba(46, 91, 186, 0.2);
        transition: all 0.2s ease;
    }
    
    .trust-badge:hover {
        background: linear-gradient(135deg, #E0E7FF, #EEF2FF);
        transform: translateY(-1px);
        box-shadow: var(--shadow-sm);
    }
    
    @media (max-width: 768px) {
        .trust-badge {
            display: block;
            margin: var(--spacing-xs) 0;
            text-align: center;
        }
    }
    
    /* How It Works Section */
    .workflow-container {
        background: var(--bg-primary);
        border-radius: var(--border-radius-lg);
        padding: var(--spacing-xl);
        margin: var(--spacing-xl) 0;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--border-color);
    }
    
    @media (max-width: 768px) {
        .workflow-container {
            padding: var(--spacing-lg);
            margin: var(--spacing-lg) 0;
        }
    }
    
    .workflow-steps {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: var(--spacing-xl);
        margin: var(--spacing-xl) 0;
    }
    
    @media (max-width: 768px) {
        .workflow-steps {
            grid-template-columns: 1fr;
            gap: var(--spacing-lg);
        }
    }
    
    .workflow-step {
        text-align: center;
        padding: var(--spacing-lg);
        background: var(--bg-secondary);
        border-radius: var(--border-radius-md);
        border: 2px solid var(--border-color);
        position: relative;
        transition: all 0.3s ease;
    }
    
    .workflow-step:hover {
        background: var(--bg-primary);
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    
    .workflow-step::before {
        content: attr(data-step);
        position: absolute;
        top: -15px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
    }
    
    .workflow-step:hover::before {
        transform: translateX(-50%) scale(1.1);
        box-shadow: var(--shadow-lg);
    }
    
    .workflow-step-icon {
        font-size: clamp(2rem, 4vw, 2.5rem);
        margin: var(--spacing-md) 0 var(--spacing-sm) 0;
        display: block;
        transition: transform 0.3s ease;
    }
    
    .workflow-step:hover .workflow-step-icon {
        transform: scale(1.1);
    }
    
    .workflow-step-title {
        font-size: clamp(1rem, 2.5vw, 1.2rem);
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: var(--spacing-xs);
        line-height: 1.3;
    }
    
    .workflow-step-description {
        color: var(--text-secondary);
        font-size: clamp(0.85rem, 2vw, 0.95rem);
        line-height: 1.6;
    }
    
    .results-preview {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, #EEF2FF 100%);
        border: 2px solid var(--border-color);
        border-radius: var(--border-radius-lg);
        padding: var(--spacing-lg);
        margin: var(--spacing-lg) 0;
        position: relative;
        overflow: hidden;
    }
    
    .results-preview::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--primary-color));
    }
    
    .results-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: var(--spacing-md);
        margin-top: var(--spacing-md);
    }
    
    @media (max-width: 768px) {
        .results-grid {
            grid-template-columns: 1fr;
            gap: var(--spacing-sm);
        }
    }
    
    .result-item {
        background: var(--bg-primary);
        padding: var(--spacing-md);
        border-radius: var(--border-radius-sm);
        border-left: 3px solid var(--primary-color);
        text-align: center;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .result-item:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    .result-icon {
        font-size: clamp(1.25rem, 3vw, 1.5rem);
        margin-bottom: var(--spacing-xs);
    }
    
    .result-label {
        font-size: clamp(0.8rem, 2vw, 0.9rem);
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: calc(var(--spacing-xs) / 2);
    }
    
    .result-description {
        font-size: clamp(0.7rem, 1.8vw, 0.8rem);
        color: var(--text-secondary);
    }
    
    /* Enhanced existing styles */
    .metric-card {
        background: var(--bg-primary);
        padding: var(--spacing-xl);
        border-radius: var(--border-radius-lg);
        box-shadow: var(--shadow-md);
        border-left: 6px solid var(--primary-color);
        margin-bottom: var(--spacing-md);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        width: 2px;
        background: linear-gradient(180deg, transparent, var(--primary-color), transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-xl);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    @media (max-width: 768px) {
        .metric-card {
            padding: var(--spacing-lg);
        }
    }
    
    .metric-value {
        font-size: clamp(2.5rem, 6vw, 3.5rem);
        font-weight: 800;
        margin: 0;
        color: var(--text-primary);
        line-height: 1;
        letter-spacing: -0.02em;
    }
    
    .metric-label {
        font-size: clamp(1rem, 2.5vw, 1.2rem);
        color: var(--text-secondary);
        margin: 0;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .quartile-top {
        border-left-color: var(--secondary-color) !important;
        background: linear-gradient(135deg, #F0FDF4, #ECFDF5);
    }
    
    .quartile-high {
        border-left-color: #84CC16 !important;
        background: linear-gradient(135deg, #F7FEE7, #ECFDF5);
    }
    
    .quartile-mid {
        border-left-color: var(--warning-color) !important;
        background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
    }
    
    .quartile-low {
        border-left-color: var(--danger-color) !important;
        background: linear-gradient(135deg, #FEF2F2, #FEE2E2);
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