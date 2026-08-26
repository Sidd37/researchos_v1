"""
Financials page.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from services.companies import INDIAN_COMPANIES
from services.data_loader import get_balance_sheet, get_cash_flow, get_income_statement

st.title("Financials")

METRIC_LABELS = {
    "Total Revenue": ["Total Revenue", "TotalRevenue"],
    "Operating Income": ["Operating Income", "OperatingIncome"],
    "Net Income": ["Net Income", "Net Income Common Stockholders", "NetIncome"],
    "EBITDA": ["EBITDA", "Normalized EBITDA"],
}


def find_row(statement_df, candidate_labels):
    for label in candidate_labels:
        if label in statement_df.index:
            return statement_df.loc[label]
    return None


def build_metrics_table(income_df):
    rows = {}
    for metric_name, candidates in METRIC_LABELS.items():
        series = find_row(income_df, candidates)
        if series is not None:
            rows[metric_name] = series
        else:
            rows[metric_name] = pd.Series([None] * len(income_df.columns), index=income_df.columns)
    return pd.DataFrame(rows).T


def format_period_columns(df):
    new_columns = []
    for col in df.columns:
        if hasattr(col, "strftime"):
            new_columns.append(col.strftime("%Y-%m-%d"))
        else:
            new_columns.append(str(col))
    df = df.copy()
    df.columns = new_columns
    return df


def format_crores(value):
    if pd.isna(value):
        return "Data not available"
    return f"{value / 1e7:,.1f}"


col1, col2 = st.columns([2, 1])
with col1:
    company_name = st.selectbox("Select a company", options=list(INDIAN_COMPANIES.keys()))
with col2:
    period_choice = st.radio("Reporting period", options=["Annual", "Quarterly"], horizontal=True)

ticker = INDIAN_COMPANIES[company_name]
period = "quarterly" if period_choice == "Quarterly" else "annual"

with st.spinner(f"Fetching {period_choice.lower()} financials for {company_name}..."):
    income_df = get_income_statement(ticker, period=period)

st.subheader(f"Income Statement — {period_choice}")

if income_df.empty:
    st.error(f"Data not available: could not retrieve {period_choice.lower()} income statement data for {company_name} ({ticker}).")
else:
    metrics_df = build_metrics_table(income_df)

    st.caption("Values in Rs Crores. 'Data not available' means yfinance did not provide this figure.")
    display_df = format_period_columns(metrics_df)
    display_df = display_df.map(format_crores)
    st.dataframe(display_df, use_container_width=True)

    st.subheader("Revenue Trend")
    revenue_series = metrics_df.loc["Total Revenue"].dropna()
    if revenue_series.empty:
        st.info("Revenue trend cannot be plotted: data not available.")
    else:
        revenue_series = revenue_series.sort_index()
        fig_revenue = px.bar(
            x=[d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d) for d in revenue_series.index],
            y=revenue_series.values / 1e7,
            labels={"x": "Period", "y": "Revenue (Rs Crores)"},
            title=f"{company_name} — Revenue ({period_choice})",
        )
        st.plotly_chart(fig_revenue, use_container_width=True)

    st.subheader("Net Income Trend")
    net_income_series = metrics_df.loc["Net Income"].dropna()
    if net_income_series.empty:
        st.info("Net Income trend cannot be plotted: data not available.")
    else:
        net_income_series = net_income_series.sort_index()
        fig_net_income = px.line(
            x=[d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d) for d in net_income_series.index],
            y=net_income_series.values / 1e7,
            markers=True,
            labels={"x": "Period", "y": "Net Income (Rs Crores)"},
            title=f"{company_name} — Net Income ({period_choice})",
        )
        st.plotly_chart(fig_net_income, use_container_width=True)

with st.expander("Balance Sheet (raw data)"):
    with st.spinner("Fetching balance sheet..."):
        balance_df = get_balance_sheet(ticker, period=period)
    if balance_df.empty:
        st.write("Data not available.")
    else:
        st.dataframe(format_period_columns(balance_df), use_container_width=True)

with st.expander("Cash Flow Statement (raw data)"):
    with st.spinner("Fetching cash flow statement..."):
        cash_flow_df = get_cash_flow(ticker, period=period)
    if cash_flow_df.empty:
        st.write("Data not available.")
    else:
        st.dataframe(format_period_columns(cash_flow_df), use_container_width=True)
