"""Shared styling for the Streamlit dashboard."""

APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:wght@500;600&display=swap');

:root {
    --bg: #f3f0e8;
    --surface: rgba(255, 252, 245, 0.86);
    --surface-strong: #fffdf8;
    --surface-muted: #ebe4d6;
    --text: #1d2b28;
    --muted: #586663;
    --line: rgba(51, 73, 68, 0.16);
    --accent: #1f5c4f;
    --accent-soft: #dce9e4;
    --warn: #b85c38;
    --shadow: 0 18px 40px rgba(35, 49, 46, 0.08);
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    color: var(--text);
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(100, 138, 126, 0.16), transparent 28%),
        radial-gradient(circle at top right, rgba(201, 167, 111, 0.18), transparent 24%),
        linear-gradient(180deg, #f7f3ea 0%, #efe8da 100%);
}

.block-container {
    padding-top: 2.2rem;
    padding-bottom: 3rem;
    max-width: 1240px;
}

[data-testid="stSidebar"] {
    background: rgba(252, 249, 242, 0.9);
    border-right: 1px solid var(--line);
}

h1, h2, h3 {
    color: var(--text);
    letter-spacing: -0.03em;
}

h1 {
    font-family: 'IBM Plex Serif', serif;
    font-size: 3.3rem !important;
    font-weight: 600;
    margin-bottom: 0.25rem;
}

h2 {
    font-size: 1.65rem !important;
    font-weight: 600;
    margin-top: 0.4rem;
}

h3 {
    font-size: 1.15rem !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--muted);
}

p, li, label, .stMarkdown, .stCaption {
    color: var(--muted);
}

.hero-shell {
    background: linear-gradient(135deg, rgba(255, 252, 246, 0.92), rgba(246, 241, 231, 0.86));
    border: 1px solid rgba(36, 61, 57, 0.08);
    border-radius: 26px;
    padding: 2rem 2rem 1.6rem 2rem;
    box-shadow: var(--shadow);
    backdrop-filter: blur(14px);
    margin-bottom: 1.5rem;
}

.hero-kicker {
    display: inline-block;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    background: var(--accent-soft);
    border-radius: 999px;
    padding: 0.35rem 0.7rem;
    margin-bottom: 0.9rem;
}

.hero-lede {
    max-width: 760px;
    font-size: 1.07rem;
    line-height: 1.75;
    color: #485854;
    margin: 0.5rem 0 1.15rem 0;
}

.status-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.9rem;
}

.status-card {
    background: rgba(255, 255, 255, 0.58);
    border: 1px solid rgba(31, 92, 79, 0.12);
    border-radius: 18px;
    padding: 1rem 1.05rem;
}

.status-label {
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.35rem;
}

.status-value {
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text);
}

.section-intro {
    max-width: 820px;
    margin: 0.1rem 0 1rem 0;
    color: #556560;
}

.insight-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.9rem;
    margin: 0.25rem 0 1.2rem 0;
}

.insight-card {
    background: rgba(255, 253, 248, 0.82);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 1rem 1.05rem;
    box-shadow: var(--shadow);
}

.insight-label {
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.45rem;
}

.insight-value {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.35rem;
}

.insight-meta {
    font-size: 0.93rem;
    line-height: 1.6;
    color: #60716c;
}

.note-panel {
    background: rgba(31, 92, 79, 0.08);
    border: 1px solid rgba(31, 92, 79, 0.14);
    border-radius: 18px;
    padding: 1rem 1.1rem;
    margin: 0.25rem 0 1rem 0;
}

.note-title {
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.35rem;
}

.note-body {
    color: #4f605c;
    line-height: 1.7;
    font-size: 0.95rem;
}

[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 1rem 1.05rem;
    box-shadow: var(--shadow);
}

[data-testid="stMetricLabel"] {
    font-size: 0.78rem !important;
    color: var(--muted);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

[data-testid="stMetricValue"] {
    color: var(--text);
    font-size: 2rem !important;
    font-weight: 700;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: rgba(250, 246, 238, 0.72);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 0.35rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 14px;
    font-weight: 600;
    color: var(--muted);
    padding: 0.7rem 1rem;
}

.stTabs [aria-selected="true"] {
    background: #ffffff;
    color: var(--text);
    border-bottom-color: transparent;
}

.stButton > button {
    background: var(--accent);
    color: white;
    font-weight: 600;
    border-radius: 14px;
    padding: 0.8rem 1.2rem;
    border: none;
    box-shadow: 0 10px 20px rgba(31, 92, 79, 0.18);
}

.stButton > button:hover {
    background: #184c42;
}

.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stTextInput > div > div > input {
    background: rgba(255, 252, 245, 0.95);
    border-color: rgba(36, 61, 57, 0.16);
    border-radius: 12px;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 18px;
    background: rgba(255, 253, 248, 0.92);
    overflow: hidden;
}

.stAlert {
    border-radius: 16px;
    border: 1px solid rgba(31, 92, 79, 0.16);
}

footer {
    color: var(--muted);
    text-align: center;
    padding: 2rem 0;
    border-top: 1px solid var(--line);
    margin-top: 3rem;
}

@media (max-width: 900px) {
    .hero-shell {
        padding: 1.4rem;
    }

    h1 {
        font-size: 2.55rem !important;
    }

    .status-grid {
        grid-template-columns: 1fr;
    }

    .insight-grid {
        grid-template-columns: 1fr;
    }
}
</style>
"""
