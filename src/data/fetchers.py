import yfinance as yf
import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime, timedelta

def fetch_sector_performance(periods: list[str]) -> pd.DataFrame:
    """
    Fetch performance and volume data for sector ETFs across multiple periods.
   
    Args:
        periods: List of time periods (e.g., ['1d', '5d', '1mo']).
   
    Returns:
        DataFrame with ETF performance and volume data.
    """
    sector_etfs = {
        'XLV': 'Health Care',
        'XLI': 'Industrials',
        'XLK': 'Technology',
        'XLRE': 'Real Estate',
        'XLE': 'Energy',
        'XLP': 'Consumer Staples',
        'XLY': 'Consumer Discretionary',
        'XLF': 'Financials',
        'XLC': 'Communication Services',
        'XLU': 'Utilities',
        'XLB': 'Materials',
        'XBI': 'Biotechnology'
    }
    data = []
    today = datetime.now()
    is_weekend = today.weekday() >= 5 # Saturday (5) or Sunday (6)
   
    for ticker, sector in sector_etfs.items():
        try:
            yf_ticker = yf.Ticker(ticker)
            row = {'Ticker': ticker, 'Sector': sector}
            last_hist = None
            for period in periods:
                if period == '1d' and is_weekend:
                    hist = yf_ticker.history(period='5d')
                    if not hist.empty and len(hist) >= 2:
                        price_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                        row[f'{period} Change (%)'] = price_change
                        row[f'{period} Volume'] = hist['Volume'].iloc[-1]
                        row[f'{period} Avg Volume'] = hist['Volume'].mean()
                    else:
                        row[f'{period} Change (%)'] = 0.0
                        row[f'{period} Volume'] = 0.0
                        row[f'{period} Avg Volume'] = 0.0
                        st.warning(f"No recent trading data for {ticker} in period {period}")
                else:
                    hist = yf_ticker.history(period=period)
                    if not hist.empty and len(hist) > 1:
                        price_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                        row[f'{period} Change (%)'] = price_change
                        row[f'{period} Volume'] = hist['Volume'].sum()
                        row[f'{period} Avg Volume'] = hist['Volume'].mean()
                    else:
                        row[f'{period} Change (%)'] = 0.0
                        row[f'{period} Volume'] = 0.0
                        row[f'{period} Avg Volume'] = 0.0
                        st.warning(f"Insufficient data for {ticker} in period {period}")
                last_hist = hist if not hist.empty else last_hist
            if last_hist is not None and not last_hist.empty:
                row['Price'] = last_hist['Close'].iloc[-1]
                row['Volume'] = last_hist['Volume'].iloc[-1]
            else:
                row['Price'] = None
                row['Volume'] = None
                st.warning(f"No valid data for {ticker}; excluding from results")
            data.append(row)
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")
   
    df = pd.DataFrame(data)
    numeric_cols = ['Price', 'Volume'] + [f'{p} Change (%)' for p in periods] + [f'{p} Volume' for p in periods] + [f'{p} Avg Volume' for p in periods]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    dropped_tickers = df[df['Price'].isna()]['Ticker'].tolist()
    if dropped_tickers:
        st.warning(f"Dropped tickers due to missing Price data: {', '.join(dropped_tickers)}")
    return df.dropna(subset=['Price'])

def fetch_historical_sector_data(tickers: list[str], start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch historical daily price and volume data for sector ETFs.
   
    Args:
        tickers: List of ETF ticker symbols.
        start_date: Start date for data (YYYY-MM-DD).
        end_date: End date for data (YYYY-MM-DD).
   
    Returns:
        DataFrame with daily Close and Volume for each ticker.
    """
    dfs = []
    for ticker in tickers:
        try:
            yf_ticker = yf.Ticker(ticker)
            hist = yf_ticker.history(start=start_date, end=end_date, auto_adjust=True)
            if hist.empty:
                st.warning(f"No historical data for ticker {ticker} from {start_date} to {end_date}")
                continue
            ticker_data = hist[['Close', 'Volume']].reset_index()
            ticker_data['Ticker'] = ticker
            ticker_data = ticker_data[['Date', 'Ticker', 'Close', 'Volume']]
            ticker_data['Date'] = pd.to_datetime(ticker_data['Date']).dt.tz_localize(None)  # Make tz-naive
            dfs.append(ticker_data)
        except Exception as e:
            st.error(f"Error fetching historical data for {ticker}: {e}")
    
    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        df = df.dropna()
        return df
    st.error("No historical data retrieved for any tickers.")
    return pd.DataFrame()