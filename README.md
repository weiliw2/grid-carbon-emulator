# Grid Carbon-Intensity Emulator

An AI-powered system to predict country-level grid carbon intensity and simulate carbon-aware computing strategies.

## 🎯 Project Overview

This project builds a machine learning emulator that predicts a country's electricity grid carbon intensity based on its power generation infrastructure. The emulator can instantly simulate policy changes (like renewable energy transitions) without recalculating complex energy models.

## 📊 Data Source

- **Global Power Plant Database (GPPD)** from World Resources Institute
- ~35,000 power plants worldwide
- Fuel types, capacity, generation data

## 🛠️ Tech Stack

- **Data Processing**: Pandas, GeoPandas
- **Machine Learning**: Scikit-learn, XGBoost
- **Visualization**: Plotly, Streamlit
- **Deployment**: Streamlit Cloud

## 📁 Project Structure

```
grid-carbon-emulator/
├── data/
│   ├── raw/              # Raw data from GPPD
│   └── processed/        # Cleaned and aggregated data
├── notebooks/            # Jupyter notebooks for exploration
├── src/                  # Python scripts
├── visualizations/       # Dashboard and plots
└── README.md
```

## 🚀 Getting Started

1. Clone the repository
2. Create virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run Phase 1: `python src/phase1_data_fetch.py`

## 📈 Project Phases

- [x] **Phase 1**: Global data engineering
- [ ] **Phase 2**: Carbon intensity calculations
- [ ] **Phase 3**: ML emulator training
- [ ] **Phase 4**: Interactive dashboard

## 👤 Author

[Your Name]
Environmental Analytics Portfolio Project

---
*Built with Python, XGBoost, and Streamlit*
