# Methodology

This document describes how the Grid Carbon Analysis Tool converts global power plant data into country-level electricity carbon-intensity estimates and then trains a machine-learning surrogate model for rapid scenario analysis.

## Scope

The project estimates annual average grid carbon intensity at the country level, expressed in `gCO2/kWh`.

This is an average generation-side estimate derived from power plant data and engineering assumptions. It is intended for:
- cross-country benchmarking
- high-level policy scenario exploration
- location-screening use cases such as data center siting

It is not intended to represent:
- real-time grid intensity
- hourly dispatch outcomes
- marginal emissions
- cross-border electricity trade flows

## Pipeline Summary

The current pipeline has three main stages:

1. `Phase 1`: download and inspect the World Resources Institute Global Power Plant Database.
2. `Phase 2`: assign fuel-specific emissions factors, estimate missing generation, and aggregate plant-level emissions to country-level intensity.
3. `Phase 3`: engineer country fuel-mix features and train a machine-learning emulator for fast prediction and scenario simulation.

The shared pipeline entry point is implemented in [pipeline_runner.py](/Users/weilynnw/grid-carbon-emulator/src/pipeline_runner.py).

## Data Source

Primary source:
- World Resources Institute Global Power Plant Database

The raw dataset includes plant-level records such as:
- country
- primary fuel
- installed capacity (`capacity_mw`)
- generation fields, where available
- plant metadata and geographic coordinates

The project currently relies on this dataset as the main structural representation of each country's electricity system.

## Carbon-Intensity Definition

For each country, annual average grid carbon intensity is calculated as:

```text
carbon intensity (gCO2/kWh)
= total annual emissions (tonnes CO2) * 1,000,000
  / total annual generation (GWh)
```

Equivalent unit logic:
- `1 GWh = 1,000,000 kWh`
- `1 tonne = 1,000,000 g`

At the plant level:

```text
annual emissions (tonnes CO2)
= generation (GWh) * emission factor (gCO2/kWh) / 1000
```

## Emissions Assumptions

Fuel-specific emissions factors are defined in [assumptions.py](/Users/weilynnw/grid-carbon-emulator/src/assumptions.py).

Current examples include:
- Coal: `820 gCO2/kWh`
- Oil: `650 gCO2/kWh`
- Gas: `490 gCO2/kWh`
- Nuclear: `12 gCO2/kWh`
- Hydro: `24 gCO2/kWh`
- Wind: `11 gCO2/kWh`
- Solar: `48 gCO2/kWh`

Important note:
- These values function as standardized engineering assumptions in the current version of the project.
- The project currently treats them as global defaults rather than country-specific or technology-specific factors.
- Unmapped fuels fall back to `Other = 500 gCO2/kWh`.

## Generation Estimation Logic

Not all plants in the source data have complete generation values. The current fallback hierarchy is:

1. Use the most recent non-estimated generation column if available.
2. Fill remaining gaps with the most recent estimated generation column.
3. If generation is still missing, estimate it from installed capacity using fuel-specific capacity factors.
4. If the fuel is not covered by the explicit table, use a default capacity factor of `0.50`.

Examples of current capacity-factor assumptions:
- Coal: `0.60`
- Gas: `0.50`
- Nuclear: `0.90`
- Hydro: `0.45`
- Wind: `0.35`
- Solar: `0.25`

These assumptions are also defined in [assumptions.py](/Users/weilynnw/grid-carbon-emulator/src/assumptions.py).

## Country-Level Aggregation

After plant-level generation and emissions are estimated, the project aggregates by country to produce:
- total installed capacity
- total annual generation
- total annual emissions
- number of plants
- dominant fuel by installed capacity
- renewable capacity and renewable share
- annual average carbon intensity

Renewable share currently uses the following fuel categories:
- Solar
- Wind
- Hydro
- Geothermal
- Wave and Tidal

## Machine-Learning Emulator

The machine-learning layer is not the source of the carbon-intensity calculation itself. Instead, it acts as a surrogate model that approximates the output of the engineering aggregation pipeline.

This distinction matters:
- the carbon-intensity estimates are first constructed from plant data and assumptions
- the ML model then learns the mapping from country fuel-mix features to the resulting carbon intensity

The current feature set includes:
- fuel-share percentages by country
- total installed capacity
- number of plants
- renewable ratio
- fossil ratio

The current modeling workflow trains:
- Random Forest
- XGBoost

The better-performing model is saved and used in the Streamlit app for instant scenario analysis.

## Scenario Logic

The Streamlit policy simulator currently supports a simplified coal-to-solar transition scenario:
- reduce coal share
- increase solar share by the same amount
- update renewable and fossil ratios
- use the trained emulator to estimate the new carbon intensity

This is best interpreted as a rapid directional scenario tool, not a full capacity-expansion or dispatch model.

## Current Limitations

The current project has several important limitations:

- It estimates annual average, not hourly or marginal, grid emissions.
- It does not explicitly model imports, exports, or cross-border electricity trade.
- It uses global default emissions factors rather than country-specific fuel quality or plant-technology detail.
- It uses simplified capacity-factor assumptions to fill missing generation.
- It does not yet differentiate direct operational emissions from full lifecycle emissions in a configurable way.
- It assumes the source database is a sufficiently representative proxy for national generation structure.
- It does not yet include a formal external validation module against benchmark datasets such as Ember, IEA, or Electricity Maps.

## Appropriate Interpretation

This project should currently be interpreted as:

- a country-level power-system approximation
- a transparent engineering-plus-ML workflow
- a fast scenario exploration tool

It should not yet be presented as:

- an official national inventory
- a dispatch-grade power-system model
- a real-time carbon-intensity estimator

## Validation Roadmap

The most important next methodological upgrade is external validation.

A stronger next version should compare project outputs against benchmark country-level grid intensity data and report:
- correlation
- MAE / RMSE / MAPE
- directional bias
- outlier countries
- case-study explanations for mismatches

Good candidate benchmark sources include:
- Ember
- IEA
- Our World in Data
- Electricity Maps
- official national electricity statistics where available

## Reproducibility

The pipeline currently generates these main artifacts:
- `data/processed/plants_with_emissions.csv`
- `data/processed/country_carbon_intensity.csv`
- `data/processed/ml_features.csv`
- `data/processed/ml_targets.csv`
- `data/processed/carbon_emulator_model.pkl`

The end-to-end generation flow is orchestrated through [pipeline_runner.py](/Users/weilynnw/grid-carbon-emulator/src/pipeline_runner.py), while the assumptions used by the calculations are centralized in [assumptions.py](/Users/weilynnw/grid-carbon-emulator/src/assumptions.py).

## Positioning

From a professional standpoint, the strongest way to frame this project is:

- a country-level grid carbon-intensity modeling and scenario-analysis tool
- built from plant-level global infrastructure data
- using transparent engineering assumptions and a machine-learning surrogate model for rapid simulation

That framing is more accurate and more credible than presenting the project as a generic AI prediction app.
