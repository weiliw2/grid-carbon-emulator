"""
Grid Carbon-Intensity Emulator - Phase 2 (FIXED)
Carbon Intensity Calculations with better data handling
"""

import pandas as pd
import numpy as np

# Emission Factors (gCO2/kWh) - Standard values from IPCC and EPA
EMISSION_FACTORS = {
    'Coal': 820,
    'Oil': 650,
    'Gas': 490,
    'Petcoke': 900,
    'Cogeneration': 400,
    'Biomass': 230,
    'Nuclear': 12,
    'Hydro': 24,
    'Wind': 11,
    'Solar': 48,
    'Geothermal': 38,
    'Wave and Tidal': 15,
    'Storage': 0,
    'Other': 500,
    'Waste': 700,
}

def load_power_plant_data():
    """Load the data from Phase 1"""
    print("📂 Loading Global Power Plant Database...")
    df = pd.read_csv('data/raw/power_plants_global.csv', low_memory=False)
    print(f"✅ Loaded {len(df):,} power plants\n")
    return df

def map_emission_factors(df):
    """Map emission factors to each fuel type"""
    
    print("🔬 Mapping emission factors to fuel types...")
    
    df['emission_factor_gco2_kwh'] = df['primary_fuel'].map(EMISSION_FACTORS)
    
    unmapped = df[df['emission_factor_gco2_kwh'].isna()]['primary_fuel'].unique()
    if len(unmapped) > 0:
        print(f"\n⚠️  Unmapped fuel types: {list(unmapped)}")
        print(f"   Setting these to 'Other' (500 gCO2/kWh)")
        df['emission_factor_gco2_kwh'].fillna(EMISSION_FACTORS['Other'], inplace=True)
    
    print(f"✅ Emission factors mapped\n")
    return df

def calculate_plant_emissions(df):
    """Calculate annual emissions for each plant"""
    
    print("⚡ Calculating plant-level emissions...")
    
    # Find all generation columns
    gen_cols = [col for col in df.columns if 'generation_gwh' in col.lower() 
                and 'note' not in col.lower() and 'source' not in col.lower()]
    
    print(f"   Found {len(gen_cols)} generation columns")
    
    # Strategy: Use the most recent year with data for each plant
    # Combine actual and estimated generation columns
    actual_cols = [col for col in gen_cols if 'estimated' not in col.lower()]
    estimated_cols = [col for col in gen_cols if 'estimated' in col.lower()]
    
    print(f"   - Actual generation columns: {len(actual_cols)}")
    print(f"   - Estimated generation columns: {len(estimated_cols)}")
    
    # First, try to use actual generation (prefer most recent year)
    if actual_cols:
        most_recent_actual = sorted(actual_cols)[-1]
        df['generation_gwh'] = df[most_recent_actual]
        print(f"   Using actual generation from: {most_recent_actual}")
    
    # Fill missing values with estimated generation
    if estimated_cols:
        most_recent_estimated = sorted(estimated_cols)[-1]
        missing_mask = df['generation_gwh'].isna()
        df.loc[missing_mask, 'generation_gwh'] = df.loc[missing_mask, most_recent_estimated]
        print(f"   Filled missing with estimates from: {most_recent_estimated}")
    
    # For plants still missing generation, estimate from capacity
    # Use capacity factor assumptions by fuel type
    capacity_factors = {
        'Coal': 0.60, 'Oil': 0.40, 'Gas': 0.50, 'Nuclear': 0.90,
        'Hydro': 0.45, 'Wind': 0.35, 'Solar': 0.25, 'Geothermal': 0.75,
        'Biomass': 0.50, 'Other': 0.50
    }
    
    still_missing = df['generation_gwh'].isna()
    for fuel, cf in capacity_factors.items():
        mask = still_missing & (df['primary_fuel'] == fuel)
        df.loc[mask, 'generation_gwh'] = df.loc[mask, 'capacity_mw'] * cf * 8760 / 1000
    
    # Final fallback: use 0.5 capacity factor for any remaining
    still_missing = df['generation_gwh'].isna()
    df.loc[still_missing, 'generation_gwh'] = df.loc[still_missing, 'capacity_mw'] * 0.5 * 8760 / 1000
    
    plants_with_data = (df['generation_gwh'] > 0).sum()
    print(f"\n   ✅ {plants_with_data:,} plants now have generation data")
    
    # Calculate emissions (GWh * 1M kWh/GWh * gCO2/kWh / 1B = tonnes CO2)
    df['annual_emissions_tonnes'] = (
        df['generation_gwh'] * 1_000_000 * df['emission_factor_gco2_kwh'] / 1_000_000_000
    )
    
    df['annual_emissions_tonnes'] = df['annual_emissions_tonnes'].clip(lower=0)
    
    total_emissions = df['annual_emissions_tonnes'].sum()
    print(f"\n🌍 Global total emissions: {total_emissions:,.0f} tonnes CO2/year")
    print(f"   That's {total_emissions/1_000_000_000:.2f} gigatonnes CO2/year")
    
    return df

def calculate_country_carbon_intensity(df):
    """Aggregate to country-level carbon intensity"""
    
    print("\n🌐 Calculating country-level carbon intensity...")
    
    # Aggregate by country
    country_data = df.groupby('country').agg({
        'capacity_mw': 'sum',
        'generation_gwh': 'sum',
        'annual_emissions_tonnes': 'sum',
        'name': 'count'
    }).reset_index()
    
    country_data.columns = ['country', 'total_capacity_mw', 'total_generation_gwh', 
                            'total_emissions_tonnes', 'num_plants']
    
    # Calculate carbon intensity (gCO2/kWh)
    # Only for countries with meaningful generation (>1 GWh)
    valid_generation = country_data['total_generation_gwh'] > 1
    
    country_data['carbon_intensity_gco2_kwh'] = np.nan
    country_data.loc[valid_generation, 'carbon_intensity_gco2_kwh'] = (
        country_data.loc[valid_generation, 'total_emissions_tonnes'] * 1_000_000_000 / 
        (country_data.loc[valid_generation, 'total_generation_gwh'] * 1_000_000)
    )
    
    # Calculate renewable percentage
    renewables = ['Solar', 'Wind', 'Hydro', 'Geothermal', 'Wave and Tidal']
    renewable_capacity = df[df['primary_fuel'].isin(renewables)].groupby('country')['capacity_mw'].sum()
    country_data['renewable_capacity_mw'] = country_data['country'].map(renewable_capacity).fillna(0)
    country_data['renewable_percentage'] = (
        country_data['renewable_capacity_mw'] / country_data['total_capacity_mw'] * 100
    )
    
    # Get dominant fuel type
    dominant_fuel = df.groupby('country').apply(
        lambda x: x.groupby('primary_fuel')['capacity_mw'].sum().idxmax()
    )
    country_data['dominant_fuel'] = country_data['country'].map(dominant_fuel)
    
    # Sort by carbon intensity
    country_data = country_data.sort_values('carbon_intensity_gco2_kwh', ascending=False)
    
    valid_countries = country_data['carbon_intensity_gco2_kwh'].notna().sum()
    print(f"✅ Processed {len(country_data)} countries")
    print(f"   {valid_countries} countries have valid carbon intensity data\n")
    
    return country_data

def show_insights(country_data):
    """Display key insights"""
    
    print("="*70)
    print("KEY INSIGHTS")
    print("="*70)
    
    # Filter to valid data
    valid_data = country_data[country_data['carbon_intensity_gco2_kwh'].notna()].copy()
    
    print(f"\n📊 Countries with complete data: {len(valid_data)}/{len(country_data)}")
    
    if len(valid_data) < 10:
        print("\n⚠️  Limited data available. Showing what we have:")
        print(valid_data[['country', 'carbon_intensity_gco2_kwh', 'renewable_percentage', 'dominant_fuel']])
        return
    
    print("\n🏆 TOP 10 CLEANEST GRIDS (Lowest Carbon Intensity):")
    cleanest = valid_data.nsmallest(10, 'carbon_intensity_gco2_kwh')
    for i, row in enumerate(cleanest.itertuples(), 1):
        print(f"   {i:2d}. {row.country:20s}: {row.carbon_intensity_gco2_kwh:>6.0f} gCO2/kWh "
              f"({row.renewable_percentage:>5.1f}% renewable, {row.dominant_fuel})")
    
    print("\n🚨 TOP 10 DIRTIEST GRIDS (Highest Carbon Intensity):")
    dirtiest = valid_data.nlargest(10, 'carbon_intensity_gco2_kwh')
    for i, row in enumerate(dirtiest.itertuples(), 1):
        print(f"   {i:2d}. {row.country:20s}: {row.carbon_intensity_gco2_kwh:>6.0f} gCO2/kWh "
              f"({row.renewable_percentage:>5.1f}% renewable, {row.dominant_fuel})")
    
    print("\n🌍 MAJOR ECONOMIES:")
    major = ['USA', 'CHN', 'IND', 'DEU', 'GBR', 'FRA', 'JPN', 'BRA']
    major_data = valid_data[valid_data['country'].isin(major)]
    for row in major_data.itertuples():
        print(f"   {row.country:5s}: {row.carbon_intensity_gco2_kwh:>6.0f} gCO2/kWh "
              f"({row.renewable_percentage:>5.1f}% renewable, {row.dominant_fuel})")
    
    print("\n💡 Global Averages:")
    avg_intensity = (valid_data['total_emissions_tonnes'].sum() * 1_000_000_000 / 
                     (valid_data['total_generation_gwh'].sum() * 1_000_000))
    avg_renewable = (valid_data['renewable_capacity_mw'].sum() / 
                     valid_data['total_capacity_mw'].sum() * 100)
    print(f"   Average carbon intensity: {avg_intensity:.0f} gCO2/kWh")
    print(f"   Global renewable percentage: {avg_renewable:.1f}%")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("GRID CARBON-INTENSITY EMULATOR")
    print("Phase 2: Carbon Intensity Calculations (FIXED)")
    print("="*70 + "\n")
    
    df = load_power_plant_data()
    df = map_emission_factors(df)
    df = calculate_plant_emissions(df)
    country_data = calculate_country_carbon_intensity(df)
    show_insights(country_data)
    
    print("\n💾 Saving processed data...")
    df.to_csv('data/processed/plants_with_emissions.csv', index=False)
    country_data.to_csv('data/processed/country_carbon_intensity.csv', index=False)
    print("   ✅ Saved to 'data/processed/plants_with_emissions.csv'")
    print("   ✅ Saved to 'data/processed/country_carbon_intensity.csv'")
    
    print("\n" + "="*70)
    print("✅ PHASE 2 COMPLETE!")
    print("="*70)
    print("\n📋 Next Steps:")
    print("   1. Commit: git add . && git commit -m 'Phase 2: Fixed carbon calculations'")
    print("   2. Phase 3: Build the ML emulator")
    print("="*70 + "\n")