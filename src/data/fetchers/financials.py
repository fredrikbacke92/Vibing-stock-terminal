# src/data/fetchers/financials.py
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_sector_financials(sector: str, sector_stocks: dict) -> pd.DataFrame:
    """
    Fetch and aggregate financial metrics for representative stocks in a sector.
    
    Args:
        sector: Sector name.
        sector_stocks: Dict of sector to list of stock tickers.
    
    Returns:
        DataFrame with averaged metrics.
    """
    stocks = sector_stocks.get(sector, [])
    if not stocks:
        return pd.DataFrame()
    
    data = []
    for ticker in stocks:
        try:
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info
            peg = info.get('pegRatio', np.nan)
            if pd.isna(peg):
                trailing_pe = info.get('trailingPE', np.nan)
                growth = info.get('earningsGrowth', np.nan)
                if pd.isna(growth):  # Fallback: calculate growth from quarterly income statement
                    q_income = yf_ticker.quarterly_income_stmt
                    if q_income is not None and 'Net Income' in q_income.index and len(q_income.columns) >= 8:
                        recent_earnings = q_income.loc['Net Income'].iloc[-4:].sum()
                        prior_earnings = q_income.loc['Net Income'].iloc[-8:-4].sum()
                        if prior_earnings != 0:
                            growth = (recent_earnings - prior_earnings) / abs(prior_earnings)
                if not pd.isna(trailing_pe) and not pd.isna(growth) and growth != 0:
                    peg = trailing_pe / (growth * 100)
            data.append({
                'trailing_pe': info.get('trailingPE', np.nan),
                'forward_pe': info.get('forwardPE', np.nan),
                'peg_ratio': peg,
                'price_sales': info.get('priceToSalesTrailing12Months', np.nan),
                'price_book': info.get('priceToBook', np.nan),
            })
        except Exception as e:
            st.warning(f"Failed to fetch data for {ticker}: {str(e)}")
            continue
    
    if data:
        df = pd.DataFrame(data)
        return df.mean(numeric_only=True, skipna=True).to_frame().T
    return pd.DataFrame()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_market_financials(sector_stocks: dict) -> pd.DataFrame:
    """
    Fetch and aggregate financial metrics across all sectors' stocks.
    
    Args:
        sector_stocks: Dict of sector to list of stock tickers.
    
    Returns:
        DataFrame with averaged metrics.
    """
    all_data = []
    for t in [ticker for stocks in sector_stocks.values() for ticker in stocks]:
        try:
            yf_ticker = yf.Ticker(t)
            info = yf_ticker.info
            peg = info.get('pegRatio', np.nan)
            if pd.isna(peg):
                trailing_pe = info.get('trailingPE', np.nan)
                growth = info.get('earningsGrowth', np.nan)
                if pd.isna(growth):  # Fallback: calculate growth from quarterly income statement
                    q_income = yf_ticker.quarterly_income_stmt
                    if q_income is not None and 'Net Income' in q_income.index and len(q_income.columns) >= 8:
                        recent_earnings = q_income.loc['Net Income'].iloc[-4:].sum()
                        prior_earnings = q_income.loc['Net Income'].iloc[-8:-4].sum()
                        if prior_earnings != 0:
                            growth = (recent_earnings - prior_earnings) / abs(prior_earnings)
                if not pd.isna(trailing_pe) and not pd.isna(growth) and growth != 0:
                    peg = trailing_pe / (growth * 100)
            all_data.append({
                'trailing_pe': info.get('trailingPE', np.nan),
                'forward_pe': info.get('forwardPE', np.nan),
                'peg_ratio': peg,
                'price_sales': info.get('priceToSalesTrailing12Months', np.nan),
                'price_book': info.get('priceToBook', np.nan),
            })
        except Exception as e:
            st.warning(f"Failed to fetch data for {t}: {str(e)}")
            continue
    
    if all_data:
        df = pd.DataFrame(all_data)
        return df.mean(numeric_only=True, skipna=True).to_frame().T
    return pd.DataFrame()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_trailing_multiples(ticker: str, target_date: datetime) -> dict:
    """
    Calculate trailing multiples for a stock at a specific date using historical financials.
    
    Args:
        ticker: Stock ticker.
        target_date: Date for calculation.
    
    Returns:
        Dict with 'Trailing P/E', 'Price/Sales (ttm)', 'Price/Book' or None if data missing.
    """
    try:
        yf_ticker = yf.Ticker(ticker)
        
        # Get price around target_date (handle weekends)
        start = target_date - timedelta(days=5)
        end = target_date + timedelta(days=1)
        hist = yf_ticker.history(start=start.date(), end=end.date())
        if hist.empty:
            return None
        price = hist['Close'].iloc[-1]
        
        # Quarterly income statement before date
        q_income = yf_ticker.quarterly_income_stmt
        if q_income is None or 'Net Income' not in q_income.index or len(q_income.columns) < 4:
            return None
        q_income = q_income.T
        q_income['Date'] = pd.to_datetime(q_income.index)
        past_income = q_income[q_income['Date'] < target_date].sort_values('Date').tail(4)
        if len(past_income) < 4:
            return None
        ttm_earnings = past_income['Net Income'].sum()
        ttm_revenue = past_income.get('Total Revenue', pd.Series([np.nan] * len(past_income))).sum()
        
        # Quarterly balance sheet (latest before date)
        q_balance = yf_ticker.quarterly_balance_sheet.T
        if q_balance.empty:
            return None
        q_balance['Date'] = pd.to_datetime(q_balance.index)
        past_balance = q_balance[q_balance['Date'] < target_date].sort_values('Date').iloc[-1]
        
        shares_key = 'Ordinary Shares Number' if 'Ordinary Shares Number' in past_balance else 'Common Stock Shares Outstanding'
        shares = past_balance.get(shares_key, np.nan)
        if pd.isna(shares):
            return None
        
        book_value = past_balance.get('Total Stockholder Equity', np.nan)
        
        market_cap = price * shares
        
        trailing_pe = market_cap / ttm_earnings if ttm_earnings != 0 else np.nan
        price_sales = market_cap / ttm_revenue if ttm_revenue != 0 else np.nan
        price_book = market_cap / book_value if book_value != 0 and not pd.isna(book_value) else np.nan
        
        return {
            'Trailing P/E': trailing_pe,
            'Price/Sales (ttm)': price_sales,
            'Price/Book': price_book
        }
    except Exception as e:
        st.warning(f"Failed to fetch historical data for {ticker}: {str(e)}")
        return None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_historical_multiples(stocks: list[str], years_ago: list[int] = [0, 1, 3]) -> pd.DataFrame:
    """
    Aggregate historical trailing multiples for a list of stocks at specified times.
    
    Args:
        stocks: List of tickers.
        years_ago: List of years back (0 for current).
    
    Returns:
        DataFrame with rows as times, columns as metrics.
    """
    data = {y: [] for y in years_ago}
    for y in years_ago:
        date = datetime.now() - timedelta(days=y * 365)
        for ticker in stocks:
            multiples = get_trailing_multiples(ticker, date)
            if multiples:
                data[y].append(multiples)
    
    avg_df = pd.DataFrame()
    for y in years_ago:
        if data[y]:
            df = pd.DataFrame(data[y])
            avg = df.mean(skipna=True)
            avg.name = f'{y}Y Ago' if y > 0 else 'Current'
            avg_df = pd.concat([avg_df, avg.to_frame().T])
    
    return avg_df

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_market_historical_financials(sector_stocks: dict) -> pd.DataFrame:
    """
    Get historical aggregated financials for the whole market.
    
    Args:
        sector_stocks: Dict of sector to stocks.
    
    Returns:
        DataFrame with times as rows, metrics as columns.
    """
    all_stocks = [t for stocks in sector_stocks.values() for t in stocks]
    hist_df = fetch_historical_multiples(all_stocks)
    
    # Add current forward/PEG from .info averages
    current_data = []
    for t in all_stocks:
        try:
            yf_ticker = yf.Ticker(t)
            info = yf_ticker.info
            peg = info.get('pegRatio', np.nan)
            if pd.isna(peg):
                trailing_pe = info.get('trailingPE', np.nan)
                growth = info.get('earningsGrowth', np.nan)
                if pd.isna(growth):  # Fallback: calculate growth from quarterly income statement
                    q_income = yf_ticker.quarterly_income_stmt
                    if q_income is not None and 'Net Income' in q_income.index and len(q_income.columns) >= 8:
                        recent_earnings = q_income.loc['Net Income'].iloc[-4:].sum()
                        prior_earnings = q_income.loc['Net Income'].iloc[-8:-4].sum()
                        if prior_earnings != 0:
                            growth = (recent_earnings - prior_earnings) / abs(prior_earnings)
                if not pd.isna(trailing_pe) and not pd.isna(growth) and growth != 0:
                    peg = trailing_pe / (growth * 100)
            current_data.append({
                'Forward P/E': info.get('forwardPE', np.nan),
                'PEG Ratio': peg,
            })
        except Exception as e:
            st.warning(f"Failed to fetch data for {t}: {str(e)}")
            continue
    
    if current_data:
        current_avg = pd.DataFrame(current_data).mean(skipna=True)
        hist_df.loc['Current', 'Forward P/E'] = current_avg['Forward P/E']
        hist_df.loc['Current', 'PEG Ratio'] = current_avg['PEG Ratio']
    
    return hist_df[['Trailing P/E', 'Forward P/E', 'PEG Ratio', 'Price/Sales (ttm)', 'Price/Book']].fillna(np.nan)