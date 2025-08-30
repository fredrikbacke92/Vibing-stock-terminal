# src/ui/pages/options.py
import streamlit as st
from src.data.fetchers.options import fetch_option_chain
from src.data.processors.options import process_option_chain, generate_option_insights, generate_overall_sentiment
from src.ui.renderers.options import render_option_chain_table
import yfinance as yf

def render_options_page():
    """
    Render the options chain page with interactive table, descriptive insights, and overall sentiment.
    """
    st.title("Options Chain")
    
    # Sidebar for ETF and expiration selection
    st.sidebar.header("Options Chain Options")
    etfs = {
        'XLV': 'Health Care',
        'XLI': 'Industrials',
        'XLK': 'Technology',
        'XLRE': 'Real Estate',
        'XLE': 'Energy',
        'XLP': 'Consumer Staples',
        'XLY': 'Consumer Discretionary',
        'XLF': 'Financials',
        'XLC': 'Communication Services',
        'XLU': 'Utilities',
        'XLB': 'Materials',
        'XBI': 'Biotechnology'
    }
    selected_ticker = st.sidebar.selectbox("Select ETF", options=list(etfs.keys()), format_func=lambda x: f"{x} ({etfs[x]})")
    
    # Fetch option chain to get expiration dates
    option_data = fetch_option_chain(selected_ticker)
    expiration_dates = option_data.get('expiration_dates', [])
    
    if not expiration_dates:
        st.error("No expiration dates available for the selected ETF.")
        return
    
    selected_expiration = st.sidebar.selectbox("Select Expiration Date", options=expiration_dates)
    call_put = st.sidebar.radio("Select Option Type", ['Calls', 'Puts'], index=0).lower()
    
    # Fetch current price for ITM calculation and insights
    yf_ticker = yf.Ticker(selected_ticker)
    current_price = yf_ticker.history(period='1d')['Close'].iloc[-1] if not yf_ticker.history(period='1d').empty else 0.0
    
    # Process and render option chain
    with st.spinner("Fetching option chain data..."):
        option_data = fetch_option_chain(selected_ticker, selected_expiration)
        processed_data = process_option_chain(option_data, call_put, current_price)
        st.subheader(f"{call_put.capitalize()} Option Chain for {selected_ticker} ({etfs[selected_ticker]})")
        render_option_chain_table(processed_data, call_put)
        st.markdown("---")
        
        # Generate insights
        st.subheader("What the Market Says")
        insights = generate_option_insights(processed_data, call_put, current_price)
        st.markdown(insights)
        st.markdown("---")
        
        # Generate overall sentiment
        st.subheader("Overall Market Sentiment")
        full_option_data = fetch_option_chain(selected_ticker, selected_expiration)
        sentiment = generate_overall_sentiment(full_option_data, current_price)
        st.markdown(sentiment)