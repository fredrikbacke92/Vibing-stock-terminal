import streamlit as st
import plotly.express as px
import pandas as pd
import yfinance as yf

def safe_format(value: float, fmt: str) -> str:
    """
    Format a value safely, handling NaN/None.
    
    Args:
        value: Value to format.
        fmt: Format string (e.g., '{:.2f}%' for percentage, '{:.1f}M' for volume in millions).
    
    Returns:
        Formatted string or '-' if invalid.
    """
    if pd.notnull(value):
        if fmt.endswith('M'):  # Handle millions format for volumes
            return f"{value / 1_000_000:.1f}M"
        return fmt.format(value)
    return "-"

def render_order_flow_table(df: pd.DataFrame, periods: list[str]) -> None:
    """
    Render a table of order flow scores.
    
    Args:
        df: DataFrame with order flow scores.
        periods: List of periods (e.g., ['1d', '1mo']).
    """
    format_dict = {
        'Short-term Order Flow Score': lambda x: safe_format(x, '{:.2f}'),
        'Long-term Order Flow Score': lambda x: safe_format(x, '{:.2f}')
    }
    format_dict.update({f'{p} Change (%)': lambda x: safe_format(x, '{:.2f}%') for p in periods})
    format_dict.update({f'{p} Volume': lambda x: safe_format(x, '{:.1f}M') for p in periods})
    st.dataframe(df[['Ticker', 'Sector', 'Short-term Order Flow Score', 'Long-term Order Flow Score'] + [f'{p} Change (%)' for p in periods] + [f'{p} Volume' for p in periods]].style.format(format_dict), width=1200)

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
        hover_data=['Ticker'] + [f'{p} Change (%)' for p in periods] + [f'{p} Volume' for p in periods]
    )
    st.plotly_chart(fig)

def render_order_flow_comparison_chart(hist_data: pd.DataFrame, selected_sector: str) -> None:
    """
    Render a line chart comparing historical Short-term and Long-term Order Flow Scores for a selected sector.
    
    Args:
        hist_data: DataFrame with historical [Date, Ticker, Sector, Short-term Order Flow Score, Long-term Order Flow Score].
        selected_sector: Selected sector to display.
    """
    sector_data = hist_data[hist_data['Sector'] == selected_sector]
    if sector_data.empty:
        st.warning(f"No historical data available for sector: {selected_sector}")
        return
    
    # Melt data for Plotly
    melted_data = pd.melt(
        sector_data,
        id_vars=['Date'],
        value_vars=['Short-term Order Flow Score', 'Long-term Order Flow Score'],
        var_name='Score Type',
        value_name='Order Flow Score'
    )
    
    fig = px.line(
        melted_data,
        x='Date',
        y='Order Flow Score',
        color='Score Type',
        title=f"1-Year Order Flow Scores for {selected_sector}",
        color_discrete_map={'Short-term Order Flow Score': '#00CC96', 'Long-term Order Flow Score': '#EF553B'},
        hover_data=['Order Flow Score']
    )
    fig.update_traces(mode='lines+markers', marker=dict(size=4))
    fig.update_layout(
        yaxis_title="Order Flow Score",
        xaxis_title="Date",
        showlegend=True,
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

def render_net_order_flow_chart(hist_data: pd.DataFrame) -> None:
    """
    Render a line chart showing historical net Short-term and Long-term Order Flow Scores across all sectors.
    
    Args:
        hist_data: DataFrame with historical [Date, Ticker, Sector, Short-term Order Flow Score, Long-term Order Flow Score].
    """
    if hist_data.empty:
        st.warning("No historical data available for net order flow chart.")
        return
    
    # Aggregate net scores by date (mean across sectors)
    net_scores = hist_data.groupby('Date').agg({
        'Short-term Order Flow Score': 'mean',
        'Long-term Order Flow Score': 'mean'
    }).reset_index()
    
    # Melt data for Plotly
    melted_data = pd.melt(
        net_scores,
        id_vars=['Date'],
        value_vars=['Short-term Order Flow Score', 'Long-term Order Flow Score'],
        var_name='Score Type',
        value_name='Net Order Flow Score'
    )
    
    fig = px.line(
        melted_data,
        x='Date',
        y='Net Order Flow Score',
        color='Score Type',
        title="1-Year Net Order Flow Scores Across All Sectors",
        color_discrete_map={'Short-term Order Flow Score': '#00CC96', 'Long-term Order Flow Score': '#EF553B'},
        hover_data=['Net Order Flow Score']
    )
    fig.update_traces(mode='lines+markers', marker=dict(size=4))
    fig.update_layout(
        yaxis_title="Net Order Flow Score",
        xaxis_title="Date",
        showlegend=True,
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

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