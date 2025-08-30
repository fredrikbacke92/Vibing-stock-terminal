import pandas as pd

def sort_performance_data(df: pd.DataFrame, sort_period: str) -> pd.DataFrame:
    """
    Sort performance data by the specified period.
    
    Args:
        df: DataFrame with performance data.
        sort_period: Period to sort by (e.g., '1mo').
    
    Returns:
        Sorted DataFrame.
    """
    return df.sort_values(f'{sort_period} Change (%)', ascending=False, na_position='last')