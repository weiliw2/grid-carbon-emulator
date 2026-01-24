"""
Debug script to check what went wrong in Phase 2
"""

import pandas as pd

print("🔍 Debugging Phase 2 Data...\n")
print("="*70)

# Check raw data
print("\n1. CHECKING RAW DATA:")
raw_df = pd.read_csv('data/raw/power_plants_global.csv')
print(f"   Total plants: {len(raw_df):,}")
print(f"   Countries: {raw_df['country'].nunique()}")
print(f"   Sample countries: {list(raw_df['country'].unique()[:10])}")

# Check if generation columns exist
gen_cols = [col for col in raw_df.columns if 'generation' in col.lower()]
print(f"\n   Generation columns found: {gen_cols}")

# Check processed plants data
print("\n2. CHECKING PROCESSED PLANTS DATA:")
try:
    plants_df = pd.read_csv('data/processed/plants_with_emissions.csv')
    print(f"   Total plants: {len(plants_df):,}")
    print(f"   Countries: {plants_df['country'].nunique()}")
    
    # Check emissions column
    if 'annual_emissions_tonnes' in plants_df.columns:
        valid_emissions = (plants_df['annual_emissions_tonnes'] > 0).sum()
        print(f"   Plants with valid emissions: {valid_emissions:,}")
        print(f"   Emissions range: {plants_df['annual_emissions_tonnes'].min():.2f} - {plants_df['annual_emissions_tonnes'].max():.2f}")
    else:
        print("   ❌ Missing 'annual_emissions_tonnes' column!")
        
except Exception as e:
    print(f"   ❌ Error reading plants data: {e}")

# Check country data
print("\n3. CHECKING COUNTRY CARBON INTENSITY DATA:")
try:
    country_df = pd.read_csv('data/processed/country_carbon_intensity.csv')
    print(f"   Total countries: {len(country_df)}")
    print(f"\n   First few rows:")
    print(country_df.head(10))
    
    print(f"\n   Carbon intensity stats:")
    print(f"   - Valid values: {country_df['carbon_intensity_gco2_kwh'].notna().sum()}")
    print(f"   - NaN values: {country_df['carbon_intensity_gco2_kwh'].isna().sum()}")
    print(f"   - Infinite values: {(~np.isfinite(country_df['carbon_intensity_gco2_kwh'])).sum()}")
    print(f"   - Range: {country_df['carbon_intensity_gco2_kwh'].min():.2f} - {country_df['carbon_intensity_gco2_kwh'].max():.2f}")
    
    # Check for problematic values
    problematic = country_df[
        (country_df['carbon_intensity_gco2_kwh'].isna()) | 
        (~np.isfinite(country_df['carbon_intensity_gco2_kwh'])) |
        (country_df['carbon_intensity_gco2_kwh'] <= 0)
    ]
    
    if len(problematic) > 0:
        print(f"\n   ⚠️  Found {len(problematic)} countries with problematic data:")
        print(problematic[['country', 'carbon_intensity_gco2_kwh', 'total_generation_gwh']].head(20))
        
except Exception as e:
    print(f"   ❌ Error reading country data: {e}")

print("\n" + "="*70)
print("\n💡 DIAGNOSIS:")
print("If you see very few countries with valid data, the issue is likely:")
print("1. Missing generation data in the raw dataset")
print("2. Division by zero when calculating carbon intensity")
print("3. All generation values are NaN or zero")
print("\nLet's re-run Phase 2 with a fix!")
