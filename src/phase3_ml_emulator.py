"""
Grid Carbon-Intensity Emulator - Phase 3
Machine Learning Emulator Training
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb
import joblib
import matplotlib.pyplot as plt

from assumptions import FOSSIL_FUELS, RENEWABLE_FUELS

def load_processed_data():
    """Load the processed data from Phase 2"""
    print("📂 Loading processed data from Phase 2...")
    
    plants_df = pd.read_csv('data/processed/plants_with_emissions.csv')
    country_df = pd.read_csv('data/processed/country_carbon_intensity.csv')
    
    print(f"✅ Loaded {len(plants_df):,} plants")
    print(f"✅ Loaded {len(country_df)} countries\n")
    
    return plants_df, country_df

def create_fuel_mix_features(plants_df):
    """Create detailed fuel mix features for each country"""
    
    print("🔧 Engineering features from fuel mix...")
    
    # Calculate capacity by fuel type for each country
    fuel_pivot = plants_df.pivot_table(
        index='country',
        columns='primary_fuel',
        values='capacity_mw',
        aggfunc='sum',
        fill_value=0
    )
    
    # Calculate percentages
    total_capacity = fuel_pivot.sum(axis=1)
    fuel_pct = fuel_pivot.div(total_capacity, axis=0) * 100
    fuel_pct.columns = [f'{col}_pct' for col in fuel_pct.columns]
    
    # Add total capacity
    fuel_pct['total_capacity_mw'] = total_capacity
    
    # Add number of plants
    plant_counts = plants_df.groupby('country').size()
    fuel_pct['num_plants'] = plant_counts
    
    # Calculate renewable ratio
    renewable_cols = [f'{fuel}_pct' for fuel in RENEWABLE_FUELS if f'{fuel}_pct' in fuel_pct.columns]
    fuel_pct['renewable_ratio'] = fuel_pct[renewable_cols].sum(axis=1) / 100
    
    # Calculate fossil fuel ratio
    fossil_cols = [f'{fuel}_pct' for fuel in FOSSIL_FUELS if f'{fuel}_pct' in fuel_pct.columns]
    fuel_pct['fossil_ratio'] = fuel_pct[fossil_cols].sum(axis=1) / 100
    
    print(f"✅ Created {len(fuel_pct.columns)} features for {len(fuel_pct)} countries\n")
    
    return fuel_pct

def prepare_ml_dataset(fuel_features, country_data):
    """Prepare the dataset for machine learning"""
    
    print("🎯 Preparing ML dataset...")
    
    # Merge features with target (carbon intensity)
    ml_data = fuel_features.join(
        country_data.set_index('country')[['carbon_intensity_gco2_kwh']], 
        how='inner'
    )
    
    print(f"   Initial dataset: {len(ml_data)} countries")
    
    # Check for missing or invalid values
    print(f"   Countries with valid carbon intensity: {ml_data['carbon_intensity_gco2_kwh'].notna().sum()}")
    print(f"   Carbon intensity range: {ml_data['carbon_intensity_gco2_kwh'].min():.0f} - {ml_data['carbon_intensity_gco2_kwh'].max():.0f} gCO2/kWh")
    
    # Remove only clearly invalid data (NaN, negative, or extremely high outliers)
    ml_data = ml_data[
        (ml_data['carbon_intensity_gco2_kwh'].notna()) & 
        (ml_data['carbon_intensity_gco2_kwh'] > 0) & 
        (ml_data['carbon_intensity_gco2_kwh'] < 5000) &  # More lenient outlier threshold
        (np.isfinite(ml_data['carbon_intensity_gco2_kwh']))
    ]
    
    # Fill any remaining NaN values in features with 0
    ml_data = ml_data.fillna(0)
    
    print(f"✅ Final dataset: {len(ml_data)} countries with valid data\n")
    
    if len(ml_data) < 10:
        print("⚠️  WARNING: Very few countries in dataset. This might indicate a data issue.")
        print("   Showing sample of the data:")
        print(ml_data[['carbon_intensity_gco2_kwh']].head(10))
    
    # Separate features and target
    X = ml_data.drop('carbon_intensity_gco2_kwh', axis=1)
    y = ml_data['carbon_intensity_gco2_kwh']
    
    print(f"📊 Features: {X.shape[1]} columns")
    print(f"🎯 Target: Carbon Intensity (gCO2/kWh)")
    print(f"   Range: {y.min():.0f} - {y.max():.0f} gCO2/kWh")
    print(f"   Mean: {y.mean():.0f} gCO2/kWh\n")
    
    return X, y, ml_data

def train_models(X, y):
    """Train multiple models and compare performance"""
    
    print("🤖 Training machine learning models...")
    print("="*70)
    
    # Check if we have enough data
    if len(X) < 10:
        print(f"⚠️  Only {len(X)} countries available - need at least 10 for reliable training")
        print("    This might be due to data quality issues in Phase 2")
        print("\n💡 Suggestion: Check data/processed/country_carbon_intensity.csv")
        return None, None, None, None, None
    
    # Adjust test size based on dataset size
    test_size = 0.2 if len(X) >= 20 else 0.15
    if len(X) < 15:
        test_size = max(2, int(len(X) * 0.15))  # At least 2 samples in test
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    print(f"📊 Training set: {len(X_train)} countries")
    print(f"📊 Test set: {len(X_test)} countries\n")
    
    models = {}
    results = {}
    
    # Model 1: Random Forest
    print("🌲 Training Random Forest...")
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    
    rf_pred = rf_model.predict(X_test)
    rf_mae = mean_absolute_error(y_test, rf_pred)
    rf_r2 = r2_score(y_test, rf_pred)
    
    models['random_forest'] = rf_model
    results['Random Forest'] = {'MAE': rf_mae, 'R2': rf_r2}
    
    print(f"   ✅ MAE: {rf_mae:.2f} gCO2/kWh")
    print(f"   ✅ R² Score: {rf_r2:.3f}\n")
    
    # Model 2: XGBoost
    print("⚡ Training XGBoost...")
    xgb_model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1
    )
    xgb_model.fit(X_train, y_train)
    
    xgb_pred = xgb_model.predict(X_test)
    xgb_mae = mean_absolute_error(y_test, xgb_pred)
    xgb_r2 = r2_score(y_test, xgb_pred)
    
    models['xgboost'] = xgb_model
    results['XGBoost'] = {'MAE': xgb_mae, 'R2': xgb_r2}
    
    print(f"   ✅ MAE: {xgb_mae:.2f} gCO2/kWh")
    print(f"   ✅ R² Score: {xgb_r2:.3f}\n")
    
    # Choose best model
    best_model_name = 'XGBoost' if xgb_r2 > rf_r2 else 'Random Forest'
    best_model = models['xgboost'] if xgb_r2 > rf_r2 else models['random_forest']
    
    print("="*70)
    print(f"🏆 Best Model: {best_model_name}")
    print(f"   MAE: {results[best_model_name]['MAE']:.2f} gCO2/kWh")
    print(f"   R² Score: {results[best_model_name]['R2']:.3f}")
    print("="*70 + "\n")
    
    return best_model, best_model_name, X_test, y_test, results

def analyze_feature_importance(model, model_name, X):
    """Analyze which features matter most"""
    
    print("🔍 Feature Importance Analysis...")
    
    if hasattr(model, 'feature_importances_'):
        importances = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n🌟 Top 10 Most Important Features ({model_name}):")
        for i, row in importances.head(10).iterrows():
            print(f"   {row['feature']:30s}: {row['importance']:.4f}")
        
        return importances
    else:
        print("   Model doesn't support feature importance\n")
        return None

def test_scenario_predictions(model, X_full, ml_data):
    """Test the emulator with real-world scenarios"""
    
    print("\n🧪 Testing Scenario Predictions...")
    print("="*70)
    
    test_countries = ['USA', 'CHN', 'IND', 'DEU', 'FRA', 'BRA']
    
    for country in test_countries:
        if country in X_full.index:
            # Get features only (no target column)
            features = X_full.loc[[country]]
            prediction = model.predict(features)[0]
            actual = ml_data.loc[country, 'carbon_intensity_gco2_kwh']
            error = abs(prediction - actual)
            
            print(f"\n{country}:")
            print(f"   Predicted: {prediction:.0f} gCO2/kWh")
            print(f"   Actual:    {actual:.0f} gCO2/kWh")
            print(f"   Error:     {error:.0f} gCO2/kWh ({error/actual*100:.1f}%)")
        else:
            print(f"\n{country}: Not in dataset")

def simulate_policy_change(model, X, country_code='USA'):
    """Simulate 'What if?' scenarios"""
    
    print("\n" + "="*70)
    print("🔮 POLICY SIMULATION: What if scenarios?")
    print("="*70)
    
    if country_code not in X.index:
        print(f"   Country {country_code} not found in dataset")
        return
    
    # Get baseline
    baseline = X.loc[[country_code]].copy()
    baseline_prediction = model.predict(baseline)[0]
    
    print(f"\n📍 Country: {country_code}")
    print(f"   Current carbon intensity: {baseline_prediction:.0f} gCO2/kWh")
    
    # Scenario 1: Replace 10% of coal with solar
    if 'Coal_pct' in baseline.columns and 'Solar_pct' in baseline.columns:
        scenario1 = baseline.copy()
        coal_reduction = min(10, scenario1['Coal_pct'].values[0])
        scenario1['Coal_pct'] -= coal_reduction
        scenario1['Solar_pct'] += coal_reduction
        scenario1['renewable_ratio'] = scenario1['renewable_ratio'] + (coal_reduction / 100)
        scenario1['fossil_ratio'] = scenario1['fossil_ratio'] - (coal_reduction / 100)
        
        s1_prediction = model.predict(scenario1)[0]
        s1_reduction = baseline_prediction - s1_prediction
        
        print(f"\n💡 Scenario 1: Replace 10% coal with solar")
        print(f"   New carbon intensity: {s1_prediction:.0f} gCO2/kWh")
        print(f"   Reduction: {s1_reduction:.0f} gCO2/kWh ({s1_reduction/baseline_prediction*100:.1f}%)")
    
    # Scenario 2: Replace 20% of coal with solar
    if 'Coal_pct' in baseline.columns and 'Solar_pct' in baseline.columns:
        scenario2 = baseline.copy()
        coal_reduction = min(20, scenario2['Coal_pct'].values[0])
        scenario2['Coal_pct'] -= coal_reduction
        scenario2['Solar_pct'] += coal_reduction
        scenario2['renewable_ratio'] = scenario2['renewable_ratio'] + (coal_reduction / 100)
        scenario2['fossil_ratio'] = scenario2['fossil_ratio'] - (coal_reduction / 100)
        
        s2_prediction = model.predict(scenario2)[0]
        s2_reduction = baseline_prediction - s2_prediction
        
        print(f"\n💡 Scenario 2: Replace 20% coal with solar")
        print(f"   New carbon intensity: {s2_prediction:.0f} gCO2/kWh")
        print(f"   Reduction: {s2_reduction:.0f} gCO2/kWh ({s2_reduction/baseline_prediction*100:.1f}%)")
    
    # Scenario 3: Double renewable capacity
    scenario3 = baseline.copy()
    renewable_cols = [col for col in baseline.columns if any(r in col for r in ['Solar', 'Wind', 'Hydro'])]
    for col in renewable_cols:
        original = scenario3[col].values[0]
        scenario3[col] = original * 2
    
    # Normalize percentages
    total = scenario3[[col for col in baseline.columns if '_pct' in col]].sum(axis=1).values[0]
    for col in [c for c in baseline.columns if '_pct' in c]:
        scenario3[col] = scenario3[col] / total * 100
    
    s3_prediction = model.predict(scenario3)[0]
    s3_reduction = baseline_prediction - s3_prediction
    
    print(f"\n💡 Scenario 3: Double all renewable capacity")
    print(f"   New carbon intensity: {s3_prediction:.0f} gCO2/kWh")
    print(f"   Reduction: {s3_reduction:.0f} gCO2/kWh ({s3_reduction/baseline_prediction*100:.1f}%)")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("GRID CARBON-INTENSITY EMULATOR")
    print("Phase 3: Machine Learning Emulator Training")
    print("="*70 + "\n")
    
    # Load data
    plants_df, country_df = load_processed_data()
    
    # Create features
    fuel_features = create_fuel_mix_features(plants_df)
    
    # Prepare ML dataset
    X, y, ml_data = prepare_ml_dataset(fuel_features, country_df)
    
    # Train models
    model_result = train_models(X, y)
    
    # Check if training was successful
    if model_result[0] is None:
        print("\n❌ Model training failed - insufficient data")
        print("\n🔍 Debugging suggestions:")
        print("   1. Check: data/processed/country_carbon_intensity.csv")
        print("   2. Look for NaN or infinite values")
        print("   3. Re-run Phase 2 if needed")
    else:
        best_model, model_name, X_test, y_test, results = model_result
        
        # Feature importance
        importances = analyze_feature_importance(best_model, model_name, X)
        
        # Test predictions (use full X, not X_test)
        test_scenario_predictions(best_model, X, ml_data)
        
        # Policy simulation
        simulate_policy_change(best_model, X, 'USA')
        simulate_policy_change(best_model, X, 'IND')
        simulate_policy_change(best_model, X, 'CHN')
        
        # Save model and data
        print("\n💾 Saving model and processed data...")
        joblib.dump(best_model, 'data/processed/carbon_emulator_model.pkl')
        X.to_csv('data/processed/ml_features.csv')
        y.to_csv('data/processed/ml_targets.csv')
        if importances is not None:
            importances.to_csv('data/processed/feature_importances.csv', index=False)
        
        print("   ✅ Model saved to 'data/processed/carbon_emulator_model.pkl'")
        print("   ✅ Features saved to 'data/processed/ml_features.csv'")
        print("   ✅ Targets saved to 'data/processed/ml_targets.csv'")
        
        print("\n" + "="*70)
        print("✅ PHASE 3 COMPLETE!")
        print("="*70)
        print(f"\n🎉 Your AI emulator is trained and ready!")
        print(f"   Model: {model_name}")
        print(f"   Accuracy: R² = {results[model_name]['R2']:.3f}")
        print(f"   Error: MAE = {results[model_name]['MAE']:.0f} gCO2/kWh")
        print("\n📋 Next Steps:")
        print("   1. Commit: git add . && git commit -m 'Phase 3: ML emulator trained'")
        print("   2. Phase 4: Build interactive Streamlit dashboard")
        print("   3. Test different policy scenarios")
        print("="*70 + "\n")
