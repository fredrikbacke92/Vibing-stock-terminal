import streamlit as st
import plotly.express as px
import pandas as pd

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