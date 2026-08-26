# ResearchOS

ResearchOS is a lightweight equity research workspace for Indian listed
companies. It lets you pull up a company's fundamentals, financial
statements, key ratios, price history, and compare it against peers,
all in one place, plus keep your own notes and a personal watchlist.

Built with Streamlit, Pandas, Plotly, SQLite, and yfinance.

## What ResearchOS Does

- Select an Indian listed company from a curated list of large-caps
- View company information (sector, industry, market cap, price, description)
- View financial performance (income statement, balance sheet, cash flow)
- View financial ratios (growth, margins, ROE, ROCE)
- View stock price performance (historical charts and returns)
- Compare a company against 1-4 peer companies
- Save personal research notes per company
- Maintain a personal watchlist of companies

## Architecture

Two simple rules hold the whole project together.

Rule one: pages only render UI. No page calls yfinance or sqlite3
directly, they call functions in services and display whatever comes back.

Rule two: one source of truth per concern. There is exactly one company
list in services companies.py, one place that talks to Yahoo Finance in
services data_loader.py, one place that computes ratios in services
financials.py, and one place that talks to SQLite in services database.py.

## Data Source

All market and financial data is fetched live from Yahoo Finance via the
yfinance library, nothing is hardcoded or invented. Indian NSE tickers
require a dot NS suffix, for example TCS.NS or INFY.NS, which yfinance
needs to locate the right listing.

## Database Usage

SQLite, stored at data researchos.db, is used only for data the user
creates: research notes and watchlist entries. It never caches or stores
market data. Every price, ratio, and financial figure shown in the app is
fetched fresh from Yahoo Finance each time. The database file and its
tables are created automatically the first time they are needed.

## Project Structure

Top level: app.py is the home page, requirements.txt lists dependencies,
README.md is this file.

The data folder holds researchos.db, the SQLite database, created
automatically.

The services folder holds four files. companies.py has the one list of
Indian companies and tickers. data_loader.py has all yfinance calls:
company info, financial statements, price history. financials.py has
ratio calculations using pure pandas and Python, no yfinance calls.
database.py has all SQLite access for notes and watchlist.

The pages folder holds seven files. 1_Company_Overview.py shows company
info. 2_Financials.py shows income statement, balance sheet, cash flow.
3_Ratios.py shows financial ratios. 4_Price_Performance.py shows
historical price charts and returns. 5_Peer_Comparison.py compares a
company against peers. 6_Notes.py handles research notes: create, edit,
delete. 7_Watchlist.py handles a personal watchlist: add, remove.

## Setup Instructions

Step 1, prerequisites: Python 3.9 or newer, and pip available on your PATH.

Step 2, create a virtual environment from inside the researchos project
folder by running: python -m venv venv

Then activate it. On Windows PowerShell, run: venv\Scripts\Activate.ps1
On macOS or Linux, run: source venv/bin/activate

You should see (venv) appear at the start of your terminal prompt.

Step 3, install dependencies by running: pip install -r requirements.txt

Step 4, run the app by running: streamlit run app.py

This opens the app automatically in your browser, usually at
http localhost colon 8501. If it does not open automatically, copy that
URL into your browser manually.

Step 5, stop the app by pressing Ctrl+C in the terminal where Streamlit
is running.

Step 6, deactivate the virtual environment when done by running: deactivate

## Available Pages

Company Overview: sector, industry, market cap, current price, website,
business description.

Financials: Total Revenue, Operating Income, Net Income, EBITDA where
available, Annual or Quarterly, plus trend charts and raw balance sheet
and cash flow statements.

Ratios: Revenue Growth, Net Income Growth, Operating Margin, Net Profit
Margin, ROE, ROCE, each with its formula shown alongside.

Price Performance: historical closing price chart from 1 Month to 5
Years, performance summary covering change, return, high and low, daily
return stats, and a cumulative return chart.

Peer Comparison: the same six ratios side by side for a primary company
and up to 4 peers, plus a short data-driven Key Takeaways summary.

Notes: create, edit, and delete free-text research notes tied to a company.

Watchlist: add or remove companies from a personal tracking list.

## Key Financial Metrics

Revenue Growth equals Current Revenue minus Previous Revenue, divided by
Previous Revenue, times 100.

Net Income Growth equals Current Net Income minus Previous Net Income,
divided by Previous Net Income, times 100.

Operating Margin equals Operating Income divided by Revenue, times 100.

Net Profit Margin equals Net Income divided by Revenue, times 100.

ROE equals Net Income divided by Average Shareholders Equity, times 100.

ROCE equals Operating Profit divided by Capital Employed, times 100,
where Capital Employed equals Total Assets minus Current Liabilities.

Note on ROE: it requires shareholders equity from two periods to compute
a proper average. If only one period of equity data is available, ROE is
shown as Data not available rather than approximated from a single
period, which would be a different, less standard ratio.

## Missing Data and Error Handling Philosophy

If a figure cannot be retrieved or calculated, the app shows Data not
available. It never guesses, estimates, or substitutes zero.

Every calculation checks for missing inputs and division by zero before
computing anything. A bad input produces Data not available, not a crash
or a nonsensical number.

Network or data source failures, such as an invalid ticker, Yahoo
Finance being unavailable, or no data for a company, are caught and
shown as a clear message. The app does not crash.

## Known Limitations

The company list is a static, hardcoded set of about 20 well-known
Indian large-caps, not the full NSE listing.

yfinance's row labels for financial statements can vary slightly by
company. services financials.py checks a few common label variants for
each metric, but an unusual label on a specific company could still show
as Data not available even if the underlying data technically exists.

Peer Comparison and Ratios reuse the same statement-matching approach:
periods are aligned by position, meaning the most recent column is
assumed to match the most recent column across statements, rather than
by matching exact report dates.

The watchlist is a simple saved list. It does not show live prices,
alerts, or portfolio-style tracking.

Notes and watchlist data are stored locally in data researchos.db and
are specific to the machine running the app. There is no user login or
cloud sync.
