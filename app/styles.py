"""Shared styling for the Streamlit dashboard."""

APP_CSS = """
<style>
/* Global Settings */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Main Background - Very Light Mint */
.stApp {
    background-color: #F0FDF4;
}

/* Sidebar - White with border */
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #D1FAE5;
}

/* Headers - Deep Emerald Green */
h1 {
    color: #064E3B;
    font-weight: 800;
    letter-spacing: -0.5px;
    padding-bottom: 1rem;
    border-bottom: 2px solid #10B981;
    font-size: 2.5rem !important;
}

h2 {
    color: #065F46;
    font-weight: 700;
    margin-top: 2rem;
    font-size: 1.8rem !important;
}

h3 {
    color: #047857;
    font-weight: 600;
    font-size: 1.4rem !important;
}

/* Metrics Cards - Modern & Clean */
[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #A7F3D0;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 700;
    color: #059669;
}

[data-testid="stMetricLabel"] {
    font-size: 1rem !important;
    color: #4B5563;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 2rem;
    border-bottom: 2px solid #E5E7EB;
    background-color: transparent;
}

.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    font-size: 1.1rem;
    color: #4B5563;
    padding: 1rem 0;
}

.stTabs [aria-selected="true"] {
    color: #059669;
    border-bottom-color: #059669;
}

/* Buttons */
.stButton > button {
    background-color: #059669;
    color: white;
    font-weight: 600;
    border-radius: 6px;
    padding: 0.75rem 2rem;
    border: none;
    font-size: 1rem;
    transition: all 0.2s;
    width: 100%;
}

.stButton > button:hover {
    background-color: #047857;
    box-shadow: 0 4px 12px rgba(5, 150, 105, 0.2);
}

/* Input Fields */
.stSelectbox > div > div {
    background-color: #FFFFFF;
    border-color: #D1FAE5;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    background-color: white;
}

/* Alert Boxes */
.stAlert {
    background-color: #ECFDF5;
    border: 1px solid #10B981;
    color: #064E3B;
}

/* Footer */
footer {
    color: #6B7280;
    text-align: center;
    padding: 3rem 0;
    border-top: 1px solid #E5E7EB;
    margin-top: 4rem;
    background-color: transparent;
}
</style>
"""
