
"""
Mobile detection utilities for the HAILIE TSM Insights Engine
"""

import streamlit as st
import streamlit.components.v1 as components

def detect_mobile():
    """
    Detect if the user is on a mobile device using JavaScript injection
    Returns: bool - True if mobile device detected, False otherwise
    """
    
    # Check for manual toggle in session state
    if hasattr(st.session_state, 'force_mobile_view'):
        return st.session_state.force_mobile_view
    
    # Check for manual override via query params
    query_params = st.query_params
    if 'mobile' in query_params:
        override_value = query_params['mobile'].lower() == 'true'
        return override_value
    
    # Initialize session state for mobile detection if not exists
    if 'is_mobile_device' not in st.session_state:
        st.session_state.is_mobile_device = False
    
    # Use JavaScript to detect mobile device
    # This runs on the client side and stores result in session state
    mobile_check_js = """
    <script>
        function checkMobile() {
            // Check multiple indicators
            const isMobile = /iPhone|iPad|iPod|Android|webOS|BlackBerry|Windows Phone/i.test(navigator.userAgent);
            const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
            const smallScreen = window.innerWidth <= 768;
            
            // Consider it mobile if user agent matches OR (touch + small screen)
            const mobile = isMobile || (hasTouch && smallScreen);
            
            // Send result back to Streamlit
            if (window.parent) {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: mobile
                }, '*');
            }
            
            // Also update URL parameter for persistence
            if (mobile) {
                const url = new URL(window.location);
                url.searchParams.set('mobile', 'true');
                window.history.replaceState({}, '', url);
            }
        }
        
        // Run check when page loads
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', checkMobile);
        } else {
            checkMobile();
        }
    </script>
    """
    
    # Inject the JavaScript (only once per session)
    if 'mobile_check_injected' not in st.session_state:
        components.html(mobile_check_js, height=0)
        st.session_state.mobile_check_injected = True
    
    # Fallback: Try headers API as backup
    try:
        headers = st.context.headers
        if headers:
            user_agent = headers.get('User-Agent', '').lower()
            
            mobile_indicators = [
                'iphone', 'ipod', 'android', 'mobile',
                'webos', 'blackberry', 'windows phone'
            ]
            
            is_mobile = any(indicator in user_agent for indicator in mobile_indicators)
            
            # Don't treat tablets as mobile
            if 'ipad' in user_agent or 'tablet' in user_agent:
                is_mobile = False
            
            # Store in session state
            st.session_state.is_mobile_device = is_mobile
            return is_mobile
    except Exception:
        pass
    
    # Return stored value or default to False
    return st.session_state.get('is_mobile_device', False)


def get_mobile_config():
    """
    Get configuration settings optimized for mobile devices
    Returns: dict - Configuration settings
    """
    return {
        'layout': 'centered',
        'sidebar_state': 'collapsed',
        'show_tables': False,
        'show_charts': True,
        'chart_height': 300,
        'max_columns': 1,
        'show_expanders': False,
        'touch_target_size': 48,
        'font_size_multiplier': 1.1,
    }


def get_desktop_config():
    """
    Get configuration settings optimized for desktop devices
    Returns: dict - Configuration settings
    """
    return {
        'layout': 'wide',
        'sidebar_state': 'expanded',
        'show_tables': True,
        'show_charts': True,
        'chart_height': 500,
        'max_columns': 3,
        'show_expanders': True,
        'touch_target_size': 40,
        'font_size_multiplier': 1.0,
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
        return [st.container()]
    else:
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
        'detailed_analysis': not config['max_columns'] == 1,
        'raw_data': not config['max_columns'] == 1,
    }
    
    return component_map.get(component_type, True)
