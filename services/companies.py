"""
companies.py

A small, hardcoded list of well-known Indian large-cap companies,
mapping a display name to its NSE ticker symbol (as used by yfinance,
which requires the ".NS" suffix for NSE-listed stocks).

This is intentionally static and small (~15-20 companies) rather than
a full exchange listing, since that's outside the scope of this project.
The dict can be extended later just by adding more entries -- no other
code needs to change when new companies are added.
"""

INDIAN_COMPANIES = {
    "Tata Consultancy Services": "TCS.NS",
    "Infosys": "INFY.NS",
    "Reliance Industries": "RELIANCE.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "State Bank of India": "SBIN.NS",
    "Hindustan Unilever": "HINDUNILVR.NS",
    "ITC": "ITC.NS",
    "Larsen & Toubro": "LT.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Axis Bank": "AXISBANK.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "Wipro": "WIPRO.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Sun Pharmaceutical": "SUNPHARMA.NS",
    "Titan Company": "TITAN.NS",
    "Adani Enterprises": "ADANIENT.NS",
}
