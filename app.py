# app.py
import streamlit as st
import yaml
from pathlib import Path
from src.data.fetchers.etf_data import fetch_sector_performance
from src.ui.pages.sector_rotation import render_sector_rotation_page
from src.ui.pages.options import render_options_page
from src.ui.pages.geo_flow import render_geo_flow_page

st.set_page_config(layout="wide")  # Make the app full-width for wider table

# Resolve path to config.yaml in config/ subfolder
config_path = Path(__file__).parent / 'config' / 'config.yaml'

try:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    st.error(f"Error: config.yaml not found at {config_path}. Please ensure the file exists in the config/ folder.")
    st.stop()

# Define pages for tabbed navigation
pages = [
    st.Page(
        lambda: render_sector_rotation_page(
            sector_data=fetch_sector_performance(config['periods']),
            etfs=config['etfs'],
            periods=config['periods'],
            period_weights=config['period_weights'],
            short_term_periods=config['short_term_periods'],
            long_term_periods=config['long_term_periods'],
            thresholds=config['thresholds'],
            sector_stocks=config['sector_stocks']
        ),
        title="Sector Rotation"
    ),
    st.Page(render_options_page, title="Options Chain"),
    st.Page(render_geo_flow_page, title="Geographical Flow")
]

# Render tabbed navigation
pg = st.navigation(pages)
pg.run()