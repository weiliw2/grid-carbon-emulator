"""
Grid Carbon-Intensity Emulator - Streamlit Dashboard
Interactive web application to explore carbon intensity predictions
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib

# Page configuration
st.set_page_config(
    page_title="Grid Carbon Emulator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data and model
@st.cache_data
def load_data():
    """Load processed data"""
    country_data = pd.read_csv('data/processed/country_carbon_intensity.csv')
    ml_features = pd.read_csv('data/processed/ml_features.csv', index_col=0)
    ml_targets = pd.read_csv('data/processed/ml_targets.csv', index_col=0)
    
    return country_data, ml_features, ml_targets

@st.cache_resource
def load_model():
    """Load trained model"""
    return joblib.load('data/processed/carbon_emulator_model.pkl')

# Load everything
try:
    country_data, ml_features, ml_targets = load_data()
    model = load_model()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please make sure you've run Phase 2 and Phase 3 first!")
    data_loaded = False

if data_loaded:
    # Title and description
    st.title("⚡ Grid Carbon-Intensity Emulator")
    st.markdown("""
    An AI-powered tool to predict and simulate grid carbon intensity based on energy mix.
    Explore how different countries' electricity generation affects their carbon footprint.
    """)
    
    # Sidebar
    st.sidebar.header("🎛️ Controls")
    
    # Tab selection
    tab1, tab2, tab3 = st.tabs(["🌍 Global Overview", "🔮 Policy Simulator", "📊 Country Deep Dive"])
    
    # TAB 1: Global Overview
    with tab1:
        st.header("Global Carbon Intensity Map")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_intensity = country_data['carbon_intensity_gco2_kwh'].mean()
            st.metric("Global Average", f"{avg_intensity:.0f} gCO2/kWh")
        
        with col2:
            cleanest = country_data.nsmallest(1, 'carbon_intensity_gco2_kwh').iloc[0]
            st.metric("Cleanest Grid", f"{cleanest['country']}: {cleanest['carbon_intensity_gco2_kwh']:.0f}")
        
        with col3:
            dirtiest = country_data.nlargest(1, 'carbon_intensity_gco2_kwh').iloc[0]
            st.metric("Dirtiest Grid", f"{dirtiest['country']}: {dirtiest['carbon_intensity_gco2_kwh']:.0f}")
        
        with col4:
            avg_renewable = country_data['renewable_percentage'].mean()
            st.metric("Avg Renewable %", f"{avg_renewable:.1f}%")
        
        # World map
        st.subheader("Carbon Intensity by Country")
        
        fig = px.choropleth(
            country_data,
            locations='country',
            locationmode='ISO-3',
            color='carbon_intensity_gco2_kwh',
            hover_name='country',
            hover_data={
                'carbon_intensity_gco2_kwh': ':.0f',
                'renewable_percentage': ':.1f',
                'dominant_fuel': True,
                'country': False
            },
            color_continuous_scale='RdYlGn_r',
            labels={'carbon_intensity_gco2_kwh': 'Carbon Intensity (gCO2/kWh)'},
            title='Global Grid Carbon Intensity'
        )
        
        fig.update_layout(
            height=500,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top/Bottom countries
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top 10 Cleanest Grids")
            cleanest_10 = country_data.nsmallest(10, 'carbon_intensity_gco2_kwh')[
                ['country', 'carbon_intensity_gco2_kwh', 'renewable_percentage', 'dominant_fuel']
            ]
            cleanest_10.columns = ['Country', 'gCO2/kWh', 'Renewable %', 'Dominant Fuel']
            st.dataframe(cleanest_10, hide_index=True, use_container_width=True)
        
        with col2:
            st.subheader("🚨 Top 10 Dirtiest Grids")
            dirtiest_10 = country_data.nlargest(10, 'carbon_intensity_gco2_kwh')[
                ['country', 'carbon_intensity_gco2_kwh', 'renewable_percentage', 'dominant_fuel']
            ]
            dirtiest_10.columns = ['Country', 'gCO2/kWh', 'Renewable %', 'Dominant Fuel']
            st.dataframe(dirtiest_10, hide_index=True, use_container_width=True)
    
    # TAB 2: Policy Simulator
    with tab2:
        st.header("🔮 Policy Impact Simulator")
        st.markdown("Simulate 'What If?' scenarios for energy transitions")
        
        # Country selection
        countries_with_coal = ml_features[ml_features.get('Coal_pct', 0) > 5].index.tolist()
        
        if len(countries_with_coal) > 0:
            selected_country = st.sidebar.selectbox(
                "Select Country",
                countries_with_coal,
                index=0 if 'USA' not in countries_with_coal else countries_with_coal.index('USA')
            )
            
            # Get baseline
            baseline_features = ml_features.loc[[selected_country]].copy()
            baseline_intensity = model.predict(baseline_features)[0]
            
            # Display current state
            st.subheader(f"Current State: {selected_country}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Current Carbon Intensity", f"{baseline_intensity:.0f} gCO2/kWh")
            
            with col2:
                coal_pct = baseline_features.get('Coal_pct', pd.Series([0])).values[0]
                st.metric("Coal Percentage", f"{coal_pct:.1f}%")
            
            with col3:
                renewable_ratio = baseline_features.get('renewable_ratio', pd.Series([0])).values[0]
                st.metric("Renewable Ratio", f"{renewable_ratio*100:.1f}%")
            
            # Scenario sliders
            st.subheader("🎚️ Adjust Energy Mix")
            
            coal_reduction = st.slider(
                "Replace Coal with Solar (%)",
                min_value=0,
                max_value=min(100, int(coal_pct)),
                value=0,
                step=5,
                help="Percentage of coal capacity to replace with solar"
            )
            
            # Calculate scenario
            scenario_features = baseline_features.copy()
            
            if coal_reduction > 0 and 'Coal_pct' in scenario_features.columns and 'Solar_pct' in scenario_features.columns:
                scenario_features['Coal_pct'] -= coal_reduction
                scenario_features['Solar_pct'] += coal_reduction
                
                # Update renewable ratio
                renewables = ['Solar', 'Wind', 'Hydro', 'Geothermal']
                renewable_cols = [f'{r}_pct' for r in renewables if f'{r}_pct' in scenario_features.columns]
                new_renewable_pct = scenario_features[renewable_cols].sum(axis=1).values[0]
                scenario_features['renewable_ratio'] = new_renewable_pct / 100
                
                # Update fossil ratio
                fossils = ['Coal', 'Oil', 'Gas']
                fossil_cols = [f'{f}_pct' for f in fossils if f'{f}_pct' in scenario_features.columns]
                new_fossil_pct = scenario_features[fossil_cols].sum(axis=1).values[0]
                scenario_features['fossil_ratio'] = new_fossil_pct / 100
            
            scenario_intensity = model.predict(scenario_features)[0]
            reduction = baseline_intensity - scenario_intensity
            reduction_pct = (reduction / baseline_intensity) * 100
            
            # Results
            st.subheader("📊 Scenario Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "New Carbon Intensity",
                    f"{scenario_intensity:.0f} gCO2/kWh",
                    delta=f"-{reduction:.0f} gCO2/kWh",
                    delta_color="inverse"
                )
            
            with col2:
                st.metric(
                    "Reduction",
                    f"{reduction_pct:.1f}%",
                    help="Percentage reduction in carbon intensity"
                )
            
            with col3:
                # Estimate CO2 saved (assuming 100 TWh annual generation)
                annual_generation_twh = 100
                co2_saved = reduction * annual_generation_twh * 1_000_000_000 / 1_000_000_000
                st.metric(
                    "CO₂ Saved (Mt/year)",
                    f"{co2_saved:.1f}",
                    help="Assumes 100 TWh annual generation"
                )
            
            # Visualization
            comparison_df = pd.DataFrame({
                'Scenario': ['Current', 'With Transition'],
                'Carbon Intensity (gCO2/kWh)': [baseline_intensity, scenario_intensity]
            })
            
            fig = px.bar(
                comparison_df,
                x='Scenario',
                y='Carbon Intensity (gCO2/kWh)',
                color='Scenario',
                color_discrete_map={'Current': '#ff7f0e', 'With Transition': '#2ca02c'},
                title='Carbon Intensity Comparison'
            )
            
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.warning("No countries with significant coal capacity found in the dataset.")
    
    # TAB 3: Country Deep Dive
    with tab3:
        st.header("📊 Country Deep Dive")
        
        # Country selector
        all_countries = sorted(country_data['country'].tolist())
        selected_country_dive = st.sidebar.selectbox(
            "Select Country for Analysis",
            all_countries,
            index=all_countries.index('USA') if 'USA' in all_countries else 0
        )
        
        country_info = country_data[country_data['country'] == selected_country_dive].iloc[0]
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Carbon Intensity", f"{country_info['carbon_intensity_gco2_kwh']:.0f} gCO2/kWh")
        
        with col2:
            st.metric("Total Capacity", f"{country_info['total_capacity_mw']:,.0f} MW")
        
        with col3:
            st.metric("Renewable %", f"{country_info['renewable_percentage']:.1f}%")
        
        with col4:
            st.metric("Dominant Fuel", country_info['dominant_fuel'])
        
        # Fuel mix breakdown
        if selected_country_dive in ml_features.index:
            st.subheader("Energy Mix Breakdown")
            
            fuel_cols = [col for col in ml_features.columns if col.endswith('_pct')]
            fuel_data = ml_features.loc[selected_country_dive, fuel_cols]
            fuel_data = fuel_data[fuel_data > 0].sort_values(ascending=False)
            
            if len(fuel_data) > 0:
                fuel_df = pd.DataFrame({
                    'Fuel Type': [col.replace('_pct', '') for col in fuel_data.index],
                    'Percentage': fuel_data.values
                })
                
                fig = px.pie(
                    fuel_df,
                    values='Percentage',
                    names='Fuel Type',
                    title=f'{selected_country_dive} Energy Mix',
                    hole=0.4
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No fuel mix data available for this country")
        
        # Comparison with global average
        st.subheader("Comparison with Global Average")
        
        comparison_data = pd.DataFrame({
            'Metric': ['Carbon Intensity', 'Renewable %'],
            selected_country_dive: [
                country_info['carbon_intensity_gco2_kwh'],
                country_info['renewable_percentage']
            ],
            'Global Average': [
                country_data['carbon_intensity_gco2_kwh'].mean(),
                country_data['renewable_percentage'].mean()
            ]
        })
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name=selected_country_dive,
            x=comparison_data['Metric'],
            y=comparison_data[selected_country_dive],
            marker_color='#1f77b4'
        ))
        
        fig.add_trace(go.Bar(
            name='Global Average',
            x=comparison_data['Metric'],
            y=comparison_data['Global Average'],
            marker_color='#ff7f0e'
        ))
        
        fig.update_layout(
            barmode='group',
            title='Country vs Global Average',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Grid Carbon-Intensity Emulator** | Built with Python, XGBoost, and Streamlit  
    Data source: [Global Power Plant Database](https://github.com/wri/global-power-plant-database) by World Resources Institute
    """)

else:
    st.warning("Please run Phase 2 and Phase 3 to generate the required data files.")
