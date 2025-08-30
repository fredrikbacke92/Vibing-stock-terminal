# src/data/processors/options.py
import pandas as pd
import numpy as np
from scipy.stats import norm
from datetime import datetime
import streamlit as st

def process_option_chain(option_data: dict, call_put: str, current_price: float) -> pd.DataFrame:
    """
    Process option chain data, adding ITM status and delta.
    
    Args:
        option_data: Dict with 'calls' and 'puts' DataFrames.
        call_put: 'calls' or 'puts' to select option type.
        current_price: Current price of the underlying asset.
    
    Returns:
        Processed DataFrame with selected columns, ITM status, and delta.
    """
    df = option_data.get(call_put, pd.DataFrame())
    if df.empty:
        return df
    
    # Select relevant columns
    columns = ['Ticker', 'Expiration', 'strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']
    df = df[columns].copy()
    
    # Rename columns for display
    df.columns = ['Ticker', 'Expiration', 'Strike', 'Last Price', 'Bid', 'Ask', 'Volume', 'Open Interest', 'Implied Volatility']
    
    # Remove any duplicate strikes
    df = df.drop_duplicates(subset=['Strike'])
    
    # Add ITM status
    df['ITM'] = df.apply(
        lambda row: row['Strike'] < current_price if call_put == 'calls' else row['Strike'] > current_price,
        axis=1
    )
    
    # Simplified delta calculation (Black-Scholes approximation)
    def calculate_delta(row, is_call: bool):
        S = current_price  # Underlying price
        K = row['Strike']  # Strike price
        sigma = row['Implied Volatility']  # Volatility
        T = (datetime.strptime(row['Expiration'], '%Y-%m-%d') - datetime.now()).days / 365.0
        r = 0.05  # Risk-free rate (assumed 5%)
        
        if T <= 0 or pd.isna(sigma) or sigma <= 0:
            return np.nan
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        if is_call:
            delta = norm.cdf(d1)
        else:
            delta = norm.cdf(d1) - 1
        return round(delta, 3)
    
    df['Delta'] = df.apply(calculate_delta, axis=1, is_call=call_put == 'calls')
    
    # Format numbers (except Implied Volatility, keep numeric for calculations)
    df[['Last Price', 'Bid', 'Ask']] = df[['Last Price', 'Bid', 'Ask']].apply(lambda x: x.map(lambda y: f"{y:.2f}" if pd.notnull(y) else '-'))
    df[['Volume', 'Open Interest']] = df[['Volume', 'Open Interest']].fillna(0).astype(int)
    
    # Debug: Check for duplicates
    if df.duplicated(subset=['Strike']).any():
        st.warning(f"Warning: Duplicate strikes found in {call_put} data after processing.")
    
    return df.sort_values('Strike')

def generate_option_insights(df: pd.DataFrame, call_put: str, current_price: float) -> str:
    """
    Generate simple, beginner-friendly insights from option chain data.
    
    Args:
        df: Processed DataFrame with option chain data.
        call_put: 'calls' or 'puts' to select option type.
        current_price: Current price of the underlying asset.
    
    Returns:
        Descriptive text summarizing key insights.
    """
    if df.empty:
        return "No option data available to analyze."
    
    insights = []
    
    # Detect hot trading (volume > 2 * open interest, min volume 10 for significance)
    unusual = df[(df['Volume'] > 2 * df['Open Interest']) & (df['Volume'] >= 10)].drop_duplicates(subset=['Strike'])
    if not unusual.empty:
        hot_strikes = [f"${row['Strike']:.2f} (Volume: {row['Volume']}, Open Interest: {row['Open Interest']})" for _, row in unusual.iterrows()]
        insights.append(f"Hot Trading: Traders are betting big at strikes {', '.join(set(hot_strikes))}.")
    
    # Compute IV skew at ATM strike
    atm_index = (df['Strike'] - current_price).abs().idxmin()
    atm_strike = df.loc[atm_index, 'Strike']
    atm_iv = df.loc[atm_index, 'Implied Volatility']
    avg_iv = df['Implied Volatility'].mean()
    iv_skew = atm_iv - avg_iv
    if pd.notna(iv_skew):
        skew_type = "High" if iv_skew > 0.05 else "Low" if iv_skew < -0.05 else "Normal"
        skew_desc = "expecting big price swings soon." if iv_skew > 0.05 else "expecting stable prices." if iv_skew < -0.05 else "expecting normal price movement."
        insights.append(f"Price Movement: {skew_type} volatility at strike ${atm_strike:.2f} ({atm_iv*100:.2f}% vs. average {avg_iv*100:.2f}%), {skew_desc}")
    
    # Suggest sentiment
    total_volume = df['Volume'].sum()
    itm_volume = df[df['ITM']]['Volume'].sum()
    if total_volume > 0 and itm_volume / total_volume > 0.5:
        sentiment = "Upward" if call_put == 'calls' else "Downward"
        sentiment_desc = "traders expect the price to rise." if call_put == 'calls' else "traders expect the price to fall."
        insights.append(f"Market Mood: {sentiment} bias, with most trading in profitable {call_put} ({sentiment_desc})")
    
    # Add context for beginners
    if insights:
        insights.insert(0, f"**Easy {call_put.capitalize()} Insights for {df['Ticker'].iloc[0]} (Expiration: {df['Expiration'].iloc[0]})**")
        insights.append("\n**What’s Happening?** Hot trading means lots of people are buying or selling at those prices—maybe big news! Volatility shows if prices might jump or stay calm. The market mood shows if traders expect the price to go up (upward) or down (downward).")
    
    return "\n\n".join(insights) if insights else "The market is quiet for these options, no big activity to report."

def generate_overall_sentiment(option_data: dict, current_price: float) -> str:
    """
    Analyze both calls and puts to determine overall bullish, neutral, or bearish sentiment.
    
    Args:
        option_data: Dict with 'calls' and 'puts' DataFrames.
        current_price: Current price of the underlying asset.
    
    Returns:
        Descriptive text with overall sentiment and reasoning.
    """
    calls = process_option_chain(option_data, 'calls', current_price)
    puts = process_option_chain(option_data, 'puts', current_price)
    
    if calls.empty and puts.empty:
        return "No option data available to analyze."
    
    # Calculate total volumes
    call_volume = calls['Volume'].sum()
    put_volume = puts['Volume'].sum()
    total_volume = call_volume + put_volume
    
    # Call/Put Volume Ratio
    volume_ratio = call_volume / put_volume if put_volume > 0 else float('inf')
    
    # Hot trading counts (volume > 2 * open interest, min volume 10)
    call_hot = len(calls[(calls['Volume'] > 2 * calls['Open Interest']) & (calls['Volume'] >= 10)])
    put_hot = len(puts[(puts['Volume'] > 2 * puts['Open Interest']) & (puts['Volume'] >= 10)])
    
    # IV averages
    call_avg_iv = calls['Implied Volatility'].mean() if not calls.empty else 0
    put_avg_iv = puts['Implied Volatility'].mean() if not puts.empty else 0
    
    # Sentiment score (positive for calls, negative for puts)
    sentiment_score = (call_volume - put_volume) / total_volume if total_volume > 0 else 0
    sentiment_score += (call_hot - put_hot) / (call_hot + put_hot + 1)  # Avoid division by zero
    sentiment_score += (call_avg_iv - put_avg_iv) * 10  # Amplify IV difference
    
    # Determine sentiment
    if sentiment_score > 0.3:
        sentiment = "Bullish"
        reasoning = "More trading in calls means traders expect the price to go up."
    elif sentiment_score < -0.3:
        sentiment = "Bearish"
        reasoning = "More trading in puts means traders expect the price to go down."
    else:
        sentiment = "Neutral"
        reasoning = "Trading in calls and puts is balanced, no strong direction."
    
    # Add details
    reasoning += f"\n\nCall vs. Put Trading: Calls have {call_volume} trades, Puts have {put_volume}."
    reasoning += f"\nHot Call Strikes: {call_hot} with high activity."
    reasoning += f"\nHot Put Strikes: {put_hot} with high activity."
    reasoning += f"\nCall Volatility: {call_avg_iv*100:.2f}% (expected price swings for calls)."
    reasoning += f"\nPut Volatility: {put_avg_iv*100:.2f}% (expected price swings for puts)."
    
    return f"**Overall Market Mood: {sentiment}**\n{reasoning}\n\n**Simple Explanation**: Bullish means traders think the price will rise. Bearish means they expect a fall. Neutral means no big moves are expected."