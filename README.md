Stock Market Terminal
A Streamlit-based web app for monitoring stock market sector rotation using SPDR ETFs. Displays performance across multiple time periods (1d, 5d, 1mo, 3mo, 6mo, 1y) with interactive tables and charts.
Features

Sector rotation dashboard with performance metrics for SPDR ETFs.
Interactive bar charts and 1-year price history for selected ETFs.
Auto-refresh option for near-real-time updates.
Modular codebase for easy extension (e.g., watchlists, technical indicators).

Installation

Clone the repository:git clone https://github.com/yourusername/stock_terminal.git
cd stock_terminal


Create a virtual environment:python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate


Install dependencies:pip install -r requirements.txt


Run the app:streamlit run app.py


Open http://localhost:8501 in your browser.

Usage

Select a period to sort the sector performance table (e.g., 1mo).
Choose an ETF to view its price history and financials.
Enable auto-refresh for updates every 5 minutes.

Project Structure

app.py: Main entry point for the Streamlit app.
src/data/: Data fetching and processing logic.
src/models/: Data models (e.g., ETF class).
src/ui/: Streamlit UI components and pages.
config/: Configuration files (e.g., ETF tickers, periods).
tests/: Unit tests for data fetching and processing.

Testing
Run tests with:
pytest tests/

Contributing

Fork the repository.
Create a feature branch (git checkout -b feature/new-feature).
Commit changes (git commit -m "Add new feature").
Push to the branch (git push origin feature/new-feature).
Open a pull request.

License
MIT License (see LICENSE).
Notes

Data is sourced from Yahoo Finance via yfinance, which may have delays or rate limits.
For non-trading days (e.g., weekends), 1d performance uses the previous trading day's close.
