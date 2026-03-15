"""Grid Carbon-Intensity Emulator Streamlit entry point."""

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
    page_title="Grid Carbon Emulator",
    layout="wide",
    initial_sidebar_state="expanded",
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
    st.title("Grid Carbon-Intensity Emulator")
    st.markdown(
        """
        <p style='font-size: 1.25rem; color: #374151; margin-bottom: 2.5rem; line-height: 1.6;'>
        AI-powered analysis and simulation of electricity grid carbon intensity across 167 countries.
        Predict the impact of energy policy changes and optimize data center location strategies.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("### Navigation")
    st.sidebar.markdown("Use the tabs above to explore different features of the emulator.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Global Overview", "Policy Simulator", "Country Analysis", "Data Center Calculator", "Validation"]
    )

    with tab1:
        render_global_overview(country_data)

    with tab2:
        render_policy_simulator(ml_features, model)

    with tab3:
        render_country_analysis(country_data, ml_features)

    with tab4:
        render_data_center_calculator(country_data)

    with tab5:
        render_validation(validation_data)

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #6B7280; font-size: 0.9rem;'>
        <strong>Grid Carbon-Intensity Emulator</strong> | Built with Python, XGBoost, and Streamlit<br>
        Data source: Global Power Plant Database by World Resources Institute
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.warning("Please run Phase 2 and Phase 3 to generate the required data files.")
