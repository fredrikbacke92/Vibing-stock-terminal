# src/data/processors/order_flow.py
import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data(ttl=3600)  # Cache for 1 hour
def calculate_order_flow_scores(df: pd.DataFrame, periods: list[str], period_weights: dict, short_term_periods: list[str], long_term_periods: list[str]) -> pd.DataFrame:
    """
    Calculate Short-term and Long-term Order Flow Scores for each sector based on performance and volume.
    
    Args:
        df: DataFrame with performance and volume data.
        periods: List of periods (e.g., ['1d', '1mo']).
        period_weights: Dict with 'short_term' and 'long_term' weights for each period.
        short_term_periods: List of short-term periods.
        long_term_periods: List of long-term periods.
    
    Returns:
        DataFrame with Short-term and Long-term Order Flow Scores added.
    """
    df = df.copy()
    
    # Normalize performance and volume
    for period in periods:
        abs_max_change = df[f'{period} Change (%)'].abs().max()
        df[f'{period} Norm Change'] = df[f'{period} Change (%)'] / abs_max_change if abs_max_change != 0 else 0
        df[f'{period} Norm Volume'] = df[f'{period} Volume'] / df[f'{period} Avg Volume']
    
    # Calculate Short-term and Long-term Order Flow Scores
    df['Short-term Order Flow Score'] = 0.0
    df['Long-term Order Flow Score'] = 0.0
    
    for period in short_term_periods:
        if period in periods:
            weight = period_weights['short_term'].get(period, 1.0 / len(short_term_periods))
            df['Short-term Order Flow Score'] += weight * (df[f'{period} Norm Change'] * df[f'{period} Norm Volume']).fillna(0)
    
    for period in long_term_periods:
        if period in periods:
            weight = period_weights['long_term'].get(period, 1.0 / len(long_term_periods))
            df['Long-term Order Flow Score'] += weight * (df[f'{period} Norm Change'] * df[f'{period} Norm Volume']).fillna(0)
    
    return df.sort_values('Long-term Order Flow Score', ascending=False)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def calculate_historical_order_flow_scores(hist_data: pd.DataFrame, sector_etfs: dict, periods: list[str], period_weights: dict, short_term_periods: list[str], long_term_periods: list[str], start_date: str, end_date: str) -> pd.DataFrame:
    """
    Calculate historical Short-term and Long-term Order Flow Scores for each trading day.
    
    Args:
        hist_data: DataFrame with daily [Date, Ticker, Close, Volume].
        sector_etfs: Dict mapping ETF tickers to sector names.
        periods: List of periods (e.g., ['1d', '1mo']).
        period_weights: Dict with 'short_term' and 'long_term' weights.
        short_term_periods: List of short-term periods.
        long_term_periods: List of long-term periods.
        start_date: Start date for scores (YYYY-MM-DD).
        end_date: End date for scores (YYYY-MM-DD).
    
    Returns:
        DataFrame with [Date, Ticker, Sector, Short-term Order Flow Score, Long-term Order Flow Score].
    """
    period_days = {
        '1d': 1,
        '5d': 5,
        '1mo': 20,  # Approx 20 trading days
        '3mo': 60,
        '6mo': 120,
        '1y': 252
    }
    
    start_date = pd.to_datetime(start_date).tz_localize(None)
    end_date = pd.to_datetime(end_date).tz_localize(None)
    dates = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days
    dates = [d.tz_localize(None) for d in dates]  # Ensure tz-naive
    
    results = []
    for date in dates:
        df_date = []
        for ticker, sector in sector_etfs.items():
            row = {'Date': date, 'Ticker': ticker, 'Sector': sector}
            ticker_data = hist_data[hist_data['Ticker'] == ticker].set_index('Date')
            ticker_data = ticker_data.loc[:date].tail(period_days['1y'] + 1)  # Up to 1y prior
            
            if len(ticker_data) < 2:
                continue
            
            for period in periods:
                days = period_days.get(period, 1)
                period_data = ticker_data.tail(days + 1)
                if len(period_data) > 1:
                    price_change = ((period_data['Close'].iloc[-1] - period_data['Close'].iloc[0]) / period_data['Close'].iloc[0]) * 100
                    row[f'{period} Change (%)'] = price_change
                    row[f'{period} Volume'] = period_data['Volume'].sum()
                    row[f'{period} Avg Volume'] = period_data['Volume'].mean()
                else:
                    row[f'{period} Change (%)'] = 0.0
                    row[f'{period} Volume'] = 0.0
                    row[f'{period} Avg Volume'] = 0.0
            df_date.append(row)
        
        if df_date:
            df = pd.DataFrame(df_date)
            df = calculate_order_flow_scores(df, periods, period_weights, short_term_periods, long_term_periods)
            df['Date'] = date
            results.append(df[['Date', 'Ticker', 'Sector', 'Short-term Order Flow Score', 'Long-term Order Flow Score']])
    
    if results:
        return pd.concat(results, ignore_index=True).dropna()
    return pd.DataFrame()