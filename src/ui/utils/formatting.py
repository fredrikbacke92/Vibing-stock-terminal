import pandas as pd

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