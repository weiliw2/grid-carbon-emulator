"""Utilities for mapping ISO-3 country codes to display names."""

from __future__ import annotations

import pandas as pd

try:
    import pycountry
except ImportError:  # pragma: no cover - optional dependency fallback
    pycountry = None


COUNTRY_NAME_OVERRIDES = {
    "KOS": "Kosovo",
}


def code_to_country_name(country_code: str) -> str:
    """Convert an ISO-3 country code to a human-readable country name."""
    if not country_code:
        return ""

    country_code = str(country_code).upper()
    if country_code in COUNTRY_NAME_OVERRIDES:
        return COUNTRY_NAME_OVERRIDES[country_code]

    if pycountry is not None:
        country = pycountry.countries.get(alpha_3=country_code)
        if country is not None:
            return country.name

    return country_code


def add_country_names(
    df: pd.DataFrame,
    code_col: str = "country",
    name_col: str = "country_name",
) -> pd.DataFrame:
    """Return a copy of a DataFrame with a country-name display column."""
    enriched = df.copy()
    enriched[name_col] = enriched[code_col].map(code_to_country_name)
    return enriched
