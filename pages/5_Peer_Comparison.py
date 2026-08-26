"""
Peer Comparison page.

Lets the user compare one selected company against 1-4 peer companies
using the same six financial ratios already defined in Phase 3.

This page does NOT call yfinance and does NOT define any new ratio
formulas. It only:
1. calls services/data_loader.py to fetch each company's income
   statement and balance sheet, and
2. calls services/financials.py's build_ratios_table() - the exact
   same function used on the Ratios page - to compute ratios for
   each company,
then arranges the results into a side-by-side comparison table and a
short, data-driven "Key Takeaways" summary.
"""

import pandas as pd
import streamlit as st

from services.companies import INDIAN_COMPANIES
from services.data_loader import get_balance_sheet, get_income_statement
from services.financials import build_ratios_table

st.title("Peer Comparison")

st.caption(
    "Compare a company against a small group of peers using the same "
    "ratios shown on the Ratios page: Revenue Growth, Net Income Growth, "
    "Operating Margin, Net Profit Margin, ROE, and ROCE."
)

# Metrics used for the data-driven "Key Takeaways" section below the table.
# These are exactly the ones called out in the Phase 5 requirements -
# growth and margin/return metrics where "highest" is a meaningful,
# easy-to-explain comparison. Net Income Growth and ROCE are still shown
# in the full table, just not summarized as a takeaway.
TAKEAWAY_METRICS = ["Revenue Growth", "Operating Margin", "Net Profit Margin", "ROE"]


def format_percent(value):
    """Format a ratio value as a percentage, or say it's not available."""
    if value is None or pd.isna(value):
        return "Data not available"
    return f"{value:.2f}%"


def get_company_ratios(ticker, period):
    """
    Fetch a company's statements and compute its ratios.

    This is the only place Phase 5 talks to the data layer, and it
    reuses the exact same functions Phase 2/3 already use - no new
    yfinance calls or ratio formulas are introduced here.

    Returns
    -------
    dict
        The same shape returned by build_ratios_table(): metric name
        -> {"latest": ..., "previous": ..., "formula": ...}.
    """
    income_df = get_income_statement(ticker, period=period)
    balance_df = get_balance_sheet(ticker, period=period)
    return build_ratios_table(income_df, balance_df)


# --- Company selection ---
col1, col2 = st.columns([2, 1])
with col1:
    primary_name = st.selectbox("Primary Company", options=list(INDIAN_COMPANIES.keys()))
with col2:
    period_choice = st.radio("Reporting period", options=["Annual", "Quarterly"], horizontal=True)

period = "quarterly" if period_choice == "Quarterly" else "annual"

# Peers can never include the primary company - it's simply excluded
# from the options list, so there's nothing for the user to un-select.
peer_options = [name for name in INDIAN_COMPANIES if name != primary_name]
peer_names = st.multiselect(
    "Peer Companies (choose 2-4)",
    options=peer_options,
    max_selections=4,
    help="Select a few companies to compare against the primary company.",
)

if not peer_names:
    st.info("Select at least one peer company above to see a comparison.")
    st.stop()

# --- Fetch + compute ratios for the primary company and each peer ---
# Each company is fetched exactly once here, regardless of how many of
# its metrics get used below - no repeated calls per metric.
company_order = [primary_name] + peer_names
ratios_by_company = {}

with st.spinner("Fetching financial statements for the selected companies..."):
    for name in company_order:
        ticker = INDIAN_COMPANIES[name]
        ratios_by_company[name] = get_company_ratios(ticker, period)

# A company with no usable data at all (both statements empty/unavailable)
# will have every metric come back None from build_ratios_table - this is
# handled automatically by the reused Phase 3 functions, not special-cased
# here. We just track it so the takeaways section can mention it if needed.
companies_with_no_data = [
    name
    for name in company_order
    if all(ratios_by_company[name][m]["latest"] is None for m in ratios_by_company[name])
]

# --- Comparison table: rows = metrics, columns = companies ---
st.subheader(f"Comparison — {period_choice}")

metric_names = list(next(iter(ratios_by_company.values())).keys())
table_data = {
    name: [format_percent(ratios_by_company[name][metric]["latest"]) for metric in metric_names]
    for name in company_order
}
comparison_df = pd.DataFrame(table_data, index=metric_names)

# Highlight the primary company's column so it's visually distinguishable
# from the peers, as requested.
styled_table = comparison_df.style.set_properties(
    subset=[primary_name], **{"background-color": "#FFF3CD", "font-weight": "bold"}
)
st.dataframe(styled_table, use_container_width=True)

if companies_with_no_data:
    st.caption(
        "No financial data could be retrieved for: "
        + ", ".join(companies_with_no_data)
        + ". Their columns show 'Data not available' for every metric."
    )

# --- Key Takeaways: simple, data-driven observations, no recommendations ---
st.subheader("Key Takeaways")

takeaways = []
for metric in TAKEAWAY_METRICS:
    values = {
        name: ratios_by_company[name][metric]["latest"]
        for name in company_order
        if ratios_by_company[name][metric]["latest"] is not None
        and not pd.isna(ratios_by_company[name][metric]["latest"])
    }
    # A comparison needs at least two companies with a real value for
    # this metric - with only one (or zero), there's nothing to compare.
    if len(values) >= 2:
        best_name = max(values, key=values.get)
        takeaways.append(
            f"**{best_name}** has the highest {metric.lower()} among the selected "
            f"companies ({format_percent(values[best_name])})."
        )

if takeaways:
    for line in takeaways:
        st.markdown(f"- {line}")
else:
    st.info(
        "Not enough data was available among the selected companies to "
        "generate a comparison summary."
    )
