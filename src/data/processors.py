import pandas as pd
import numpy as np

def calculate_order_flow_scores(df: pd.DataFrame, periods: list[str], period_weights: dict) -> pd.DataFrame:
    """
    Calculate Short-term and Long-term Order Flow Scores for each sector based on performance and volume.
    
    Args:
        df: DataFrame with performance and volume data.
        periods: List of periods (e.g., ['1d', '1mo']).
        period_weights: Dict with 'short_term' and 'long_term' weights for each period.
    
    Returns:
        DataFrame with Short-term and Long-term Order Flow Scores added.
    """
    df = df.copy()
    short_term_periods = ['1d', '5d', '1mo']
    long_term_periods = ['3mo', '6mo', '1y']
    
    # Normalize performance and volume
    for period in periods:
        df[f'{period} Norm Change'] = df[f'{period} Change (%)'] / df[f'{period} Change (%)'].abs().max()
        df[f'{period} Norm Volume'] = df[f'{period} Volume'] / df[f'{period} Avg Volume']
    
    # Calculate Short-term and Long-term Order Flow Scores
    df['Short-term Order Flow Score'] = 0.0
    df['Long-term Order Flow Score'] = 0.0
    
    for period in short_term_periods:
        weight = period_weights['short_term'].get(period, 1.0 / len(short_term_periods))
        df['Short-term Order Flow Score'] += weight * (df[f'{period} Norm Change'] * df[f'{period} Norm Volume']).fillna(0)
    
    for period in long_term_periods:
        weight = period_weights['long_term'].get(period, 1.0 / len(long_term_periods))
        df['Long-term Order Flow Score'] += weight * (df[f'{period} Norm Change'] * df[f'{period} Norm Volume']).fillna(0)
    
    return df.sort_values('Long-term Order Flow Score', ascending=False)

def generate_market_insights(df: pd.DataFrame, periods: list[str]) -> str:
    """
    Generate descriptive market insights based on short-term and long-term order flow scores.
    
    Args:
        df: DataFrame with order flow scores.
        periods: List of periods.
    
    Returns:
        Descriptive text summarizing market rotation and momentum.
    """
    insights = []
    
    # Top and bottom sectors for short-term and long-term
    short_top = df.sort_values('Short-term Order Flow Score', ascending=False).iloc[0]['Sector']
    short_bottom = df.sort_values('Short-term Order Flow Score', ascending=False).iloc[-1]['Sector']
    long_top = df.sort_values('Long-term Order Flow Score', ascending=False).iloc[0]['Sector']
    long_bottom = df.sort_values('Long-term Order Flow Score', ascending=False).iloc[-1]['Sector']
    
    # Rotation insight
    if short_top != long_top:
        insights.append(f"Market is shifting out of {long_top} to {short_top} in the short term.")
    
    # Momentum insights
    for sector in df['Sector'].unique():
        row = df[df['Sector'] == sector].iloc[0]
        if row['Short-term Order Flow Score'] > row['Long-term Order Flow Score'] + 0.2:
            insights.append(f"{sector} is experiencing accelerating momentum.")
        elif row['Short-term Order Flow Score'] < row['Long-term Order Flow Score'] - 0.2:
            insights.append(f"{sector} is experiencing reduced momentum.")
    
    # Overall market bias
    avg_short = df['Short-term Order Flow Score'].mean()
    avg_long = df['Long-term Order Flow Score'].mean()
    if avg_short > 0.5 and avg_long > 0.5:
        insights.append("Overall market shows strong bullish flow in both short and long term.")
    elif avg_short < -0.5 and avg_long < -0.5:
        insights.append("Overall market shows strong bearish flow in both short and long term.")
    elif avg_short > avg_long:
        insights.append("Short-term flow is more bullish than long-term, indicating potential recovery.")
    elif avg_short < avg_long:
        insights.append("Short-term flow is more bearish than long-term, indicating potential pullback.")
    
    return "\n".join(insights) if insights else "No significant market insights detected."