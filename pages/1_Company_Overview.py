"""
Company Overview page.

Lets the user pick an Indian listed company and view basic
information about it. All data comes from services/data_loader.py,
which is the only module allowed to call yfinance - this page just
displays whatever it gets back.
"""

import streamlit as st

from services.companies import INDIAN_COMPANIES
from services.data_loader import get_company_info

st.title("Company Overview")


def format_market_cap(value):
    """
    Turn a raw market cap number into a readable Indian-crore string.

    Example: 1_500_000_000_000 -> "Rs 1,50,000 Cr" (approx formatting)
    We keep this simple: just convert to crores (1 crore = 10,000,000)
    and show it with commas. Returns "Data not available" if value is None.
    """
    if value is None:
        return "Data not available"
    crores = value / 1e7
    return f"Rs {crores:,.0f} Cr"


def format_price(value):
    """Format a price as Indian Rupees, or say it's not available."""
    if value is None:
        return "Data not available"
    return f"Rs {value:,.2f}"


# --- Company selector ---
company_name = st.selectbox(
    "Select a company",
    options=list(INDIAN_COMPANIES.keys()),
)
ticker = INDIAN_COMPANIES[company_name]

# --- Fetch and display ---
with st.spinner(f"Fetching data for {company_name} ({ticker})..."):
    info = get_company_info(ticker)

if "error" in info:
    st.error(info["error"])
else:
    st.subheader(info["name"] or company_name)
    st.caption(f"Ticker: {info['ticker']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Sector", info["sector"] or "Data not available")
    col2.metric("Industry", info["industry"] or "Data not available")
    col3.metric("Current Price", format_price(info["current_price"]))

    st.metric("Market Capitalization", format_market_cap(info["market_cap"]))

    st.markdown("**Website**")
    if info["website"]:
        st.markdown(f"[{info['website']}]({info['website']})")
    else:
        st.write("Data not available")

    st.markdown("**Business Description**")
    st.write(info["description"] or "Data not available")
