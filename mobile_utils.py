"""
Mobile detection utilities for the HAILIE TSM Insights Engine
"""

import streamlit as st
from streamlit.components.v1 import html
import re

def detect_mobile():
    """
    Detect if the user is on a mobile device using viewport width detection
    Returns: bool - True if mobile device detected, False otherwise
    
    Note: This is called AFTER st.set_page_config() to avoid conflicts
    """
    
    # Initialize mobile detection in session state
    if 'is_mobile' not in st.session_state:
        st.session_state.is_mobile = False
        st.session_state.mobile_detection_attempted = False
    
    # Check for manual override via query params
    query_params = st.query_params
    if 'mobile' in query_params:
        override_value = query_params['mobile'].lower() == 'true'
        st.session_state.is_mobile = override_value
        return override_value
    
    # Use JavaScript injection to detect viewport width (runs once)
    if not st.session_state.mobile_detection_attempted:
        st.session_state.mobile_detection_attempted = True
        
        # Simple viewport-based detection
        mobile_detect_script = """
        <script>
        (function() {
            const viewportWidth = window.innerWidth || document.documentElement.clientWidth;
            const isMobile = viewportWidth < 769;
            
            // Log for debugging
            console.log('HAILIE Mobile Detection - Viewport:', viewportWidth, 'px, Mobile:', isMobile);
            
            // Store in sessionStorage
            sessionStorage.setItem('hailie_mobile', isMobile ? 'true' : 'false');
        })();
        </script>
        """
        
        # Inject detection script (silent, no visual output)
        html(mobile_detect_script, height=0)
    
    return st.session_state.is_mobile


def get_mobile_config():
    """
    Get configuration settings optimized for mobile devices
    Returns: dict - Configuration settings
    """
    return {
        'layout': 'centered',  # Use centered instead of wide for mobile
        'sidebar_state': 'collapsed',  # Collapse sidebar on mobile
        'show_tables': False,  # Don't show data tables on mobile
        'show_charts': True,  # Show charts but simplified
        'chart_height': 300,  # Smaller chart height for mobile
        'max_columns': 1,  # Single column layout
        'show_expanders': False,  # Hide detailed expanders on mobile
        'touch_target_size': 48,  # Minimum touch target size in pixels
        'font_size_multiplier': 1.1,  # Slightly larger fonts for readability
    }


def get_desktop_config():
    """
    Get configuration settings optimized for desktop devices
    Returns: dict - Configuration settings
    """
    return {
        'layout': 'wide',  # Wide layout for desktop
        'sidebar_state': 'expanded',  # Expanded sidebar on desktop
        'show_tables': True,  # Show all data tables
        'show_charts': True,  # Show all charts
        'chart_height': 500,  # Full chart height
        'max_columns': 3,  # Multi-column layout
        'show_expanders': True,  # Show all detailed expanders
        'touch_target_size': 40,  # Standard target size
        'font_size_multiplier': 1.0,  # Standard font size
    }


def get_device_config():
    """
    Get the appropriate configuration based on device type
    Returns: dict - Configuration settings for current device
    """
    is_mobile = detect_mobile()
    return get_mobile_config() if is_mobile else get_desktop_config()


def mobile_friendly_columns(num_columns, gaps='medium'):
    """
    Create columns that adapt to mobile devices
    On mobile: returns single column
    On desktop: returns requested number of columns
    """
    config = get_device_config()
    
    if config['max_columns'] == 1:
        # Mobile: Return a list with a single container
        return [st.container()]
    else:
        # Desktop: Return normal columns
        return st.columns(num_columns, gap=gaps)


def render_mobile_info():
    """
    Render an info message for mobile users about limited functionality
    """
    st.info("""
    📱 **Mobile View Activated**
    
    You're viewing a simplified version optimized for mobile devices. 
    For full analytics including detailed charts, tables, and comprehensive reports, 
    please visit this page on a desktop or tablet device.
    """)


def should_show_component(component_type):
    """
    Check if a specific component type should be shown based on device
    
    Args:
        component_type: string - Type of component ('table', 'chart', 'expander', etc.)
    
    Returns:
        bool - True if component should be shown
    """
    config = get_device_config()
    
    component_map = {
        'table': config.get('show_tables', True),
        'chart': config.get('show_charts', True),
        'expander': config.get('show_expanders', True),
        'detailed_analysis': not config['max_columns'] == 1,  # Hide on mobile
        'raw_data': not config['max_columns'] == 1,  # Hide on mobile
    }
    
    return component_map.get(component_type, True)