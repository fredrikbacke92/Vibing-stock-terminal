import streamlit as st
import pandas as pd
from src.ui.components import render_order_flow_table, render_order_flow_chart, render_etf_details
from src.data.processors import calculate_order_flow_scores, generate_market_insights

def render_sector_rotation_page(sector_data: pd.DataFrame, etfs: dict, periods: list[str], period_weights: dict) -> None:
    """
    Render the sector rotation page with order flow analysis.
    
    Args:
        sector_data: DataFrame with sector performance data.
        etfs: Dict mapping ETF tickers to sector names.
        periods: List of periods (e.g., ['1d', '1mo']).
        period_weights: Dict of weights for order flow calculation.
    """
    st.title("Stock Market Terminal - Sector Rotation Monitor")
    
    # Sidebar options
    st.sidebar.header("Terminal Options")
    sort_score = st.sidebar.selectbox("Sort Order Flow Table by", ['Long-term Order Flow Score', 'Short-term Order Flow Score'], index=0)
    selected_ticker = st.sidebar.selectbox("Select Sector ETF for Details", list(etfs.keys()))
    
    # Calculate order flow scores
    order_flow_data = calculate_order_flow_scores(sector_data, periods, period_weights)
    order_flow_data = order_flow_data.sort_values(sort_score, ascending=False)
    
    # Render order flow section
    st.subheader("Sector Order Flow Analysis")
    render_order_flow_table(order_flow_data, periods)
    render_order_flow_chart(order_flow_data, sort_score, periods)
    
    # Render market insights
    st.subheader("Market Insights")
    insights = generate_market_insights(order_flow_data, periods)
    st.text(insights)
    
    # Render ETF details
    if selected_ticker:
        render_etf_details(selected_ticker, etfs[selected_ticker])
    
    # Auto-refresh
    if st.sidebar.checkbox("Auto-refresh (every 5 minutes)", value=False):
        import time
        time.sleep(300)
        st.rerun()