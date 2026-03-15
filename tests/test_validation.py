"""Unit tests for benchmark validation utilities."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from validation import compare_against_benchmark, save_validation_outputs


class ValidationTests(unittest.TestCase):
    def test_compare_against_benchmark_calculates_expected_metrics(self) -> None:
        country_data = pd.DataFrame(
            {
                "country": ["AAA", "BBB", "CCC"],
                "carbon_intensity_gco2_kwh": [100.0, 250.0, 300.0],
            }
        )
        benchmark_df = pd.DataFrame(
            {
                "country": ["AAA", "BBB", "DDD"],
                "benchmark_carbon_intensity_gco2_kwh": [110.0, 200.0, 50.0],
            }
        )

        comparison_df, metrics = compare_against_benchmark(country_data, benchmark_df)

        self.assertEqual(metrics["num_countries_compared"], 2)
        self.assertAlmostEqual(metrics["mae_gco2_kwh"], 30.0, places=6)
        self.assertAlmostEqual(metrics["rmse_gco2_kwh"], 36.05551275, places=5)
        self.assertAlmostEqual(metrics["mean_bias_gco2_kwh"], 20.0, places=6)
        self.assertEqual(set(comparison_df["country"]), {"AAA", "BBB"})
        self.assertIn("absolute_percentage_error", comparison_df.columns)

    def test_save_validation_outputs_writes_expected_files(self) -> None:
        comparison_df = pd.DataFrame(
            {
                "country": ["AAA"],
                "carbon_intensity_gco2_kwh": [100.0],
                "benchmark_carbon_intensity_gco2_kwh": [90.0],
                "error_gco2_kwh": [10.0],
                "absolute_error_gco2_kwh": [10.0],
                "absolute_percentage_error": [11.111111],
            }
        )
        metrics = {
            "num_countries_compared": 1,
            "mae_gco2_kwh": 10.0,
            "rmse_gco2_kwh": 10.0,
            "mape_percent": 11.111111,
            "mean_bias_gco2_kwh": 10.0,
            "correlation": 1.0,
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            save_validation_outputs(comparison_df, metrics, output_dir)

            self.assertTrue((output_dir / "benchmark_comparison.csv").exists())
            self.assertTrue((output_dir / "benchmark_metrics.csv").exists())
            self.assertTrue((output_dir / "benchmark_metrics.json").exists())


if __name__ == "__main__":
    unittest.main()
