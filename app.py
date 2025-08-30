import streamlit as st
from src.ui.pages import render_sector_rotation_page
from src.data.fetchers import fetch_sector_performance
import yaml
import os

def load_config():
    """Load configuration from config.yaml."""
    with open(os.path.join("config", "config.yaml"), "r") as f:
        return yaml.safe_load(f)

def main():
    """Main entry point for the Streamlit app."""
    st.set_page_config(page_title="Stock Market Terminal", layout="wide")
    config = load_config()
    sector_data = fetch_sector_performance(config["periods"])
    render_sector_rotation_page(sector_data, config["etfs"], config["periods"], config["period_weights"])

if __name__ == "__main__":
    main()