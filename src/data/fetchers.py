import yfinance as yf
import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime, timedelta

def fetch_sector_performance(periods: list[str]) -> pd.DataFrame:
    """
    Fetch performance data for sector ETFs across multiple periods.
    
    Args:
        periods: List of time periods (e.g., ['1d', '5d', '1mo']).
    
    Returns:
        DataFrame with ETF performance data.
    """
    # Define SPDR ETFs (loaded from config in app.py, but hardcoded here for fallback)
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
        'XLB': 'Materials'
    }
    data = []
    today = datetime.now()
    is_weekend = today.weekday() >= 5  # Saturday (5) or Sunday (6)
    
    for ticker, sector in sector_etfs.items():
        try:
            yf_ticker = yf.Ticker(ticker)
            row = {'Ticker': ticker, 'Sector': sector}
            last_hist = None
            for period in periods:
                # For 1d on weekends, fetch 5d and take the last two trading days
                if period == '1d' and is_weekend:
                    hist = yf_ticker.history(period='5d')
                    if not hist.empty and len(hist) >= 2:
                        price_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                        row[f'{period} Change (%)'] = price_change
                    else:
                        row[f'{period} Change (%)'] = 0.0
                        st.write(f"Warning: No recent trading data for {ticker} in period {period}")
                else:
                    hist = yf_ticker.history(period=period)
                    if not hist.empty and len(hist) > 1:
                        price_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                        row[f'{period} Change (%)'] = price_change
                    else:
                        row[f'{period} Change (%)'] = 0.0
                        st.write(f"Warning: Insufficient data for {ticker} in period {period}")
                last_hist = hist if not hist.empty else last_hist
            # Add latest price and volume
            if last_hist is not None and not last_hist.empty:
                row['Price'] = last_hist['Close'].iloc[-1]
                row['Volume'] = last_hist['Volume'].iloc[-1]
            else:
                row['Price'] = None
                row['Volume'] = None
            data.append(row)
        except Exception as e:
            st.write(f"Error fetching data for {ticker}: {e}")
    
    df = pd.DataFrame(data)
    numeric_cols = ['Price', 'Volume'] + [f'{p} Change (%)' for p in periods]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    return df.dropna(subset=['Price'])