# Validation Workflow

This project now supports a formal benchmark-validation workflow for country-level grid carbon intensity.

## Expected Benchmark File

Place a benchmark CSV at:

`data/benchmarks/country_carbon_intensity_benchmark.csv`

Required columns:
- `country`
- `benchmark_carbon_intensity_gco2_kwh`

Optional but recommended columns:
- `source`
- `year`
- `notes`

A template is provided at [country_carbon_intensity_benchmark_template.csv](/Users/weilynnw/grid-carbon-emulator/data/benchmarks/country_carbon_intensity_benchmark_template.csv).

## What the Validation Module Produces

When a benchmark file is present, the validation workflow:
- aligns countries by ISO-3 code
- compares model output against benchmark intensity values
- calculates summary metrics
- writes comparison artifacts to `data/validation/`

Current outputs:
- `benchmark_comparison.csv`
- `benchmark_metrics.csv`
- `benchmark_metrics.json`

## Current Metrics

The validation module reports:
- number of countries compared
- MAE
- RMSE
- MAPE
- mean bias
- Pearson correlation

## Suggested Benchmark Sources

Good next benchmark candidates include:
- Ember
- IEA
- Electricity Maps
- Our World in Data
- official national electricity statistics

## Notes on Interpretation

Validation should be interpreted with care because benchmark datasets may differ in:
- year
- system boundary
- treatment of imports/exports
- operational versus lifecycle emissions
- methodology for renewable and thermal generation accounting

That means benchmark gaps are useful signals, but not every difference is necessarily a model error.
