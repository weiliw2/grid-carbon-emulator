"""Shared pipeline runner for generating processed dashboard artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import joblib

import phase1_data_fetch as p1
import phase2_carbon_intensity as p2
import phase3_ml_emulator as p3
import validation

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "data/raw"
PROCESSED_DIR = ROOT_DIR / "data/processed"

REQUIRED_FILES = [
    PROCESSED_DIR / "country_carbon_intensity.csv",
    PROCESSED_DIR / "plants_with_emissions.csv",
    PROCESSED_DIR / "carbon_emulator_model.pkl",
    PROCESSED_DIR / "ml_features.csv",
    PROCESSED_DIR / "ml_targets.csv",
]

ProgressCallback = Callable[[int, str], None]


def data_files_exist() -> bool:
    """Check whether all expected processed artifacts exist."""
    return all(path.exists() for path in REQUIRED_FILES)


def ensure_data_directories() -> None:
    """Create raw and processed data directories if needed."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def run_full_pipeline(progress_callback: ProgressCallback | None = None) -> dict[str, object]:
    """Run the end-to-end data and model pipeline."""
    ensure_data_directories()

    _notify(progress_callback, 10, "Phase 1/3: Fetching global power plant data...")
    plants_df = p1.fetch_power_plant_data()
    if plants_df is None:
        raise RuntimeError("Phase 1 failed to fetch the global power plant dataset.")

    p1.explore_data(plants_df)

    _notify(progress_callback, 33, "Phase 2/3: Calculating carbon intensity...")
    plants_with_emissions = p2.map_emission_factors(plants_df.copy())
    plants_with_emissions = p2.calculate_plant_emissions(plants_with_emissions)
    country_data = p2.calculate_country_carbon_intensity(plants_with_emissions)

    plants_with_emissions.to_csv(PROCESSED_DIR / "plants_with_emissions.csv", index=False)
    country_data.to_csv(PROCESSED_DIR / "country_carbon_intensity.csv", index=False)

    _notify(progress_callback, 66, "Phase 3/3: Training ML emulator...")
    fuel_features = p3.create_fuel_mix_features(plants_with_emissions)
    features, targets, ml_data = p3.prepare_ml_dataset(fuel_features, country_data)

    best_model, best_model_name, X_test, y_test, results = p3.train_models(features, targets)
    if best_model is None:
        raise RuntimeError("Phase 3 failed: insufficient data to train a model.")

    joblib.dump(best_model, PROCESSED_DIR / "carbon_emulator_model.pkl")
    features.to_csv(PROCESSED_DIR / "ml_features.csv")
    targets.to_csv(PROCESSED_DIR / "ml_targets.csv")

    importances = p3.analyze_feature_importance(best_model, best_model_name, features)
    if importances is not None:
        importances.to_csv(PROCESSED_DIR / "feature_importances.csv", index=False)

    validation_result = None
    if validation.benchmark_exists():
        _notify(progress_callback, 90, "Validation: Comparing against benchmark dataset...")
        comparison_df, metrics = validation.run_validation(country_data)
        validation_result = {
            "comparison": comparison_df,
            "metrics": metrics,
        }

    _notify(progress_callback, 100, "Setup complete!")
    return {
        "plants": plants_with_emissions,
        "country_data": country_data,
        "features": features,
        "targets": targets,
        "ml_data": ml_data,
        "model": best_model,
        "model_name": best_model_name,
        "X_test": X_test,
        "y_test": y_test,
        "results": results,
        "validation": validation_result,
    }


def _notify(progress_callback: ProgressCallback | None, percent: int, message: str) -> None:
    """Emit progress updates when a callback is provided."""
    if progress_callback is not None:
        progress_callback(percent, message)
