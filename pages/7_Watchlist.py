"""
Watchlist page.

Lets the user maintain a personal list of companies to keep an eye
on: add a company, see the current list, and remove one.

All SQLite access lives in services/database.py. This page only
calls those helper functions and renders the results - it never
opens a database connection or runs SQL directly.
"""

import streamlit as st

from services.companies import INDIAN_COMPANIES
from services.database import (
    add_to_watchlist,
    get_watchlist,
    init_db,
    is_watchlisted,
    remove_from_watchlist,
)

st.title("Watchlist")

st.caption(
    "A personal list of companies you want to keep track of. This is just "
    "a saved list of names - it does not show live prices or alerts."
)

if not INDIAN_COMPANIES:
    st.error("No companies are available to add to a watchlist.")
    st.stop()

db_ready = init_db()
if not db_ready:
    st.error(
        "Could not set up the watchlist database. Companies cannot be "
        "added or loaded right now - please check that the app has "
        "permission to create files in the data/ folder."
    )
    st.stop()

# Reverse lookup so we can show a company's display name given its ticker
TICKER_TO_NAME = {ticker: name for name, ticker in INDIAN_COMPANIES.items()}

# --- Section 1: Add to Watchlist ---
st.subheader("Add to Watchlist")

col1, col2 = st.columns([3, 1])
with col1:
    company_name = st.selectbox("Select a company", options=list(INDIAN_COMPANIES.keys()))
with col2:
    st.write("")
    st.write("")
    add_clicked = st.button("Add to Watchlist")

ticker = INDIAN_COMPANIES[company_name]

if add_clicked:
    if is_watchlisted(ticker):
        st.warning(f"{company_name} is already in your watchlist.")
    else:
        result = add_to_watchlist(ticker)
        if result == "added":
            st.success(f"Added {company_name} to your watchlist.")
            st.rerun()
        elif result == "duplicate":
            st.warning(f"{company_name} is already in your watchlist.")
        else:
            st.error("Something went wrong adding this company. Please try again.")

# --- Section 2: Current Watchlist ---
st.subheader("Current Watchlist")

watchlist = get_watchlist()

if not watchlist:
    st.info("No companies in your watchlist yet.")
else:
    for entry in watchlist:
        entry_ticker = entry["company"]
        display_name = TICKER_TO_NAME.get(entry_ticker, entry_ticker)

        with st.container(border=True):
            info_col, action_col = st.columns([4, 1])
            with info_col:
                st.markdown(f"**{display_name}**")
                st.caption(f"Ticker: {entry_ticker}  •  Added {entry['added_at']}")
            with action_col:
                if st.button("Remove", key=f"remove_{entry_ticker}"):
                    st.session_state[f"confirm_remove_{entry_ticker}"] = True

            if st.session_state.get(f"confirm_remove_{entry_ticker}"):
                st.warning(f"Remove {display_name} from your watchlist?")
                yes_col, no_col = st.columns(2)
                if yes_col.button("Yes, remove", key=f"confirm_yes_{entry_ticker}"):
                    removed = remove_from_watchlist(entry_ticker)
                    st.session_state.pop(f"confirm_remove_{entry_ticker}", None)
                    if not removed:
                        st.error("Could not remove this company. Please try again.")
                    st.rerun()
                if no_col.button("Cancel", key=f"confirm_no_{entry_ticker}"):
                    st.session_state.pop(f"confirm_remove_{entry_ticker}", None)
                    st.rerun()
