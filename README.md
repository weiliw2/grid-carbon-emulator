# Grid Carbon Analysis Tool

**Author:** Weilin  

A country-level grid carbon analysis and scenario tool for exploring electricity carbon intensity across 167 countries.
https://grid-carbon-emulator-kmqkovap6aldgbbqgimcxs.streamlit.app/
---

## Overview

This project estimates country-level grid carbon intensity from power generation infrastructure data and uses a surrogate model for rapid scenario analysis. It is designed for benchmarking electricity systems, exploring energy-transition pathways, and comparing location-specific carbon exposure.

**Key Achievement:** Trained XGBoost/Random Forest models achieve R² = 0.64 with MAE of 60 gCO2/kWh, enabling instant policy impact predictions.

---

**Features:**
- **Global Map**: Interactive choropleth showing carbon intensity across 167 countries
- **Policy Simulator**: Real-time "what-if" scenarios for energy transitions
- **Country Analysis**: Deep-dive into individual country energy profiles

---

## Methodology

**Data Source:** [Global Power Plant Database](https://github.com/wri/global-power-plant-database) (World Resources Institute)
- 34,936 power plants worldwide
- Fuel types, capacity, and generation data

**Emission Factors:** Standard IPCC/EPA values (Coal: 820 gCO2/kWh, Gas: 490, Solar: 48, etc.)

Detailed methodology, assumptions, and current limitations are documented in [docs/methodology.md](/Users/weilynnw/grid-carbon-emulator/docs/methodology.md).
The benchmark validation workflow is documented in [docs/validation.md](/Users/weilynnw/grid-carbon-emulator/docs/validation.md).

## Key Results

### Model Performance
- **Algorithm:** Random Forest / XGBoost
- **R² Score:** 0.636
- **Mean Absolute Error:** 60 gCO2/kWh
- **Training Data:** 167 countries with complete energy mix data

### Sample Insights
- **Cleanest Grids:** Countries with 90%+ hydro/nuclear (e.g., Paraguay, Iceland)
- **Highest Emitters:** Coal-dependent grids (>800 gCO2/kWh)
- **Policy Impact:** Replacing 20% coal with solar reduces carbon intensity by 10-15%


## 📄 License

Data: [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/) (WRI GPPD)  
Code: MIT License

---

*Built as a portfolio project demonstrating expertise in environmental and energy analysis, carbon-intensity modeling, and interactive data visualization.*
