import streamlit as st
import plotly.express as px
import pandas as pd
import yfinance as yf

def safe_format(value: float, fmt: str) -> str:
    """
    Format a value safely, handling NaN/None.
    
    Args:
        value: Value to format.
        fmt: Format string (e.g., '{:.2f}%').
    
    Returns:
        Formatted string or '-' if invalid.
    """
    return fmt.format(value) if pd.notnull(value) else "-"

def render_order_flow_table(df: pd.DataFrame, periods: list[str]) -> None:
    """
    Render a table of order flow scores.
    
    Args:
        df: DataFrame with order flow scores.
        periods: List of periods (e.g., ['1d', '1mo']).
    """
    format_dict = {
        'Price': lambda x: safe_format(x, '{:.2f}'),
        'Volume': lambda x: safe_format(x, '{:,.0f}'),
        'Short-term Order Flow Score': lambda x: safe_format(x, '{:.2f}'),
        'Long-term Order Flow Score': lambda x: safe_format(x, '{:.2f}')
    }
    format_dict.update({f'{p} Change (%)': lambda x: safe_format(x, '{:.2f}%') for p in periods})
    format_dict.update({f'{p} Volume': lambda x: safe_format(x, '{:,.0f}') for p in periods})
    st.dataframe(df[['Ticker', 'Sector', 'Short-term Order Flow Score', 'Long-term Order Flow Score'] + [f'{p} Change (%)' for p in periods] + [f'{p} Volume' for p in periods]].style.format(format_dict))

def render_order_flow_chart(df: pd.DataFrame, sort_score: str, periods: list[str]) -> None:
    """
    Render a bar chart of order flow scores.
    
    Args:
        df: DataFrame with order flow scores.
        sort_score: Score to display ('Short-term Order Flow Score' or 'Long-term Order Flow Score').
        periods: List of periods for hover data.
    """
    fig = px.bar(
        df,
        x='Sector',
        y=sort_score,
        title=f"{sort_score} by Sector",
        color=sort_score,
        color_continuous_scale='RdYlGn',
        hover_data=['Ticker', 'Price', 'Volume'] + [f'{p} Change (%)' for p in periods] + [f'{p} Volume' for p in periods]
    )
    st.plotly_chart(fig)

def render_etf_details(ticker: str, sector: str) -> None:
    """
    Render details for a selected ETF.
    
    Args:
        ticker: ETF ticker symbol.
        sector: ETF sector name.
    """
    st.subheader(f"Details for {ticker} ({sector})")
    yf_ticker = yf.Ticker(ticker)
    history = yf_ticker.history(period='1y')
    if not history.empty:
        fig = px.line(history, x=history.index, y='Close', title=f"{ticker} 1-Year Price History")
        st.plotly_chart(fig)
    
    st.subheader("Key Info")
    info = yf_ticker.info
    info_df = pd.DataFrame.from_dict(info, orient='index', columns=['Value'])
    info_df['Value'] = info_df['Value'].astype(str)  # Fix Arrow serialization
    st.dataframe(info_df)
    
    st.subheader("Recent Financials")
    financials = yf_ticker.financials
    if not financials.empty:
        st.dataframe(financials)