"""Shared modeling assumptions for emissions and fuel categories."""

from __future__ import annotations

EMISSION_FACTORS_GCO2_PER_KWH = {
    "Coal": 820,
    "Oil": 650,
    "Gas": 490,
    "Petcoke": 900,
    "Cogeneration": 400,
    "Biomass": 230,
    "Nuclear": 12,
    "Hydro": 24,
    "Wind": 11,
    "Solar": 48,
    "Geothermal": 38,
    "Wave and Tidal": 15,
    "Storage": 0,
    "Other": 500,
    "Waste": 700,
}

DEFAULT_EMISSION_FACTOR_FUEL = "Other"

CAPACITY_FACTORS = {
    "Coal": 0.60,
    "Oil": 0.40,
    "Gas": 0.50,
    "Nuclear": 0.90,
    "Hydro": 0.45,
    "Wind": 0.35,
    "Solar": 0.25,
    "Geothermal": 0.75,
    "Biomass": 0.50,
    "Other": 0.50,
}

DEFAULT_CAPACITY_FACTOR = 0.50

RENEWABLE_FUELS = [
    "Solar",
    "Wind",
    "Hydro",
    "Geothermal",
    "Wave and Tidal",
]

FOSSIL_FUELS = [
    "Coal",
    "Oil",
    "Gas",
]

MAJOR_ECONOMY_COUNTRIES = [
    "USA",
    "CHN",
    "IND",
    "DEU",
    "GBR",
    "FRA",
    "JPN",
    "BRA",
]
