"""
Simple test to see if Streamlit is working
"""

import streamlit as st

st.title("🔧 Streamlit Test")
st.write("If you can see this, Streamlit is working!")

st.header("Testing data loading...")

try:
    import pandas as pd
    st.success("✅ Pandas loaded successfully")
    
    # Try to load country data
    country_data = pd.read_csv('data/processed/country_carbon_intensity.csv')
    st.success(f"✅ Country data loaded: {len(country_data)} countries")
    st.dataframe(country_data.head())
    
except Exception as e:
    st.error(f"❌ Error: {e}")
    st.write("Full error:")
    st.write(str(e))

try:
    import plotly.express as px
    st.success("✅ Plotly loaded successfully")
except Exception as e:
    st.error(f"❌ Plotly error: {e}")

try:
    import joblib
    model = joblib.load('data/processed/carbon_emulator_model.pkl')
    st.success("✅ Model loaded successfully")
except Exception as e:
    st.error(f"❌ Model loading error: {e}")

st.write("---")
st.write("If you see green checkmarks above, everything is working!")
