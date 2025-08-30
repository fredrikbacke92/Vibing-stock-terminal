# src/data/fetchers/options.py
import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_option_chain(ticker: str, expiration_date: str = None) -> dict:
    """
    Fetch option chain data for a given ticker and optional expiration date.
    
    Args:
        ticker: Stock or ETF ticker symbol.
        expiration_date: Specific expiration date (YYYY-MM-DD) or None for all dates.
    
    Returns:
        Dict with 'calls' and 'puts' DataFrames, or empty dict if no data.
    """
    try:
        yf_ticker = yf.Ticker(ticker)
        # Get available expiration dates
        expiration_dates = yf_ticker.options
        if not expiration_dates:
            st.warning(f"No option chain data available for {ticker}.")
            return {'calls': pd.DataFrame(), 'puts': pd.DataFrame(), 'expiration_dates': []}
        
        # Use first expiration if none specified
        selected_date = expiration_date if expiration_date in expiration_dates else expiration_dates[0]
        
        # Fetch option chain
        option_chain = yf_ticker.option_chain(selected_date)
        calls = option_chain.calls
        puts = option_chain.puts
        
        # Remove duplicate strikes
        calls = calls.drop_duplicates(subset=['strike'])
        puts = puts.drop_duplicates(subset=['strike'])
        
        # Debug: Check for duplicates
        if calls['strike'].duplicated().any():
            st.warning(f"Duplicate strikes found in calls data for {ticker}.")
        if puts['strike'].duplicated().any():
            st.warning(f"Duplicate strikes found in puts data for {ticker}.")
        
        # Add ticker and expiration for reference
        calls['Ticker'] = ticker
        puts['Ticker'] = ticker
        calls['Expiration'] = selected_date
        puts['Expiration'] = selected_date
        
        return {
            'calls': calls,
            'puts': puts,
            'expiration_dates': expiration_dates
        }
    except Exception as e:
        st.warning(f"Failed to fetch option chain for {ticker}: {str(e)}")
        return {'calls': pd.DataFrame(), 'puts': pd.DataFrame(), 'expiration_dates': []}