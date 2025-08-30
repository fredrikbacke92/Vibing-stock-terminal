import streamlit as st
import pandas as pd
from src.ui.utils.formatting import safe_format

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