"""
Price Performance page.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from services.companies import INDIAN_COMPANIES
from services.data_loader import get_price_history

st.title("Price Performance")

st.caption(
    "Prices use yfinance's default auto-adjusted 'Close', which already accounts "
    "for stock splits and dividends. There is no separate Adj Close column to "
    "choose from, so 'Close' is used consistently throughout this page."
)

PERIOD_OPTIONS = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "3 Years": "3y",
    "5 Years": "5y",
}


def format_price(value):
    if value is None or pd.isna(value):
        return "Data not available"
    return f"Rs {value:,.2f}"


def format_percent(value):
    if value is None or pd.isna(value):
        return "Data not available"
    return f"{value:.2f}%"


def calculate_performance_metrics(price_df):
    metrics = {
        "latest_price": None, "start_price": None, "abs_change": None,
        "pct_return": None, "period_high": None, "period_low": None,
    }
    if price_df.empty:
        return metrics

    closes = price_df["Close"]
    metrics["latest_price"] = closes.iloc[-1]
    metrics["start_price"] = closes.iloc[0]
    metrics["period_high"] = closes.max()
    metrics["period_low"] = closes.min()

    if len(closes) >= 2:
        start_price = closes.iloc[0]
        latest_price = closes.iloc[-1]
        metrics["abs_change"] = latest_price - start_price
        if start_price != 0:
            metrics["pct_return"] = (latest_price - start_price) / start_price * 100

    return metrics


def add_daily_returns(price_df):
    df = price_df.copy()
    df["Daily Return"] = df["Close"].pct_change() * 100
    return df


col1, col2 = st.columns([2, 1])
with col1:
    company_name = st.selectbox("Select a company", options=list(INDIAN_COMPANIES.keys()))
with col2:
    period_choice = st.selectbox("Historical period", options=list(PERIOD_OPTIONS.keys()), index=3)

ticker = INDIAN_COMPANIES[company_name]
yf_period = PERIOD_OPTIONS[period_choice]

with st.spinner(f"Fetching {period_choice.lower()} price history for {company_name}..."):
    price_df = get_price_history(ticker, period=yf_period)

if price_df.empty:
    st.error(f"Data not available: could not retrieve price history for {company_name} ({ticker}) over the selected period ({period_choice}).")
    st.stop()

price_df = add_daily_returns(price_df)

st.subheader(f"Closing Price — {period_choice}")
fig_price = px.line(
    price_df, x="Date", y="Close",
    labels={"Date": "Date", "Close": "Price (Rs)"},
    title=f"{company_name} — Closing Price ({period_choice})",
)
fig_price.update_traces(hovertemplate="Date: %{x}<br>Price: Rs %{y:,.2f}")
st.plotly_chart(fig_price, use_container_width=True)

st.subheader("Performance Summary")
metrics = calculate_performance_metrics(price_df)

col1, col2, col3 = st.columns(3)
col1.metric("Latest Price", format_price(metrics["latest_price"]))
col2.metric("Period Start Price", format_price(metrics["start_price"]))
col3.metric("Absolute Change", format_price(metrics["abs_change"]))

col4, col5, col6 = st.columns(3)
col4.metric("Percentage Return", format_percent(metrics["pct_return"]))
col5.metric("Period High", format_price(metrics["period_high"]))
col6.metric("Period Low", format_price(metrics["period_low"]))

st.subheader("Daily Return Analysis")
valid_returns = price_df["Daily Return"].dropna()

if valid_returns.empty:
    st.info("Not enough data available to compute daily returns for this period.")
else:
    avg_return = valid_returns.mean()
    best_idx = valid_returns.idxmax()
    worst_idx = valid_returns.idxmin()
    best_return = valid_returns.loc[best_idx]
    worst_return = valid_returns.loc[worst_idx]
    best_date = price_df.loc[best_idx, "Date"]
    worst_date = price_df.loc[worst_idx, "Date"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Average Daily Return", format_percent(avg_return))
    col2.metric("Best Day", format_percent(best_return), help=f"On {best_date.strftime('%Y-%m-%d')}")
    col3.metric("Worst Day", format_percent(worst_return), help=f"On {worst_date.strftime('%Y-%m-%d')}")

st.subheader("Cumulative Return")
if len(price_df) < 2 or price_df["Close"].iloc[0] == 0:
    st.info("Not enough data available to plot cumulative return for this period.")
else:
    start_price = price_df["Close"].iloc[0]
    cumulative_return = (price_df["Close"] / start_price - 1) * 100
    fig_cumulative = px.line(
        x=price_df["Date"], y=cumulative_return,
        labels={"x": "Date", "y": "Cumulative Return (%)"},
        title=f"{company_name} — Cumulative Return ({period_choice})",
    )
    fig_cumulative.update_traces(hovertemplate="Date: %{x}<br>Cumulative Return: %{y:.2f}%")
    st.plotly_chart(fig_cumulative, use_container_width=True)

with st.expander("Historical Price Data"):
    display_df = price_df.copy()
    display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
    display_df["Close"] = display_df["Close"].map(lambda v: f"Rs {v:,.2f}")
    display_df["Daily Return"] = display_df["Daily Return"].map(lambda v: "N/A" if pd.isna(v) else f"{v:.2f}%")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
