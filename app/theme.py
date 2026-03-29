from __future__ import annotations

import streamlit as st

SCRIPBOX_ORANGE = "#F58024"
SCRIPBOX_ORANGE_DARK = "#D96D1C"
SCRIPBOX_TEXT = "#1F2937"
SCRIPBOX_MUTED = "#6B7280"
SCRIPBOX_BG = "#F8F9FB"
SCRIPBOX_BORDER = "#E5E7EB"
SCRIPBOX_CARD = "#FFFFFF"


def apply_theme() -> None:
    st.set_page_config(
        page_title="RM Capability Engine",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

        html, body, [class*="css"], .stApp {{
            font-family: 'Inter', sans-serif !important;
            color: {SCRIPBOX_TEXT};
        }}

        .block-container {{
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }}

        h1, h2, h3 {{
            color: {SCRIPBOX_TEXT};
            letter-spacing: -0.02em;
        }}

        .brand-title {{
            color: {SCRIPBOX_ORANGE};
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 0.15rem;
            white-space: normal;
            word-break: break-word;
        }}

        .brand-subtitle {{
            color: {SCRIPBOX_TEXT};
            font-weight: 700;
            font-size: 1.05rem;
            line-height: 1.3;
            white-space: normal;
            word-break: break-word;
            margin-bottom: 0.8rem;
        }}

        .section-card {{
            background: {SCRIPBOX_CARD};
            border: 1px solid {SCRIPBOX_BORDER};
            border-radius: 16px;
            padding: 18px;
            box-shadow: 0 4px 18px rgba(0,0,0,0.04);
            margin-bottom: 1rem;
        }}

        .helper-text {{
            color: {SCRIPBOX_MUTED};
            font-size: 0.93rem;
        }}

        .badge {{
            display: inline-block;
            background: {SCRIPBOX_TEXT};
            color: white;
            padding: 6px 12px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
        }}

        .xp-shell {{
            width: 100%;
            background: #E5E7EB;
            border-radius: 999px;
            height: 12px;
            overflow: hidden;
        }}

        .xp-fill {{
            height: 12px;
            background: {SCRIPBOX_ORANGE};
            border-radius: 999px;
        }}

        .stButton > button {{
            background: {SCRIPBOX_ORANGE};
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 700;
            padding: 0.6rem 1rem;
        }}

        .stButton > button:hover {{
            background: {SCRIPBOX_ORANGE_DARK};
            color: white;
        }}

        div[data-testid="stSidebar"] {{
            min-width: 290px;
        }}

        div[data-testid="stExpander"] {{
            border: 1px solid {SCRIPBOX_BORDER};
            border-radius: 14px;
            overflow: hidden;
        }}

        .small-muted {{
            font-size: 0.84rem;
            color: {SCRIPBOX_MUTED};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )