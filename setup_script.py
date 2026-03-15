"""
Setup script to generate data files for Streamlit Cloud deployment
This runs automatically when the app is deployed
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pipeline_runner import data_files_exist, run_full_pipeline


def run_data_pipeline():
    """Run the full data pipeline"""
    print("🔄 Data files not found. Running data pipeline...")

    try:
        run_full_pipeline(progress_callback=_log_progress)
        print("\n✅ Data pipeline completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Error running data pipeline: {e}")
        return False


def _log_progress(percent: int, message: str) -> None:
    """Emit simple text progress for deployment and local setup flows."""
    print(f"\n[{percent}%] {message}")

if __name__ == "__main__":
    if not data_files_exist():
        success = run_data_pipeline()
        if not success:
            sys.exit(1)
    else:
        print("✅ All data files already exist. Skipping pipeline.")
