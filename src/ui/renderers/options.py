# src/ui/renderers/options.py
import streamlit as st
import plotly.express as px
import pandas as pd

def render_option_chain_table(df: pd.DataFrame, call_put: str) -> None:
    """
    Render an interactive option chain table with color-coding for ITM options.
    
    Args:
        df: Processed DataFrame with option chain data.
        call_put: 'calls' or 'puts' to indicate option type.
    """
    if df.empty:
        st.warning(f"No {call_put} data available for the selected ticker and expiration.")
        return
    
    # Format Implied Volatility for display
    df_display = df.copy()
    df_display['Implied Volatility'] = df_display['Implied Volatility'].apply(lambda x: f"{x*100:.2f}%" if pd.notnull(x) else '-')
    
    # Create Plotly table
    fig = px.scatter(df_display, x='Strike', y='Last Price', hover_data=df_display.columns, title=f"{call_put.capitalize()} Option Chain")
    
    # Style table (simulating a table with Plotly)
    fig.update_traces(
        marker=dict(size=0),  # Hide scatter points
        text=df_display.apply(lambda row: f"{'<b>ITM</b>' if row['ITM'] else 'OTM'}", axis=1),
        textposition='top center',
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"  # Ticker
            "Expiration: %{customdata[1]}<br>"  # Expiration
            "Strike: $%{x}<br>"
            "Last Price: $%{y}<br>"
            "Bid: $%{customdata[4]}<br>"
            "Ask: $%{customdata[5]}<br>"
            "Volume: %{customdata[6]}<br>"
            "Open Interest: %{customdata[7]}<br>"
            "Implied Volatility: %{customdata[8]}<br>"
            "Delta: %{customdata[9]}<br>"
            "<extra></extra>"
        ),
        customdata=df_display.values
    )
    
    # Color-code ITM (green for calls, red for puts)
    df_display['Color'] = df_display['ITM'].apply(lambda x: 'green' if x and call_put == 'calls' else 'red' if x and call_put == 'puts' else 'gray')
    fig.update_traces(marker=dict(color=df_display['Color']))
    
    fig.update_layout(
        showlegend=False,
        xaxis_title="Strike Price",
        yaxis_title="Last Price",
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add tooltip help
    st.markdown("""
    **Table Guide**:
    - **ITM**: In-the-money options (green for calls, red for puts).
    - **Strike**: Price at which the option can be exercised.
    - **Last Price**: Most recent trade price.
    - **Bid/Ask**: Current buy/sell quotes.
    - **Implied Volatility**: Expected price fluctuation (%).
    - **Delta**: Sensitivity of option price to underlying price change.
    - Hover over rows for details, click headers to sort.
    """)