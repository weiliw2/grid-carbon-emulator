"""Unit tests for core carbon-intensity calculations."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from assumptions import (
    DEFAULT_CAPACITY_FACTOR,
    EMISSION_FACTORS_GCO2_PER_KWH,
    RENEWABLE_FUELS,
)
from phase2_carbon_intensity import (
    calculate_country_carbon_intensity,
    calculate_plant_emissions,
    map_emission_factors,
)


class Phase2CarbonIntensityTests(unittest.TestCase):
    def test_map_emission_factors_applies_defaults_for_unknown_fuels(self) -> None:
        df = pd.DataFrame(
            {
                "primary_fuel": ["Coal", "Solar", "MysteryFuel"],
                "capacity_mw": [100.0, 50.0, 10.0],
            }
        )

        result = map_emission_factors(df.copy())

        self.assertEqual(result.loc[0, "emission_factor_gco2_kwh"], EMISSION_FACTORS_GCO2_PER_KWH["Coal"])
        self.assertEqual(result.loc[1, "emission_factor_gco2_kwh"], EMISSION_FACTORS_GCO2_PER_KWH["Solar"])
        self.assertEqual(result.loc[2, "emission_factor_gco2_kwh"], EMISSION_FACTORS_GCO2_PER_KWH["Other"])

    def test_calculate_plant_emissions_uses_generation_fallbacks_and_clips_negative_emissions(self) -> None:
        df = pd.DataFrame(
            {
                "primary_fuel": ["Coal", "MysteryFuel", "Storage"],
                "capacity_mw": [100.0, 10.0, 20.0],
                "generation_gwh_2019": [None, None, -5.0],
                "estimated_generation_gwh_2019": [None, None, None],
                "emission_factor_gco2_kwh": [EMISSION_FACTORS_GCO2_PER_KWH["Coal"], 500.0, 0.0],
            }
        )

        result = calculate_plant_emissions(df.copy())

        expected_coal_generation = 100.0 * 0.60 * 8760 / 1000
        expected_other_generation = 10.0 * DEFAULT_CAPACITY_FACTOR * 8760 / 1000

        self.assertAlmostEqual(result.loc[0, "generation_gwh"], expected_coal_generation, places=6)
        self.assertAlmostEqual(result.loc[1, "generation_gwh"], expected_other_generation, places=6)
        self.assertEqual(result.loc[2, "annual_emissions_tonnes"], 0.0)

        expected_coal_emissions = expected_coal_generation * EMISSION_FACTORS_GCO2_PER_KWH["Coal"] / 1000
        self.assertAlmostEqual(result.loc[0, "annual_emissions_tonnes"], expected_coal_emissions, places=6)

    def test_calculate_country_carbon_intensity_aggregates_generation_emissions_and_renewables(self) -> None:
        hydro_fuel = "Hydro" if "Hydro" in RENEWABLE_FUELS else RENEWABLE_FUELS[0]
        df = pd.DataFrame(
            {
                "country": ["AAA", "AAA", "BBB"],
                "primary_fuel": ["Coal", hydro_fuel, "Gas"],
                "capacity_mw": [100.0, 50.0, 80.0],
                "generation_gwh": [400.0, 200.0, 300.0],
                "annual_emissions_tonnes": [328.0, 4.8, 147.0],
                "name": ["Plant A", "Plant B", "Plant C"],
            }
        )

        result = calculate_country_carbon_intensity(df.copy()).set_index("country")

        self.assertAlmostEqual(result.loc["AAA", "total_generation_gwh"], 600.0, places=6)
        self.assertAlmostEqual(result.loc["AAA", "total_emissions_tonnes"], 332.8, places=6)
        self.assertAlmostEqual(result.loc["AAA", "carbon_intensity_gco2_kwh"], 554.6666667, places=5)
        self.assertAlmostEqual(result.loc["AAA", "renewable_percentage"], 33.3333333, places=5)
        self.assertEqual(result.loc["AAA", "dominant_fuel"], "Coal")

        self.assertAlmostEqual(result.loc["BBB", "carbon_intensity_gco2_kwh"], 490.0, places=6)
        self.assertAlmostEqual(result.loc["BBB", "renewable_percentage"], 0.0, places=6)


if __name__ == "__main__":
    unittest.main()
