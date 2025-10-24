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
    /* Global Responsive Variables - Mobile First Approach */
    :root {
        --primary-color: #2E5BBA;
        --primary-dark: #050B1F;
        --secondary-color: #22C55E;
        --warning-color: #F59E0B;
        --danger-color: #EF4444;
        --text-primary: #1E293B;
        --text-secondary: #111827;
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

        /* Mobile-first spacing */
        --spacing-xs: 0.25rem;
        --spacing-sm: 0.5rem;
        --spacing-md: 0.75rem;
        --spacing-lg: 1rem;
        --spacing-xl: 1.25rem;
        --spacing-2xl: 1.5rem;

        /* Responsive breakpoints */
        --breakpoint-sm: 576px;
        --breakpoint-md: 768px;
        --breakpoint-lg: 992px;
        --breakpoint-xl: 1200px;

        /* Touch-friendly sizing */
        --touch-target-min: 44px;
        --button-height-mobile: 48px;
        --button-height-desktop: 40px;
    }

    /* Tablet and up spacing adjustments */
    @media (min-width: 768px) {
        :root {
            --spacing-xs: 0.5rem;
            --spacing-sm: 0.75rem;
            --spacing-md: 1rem;
            --spacing-lg: 1.5rem;
            --spacing-xl: 2rem;
            --spacing-2xl: 3rem;
        }
    }

    /* Base font sizing - mobile first, responsive */
    html {
        font-size: 14px;
        -webkit-text-size-adjust: 100%;
        -ms-text-size-adjust: 100%;
        scroll-behavior: smooth;
    }

    @media (min-width: 576px) {
        html {
            font-size: 15px;
        }
    }

    @media (min-width: 768px) {
        html {
            font-size: 16px;
        }
    }

    /* Enhanced body and container styles */
    body {
        margin: 0;
        padding: 0;
        overflow-x: hidden;
    }

    /* Streamlit container improvements */
    .main .block-container {
        padding-top: var(--spacing-md) !important;
        padding-left: var(--spacing-sm) !important;
        padding-right: var(--spacing-sm) !important;
        max-width: none !important;
    }

    @media (min-width: 768px) {
        .main .block-container {
            padding-top: var(--spacing-xl) !important;
            padding-left: var(--spacing-lg) !important;
            padding-right: var(--spacing-lg) !important;
        }
    }

    @media (min-width: 1200px) {
        .main .block-container {
            max-width: 1200px !important;
            margin: 0 auto !important;
        }
    }

    /* Streamlit sidebar responsive improvements */
    .sidebar .sidebar-content {
        padding: var(--spacing-sm) !important;
        width: 100% !important;
    }

    @media (min-width: 768px) {
        .sidebar .sidebar-content {
            padding: var(--spacing-lg) !important;
        }
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

    /* Mobile-friendly touch targets */
    button, .stButton > button, .stSelectbox > div, .stCheckbox > label {
        min-height: var(--touch-target-min);
        min-width: var(--touch-target-min);
        padding: var(--spacing-sm) var(--spacing-md);
        border-radius: var(--border-radius-md);
        transition: all 0.2s ease;
        touch-action: manipulation;
        -webkit-tap-highlight-color: rgba(0, 0, 0, 0.1);
    }

    @media (min-width: 768px) {
        button, .stButton > button {
            min-height: var(--button-height-desktop);
        }
    }

    /* Enhanced touch targets for mobile interactions */
    .stSelectbox > div > div {
        min-height: var(--touch-target-min) !important;
        font-size: clamp(14px, 3vw, 16px) !important;
    }

    .stTextInput > div > div > input {
        min-height: var(--touch-target-min) !important;
        font-size: clamp(14px, 3vw, 16px) !important;
        padding: var(--spacing-sm) var(--spacing-md) !important;
    }

    .stCheckbox > label > div {
        min-height: var(--touch-target-min) !important;
        min-width: var(--touch-target-min) !important;
    }

    /* Mobile-optimized expander touch target */
    .streamlit-expanderHeader {
        min-height: var(--touch-target-min) !important;
        touch-action: manipulation;
        -webkit-tap-highlight-color: rgba(0, 0, 0, 0.05);
    }

    /* Better mobile scrolling and viewport handling */
    @media (max-width: 768px) {
        body {
            -webkit-overflow-scrolling: touch;
            position: relative;
        }

        /* Prevent horizontal scroll issues */
        .main .block-container {
            overflow-x: hidden !important;
        }

        /* Better mobile spacing for sections */
        section[data-testid="stSidebar"] {
            min-width: 260px !important;
        }
    }

    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        :root {
            --primary-color: #3B82F6;
            --primary-dark: #2563EB;
            --secondary-color: #10B981;
            --warning-color: #F59E0B;
            --danger-color: #EF4444;
            --text-primary: #F1F5F9;
            --text-secondary: #CBD5E1;
            --text-light: #94A3B8;
            --bg-primary: #1E293B;
            --bg-secondary: #0F172A;
            --bg-tertiary: #334155;
            --border-color: #334155;
        }

        body {
            background-color: var(--bg-primary);
            color: var(--text-primary);
        }

        /* Dark mode card adjustments */
        .metric-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
        }

        .feature-card {
            background: var(--bg-secondary);
            border-top-color: var(--primary-color);
        }

        .quartile-top {
            background: var(--bg-secondary) !important;
            border-left: 3px solid var(--secondary-color) !important;
        }

        .quartile-high {
            background: var(--bg-secondary) !important;
            border-left: 3px solid #84CC16 !important;
        }

        .quartile-mid {
            background: var(--bg-secondary) !important;
            border-left: 3px solid var(--warning-color) !important;
        }

        .quartile-low {
            background: var(--bg-secondary) !important;
            border-left: 3px solid var(--danger-color) !important;
        }

        .data-card {
            background: var(--bg-tertiary);
            border-left-color: var(--primary-color);
        }

        .workflow-step {
            background: var(--bg-tertiary);
            border-color: var(--border-color);
        }

        .workflow-step:hover {
            background: var(--bg-secondary);
        }

        .result-item {
            background: var(--bg-secondary);
            border-left-color: var(--primary-color);
        }

        .results-preview {
            background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
            border-color: var(--border-color);
        }

        .cta-section {
            background: linear-gradient(135deg, var(--bg-tertiary), var(--bg-secondary));
            border-color: var(--border-color);
        }

        /* Improve text contrast in dark mode */
        .hero-description,
        .hero-tagline {
            opacity: 0.95;
        }

        .feature-description,
        .workflow-step-description,
        .result-description {
            color: var(--text-secondary);
        }

        /* Dark mode table improvements */
        .stDataFrame {
            background-color: var(--bg-secondary);
        }

        /* Dark mode button improvements */
        button, .stButton > button {
            background-color: var(--primary-color);
            color: white;
        }

        button:hover, .stButton > button:hover {
            background-color: var(--primary-dark);
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
        text-align: center;
    }

    .features-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: var(--spacing-md);
        margin: var(--spacing-lg) 0;
    }

    @media (min-width: 576px) {
        .features-grid {
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: var(--spacing-lg);
        }
    }

    @media (min-width: 992px) {
        .features-grid {
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            margin: var(--spacing-xl) 0;
        }
    }

    .feature-card-link {
        text-decoration: none !important;
        color: inherit;
        display: block;
        cursor: pointer;
    }

    .feature-card-link:hover,
    .feature-card-link:focus,
    .feature-card-link:active,
    .feature-card-link:visited {
        text-decoration: none !important;
        color: inherit;
    }

    .feature-card-link * {
        text-decoration: none !important;
    }

    .feature-card {
        background: #FFFFFF;
        padding: var(--spacing-lg);
        border-radius: var(--border-radius-lg);
        box-shadow: var(--shadow-md);
        border-top: 4px solid var(--primary-color);
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        touch-action: manipulation;
    }

    .feature-card-clickable {
        cursor: pointer;
        user-select: none;
        scroll-margin-top: 20px;
    }

    .feature-card-clickable:active {
        transform: translateY(0px) scale(0.98);
    }

    @media (min-width: 768px) {
        .feature-card {
            padding: var(--spacing-xl);
        }
    }

    @media (hover: hover) {
        .feature-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-xl);
        }

        .feature-card-clickable:hover {
            border-top-color: var(--primary-dark);
        }
    }

    @media (max-width: 768px) {
        .feature-card:hover {
            transform: translateY(-2px);
        }
    }

    .feature-cta {
        margin-top: var(--spacing-md);
        color: var(--primary-color);
        font-weight: 600;
        font-size: clamp(0.85rem, 2vw, 0.95rem);
        opacity: 0.9;
        transition: all 0.2s ease;
    }

    .feature-card-clickable:hover .feature-cta {
        opacity: 1;
        transform: translateX(4px);
    }

    .feature-icon,
    .feature-icon-professional {
        font-size: clamp(2.5rem, 5vw, 3.5rem);
        margin-bottom: var(--spacing-md);
        display: block;
        transition: transform 0.3s ease;
        width: 3.5rem;
        height: 3.5rem;
        margin: 0 auto var(--spacing-md) auto;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        font-size: 1.5rem;
    }

    .feature-card:hover .feature-icon,
    .feature-card:hover .feature-icon-professional {
        transform: scale(1.1);
    }

    /* Professional icon styles for features */
    .rank-icon {
        background: linear-gradient(135deg, #22C55E, #16A34A);
    }
    .rank-icon::before {
        content: "R";
    }

    .momentum-icon {
        background: linear-gradient(135deg, #3B82F6, #1D4ED8);
    }
    .momentum-icon::before {
        content: "M";
    }

    .priority-icon {
        background: linear-gradient(135deg, #EF4444, #DC2626);
    }
    .priority-icon::before {
        content: "P";
    }

    .feature-title {
        font-size: clamp(1.1rem, 3vw, 1.4rem);
        font-weight: 700;
        color: #1E293B;
        margin-bottom: var(--spacing-sm);
        line-height: 1.3;
    }

    .feature-description {
        color: #1E293B;
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
        grid-template-columns: 1fr;
        gap: var(--spacing-lg);
        margin: var(--spacing-lg) 0;
    }

    @media (min-width: 576px) {
        .workflow-steps {
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        }
    }

    @media (min-width: 992px) {
        .workflow-steps {
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: var(--spacing-xl);
            margin: var(--spacing-xl) 0;
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

    .workflow-step-icon,
    .workflow-step-icon-professional {
        font-size: clamp(2rem, 4vw, 2.5rem);
        margin: var(--spacing-md) 0 var(--spacing-sm) 0;
        display: block;
        transition: transform 0.3s ease;
        width: 2.5rem;
        height: 2.5rem;
        margin: var(--spacing-md) auto var(--spacing-sm) auto;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        font-size: 1.2rem;
    }

    .workflow-step:hover .workflow-step-icon,
    .workflow-step:hover .workflow-step-icon-professional {
        transform: scale(1.1);
    }

    /* Professional workflow step icons */
    .building-icon {
        background: linear-gradient(135deg, #64748B, #475569);
    }
    .building-icon::before {
        content: "1";
    }

    .analytics-icon {
        background: linear-gradient(135deg, #F59E0B, #D97706);
    }
    .analytics-icon::before {
        content: "2";
    }

    .dashboard-icon {
        background: linear-gradient(135deg, #8B5CF6, #7C3AED);
    }
    .dashboard-icon::before {
        content: "3";
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
        grid-template-columns: 1fr;
        gap: var(--spacing-sm);
        margin-top: var(--spacing-md);
    }

    @media (min-width: 480px) {
        .results-grid {
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: var(--spacing-md);
        }
    }

    @media (min-width: 768px) {
        .results-grid {
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
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

    .result-icon,
    .result-icon-professional {
        font-size: clamp(1.25rem, 3vw, 1.5rem);
        margin-bottom: var(--spacing-xs);
        width: 1.5rem;
        height: 1.5rem;
        margin: 0 auto var(--spacing-xs) auto;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        font-size: 0.8rem;
    }

    /* Professional result icons */
    .rank-result {
        background: linear-gradient(135deg, #22C55E, #16A34A);
    }
    .rank-result::before {
        content: "R";
    }

    .momentum-result {
        background: linear-gradient(135deg, #3B82F6, #1D4ED8);
    }
    .momentum-result::before {
        content: "↗";
    }

    .priority-result {
        background: linear-gradient(135deg, #EF4444, #DC2626);
    }
    .priority-result::before {
        content: "!";
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

    /* Enhanced data section grid */
    .data-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: var(--spacing-lg);
    }

    @media (min-width: 576px) {
        .data-grid {
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: var(--spacing-xl);
        }
    }

    /* Enhanced existing styles - Clean White Theme */
    .metric-card {
        background: #FFFFFF;
        padding: var(--spacing-md);
        border-radius: var(--border-radius-lg);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
        margin-bottom: var(--spacing-md);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        touch-action: manipulation;
    }

    @media (min-width: 576px) {
        .metric-card {
            padding: var(--spacing-lg);
        }
    }

    @media (min-width: 768px) {
        .metric-card {
            padding: var(--spacing-xl);
        }
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
        border-color: #D1D5DB;
    }

    /* Clean white theme for quartile cards - remove colored backgrounds */
    .quartile-top,
    .quartile-high,
    .quartile-mid,
    .quartile-low {
        background: #FFFFFF !important;
    }


    .metric-value {
        font-size: clamp(2.5rem, 6vw, 3.5rem);
        font-weight: 800;
        margin: 0;
        color: #4B5563;
        line-height: 1;
        letter-spacing: -0.02em;
    }

    .metric-label {
        font-size: clamp(1rem, 2.5vw, 1.2rem);
        color: #4B5563;
        margin: 0;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .quartile-top,
    .quartile-high,
    .quartile-mid,
    .quartile-low {
        background: #FFFFFF !important;
        border-left: 3px solid var(--secondary-color) !important;
    }

    .quartile-high {
        border-left-color: #84CC16 !important;
    }

    .quartile-mid {
        border-left-color: var(--warning-color) !important;
    }

    .quartile-low {
        border-left-color: var(--danger-color) !important;
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
        background: #FFFFFF;
        border-left: 3px solid #EF4444 !important;
    }

    .main-title {
        color: #1E293B;
        font-size: clamp(1.75rem, 4vw, 2.5rem);
        font-weight: 700;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }

    .subtitle {
        color: #64748B;
        font-size: clamp(1rem, 2.5vw, 1.2rem);
        margin-bottom: var(--spacing-xl);
        line-height: 1.4;
    }

    /* Responsive table improvements */
    .stDataFrame {
        overflow-x: auto;
        margin: var(--spacing-md) 0;
        box-shadow: none !important;
        -webkit-box-shadow: none !important;
        -moz-box-shadow: none !important;
        border: 1px solid #E5E7EB;
        filter: none !important;
    }

    .stDataFrame > div {
        box-shadow: none !important;
        -webkit-box-shadow: none !important;
        -moz-box-shadow: none !important;
        border: none !important;
        filter: none !important;
    }

    .stDataFrame table {
        min-width: 100%;
        font-size: clamp(0.8rem, 2vw, 0.9rem);
        box-shadow: none !important;
        -webkit-box-shadow: none !important;
        -moz-box-shadow: none !important;
        border: none !important;
        filter: none !important;
    }

    /* AGGRESSIVE shadow removal for dataframes - targeting all possible elements */
    [data-testid="stDataFrame"],
    [data-testid="stDataFrame"] *,
    [data-testid="stDataFrameResizable"],
    [data-testid="stDataFrameResizable"] *,
    div[data-testid="stDataFrame"],
    div[data-testid="stDataFrame"] *,
    .stDataFrame,
    .stDataFrame *,
    .dataframe,
    .dataframe *,
    [class*="dataframe"],
    [class*="dataframe"] * {
        box-shadow: none !important;
        -webkit-box-shadow: none !important;
        -moz-box-shadow: none !important;
        filter: drop-shadow(0 0 0 transparent) !important;
        text-shadow: none !important;
    }
    
    /* Remove all borders except table cell borders */
    [data-testid="stDataFrame"],
    [data-testid="stDataFrameResizable"],
    div[data-testid="stDataFrame"],
    .stDataFrame {
        border: none !important;
        outline: none !important;
    }
    
    /* Target various iframe and embed elements that might contain dataframes */
    [data-testid="stDataFrame"] iframe,
    [data-testid="stDataFrame"] embed,
    [data-testid="stDataFrame"] object,
    .stDataFrame iframe,
    .stDataFrame embed,
    .stDataFrame object {
        box-shadow: none !important;
        -webkit-box-shadow: none !important;
        -moz-box-shadow: none !important;
        filter: none !important;
        border: none !important;
    }
    
    /* Target any wrapper divs with inline styles */
    div[style*="box-shadow"][data-testid*="DataFrame"],
    div[style*="box-shadow"] [data-testid*="DataFrame"],
    [data-testid="stDataFrame"] div[style*="box-shadow"],
    [data-testid="stDataFrame"] [style*="box-shadow"] {
        box-shadow: none !important;
        -webkit-box-shadow: none !important;
        -moz-box-shadow: none !important;
    }
    
    /* Override any transform shadows */
    [data-testid="stDataFrame"]:before,
    [data-testid="stDataFrame"]:after,
    [data-testid="stDataFrame"] *:before,
    [data-testid="stDataFrame"] *:after {
        box-shadow: none !important;
        -webkit-box-shadow: none !important;
        -moz-box-shadow: none !important;
        content: none !important;
    }
    
    /* Specifically target the table element */
    [data-testid="stDataFrame"] table,
    .stDataFrame table {
        border: none !important;
        border-collapse: collapse !important;
        box-shadow: none !important;
        -webkit-box-shadow: none !important;
    }
    
    /* Style table cells with subtle borders */
    [data-testid="stDataFrame"] th,
    [data-testid="stDataFrame"] td,
    .stDataFrame th,
    .stDataFrame td {
        border: none !important;
        border-bottom: 1px solid #E5E7EB !important;
        box-shadow: none !important;
        -webkit-box-shadow: none !important;
    }
    
    /* Remove any parent container shadows */
    [data-testid="stHorizontalBlock"]:has([data-testid="stDataFrame"]),
    [data-testid="stVerticalBlock"]:has([data-testid="stDataFrame"]),
    [data-testid="column"]:has([data-testid="stDataFrame"]) {
        box-shadow: none !important;
        -webkit-box-shadow: none !important;
        -moz-box-shadow: none !important;
    }
    
    /* Global override for any element with dataframe in its class or id */
    [id*="dataframe"],
    [id*="dataframe"] *,
    [class*="dataframe"],
    [class*="dataframe"] *,
    [data-testid*="dataframe" i],
    [data-testid*="dataframe" i] * {
        box-shadow: 0 0 0 transparent !important;
        -webkit-box-shadow: 0 0 0 transparent !important;
        -moz-box-shadow: 0 0 0 transparent !important;
        filter: none !important;
        -webkit-filter: none !important;
    }
    
    /* Nuclear option: override ALL box shadows in dataframe contexts with maximum specificity */
    html body [data-testid="stDataFrame"],
    html body [data-testid="stDataFrame"] * {
        box-shadow: 0 0 0 0 transparent !important;
        -webkit-box-shadow: 0 0 0 0 transparent !important;
        -moz-box-shadow: 0 0 0 0 transparent !important;
        outline: none !important;
        border-image: none !important;
    }
    
    /* Remove ALL shadows from Streamlit tabs and tab panels */
    [data-testid="stTabs"],
    [data-testid="stTabs"] *,
    [data-testid="stTabContent"],
    [data-testid="stTabContent"] *,
    .stTabs,
    .stTabs *,
    div[role="tabpanel"],
    div[role="tabpanel"] *,
    div[role="tablist"],
    div[role="tablist"] * {
        box-shadow: none !important;
        -webkit-box-shadow: none !important;
        -moz-box-shadow: none !important;
        filter: none !important;
        border: none !important;
        outline: none !important;
    }
    
    /* Remove shadows from expanders */
    [data-testid="stExpander"],
    [data-testid="stExpander"] *,
    .streamlit-expanderHeader,
    .streamlit-expanderHeader *,
    .streamlit-expanderContent,
    .streamlit-expanderContent * {
        box-shadow: none !important;
        -webkit-box-shadow: none !important;
        -moz-box-shadow: none !important;
        filter: none !important;
    }
    
    /* Remove shadows from all Streamlit containers */
    [class*="st"],
    [data-testid*="st"] {
        box-shadow: none !important;
        -webkit-box-shadow: none !important;
        -moz-box-shadow: none !important;
    }

    @media (max-width: 768px) {
        .stDataFrame {
            border-radius: var(--border-radius-md);
            box-shadow: none;
        }

        .stDataFrame table {
            font-size: 0.75rem;
        }

        .stDataFrame th,
        .stDataFrame td {
            padding: var(--spacing-xs) var(--spacing-sm) !important;
            white-space: nowrap;
        }
    }

    /* Mobile-optimized expander */
    .streamlit-expanderHeader {
        padding: var(--spacing-md) !important;
        font-size: clamp(0.9rem, 2.5vw, 1rem) !important;
        min-height: var(--touch-target-min) !important;
    }

    /* Mobile charts and plots */
    .js-plotly-plot {
        width: 100% !important;
        height: auto !important;
    }

    @media (max-width: 768px) {
        .js-plotly-plot {
            margin: var(--spacing-sm) 0 !important;
        }

        .js-plotly-plot .plotly {
            height: 300px !important;
        }
    }

    /* Responsive utility classes */
    .mobile-center {
        text-align: center;
    }

    @media (min-width: 768px) {
        .mobile-center {
            text-align: left;
        }
    }

    .mobile-stack {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-sm);
    }

    @media (min-width: 768px) {
        .mobile-stack {
            flex-direction: row;
            align-items: center;
            gap: var(--spacing-lg);
        }
    }

    /* Enhanced mobile scrolling */
    .horizontal-scroll {
        overflow-x: auto;
        overflow-y: hidden;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: thin;
        scrollbar-color: var(--border-color) transparent;
    }

    .horizontal-scroll::-webkit-scrollbar {
        height: 4px;
    }

    .horizontal-scroll::-webkit-scrollbar-track {
        background: transparent;
    }

    .horizontal-scroll::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 2px;
    }

    /* Data card styling for the About section */
    .data-card {
        background: var(--bg-secondary);
        padding: var(--spacing-lg);
        border-radius: var(--border-radius-md);
        border-left: 4px solid var(--primary-color);
        transition: all 0.3s ease;
        touch-action: manipulation;
    }

    @media (min-width: 768px) {
        .data-card {
            padding: var(--spacing-xl);
        }
    }

    .data-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    .data-card.secure {
        border-left-color: var(--secondary-color);
    }

    .data-card.realtime {
        border-left-color: var(--warning-color);
    }

    .data-card-title {
        color: var(--text-primary);
        font-size: clamp(1rem, 2.5vw, 1.2rem);
        font-weight: 700;
        margin-bottom: var(--spacing-sm);
        line-height: 1.3;
    }

    .data-card-text {
        color: var(--text-secondary);
        font-size: clamp(0.9rem, 2vw, 0.95rem);
        margin: 0;
        line-height: 1.6;
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