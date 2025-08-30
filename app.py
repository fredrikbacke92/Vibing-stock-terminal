import streamlit as st
import yaml
from pathlib import Path
from src.data.fetchers import fetch_sector_performance
from src.ui.pages import render_sector_rotation_page

st.set_page_config(layout="wide")  # Make the app full-width for wider table

# Resolve path to config.yaml in config/ subfolder
config_path = Path(__file__).parent / 'config' / 'config.yaml'

try:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    st.error(f"Error: config.yaml not found at {config_path}. Please ensure the file exists in the config/ folder.")
    st.stop()

# Fetch sector data
sector_data = fetch_sector_performance(config['periods'])

# Render the sector rotation page
render_sector_rotation_page(
    sector_data=sector_data,
    etfs=config['etfs'],
    periods=config['periods'],
    period_weights=config['period_weights'],
    short_term_periods=config['short_term_periods'],
    long_term_periods=config['long_term_periods'],
    thresholds=config['thresholds']
)