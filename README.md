Vibing Stock Terminal
A Streamlit-based web app for monitoring broad stock market activity. Vibe coding project, mostly for personal use.
Installation

Clone the repository:
```
clone https://github.com/fredrikbacke92/Vibing-stock-terminal.git
cd vibing_stock_terminal
```
Create a virtual environment:
```
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
Install dependencies:
```
install -r requirements.txt
```
Run the app:
```
streamlit run app.py
```
Open http://localhost:8501 in your browser.

Usage

Select a period to view market performance.
Choose an ETF for detailed charts and data.
Enable auto-refresh for updates every 5 minutes.

Project Structure
```
app.py: Main entry point.
src/data/: Data fetching and processing.
src/models/: Data models.
src/ui/: UI components and pages.
config/: Configuration files.
tests/: Unit tests.
```
Testing
Run tests:
```
pytest tests/

Notes

Uses Yahoo Finance via yfinance, which may have delays or rate limits.
On non-trading days, 1d performance uses the previous trading day’s close.

License
MIT License (see LICENSE).