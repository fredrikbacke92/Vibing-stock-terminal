import streamlit as st
import pandas as pd
import yaml
from datetime import datetime, timedelta
from src.ui.renderers.tables import render_order_flow_table
from src.ui.renderers.charts import render_order_flow_chart, render_order_flow_comparison_chart, render_net_order_flow_chart
from src.ui.renderers.details import render_etf_details, render_market_technical_indicators
from src.data.fetchers.etf_data import fetch_sector_performance, fetch_historical_sector_data
from src.data.processors.order_flow import calculate_order_flow_scores, calculate_historical_order_flow_scores
from src.data.processors.market_insights import generate_market_insights
from src.data.fetchers.financials import fetch_sector_financials, fetch_market_historical_financials, fetch_market_financials
from src.ui.utils.formatting import safe_format

def render_sector_rotation_page(sector_data: pd.DataFrame, etfs: dict, periods: list[str], period_weights: dict, short_term_periods: list[str], long_term_periods: list[str], thresholds: dict, sector_stocks: dict) -> None:
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
        sector_stocks: Dict mapping sector names to lists of stock tickers.
    """
    st.title("Stock Market Terminal - Sector Rotation Monitor")
    
    # Sidebar options
    st.sidebar.header("Terminal Options")
    sort_score = st.sidebar.selectbox("Sort Order Flow Table by", ['Long-term Order Flow Score', 'Short-term Order Flow Score'], index=0)
    selected_sector_indicators = st.sidebar.selectbox("Select Sector for Technical Indicators", sorted(list(set(etfs.values())) + ['Whole market']))
    selected_sector_comparison = st.sidebar.selectbox("Select Sector for Order Flow Comparison", sorted(list(set(etfs.values()))))
    selected_sector_financials = st.sidebar.selectbox("Select Sector for Financials", sorted(list(set(etfs.values())) + ['Whole market and historic']))
    
    # Map selected sector to ticker for ETF details
    ticker_for_indicators = None
    if selected_sector_indicators != 'Whole market':
        ticker_for_indicators = next(ticker for ticker, sector in etfs.items() if sector == selected_sector_indicators)
    
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
    st.subheader(f"1-Year Order Flow Comparison for {selected_sector_comparison}")
    render_order_flow_comparison_chart(hist_scores, selected_sector_comparison)
    
    # Render net order flow chart for all sectors
    st.subheader("1-Year Net Order Flow Across All Sectors")
    render_net_order_flow_chart(hist_scores)
    
    # Render technical indicators
    if selected_sector_indicators == 'Whole market':
        render_market_technical_indicators(etfs, sector_stocks)
    else:
        render_etf_details(ticker_for_indicators, selected_sector_indicators, sector_stocks)
    
    # Render aggregated financials based on selection
    st.subheader(f"{selected_sector_financials} financials")
    with st.spinner("Fetching financial data..."):
        if selected_sector_financials == 'Whole market and historic':
            hist_df = fetch_market_historical_financials(sector_stocks)
            if not hist_df.empty:
                formatted_df = hist_df.apply(lambda x: safe_format(x, '{:.2f}') if pd.notnull(x) else '-')
                st.dataframe(formatted_df.style.set_properties(**{'text-align': 'left'}), width=800)
            else:
                st.warning("No historical financial data available.")
        else:
            avg_fin = fetch_sector_financials(selected_sector_financials, sector_stocks)
            if not avg_fin.empty:
                financials = pd.DataFrame([
                    {'Metric': 'Trailing P/E', 'Value': avg_fin['trailing_pe'].iloc[0]},
                    {'Metric': 'Forward P/E', 'Value': avg_fin['forward_pe'].iloc[0]},
                    {'Metric': 'PEG Ratio', 'Value': avg_fin['peg_ratio'].iloc[0]},
                    {'Metric': 'Price/Sales (ttm)', 'Value': avg_fin['price_sales'].iloc[0]},
                    {'Metric': 'Price/Book', 'Value': avg_fin['price_book'].iloc[0]},
                ])
                financials['Value'] = financials['Value'].apply(lambda x: safe_format(x, '{:.2f}') if pd.notnull(x) else '-')
                st.dataframe(financials[['Metric', 'Value']].style.set_properties(**{'text-align': 'left'}), width=800)
            else:
                st.warning(f"No financial data available for sector: {selected_sector_financials}")
        
            # Aggregate all sectors table
            st.subheader("All Sectors Aggregate Financials")
            market_fin = fetch_market_financials(sector_stocks)
            if not market_fin.empty:
                market_financials = pd.DataFrame([
                    {'Metric': 'Trailing P/E', 'Value': market_fin['trailing_pe'].iloc[0]},
                    {'Metric': 'Forward P/E', 'Value': market_fin['forward_pe'].iloc[0]},
                    {'Metric': 'PEG Ratio', 'Value': market_fin['peg_ratio'].iloc[0]},
                    {'Metric': 'Price/Sales (ttm)', 'Value': market_fin['price_sales'].iloc[0]},
                    {'Metric': 'Price/Book', 'Value': market_fin['price_book'].iloc[0]},
                ])
                market_financials['Value'] = market_financials['Value'].apply(lambda x: safe_format(x, '{:.2f}') if pd.notnull(x) else '-')
                st.dataframe(market_financials[['Metric', 'Value']].style.set_properties(**{'text-align': 'left'}), width=800)
            else:
                st.warning("No aggregate financial data available.")
    
    # Auto-refresh
    if st.sidebar.checkbox("Auto-refresh (every 5 minutes)", value=False):
        import time
        time.sleep(300)
        st.rerun()