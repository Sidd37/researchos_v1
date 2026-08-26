"""
data_loader.py

Responsible for fetching COMPANY DATA from yfinance:
- basic company info (name, sector, market cap, etc.)
- historical stock price data
- financial statements

Rule for this module: it is the ONLY place in the app that should
call yfinance. Pages call functions here instead of talking to
yfinance directly.
"""

import pandas as pd
import yfinance as yf


def _fetch_statement(ticker, annual_attr, quarterly_attr, period):
    try:
        yf_ticker = yf.Ticker(ticker)
        attr_name = quarterly_attr if period == "quarterly" else annual_attr
        statement = getattr(yf_ticker, attr_name)
    except Exception:
        return pd.DataFrame()

    if statement is None or statement.empty:
        return pd.DataFrame()

    return statement


def get_income_statement(ticker, period="annual"):
    return _fetch_statement(ticker, "income_stmt", "quarterly_income_stmt", period)


def get_balance_sheet(ticker, period="annual"):
    return _fetch_statement(ticker, "balance_sheet", "quarterly_balance_sheet", period)


def get_cash_flow(ticker, period="annual"):
    return _fetch_statement(ticker, "cashflow", "quarterly_cashflow", period)


def get_price_history(ticker, period="1y"):
    try:
        yf_ticker = yf.Ticker(ticker)
        history = yf_ticker.history(period=period)
    except Exception:
        return pd.DataFrame()

    if history is None or history.empty or "Close" not in history.columns:
        return pd.DataFrame()

    price_df = history[["Close"]].reset_index()
    if "Date" not in price_df.columns:
        price_df = price_df.rename(columns={price_df.columns[0]: "Date"})

    price_df = price_df.sort_values("Date").reset_index(drop=True)
    return price_df


def get_company_info(ticker):
    try:
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
    except Exception as exc:
        return {"error": f"Could not fetch data for '{ticker}': {exc}"}

    name = info.get("longName") or info.get("shortName")
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")

    if not name and current_price is None:
        return {
            "error": (
                f"No data found for ticker '{ticker}'. "
                "It may be invalid, delisted, or temporarily unavailable."
            )
        }

    return {
        "ticker": ticker,
        "name": name,
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "market_cap": info.get("marketCap"),
        "current_price": current_price,
        "website": info.get("website"),
        "description": info.get("longBusinessSummary"),
    }
