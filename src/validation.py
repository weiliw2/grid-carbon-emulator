"""Benchmark validation utilities for country-level carbon intensity outputs."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
BENCHMARK_DIR = ROOT_DIR / "data/benchmarks"
DEFAULT_BENCHMARK_PATH = BENCHMARK_DIR / "country_carbon_intensity_benchmark.csv"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "data/validation"

REQUIRED_BENCHMARK_COLUMNS = {
    "country",
    "benchmark_carbon_intensity_gco2_kwh",
}


def benchmark_exists(path: Path | None = None) -> bool:
    """Check whether a benchmark file is available for validation."""
    benchmark_path = path or DEFAULT_BENCHMARK_PATH
    return benchmark_path.exists()


def load_benchmark_data(path: Path | None = None) -> pd.DataFrame:
    """Load a benchmark dataset for country-level validation."""
    benchmark_path = path or DEFAULT_BENCHMARK_PATH
    benchmark_df = pd.read_csv(benchmark_path)

    missing_columns = REQUIRED_BENCHMARK_COLUMNS - set(benchmark_df.columns)
    if missing_columns:
        missing_list = ", ".join(sorted(missing_columns))
        raise ValueError(f"Benchmark file is missing required columns: {missing_list}")

    benchmark_df = benchmark_df.copy()
    benchmark_df["country"] = benchmark_df["country"].astype(str).str.upper()
    benchmark_df["benchmark_carbon_intensity_gco2_kwh"] = pd.to_numeric(
        benchmark_df["benchmark_carbon_intensity_gco2_kwh"],
        errors="coerce",
    )
    benchmark_df = benchmark_df.dropna(subset=["benchmark_carbon_intensity_gco2_kwh"])
    return benchmark_df


def compare_against_benchmark(
    country_data: pd.DataFrame,
    benchmark_df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Merge model outputs with benchmark data and compute summary metrics."""
    model_df = country_data[["country", "carbon_intensity_gco2_kwh"]].copy()
    model_df["country"] = model_df["country"].astype(str).str.upper()
    model_df["carbon_intensity_gco2_kwh"] = pd.to_numeric(
        model_df["carbon_intensity_gco2_kwh"],
        errors="coerce",
    )

    comparison_df = model_df.merge(benchmark_df, on="country", how="inner")
    comparison_df = comparison_df.dropna(
        subset=["carbon_intensity_gco2_kwh", "benchmark_carbon_intensity_gco2_kwh"]
    ).copy()

    if comparison_df.empty:
        raise ValueError("No overlapping countries were found between model output and benchmark data.")

    comparison_df["error_gco2_kwh"] = (
        comparison_df["carbon_intensity_gco2_kwh"] - comparison_df["benchmark_carbon_intensity_gco2_kwh"]
    )
    comparison_df["absolute_error_gco2_kwh"] = comparison_df["error_gco2_kwh"].abs()
    comparison_df["absolute_percentage_error"] = np.where(
        comparison_df["benchmark_carbon_intensity_gco2_kwh"] != 0,
        comparison_df["absolute_error_gco2_kwh"] / comparison_df["benchmark_carbon_intensity_gco2_kwh"] * 100,
        np.nan,
    )

    metrics = calculate_validation_metrics(comparison_df)
    comparison_df = comparison_df.sort_values("absolute_error_gco2_kwh", ascending=False)
    return comparison_df, metrics


def calculate_validation_metrics(comparison_df: pd.DataFrame) -> dict[str, float]:
    """Calculate summary statistics for a benchmark comparison table."""
    actual = comparison_df["benchmark_carbon_intensity_gco2_kwh"]
    predicted = comparison_df["carbon_intensity_gco2_kwh"]
    error = comparison_df["error_gco2_kwh"]

    mae = float(np.mean(np.abs(error)))
    rmse = float(np.sqrt(np.mean(np.square(error))))
    bias = float(np.mean(error))
    correlation = float(actual.corr(predicted))
    mape = float(np.nanmean(comparison_df["absolute_percentage_error"]))

    return {
        "num_countries_compared": int(len(comparison_df)),
        "mae_gco2_kwh": mae,
        "rmse_gco2_kwh": rmse,
        "mape_percent": mape,
        "mean_bias_gco2_kwh": bias,
        "correlation": correlation,
    }


def save_validation_outputs(
    comparison_df: pd.DataFrame,
    metrics: dict[str, float],
    output_dir: Path | None = None,
) -> None:
    """Persist validation outputs for downstream inspection and dashboarding."""
    target_dir = output_dir or DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    comparison_df.to_csv(target_dir / "benchmark_comparison.csv", index=False)

    summary_df = pd.DataFrame(
        [{"metric": key, "value": value} for key, value in metrics.items()]
    )
    summary_df.to_csv(target_dir / "benchmark_metrics.csv", index=False)

    with open(target_dir / "benchmark_metrics.json", "w", encoding="utf-8") as file_obj:
        json.dump(metrics, file_obj, indent=2)


def run_validation(
    country_data: pd.DataFrame,
    benchmark_path: Path | None = None,
    output_dir: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Run benchmark comparison end to end and save the outputs."""
    benchmark_df = load_benchmark_data(benchmark_path)
    comparison_df, metrics = compare_against_benchmark(country_data, benchmark_df)
    save_validation_outputs(comparison_df, metrics, output_dir)
    return comparison_df, metrics
