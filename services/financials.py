"""
financials.py

Responsible for FINANCIAL RATIO CALCULATIONS. Does NOT call yfinance.
Takes DataFrames already fetched by services/data_loader.py.
"""

import pandas as pd

REVENUE_LABELS = ["Total Revenue", "TotalRevenue"]
OPERATING_INCOME_LABELS = ["Operating Income", "OperatingIncome"]
NET_INCOME_LABELS = ["Net Income", "Net Income Common Stockholders", "NetIncome"]

EQUITY_LABELS = ["Stockholders Equity", "Common Stock Equity", "Total Equity Gross Minority Interest"]
TOTAL_ASSETS_LABELS = ["Total Assets"]
CURRENT_LIABILITIES_LABELS = ["Current Liabilities", "Total Current Liabilities"]


def find_row(statement_df, candidate_labels):
    if statement_df is None or statement_df.empty:
        return None
    for label in candidate_labels:
        if label in statement_df.index:
            return statement_df.loc[label]
    return None


def get_values(row, count=3):
    if row is None:
        return [None] * count
    values = list(row)
    return [values[i] if i < len(values) else None for i in range(count)]


def calculate_growth(current_value, previous_value):
    if pd.isna(current_value) or pd.isna(previous_value):
        return None
    if previous_value == 0:
        return None
    return (current_value - previous_value) / previous_value * 100


def calculate_margin(numerator, denominator):
    if pd.isna(numerator) or pd.isna(denominator):
        return None
    if denominator == 0:
        return None
    return numerator / denominator * 100


def calculate_roe(net_income, equity_current, equity_previous):
    if pd.isna(net_income) or pd.isna(equity_current) or pd.isna(equity_previous):
        return None
    average_equity = (equity_current + equity_previous) / 2
    if average_equity == 0:
        return None
    return net_income / average_equity * 100


def calculate_roce(operating_income, total_assets, current_liabilities):
    if pd.isna(operating_income) or pd.isna(total_assets) or pd.isna(current_liabilities):
        return None
    capital_employed = total_assets - current_liabilities
    if capital_employed == 0:
        return None
    return operating_income / capital_employed * 100


def build_ratios_table(income_df, balance_df):
    revenue_row = find_row(income_df, REVENUE_LABELS)
    operating_income_row = find_row(income_df, OPERATING_INCOME_LABELS)
    net_income_row = find_row(income_df, NET_INCOME_LABELS)

    equity_row = find_row(balance_df, EQUITY_LABELS)
    total_assets_row = find_row(balance_df, TOTAL_ASSETS_LABELS)
    current_liabilities_row = find_row(balance_df, CURRENT_LIABILITIES_LABELS)

    revenue = get_values(revenue_row)
    operating_income = get_values(operating_income_row)
    net_income = get_values(net_income_row)
    equity = get_values(equity_row)
    total_assets = get_values(total_assets_row)
    current_liabilities = get_values(current_liabilities_row)

    ratios = {}

    ratios["Revenue Growth"] = {
        "latest": calculate_growth(revenue[0], revenue[1]),
        "previous": calculate_growth(revenue[1], revenue[2]),
        "formula": "(Current Revenue - Previous Revenue) / Previous Revenue x 100",
    }
    ratios["Net Income Growth"] = {
        "latest": calculate_growth(net_income[0], net_income[1]),
        "previous": calculate_growth(net_income[1], net_income[2]),
        "formula": "(Current Net Income - Previous Net Income) / Previous Net Income x 100",
    }
    ratios["Operating Margin"] = {
        "latest": calculate_margin(operating_income[0], revenue[0]),
        "previous": calculate_margin(operating_income[1], revenue[1]),
        "formula": "Operating Income / Revenue x 100",
    }
    ratios["Net Profit Margin"] = {
        "latest": calculate_margin(net_income[0], revenue[0]),
        "previous": calculate_margin(net_income[1], revenue[1]),
        "formula": "Net Income / Revenue x 100",
    }
    ratios["ROE"] = {
        "latest": calculate_roe(net_income[0], equity[0], equity[1]),
        "previous": calculate_roe(net_income[1], equity[1], equity[2]),
        "formula": "Net Income / Average Shareholders' Equity x 100 (needs 2 periods of equity)",
    }
    ratios["ROCE"] = {
        "latest": calculate_roce(operating_income[0], total_assets[0], current_liabilities[0]),
        "previous": calculate_roce(operating_income[1], total_assets[1], current_liabilities[1]),
        "formula": "Operating Profit / Capital Employed x 100, Capital Employed = Total Assets - Current Liabilities",
    }

    return ratios
