import streamlit as st
from src.ui.components import render_performance_table, render_performance_chart, render_etf_details
from src.data.processors import sort_performance_data
import pandas as pd

def render_sector_rotation_page(sector_data: pd.DataFrame, etfs: dict, periods: list[str]) -> None:
    """
    Render the sector rotation page.
    
    Args:
        sector_data: DataFrame with sector performance data.
        etfs: Dict mapping ETF tickers to sector names.
        periods: List of periods (e.g., ['1d', '1mo']).
    """
    st.title("Stock Market Terminal - Sector Rotation Monitor")
    
    # Sidebar options
    st.sidebar.header("Terminal Options")
    sort_period = st.sidebar.selectbox("Sort Table by Period", periods, index=2)
    selected_ticker = st.sidebar.selectbox("Select Sector ETF for Details", list(etfs.keys()))
    
    # Sort data
    sorted_data = sort_performance_data(sector_data, sort_period)
    
    # Render table and chart
    st.subheader("Sector Rotation Performance (All Periods)")
    render_performance_table(sorted_data, periods)
    render_performance_chart(sorted_data, sort_period, periods)
    
    # Render ETF details
    if selected_ticker:
        render_etf_details(selected_ticker, etfs[selected_ticker])
    
    # Auto-refresh
    if st.sidebar.checkbox("Auto-refresh (every 5 minutes)", value=False):
        import time
        time.sleep(300)
        st.rerun()