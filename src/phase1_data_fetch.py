"""
Grid Carbon-Intensity Emulator - Phase 1
Data Fetching and Exploration
"""

import pandas as pd
import requests
from io import StringIO
import os

def fetch_power_plant_data():
    """Download the Global Power Plant Database"""
    
    print("🌍 Fetching Global Power Plant Database...")
    
    # CSV URL from WRI
    csv_url = "http://datasets.wri.org/dataset/540dcf46-f287-47ac-985d-269b04bea4c6/resource/c240ed2e-1190-4d7e-b1da-c66b72e08858/download/global_power_plant_database_v_1_3.csv"
    
    try:
        # Download the data
        response = requests.get(csv_url, timeout=60)
        response.raise_for_status()
        
        # Load into pandas
        df = pd.read_csv(StringIO(response.text))
        
        print(f"✅ Success! Loaded {len(df):,} power plants")
        print(f"📊 Columns: {list(df.columns)}")
        
        # Save to data/raw
        output_path = 'data/raw/power_plants_global.csv'
        df.to_csv(output_path, index=False)
        print(f"\n💾 Saved to '{output_path}'")
        
        return df
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTip: You can manually download from:")
        print("https://datasets.wri.org/dataset/globalpowerplantdatabase")
        return None

def explore_data(df):
    """Quick exploration of the dataset"""
    
    if df is None:
        return
    
    print("\n" + "="*60)
    print("DATASET OVERVIEW")
    print("="*60)
    
    # Basic stats
    print(f"\n🌐 Countries: {df['country'].nunique()}")
    print(f"⚡ Fuel types: {df['primary_fuel'].nunique()}")
    print(f"🏭 Total capacity: {df['capacity_mw'].sum():,.0f} MW")
    
    # Top fuel types globally
    print("\n🔥 Top Fuel Types by Capacity:")
    fuel_capacity = df.groupby('primary_fuel')['capacity_mw'].sum().sort_values(ascending=False).head(10)
    for fuel, capacity in fuel_capacity.items():
        print(f"  {fuel}: {capacity:,.0f} MW")
    
    # USA example
    print("\n" + "="*60)
    print("USA EXAMPLE")
    print("="*60)
    
    usa_plants = df[df['country'] == 'USA']
    print(f"\n🇺🇸 USA has {len(usa_plants):,} power plants")
    
    fuel_summary = usa_plants.groupby('primary_fuel').agg({
        'capacity_mw': 'sum',
        'name': 'count'
    }).round(2)
    fuel_summary.columns = ['Total Capacity (MW)', 'Number of Plants']
    print("\n⚡ USA Fuel Mix:")
    print(fuel_summary.sort_values('Total Capacity (MW)', ascending=False).head(10))

if __name__ == "__main__":
    # Fetch data
    df = fetch_power_plant_data()
    
    # Explore it
    explore_data(df)
    
    print("\n" + "="*60)
    print("✅ Phase 1 Complete! Next: Carbon intensity calculations")
    print("="*60)
