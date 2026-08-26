"""
ResearchOS - main entry point.

This file is the "Home" page of the Streamlit multi-page app.
The actual feature pages (Company Overview, Financials, Ratios, etc.)
live in the pages/ folder.

Run with:  streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="ResearchOS",
    page_icon="📊",
    layout="wide",
)

st.title("📊 ResearchOS")
st.subheader("A lightweight equity research workspace for Indian listed companies")

st.markdown(
    """
    Welcome to **ResearchOS**.

    Use the sidebar to navigate between sections:

    - **Company Overview** – basic company information
    - **Financials** – revenue, profit, and other statement data
    - **Ratios** – derived financial ratios (Revenue Growth, Net Income
      Growth, Operating Margin, Net Profit Margin, ROE, ROCE)
    - **Price Performance** – historical stock price charts and returns
    - **Peer Comparison** – compare a company against its peers
    - **Notes** – save your own research notes
    - **Watchlist** – track companies you're following

    All market and financial data is fetched live from Yahoo Finance via
    `yfinance`. When a figure isn't available, the app shows this
    explicitly rather than guessing or defaulting to zero.
    """
)
