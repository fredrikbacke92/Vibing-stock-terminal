import pytest
import pandas as pd
from src.data.processors import sort_performance_data

def test_sort_performance_data():
    """Test sorting performance data."""
    df = pd.DataFrame({
        'Ticker': ['XLV', 'XLK'],
        'Sector': ['Health Care', 'Technology'],
        '1mo Change (%)': [5.0, 2.0]
    })
    sorted_df = sort_performance_data(df, '1mo')
    assert sorted_df.iloc[0]['Ticker'] == 'XLV'
    assert sorted_df.iloc[1]['Ticker'] == 'XLK'