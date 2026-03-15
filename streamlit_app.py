"""Grid Carbon Analysis Tool Streamlit entry point."""

import streamlit as st

from app.bootstrap import ensure_src_on_path, setup_data
from app.data import load_data, load_model, load_validation_results
from app.pages import (
    render_country_analysis,
    render_data_center_calculator,
    render_global_overview,
    render_policy_simulator,
    render_validation,
)
from app.styles import APP_CSS


st.set_page_config(
    page_title="Grid Carbon Analysis Tool",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ensure_src_on_path()
setup_data()
st.markdown(APP_CSS, unsafe_allow_html=True)

try:
    country_data, ml_features, ml_targets = load_data()
    model = load_model()
    validation_data = load_validation_results()
    data_loaded = True
except Exception as exc:
    st.error(f"Error loading data: {exc}")
    st.info("Please make sure you've run Phase 2 and Phase 3 first!")
    data_loaded = False

if data_loaded:
    st.markdown(
        """
        <section class="hero-shell">
            <div class="hero-kicker">Electricity Systems</div>
            <h1>Grid Carbon Analysis Tool</h1>
            <p class="hero-lede">
                Country-level analysis and scenario simulation of electricity grid carbon intensity across 167 countries.
                Explore energy-transition impacts, benchmark national power systems, and compare location-specific carbon exposure.
            </p>
            <div class="status-grid">
                <div class="status-card">
                    <div class="status-label">Coverage</div>
                    <div class="status-value">167 countries in the current processed dataset</div>
                </div>
                <div class="status-card">
                    <div class="status-label">Method</div>
                    <div class="status-value">Plant-level aggregation with scenario modeling and benchmark validation</div>
                </div>
                <div class="status-card">
                    <div class="status-label">Primary Data</div>
                    <div class="status-value">World Resources Institute Global Power Plant Database</div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    country_options = sorted(country_data["country"].tolist())
    default_country = "USA" if "USA" in country_options else country_options[0]
    selected_country = st.selectbox(
        "Focus Country",
        options=country_options,
        index=country_options.index(default_country),
        key="focus_country",
        help="Use one shared country selection across the country-specific views.",
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Global Overview", "Policy Simulator", "Country Analysis", "Data Center Calculator", "Validation"]
    )

    with tab1:
        render_global_overview(country_data)

    with tab2:
        render_policy_simulator(ml_features, model, selected_country)

    with tab3:
        render_country_analysis(country_data, ml_features, selected_country)

    with tab4:
        render_data_center_calculator(country_data, selected_country)

    with tab5:
        render_validation(validation_data)

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #586663; font-size: 0.95rem; line-height: 1.7;'>
        <strong>Grid Carbon Analysis Tool</strong><br>
        Country-level electricity carbon-intensity analysis, scenario exploration, and benchmark validation<br>
        Data source: Global Power Plant Database by World Resources Institute
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.warning("Please run Phase 2 and Phase 3 to generate the required data files.")
