"""Bootstrap helpers for the Streamlit app."""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"


def ensure_src_on_path() -> None:
    """Allow the app to import pipeline modules from src/."""
    src_path = str(SRC_DIR)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


def setup_data() -> None:
    """Generate processed data artifacts if they are missing."""
    ensure_src_on_path()

    from pipeline_runner import data_files_exist, run_full_pipeline

    if data_files_exist():
        return

    st.info("First-time setup: Generating data files... This takes 2-3 minutes.")
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        run_full_pipeline(progress_callback=lambda percent, message: _update_progress(progress_bar, status_text, percent, message))
        st.success("Data pipeline completed successfully! Reloading app...")
        st.rerun()

    except Exception as exc:
        st.error(f"Error during setup: {exc}")
        st.code(traceback.format_exc())
        st.stop()


def _update_progress(progress_bar, status_text, percent: int, message: str) -> None:
    """Update the Streamlit progress indicators."""
    status_text.text(message)
    progress_bar.progress(percent)
