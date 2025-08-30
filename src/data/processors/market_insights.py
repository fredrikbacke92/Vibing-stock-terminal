# src/data/processors/market_insights.py
import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data(ttl=3600)  # Cache for 1 hour
def generate_market_insights(df: pd.DataFrame, periods: list[str], momentum_threshold: float = 0.2, bias_threshold: float = 0.5, neutral_threshold: float = 0.1) -> str:
    """
    Generate descriptive market insights based on short-term and long-term order flow scores.
    
    Args:
        df: DataFrame with order flow scores.
        periods: List of periods.
        momentum_threshold: Threshold for momentum shifts.
        bias_threshold: Threshold for strong bias.
        neutral_threshold: Threshold for neutral market.
    
    Returns:
        Descriptive text summarizing market rotation and momentum.
    """
    insights = []
    
    # Top and bottom sectors for short-term and long-term
    short_top = df.sort_values('Short-term Order Flow Score', ascending=False).iloc[0]
    short_bottom = df.sort_values('Short-term Order Flow Score', ascending=False).iloc[-1]
    long_top = df.sort_values('Long-term Order Flow Score', ascending=False).iloc[0]
    long_bottom = df.sort_values('Long-term Order Flow Score', ascending=False).iloc[-1]
    
    # Rotation insight
    if short_top['Sector'] != long_top['Sector']:
        insights.append(f"Market is shifting out of **{long_top['Sector']}** (long: {long_top['Long-term Order Flow Score']:.2f}) to **{short_top['Sector']}** (short: {short_top['Short-term Order Flow Score']:.2f}) in the short term.")
    
    # Momentum insights
    for _, row in df.iterrows():
        sector = row['Sector']
        short_score = row['Short-term Order Flow Score']
        long_score = row['Long-term Order Flow Score']
        if short_score > long_score + momentum_threshold:
            insights.append(f"**{sector}** is experiencing accelerating momentum (short: {short_score:.2f} > long: {long_score:.2f}).")
        elif short_score < long_score - momentum_threshold:
            insights.append(f"**{sector}** is experiencing reduced momentum (short: {short_score:.2f} < long: {long_score:.2f}).")
    
    # Overall market bias
    avg_short = df['Short-term Order Flow Score'].mean()
    avg_long = df['Long-term Order Flow Score'].mean()
    if avg_short > bias_threshold and avg_long > bias_threshold:
        insights.append(f"Overall market shows **strong bullish flow** in both short and long term (short avg: {avg_short:.2f}, long avg: {avg_long:.2f}).")
    elif avg_short < -bias_threshold and avg_long < -bias_threshold:
        insights.append(f"Overall market shows **strong bearish flow** in both short and long term (short avg: {avg_short:.2f}, long avg: {avg_long:.2f}).")
    elif avg_short > avg_long:
        insights.append(f"Short-term flow is **more bullish** than long-term, indicating potential recovery (short avg: {avg_short:.2f}, long avg: {avg_long:.2f}).")
    elif avg_short < avg_long:
        insights.append(f"Short-term flow is **more bearish** than long-term, indicating potential pullback (short avg: {avg_short:.2f}, long avg: {avg_long:.2f}).")
    
    return "\n".join(insights) if insights else "No significant market insights detected."