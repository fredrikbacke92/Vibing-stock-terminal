import pytest
import pandas as pd
from src.data.fetchers import fetch_sector_performance

def test_fetch_sector_performance():
    """Test fetching sector performance data."""
    periods = ['1d', '1mo']
    df = fetch_sector_performance(periods)
    assert isinstance(df, pd.DataFrame)
    assert 'Ticker' in df.columns
    assert 'Sector' in df.columns
    assert 'Price' in df.columns
    assert all(f'{p} Change (%)' in df.columns for p in periods)