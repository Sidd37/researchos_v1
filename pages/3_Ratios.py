"""
Ratios page.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from services.companies import INDIAN_COMPANIES
from services.data_loader import get_balance_sheet, get_income_statement
from services.financials import build_ratios_table

st.title("Ratios & Analysis")

st.caption(
    "Ratios are calculated from the same Annual or Quarterly statements shown "
    "on the Financials page. Mixing annual and quarterly data would produce "
    "misleading ratios, so everything here uses a single, clearly labeled period type."
)


def format_percent(value):
    if value is None or pd.isna(value):
        return "Data not available"
    return f"{value:.2f}%"


col1, col2 = st.columns([2, 1])
with col1:
    company_name = st.selectbox("Select a company", options=list(INDIAN_COMPANIES.keys()))
with col2:
    period_choice = st.radio("Reporting period", options=["Annual", "Quarterly"], horizontal=True)

ticker = INDIAN_COMPANIES[company_name]
period = "quarterly" if period_choice == "Quarterly" else "annual"

with st.spinner(f"Fetching {period_choice.lower()} statements for {company_name}..."):
    income_df = get_income_statement(ticker, period=period)
    balance_df = get_balance_sheet(ticker, period=period)

if income_df.empty and balance_df.empty:
    st.error(f"Data not available: could not retrieve {period_choice.lower()} financial statements for {company_name} ({ticker}).")
    st.stop()

ratios = build_ratios_table(income_df, balance_df)

table_rows = []
for metric_name, result in ratios.items():
    table_rows.append({
        "Metric": metric_name,
        "Latest": format_percent(result["latest"]),
        "Previous": format_percent(result["previous"]),
        "Formula": result["formula"],
    })
ratios_table = pd.DataFrame(table_rows).set_index("Metric")

st.subheader(f"Key Ratios — {period_choice}")
st.dataframe(ratios_table, use_container_width=True)

st.caption(
    "ROE requires two periods of shareholders' equity to compute a proper average; "
    "if only one period is available, ROE is shown as 'Data not available' rather "
    "than using a less accurate single-period approximation."
)

st.subheader("Visual Summary")

chart_metrics = ["Operating Margin", "Net Profit Margin", "ROE", "ROCE"]
chart_data = {
    name: ratios[name]["latest"]
    for name in chart_metrics
    if ratios[name]["latest"] is not None and not pd.isna(ratios[name]["latest"])
}

if not chart_data:
    st.info("Not enough data available to plot a visual summary for this company.")
else:
    fig = px.bar(
        x=list(chart_data.keys()),
        y=list(chart_data.values()),
        labels={"x": "Metric", "y": "Percent (%)"},
        title=f"{company_name} — Latest Profitability & Returns ({period_choice})",
    )
    st.plotly_chart(fig, use_container_width=True)
