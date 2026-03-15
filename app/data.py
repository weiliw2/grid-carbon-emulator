"""Data loading helpers for the Streamlit app."""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from validation import benchmark_exists, compare_against_benchmark, load_benchmark_data
from country_names import add_country_names


@st.cache_data
def load_data():
    """Load processed tabular artifacts used by the dashboard."""
    country_data = pd.read_csv(ROOT_DIR / "data/processed/country_carbon_intensity.csv")
    country_data = add_country_names(country_data)
    ml_features = pd.read_csv(ROOT_DIR / "data/processed/ml_features.csv", index_col=0)
    ml_targets = pd.read_csv(ROOT_DIR / "data/processed/ml_targets.csv", index_col=0)
    return country_data, ml_features, ml_targets


@st.cache_resource
def load_model():
    """Load the trained emulator model."""
    return joblib.load(ROOT_DIR / "data/processed/carbon_emulator_model.pkl")


@st.cache_data
def load_validation_results():
    """Load or compute benchmark validation results when a benchmark file is available."""
    if not benchmark_exists():
        return None

    country_data = pd.read_csv(ROOT_DIR / "data/processed/country_carbon_intensity.csv")
    country_data = add_country_names(country_data)
    benchmark_df = load_benchmark_data()
    comparison_df, metrics = compare_against_benchmark(country_data, benchmark_df)
    comparison_df = add_country_names(comparison_df, code_col="country", name_col="country_name")
    return {
        "comparison": comparison_df,
        "metrics": metrics,
    }
