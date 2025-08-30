import streamlit as st
import pandas as pd
import yaml
from datetime import datetime, timedelta
from src.ui.components import render_order_flow_table, render_order_flow_chart, render_order_flow_comparison_chart, render_net_order_flow_chart, render_etf_details
from src.data.fetchers import fetch_sector_performance, fetch_historical_sector_data
from src.data.processors import calculate_order_flow_scores, calculate_historical_order_flow_scores, generate_market_insights

def render_sector_rotation_page(sector_data: pd.DataFrame, etfs: dict, periods: list[str], period_weights: dict, short_term_periods: list[str], long_term_periods: list[str], thresholds: dict) -> None:
    """
    Render the sector rotation page with order flow analysis.
    
    Args:
        sector_data: DataFrame with sector performance data.
        etfs: Dict mapping ETF tickers to sector names.
        periods: List of periods (e.g., ['1d', '1mo']).
        period_weights: Dict of weights for order flow calculation.
        short_term_periods: List of short-term periods.
        long_term_periods: List of long-term periods.
        thresholds: Dict of thresholds for market insights (momentum, bias, neutral).
    """
    st.title("Stock Market Terminal - Sector Rotation Monitor")
    
    # Sidebar options
    st.sidebar.header("Terminal Options")
    sort_score = st.sidebar.selectbox("Sort Order Flow Table by", ['Long-term Order Flow Score', 'Short-term Order Flow Score'], index=0)
    selected_ticker = st.sidebar.selectbox("Select Sector ETF for Details", list(etfs.keys()))
    selected_sector = st.sidebar.selectbox("Select Sector for Order Flow Comparison", list(etfs.values()))
    
    # Calculate order flow scores
    order_flow_data = calculate_order_flow_scores(sector_data, periods, period_weights, short_term_periods, long_term_periods)
    order_flow_data = order_flow_data.sort_values(sort_score, ascending=False)
    
    # Fetch historical data for 1-year chart
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years for lookback
    hist_data = fetch_historical_sector_data(list(etfs.keys()), start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    hist_scores = calculate_historical_order_flow_scores(
        hist_data, etfs, periods, period_weights, short_term_periods, long_term_periods,
        (end_date - timedelta(days=365)).strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    )
    
    # Render order flow section
    st.subheader("Sector Order Flow Analysis")
    render_order_flow_table(order_flow_data, periods)
    render_order_flow_chart(order_flow_data, sort_score, periods)
    
    # Render order flow comparison chart for selected sector
    st.subheader(f"1-Year Order Flow Comparison for {selected_sector}")
    render_order_flow_comparison_chart(hist_scores, selected_sector)
    
    # Render net order flow chart for all sectors
    st.subheader("1-Year Net Order Flow Across All Sectors")
    render_net_order_flow_chart(hist_scores)
    
    # Render market insights
    st.subheader("Market Insights")
    insights = generate_market_insights(order_flow_data, periods, thresholds['momentum'], thresholds['bias'], thresholds['neutral'])
    st.markdown("\n".join([f"- {line}" for line in insights.split("\n") if line.strip()]))
    
    # Render ETF details
    if selected_ticker:
        render_etf_details(selected_ticker, etfs[selected_ticker])
    
    # Auto-refresh
    if st.sidebar.checkbox("Auto-refresh (every 5 minutes)", value=False):
        import time
        time.sleep(300)
        st.rerun()