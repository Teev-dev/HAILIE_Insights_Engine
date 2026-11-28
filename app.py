# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Tom Stephenson (Teev-dev)

import streamlit as st
import pandas as pd
import numpy as np
from data_processor_enhanced import EnhancedTSMDataProcessor
from analytics_refactored import TSMAnalytics, MAX_COMPARE_PROVIDERS, MIN_COMPARE_PROVIDERS
from dashboard import ExecutiveDashboard
from styles import apply_css
from mobile_utils import detect_mobile, mobile_friendly_columns, render_mobile_info, should_show_component
from contextlib import contextmanager
from config import DB_PATH, FEEDBACK_FORM_ENABLED
from tsm_measures import LCHO_EXCLUDED
from tooltip_definitions import WHATS_NEW_MESSAGE
import html
import os

# User-facing year label for the currently-loaded TSM dataset. A provider whose
# most recent results are older than this is shown with a notice, against the
# peers of its own latest year.
# Query-layer year defaults (data_processor_enhanced.py, analytics_refactored.py)
# are updated separately per MAINTENANCE.md — do not point them at this constant.
CURRENT_DATA_YEAR = 2026

# Sentry is a no-op unless SENTRY_DSN is set in the environment.
# send_default_pii=False keeps IP/User headers out of events — this codebase
# handles public provider data but CLAUDE.md forbids anything PII-adjacent.
_sentry_dsn = os.environ.get("SENTRY_DSN", "")
if _sentry_dsn:
    import sentry_sdk
    sentry_sdk.init(
        dsn=_sentry_dsn,
        traces_sample_rate=0.1,
        environment=os.environ.get("ENVIRONMENT", "production"),
        send_default_pii=False,
    )

# HAILIE branding assets. The full wordmark logo is shown in-app (top-left);
# the browser tab icon uses just the house glyph on a page-matching background.
_LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "hailie_logo.png")
_FAVICON_PATH = os.path.join(os.path.dirname(__file__), "assets", "hailie_favicon.png")

# Page configuration - MUST be first Streamlit command
# Using 'wide' layout for all devices, content adapts responsively
st.set_page_config(
    page_title="HAILIE TSM Insights Engine",
    page_icon=_FAVICON_PATH,
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.logo(
    _LOGO_PATH,
    link="https://housingai.org",
    size="large",
)

# Apply custom CSS styles from styles module
apply_css(st)


def _report_internal_error(context: str, exc: Exception | None = None) -> None:
    """Route error details to Sentry/stdout only — never to the UI."""
    if exc is not None:
        print(f"[ERROR] {context}: {type(exc).__name__}")
    else:
        print(f"[ERROR] {context}")
    if _sentry_dsn and exc is not None:
        import sentry_sdk
        sentry_sdk.capture_exception(exc)


def render_landing_hero():
    """Render the professional hero section"""
    is_mobile = detect_mobile()
    
    if is_mobile:
        # Mobile version - styled gradient header
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #0B5C70 0%, #083E4D 100%);
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
            st.markdown("**Your Rank**")
            st.markdown("See exactly how your housing provider compares to peers with quartile-based scoring.")

            st.markdown("**Your Momentum**")
            st.markdown("Track your 12-month performance trajectory across key satisfaction measures.")

            st.markdown("**Your Priority**")
            st.markdown("Identify the single most critical area for improvement based on data-driven analysis.")
    else:
        # Desktop version - use custom HTML grid
        st.markdown("""
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon-professional rank-icon"></div>
                <p class="feature-title">Your Rank</p>
                <p class="feature-description">
                    See exactly how your housing provider compares to peers with quartile-based scoring. 
                    Get clear visual indicators showing your competitive position.
                </p>
            </div>
            <div class="feature-card">
                <div class="feature-icon-professional momentum-icon"></div>
                <p class="feature-title">Your Momentum</p>
                <p class="feature-description">
                    Track your 12-month performance trajectory. Understand if you're improving, 
                    stable, or declining across key satisfaction measures.
                </p>
            </div>
            <div class="feature-card">
                <div class="feature-icon-professional priority-icon"></div>
                <p class="feature-title">Your Priority</p>
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
    db_path = DB_PATH

    # Check if file exists
    if not os.path.exists(db_path):
        return False

    # Check if file is readable
    if not os.access(db_path, os.R_OK):
        _report_internal_error("database file exists but is not readable")
        st.error("Database is unavailable. Please contact support.")
        return False

    # Check if it's a valid DuckDB file (basic check)
    try:
        import duckdb
        conn = duckdb.connect(db_path, read_only=True)
        conn.execute("SELECT 1").fetchone()
        conn.close()
        return True
    except Exception as e:
        _report_internal_error("database corruption check failed", e)
        st.error("Database is unavailable. Please contact support.")
        return False


def parse_provider_option(option: str):
    """Split a dropdown option "Provider Name - LCRA (CODE)" into (code, name).

    Returns (None, option) when the option carries no code.
    """
    if "(" in option and ")" in option:
        provider_code = option.split("(")[-1].replace(")", "")
        provider_name = option.rsplit("(", 1)[0].strip()
        return provider_code, provider_name
    return None, option


def render_footer(caption: str):
    """Render the page footer: version caption, licence line and privacy link."""
    st.markdown("---")
    st.caption(caption)
    st.markdown(
        '<p style="text-align: center; font-size: 0.8em; color: #94A3B8; margin: 0.25rem 0;">'
        '&copy; 2026 Tom Stephenson (Teev-dev). Built for HAILIE. '
        'Licensed under <a href="https://opensource.org/licenses/MIT" style="color: #94A3B8;">MIT</a>'
        '/<a href="https://creativecommons.org/licenses/by/4.0/" style="color: #94A3B8;">CC-BY 4.0</a>.'
        '</p>'
        '<p style="text-align: center; font-size: 0.85em; color: #666; margin-top: 0.25rem;">'
        '<a href="/privacy_policy" target="_self">Privacy Policy</a>'
        '</p>',
        unsafe_allow_html=True
    )


def render_comparison_view(provider_options, show_advanced_logging: bool = False,
                           option_labels: dict | None = None):
    """Multi-provider view: two or three providers side by side."""
    option_labels = option_labels or {}
    st.subheader("Choose providers to compare")
    selected = st.multiselect(
        f"Select {MIN_COMPARE_PROVIDERS} or {MAX_COMPARE_PROVIDERS} providers:",
        options=provider_options,
        format_func=lambda x: option_labels.get(x, x),
        max_selections=MAX_COMPARE_PROVIDERS,
        placeholder="Start typing a provider name...",
        help="For group executives responsible for more than one registered provider. "
             "Providers must be of the same type (all LCRA or all LCHO) to be compared.",
    )

    footer_caption = f"HAILIE TSM Insights Engine v3.0 | Data: {CURRENT_DATA_YEAR} TSM"

    if len(selected) < MIN_COMPARE_PROVIDERS:
        st.markdown("---")
        st.info(f"""
        **Comparing providers:**

        Select {MIN_COMPARE_PROVIDERS} or {MAX_COMPARE_PROVIDERS} providers above to see their rank,
        momentum, priority and scores side by side.
        """)
        render_footer(footer_caption)
        return

    st.markdown("---")

    try:
        data_processor = EnhancedTSMDataProcessor(silent_mode=not show_advanced_logging)
    except ConnectionError as e:
        _report_internal_error("comparison processor init: ConnectionError", e)
        st.error("Database is unavailable. Please try again later or contact support.")
        return
    except Exception as e:
        _report_internal_error("comparison processor init: unexpected error", e)
        st.error("Something went wrong loading these providers. Please refresh and try again.")
        return

    selections = []
    for option in selected:
        code, name = parse_provider_option(option)
        dataset_type = data_processor.get_provider_dataset_type(name) if code else None
        if not code or not dataset_type or not data_processor.get_provider_exists(code):
            st.error("One of the selected providers could not be found. Please remove it and try again.")
            data_processor.close()
            return
        selections.append({'provider_code': code, 'provider_name': name, 'dataset_type': dataset_type})

    analytics = TSMAnalytics(data_processor)
    dashboard = ExecutiveDashboard()

    # Peer filter options only make sense once all providers share a dataset;
    # for a mixed selection compare_providers returns the explanatory error.
    size_band = region = None
    dataset_types = {sel['dataset_type'] for sel in selections}
    if len(dataset_types) == 1:
        shared_dataset_type = next(iter(dataset_types))
        size_band, region = dashboard.render_peer_group_filter(
            data_processor.get_peer_filter_options(shared_dataset_type), key_prefix="compare")
        footer_caption = (
            f"HAILIE TSM Insights Engine v3.0 | Group comparison, {shared_dataset_type} Dataset | "
            f"Data: {CURRENT_DATA_YEAR} TSM"
        )

    comparison = analytics.compare_providers(selections, size_band=size_band, region=region)
    dashboard.render_provider_comparison(comparison)

    if FEEDBACK_FORM_ENABLED:
        st.markdown("---")
        dashboard.render_feedback_form()

    render_footer(footer_caption)
    data_processor.close()


def render_dataset_indicator(dataset_type: str, peer_count: int, peer_label: str | None = None):
    """Render a visual indicator showing which dataset is being used.

    peer_label describes a narrowed peer group (size band / region); when
    given it replaces the default "<dataset> group" wording.
    """
    if dataset_type == 'LCRA':
        color = "#0B5C70"  # Deep HAILIE Teal
        description = "Large-scale Council & Registered Providers"
        note = "Full TSM metrics including repairs satisfaction"
    elif dataset_type == 'LCHO':
        color = "#1F94A3"  # Bright Teal
        description = "Large-scale Voluntary Transfer Organizations"
        note = "Core TSM metrics (repairs metrics not applicable)"
    else:
        color = "#6C7A89"  # Charcoal Muted
        description = "Combined Dataset"
        note = "Providers with combined reporting"

    safe_dataset = html.escape(dataset_type)
    safe_description = html.escape(description)
    safe_note = html.escape(note)
    safe_peer_count = html.escape(str(peer_count))
    if peer_label:
        peer_line = f"Comparing with {safe_peer_count} peer providers: {html.escape(peer_label)}"
    else:
        peer_line = f"Comparing with {safe_peer_count} peer providers in {safe_dataset} group"

    st.markdown(f"""
    <div style="background-color: {color}15; border-left: 4px solid {color}; padding: 10px; margin: 10px 0; border-radius: 4px;">
        <strong style="color: {color};">Dataset: {safe_dataset}</strong><br/>
        <small>{safe_description}</small><br/>
        <small style="opacity: 0.8;">{safe_note}</small><br/>
        <small style="opacity: 0.8;">{peer_line}</small>
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
        **Enhanced Analytics Database Not Found**

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
        # Latest year and name history per provider: drives the "formerly ..."
        # dropdown labels and the caption for renamed providers.
        provider_history = data_processor_for_options.get_provider_history()
        option_labels = ExecutiveDashboard.build_provider_option_labels(provider_options, provider_history)
    except ConnectionError as e:
        _report_internal_error("processor init: ConnectionError", e)
        st.error("""
        **Database Connection Failed**

        Unable to connect to the analytics database.

        If you're running locally and the database is missing, run:
        ```bash
        python build_analytics_db_v2.py
        ```
        """)
        return
    except Exception as e:
        _report_internal_error("processor init: unexpected error", e)
        st.error("Something went wrong starting the application. Please contact support.")
        return

    provider_code = None
    selected_dataset_type = None

    # Sidebar for analysis options
    with st.sidebar:
        # Device view toggle
        st.header("View Settings")
        force_mobile = st.checkbox(
            "Use Mobile View",
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
        **Automatic Dataset Detection**

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
        st.info(f"""
        **Enhanced Analytics Engine**

        This application uses an enhanced analytics database with:
        • Separate LCRA and LCHO datasets
        • Dataset-specific percentiles
        • Peer group isolation
        • Automatic metric adaptation

        Data source: {CURRENT_DATA_YEAR} TSM Dataset
        """)

    st.markdown('<div id="provider-search-section"></div>', unsafe_allow_html=True)
    st.markdown("## Select Your Provider")

    view_mode = "Single provider"
    if provider_options:
        view_mode = st.radio(
            "What would you like to see?",
            options=["Single provider", "Compare providers"],
            horizontal=True,
            help="Compare providers places two or three providers side by side, "
                 "for group executives responsible for more than one registered provider.",
        )

    if view_mode == "Compare providers":
        render_comparison_view(provider_options, show_advanced_logging, option_labels)
        return

    # Single column layout for provider selection
    if provider_options:
        # Provider search dropdown with autocomplete - includes all providers
        st.subheader("Search by Provider Name")
        st.markdown("<small>All LCRA and LCHO providers available</small>", unsafe_allow_html=True)

        selected_provider = st.selectbox(
            "Type or select your provider:",
            options=[""] + provider_options,
            help="Start typing to search for your provider - includes both LCRA and LCHO providers",
            format_func=lambda x: "Select a provider..." if x == "" else option_labels.get(x, x))

        # Extract provider code and name from selection
        if selected_provider and selected_provider != "":
            # Format is "Provider Name (CODE)"; the name (without the code part)
            # is used for dataset detection
            provider_code, provider_name_only = parse_provider_option(selected_provider)
        else:
            provider_code = None
            selected_provider = None
            provider_name_only = None
    else:
        st.error("Unable to load provider list. Please try refreshing the page.")
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
            _report_internal_error("per-provider processor init: ConnectionError", e)
            st.error("Database is unavailable. Please try again later or contact support.")
            return
        except Exception as e:
            _report_internal_error("per-provider processor init: unexpected error", e)
            st.error("Something went wrong loading your provider. Please try another provider or refresh.")
            return

        # Check if provider exists in database
        if not data_processor.get_provider_exists(provider_code):
            st.error(f"Provider '{provider_code}' not found. Please check the code and try again.")
            return

        # Get the dataset type for this provider (use the name without the code part)
        dataset_type = data_processor.get_provider_dataset_type(provider_name_only)
        if not dataset_type:
            st.error(f"Could not determine dataset type for provider '{provider_code}'")
            return

        # The year of results to show: the provider's own most recent year in
        # this dataset. Normally the current year; earlier for a provider that
        # is no longer in the regulator's data. Every query below is pinned to
        # it so scores, peers, percentiles and correlations share one year.
        data_year = data_processor.get_latest_year(provider_code, dataset_type)
        if data_year is None:
            st.error("Unable to load provider data. Please try again later.")
            return
        is_prior_year = data_year < CURRENT_DATA_YEAR

        # Initialize analytics and dashboard
        analytics = TSMAnalytics(data_processor, year=data_year)
        dashboard = ExecutiveDashboard()

        # Optional peer group narrowing by size band / region. resolve_peer_group
        # returns the filter actually in force (it drops a filter that would
        # leave too small a group), so always use its size_band / region.
        requested_size_band, requested_region = dashboard.render_peer_group_filter(
            data_processor.get_peer_filter_options(dataset_type, year=data_year),
            data_processor.get_provider_metadata(provider_code, dataset_type, year=data_year),
        )
        peer_group = analytics.resolve_peer_group(
            [provider_code], dataset_type, requested_size_band, requested_region)
        peer_size_band = peer_group['size_band']
        peer_region = peer_group['region']
        peer_count = peer_group['peer_group_size'] - 1  # Exclude the current provider
        peer_label = (
            dashboard.describe_peer_group(dataset_type, peer_size_band, peer_region)
            if peer_group['is_filtered'] else None
        )
        peer_heading = peer_label or f"{dataset_type} Peer Group"

        # Display dataset indicator
        render_dataset_indicator(dataset_type, peer_count, peer_label)
        if peer_group['fallback']:
            dashboard.render_peer_group_notice(peer_group, dataset_type)

        # Load provider data with automatic dataset detection (pass provider name without code)
        df = data_processor.load_default_data(provider_code, provider_name_only, year=data_year)

        if df is None or df.empty:
            st.error("Unable to load provider data. Please try again later.")
            return

        dashboard.render_former_names(
            provider_history.get((provider_code, dataset_type), {}).get('names'))

        # A provider with no results for the current year: say so in a dialog
        # once per selection, and keep the notice on the page above the summary.
        if dashboard.should_open_prior_year_dialog(st.session_state, selected_provider, is_prior_year):
            dashboard.render_prior_year_dialog(
                provider_name_only, data_year, CURRENT_DATA_YEAR, provider_code)
        if is_prior_year:
            dashboard.render_prior_year_notice(
                provider_name_only, data_year, CURRENT_DATA_YEAR, provider_code)

        # Dismissible changelog toast — appears once per session for returning users.
        # It describes the current year's results, so it is not shown (and not
        # marked as dismissed) for a provider with only earlier results.
        if 'dismissed_changelog' not in st.session_state:
            st.session_state.dismissed_changelog = False

        if not st.session_state.dismissed_changelog and not is_prior_year:
            with st.container():
                st.info(WHATS_NEW_MESSAGE)
                if st.button("Dismiss", key="dismiss_changelog"):
                    st.session_state.dismissed_changelog = True
                    st.rerun()

        # Get applicable measures for this dataset type
        applicable_measures = data_processor.get_applicable_measures(dataset_type)

        # Calculate key metrics within the correct peer group
        rankings = analytics.calculate_rankings(
            df, "All Providers", dataset_type,
            size_band=peer_size_band, region=peer_region, include_provider_codes=[provider_code])
        momentum = analytics.calculate_momentum(df, provider_code, provider_name_only, dataset_type=dataset_type)

        # Get dataset-specific correlations for priority calculation
        if dataset_type == 'LCHO':
            correlations_df = data_processor.get_dataset_correlations('LCHO', year=data_year)
        else:
            correlations_df = data_processor.get_dataset_correlations('LCRA', year=data_year)
        priority = analytics.identify_priority(
            df, provider_code, provider_name_only, dataset_type=dataset_type,
            size_band=peer_size_band, region=peer_region)

        # Executive Summary
        dashboard.render_executive_summary(provider_code, rankings, momentum,
                                          priority, provider_name=provider_name_only)

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
            
            with st.expander("Performance Analysis", expanded=True):
                st.markdown(f"### Performance Analysis - {peer_heading}")

                # Show note for LCHO providers about missing metrics
                if dataset_type == 'LCHO':
                    st.info("""
                    **Note for LCHO Providers**:
                    Repairs metrics (TP02-TP04) are not applicable to LCHO providers 
                    and are excluded from this analysis. All comparisons are made 
                    within your LCHO peer group only.
                    """)

                detailed_analysis = analytics.get_detailed_performance_analysis(
                    df, provider_code, provider_name_only, dataset_type=dataset_type,
                    size_band=peer_size_band, region=peer_region)

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
                        if k not in LCHO_EXCLUDED
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

            with st.expander("Measure Correlations", expanded=False):
                st.markdown(f"### Correlation Analysis - {dataset_type} Dataset")

                # Get dataset-specific correlations
                correlations = data_processor.get_dataset_correlations(dataset_type, year=data_year)

                if dataset_type == 'LCHO':
                    st.info("Correlations calculated using LCHO providers only (excluding repairs metrics)")
                else:
                    st.info("Correlations calculated using LCRA providers with all metrics")
                if peer_group['is_filtered']:
                    st.caption(
                        f"Correlations are measured across all {dataset_type} providers, not just your "
                        "chosen peer group: a small group is not enough to measure them reliably.")

                dashboard.render_correlation_analysis(correlations, priority)

            with st.expander("Priority Matrix", expanded=False):
                st.markdown(f"### Priority Matrix - {dataset_type} Context")

                # Filter priority matrix for LCHO if needed
                if dataset_type == 'LCHO' and priority:
                    # Ensure repairs metrics aren't in the priority recommendations
                    if 'measure' in priority and priority['measure'] in LCHO_EXCLUDED:
                        st.warning("Priority calculation adjusted for LCHO dataset")

                dashboard.render_priority_matrix(priority, detailed_analysis)

            with st.expander("Score Breakdown", expanded=False):
                st.markdown(f"### Your TSM Scores — {dataset_type}")

                scores_df = data_processor.get_provider_scores(
                    provider_code, year=data_year, dataset_type=dataset_type)
                
                if not scores_df.empty:
                    # Ensure scores_df is a DataFrame, not an array
                    if isinstance(scores_df, pd.DataFrame):
                        # Add descriptions
                        scores_df['description'] = scores_df['tp_measure'].apply(lambda x: data_processor.tp_descriptions.get(x, 'Unknown measure'))

                        if dataset_type == 'LCHO':
                            scores_df = scores_df[~scores_df['tp_measure'].isin(LCHO_EXCLUDED)]

                            st.info("**Note**: Measures TP02-TP04 (repairs and home-maintenance) are not applicable to LCHO providers and are excluded from this view.")

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
                    - Peer Group: **{peer_heading}**
                    - Peer Group Size: **{peer_count} providers**
                    - Applicable Measures: **{len(applicable_measures)}**
                    - Measures Displayed: **{len(display_df)}**
                    """)
                else:
                    st.warning("No score data available for this provider")

            with st.expander("Comparisons", expanded=False):

                # Get comparison data for the selected provider's priority measure
                priority_measure = priority["priority_measure"]
                comparison_data = data_processor.get_peer_comparison_data(provider_code, provider_name_only, priority_measure)

                dashboard.render_comparisons(provider_code, priority_measure, comparison_data)

        # Report a data issue / feature request — provider context attached.
        # Hidden by default until email delivery is configured (see
        # FEEDBACK_FORM_ENABLED in config.py).
        if FEEDBACK_FORM_ENABLED:
            st.markdown("---")
            dashboard.render_feedback_form(provider_code, dataset_type)

        # Footer
        render_footer(
            f"HAILIE TSM Insights Engine v3.0 | Enhanced Analytics with {dataset_type} Dataset | Data: {data_year} TSM"
        )

        # Close database connection when done
        data_processor.close()

    else:
        # Instructions when no provider is selected
        st.markdown("---")
        st.info("""
        **Getting Started:**

        Search for your provider name in the dropdown above.
        Start typing to filter the list and find your provider quickly.

        The system will instantly retrieve your pre-calculated analytics.
        """)

        # Report a data issue / feature request — available before selecting a
        # provider too. Hidden by default until email delivery is configured
        # (see FEEDBACK_FORM_ENABLED in config.py).
        if FEEDBACK_FORM_ENABLED:
            st.markdown("---")
            ExecutiveDashboard().render_feedback_form()

        # Footer with privacy link
        render_footer(f"HAILIE TSM Insights Engine v3.0 | Data: {CURRENT_DATA_YEAR} TSM")


if __name__ == "__main__":
    main()
