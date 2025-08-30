import streamlit as st
import plotly.express as px
import pandas as pd
import yfinance as yf
import numpy as np
from src.ui.utils.formatting import safe_format

def render_etf_details(ticker: str, sector: str, sector_stocks: dict) -> None:
    """
    Render details for a selected ETF, including enhanced technical indicators.
    
    Args:
        ticker: ETF ticker symbol.
        sector: ETF sector name.
        sector_stocks: Dict of sector to list of stock tickers.
    """
    st.subheader(f"Details for {ticker} ({sector})")
    yf_ticker = yf.Ticker(ticker)
    history = yf_ticker.history(period='1y')
    if not history.empty:
        fig = px.line(history, x=history.index, y='Close', title=f"{ticker} 1-Year Price History")
        st.plotly_chart(fig)
    
    # Calculate technical indicators
    st.subheader("Technical Indicators")
    if history.empty:
        st.warning(f"No historical data available for {ticker}")
        return
    
    # Ensure history is sorted by date
    history = history.sort_index()
    
    current_price = history['Close'].iloc[-1]
    
    # SMA (20-day, 50-day, 200-day)
    sma_20 = history['Close'].rolling(window=20).mean().iloc[-1]
    sma_20_pct = ((current_price - sma_20) / sma_20 * 100) if pd.notnull(sma_20) else np.nan
    sma_20_interpret = f"Bullish ({sma_20_pct:.2f}% above)" if sma_20_pct > 1 else f"Bearish ({abs(sma_20_pct):.2f}% below)" if sma_20_pct < -1 else "Neutral/mixed (within ±1% of SMA)"
    
    sma_50 = history['Close'].rolling(window=50).mean().iloc[-1]
    sma_50_pct = ((current_price - sma_50) / sma_50 * 100) if pd.notnull(sma_50) else np.nan
    sma_50_interpret = f"Bullish ({sma_50_pct:.2f}% above)" if sma_50_pct > 1 else f"Bearish ({abs(sma_50_pct):.2f}% below)" if sma_50_pct < -1 else "Neutral/mixed (within ±1% of SMA)"
    
    sma_200 = history['Close'].rolling(window=200).mean().iloc[-1] if len(history) >= 200 else np.nan
    sma_200_pct = ((current_price - sma_200) / sma_200 * 100) if pd.notnull(sma_200) else np.nan
    sma_200_interpret = f"Bullish ({sma_200_pct:.2f}% above)" if sma_200_pct > 1 else f"Bearish ({abs(sma_200_pct):.2f}% below)" if sma_200_pct < -1 else "Neutral/mixed (within ±1% of SMA)"
    
    # RSI (14-day, 50-day)
    delta = history['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain_14 = gain.rolling(window=14).mean().iloc[-1]
    avg_loss_14 = loss.rolling(window=14).mean().iloc[-1]
    rs_14 = avg_gain_14 / avg_loss_14 if avg_loss_14 != 0 else np.nan
    rsi_14 = 100 - (100 / (1 + rs_14)) if pd.notnull(rs_14) else np.nan
    
    avg_gain_50 = gain.rolling(window=50).mean().iloc[-1]
    avg_loss_50 = loss.rolling(window=50).mean().iloc[-1]
    rs_50 = avg_gain_50 / avg_loss_50 if avg_loss_50 != 0 else np.nan
    rsi_50 = 100 - (100 / (1 + rs_50)) if pd.notnull(rs_50) else np.nan
    
    # ATR (14-day, 50-day)
    true_range = pd.concat([
        history['High'] - history['Low'],
        (history['High'] - history['Close'].shift()).abs(),
        (history['Low'] - history['Close'].shift()).abs()
    ], axis=1).max(axis=1)
    atr_50 = true_range.rolling(window=50).mean().iloc[-1]
    atr_14 = true_range.rolling(window=14).mean().iloc[-1]
    atr_14_pct = (atr_14 / current_price * 100) if pd.notnull(atr_14) and current_price != 0 else np.nan
    atr_50_pct = (atr_50 / current_price * 100) if pd.notnull(atr_50) and current_price != 0 else np.nan
    atr_200 = true_range.rolling(window=200).mean().iloc[-1] if len(history) >= 200 else np.nan
    
    # ROC
    roc_14 = ((current_price - history['Close'].shift(14).iloc[-1]) / history['Close'].shift(14).iloc[-1] * 100) if len(history) > 14 else np.nan
    roc_50 = ((current_price - history['Close'].shift(50).iloc[-1]) / history['Close'].shift(50).iloc[-1] * 100) if len(history) > 50 else np.nan
    
    # Interpretations
    rsi_14_interpret = f"Overbought (sell signal, {rsi_14:.2f} > 70)" if rsi_14 > 70 else f"Oversold (buy signal, {rsi_14:.2f} < 30)" if rsi_14 < 30 else f"Neutral (momentum {'strengthening' if rsi_14 > 50 else 'weakening' if rsi_14 < 50 else 'stable'})"
    rsi_50_interpret = f"Overbought (sell signal, {rsi_50:.2f} > 70)" if rsi_50 > 70 else f"Oversold (buy signal, {rsi_50:.2f} < 30)" if rsi_50 < 30 else f"Neutral (momentum {'strong' if rsi_50 > 50 else 'weak' if rsi_50 < 50 else 'stable'})"
    atr_14_interpret = f"High volatility ({atr_14_pct:.2f}% of price, ATR > 50-day)" if atr_14_pct > atr_50_pct else f"Low volatility ({atr_14_pct:.2f}% of price, ATR < 50-day)" if atr_14_pct < atr_50_pct else f"Neutral volatility ({atr_14_pct:.2f}% of price)"
    atr_50_interpret = f"High volatility ({atr_50_pct:.2f}% of price)" if atr_50_pct > atr_14_pct else f"Low volatility ({atr_50_pct:.2f}% of price)" if atr_50_pct < atr_14_pct else f"Neutral volatility ({atr_50_pct:.2f}% of price)"
    roc_14_interpret = f"Bullish ({roc_14:.2f}% change)" if roc_14 > 0 else f"Bearish ({abs(roc_14):.2f}% change)" if roc_14 < 0 else "Neutral (no change)"
    roc_50_interpret = f"Bullish ({roc_50:.2f}% change)" if roc_50 > 0 else f"Bearish ({abs(roc_50):.2f}% change)" if roc_50 < 0 else "Neutral (no change)"
    
    # Overall Sentiment
    signals = [
        (1, 1 if sma_20_pct > 1 else -1 if sma_20_pct < -1 else 0),  # Short SMA
        (0.5, 1 if sma_50_pct > 1 else -1 if sma_50_pct < -1 else 0),  # Mid SMA
        (0.5, 1 if sma_200_pct > 1 else -1 if sma_200_pct < -1 else 0),  # Long SMA
        (1, 1 if rsi_14 > 70 else -1 if rsi_14 < 30 else 1 if rsi_14 > 50 else -1 if rsi_14 < 50 else 0),  # Short RSI
        (0.5, 1 if rsi_50 > 70 else -1 if rsi_50 < 30 else 1 if rsi_50 > 50 else -1 if rsi_50 < 50 else 0),  # Long RSI
        (1, 1 if atr_14_pct > atr_50_pct else -1 if atr_14_pct < atr_50_pct else 0),  # Short ATR
        (0.5, 1 if atr_50_pct > atr_14_pct else -1 if atr_50_pct < atr_14_pct else 0),  # Long ATR
        (1, 1 if roc_14 > 0 else -1 if roc_14 < 0 else 0),  # Short ROC
        (0.5, 1 if roc_50 > 0 else -1 if roc_50 < 0 else 0)  # Long ROC
    ]
    sentiment_score = sum(weight * signal for weight, signal in signals)
    overall_interpret = ("Bullish overall (short-term strength)" if sentiment_score > 1 else
                        "Bearish overall (long-term weakness)" if sentiment_score < -1 else
                        "Mixed/neutral signals")
    
    # Create indicators table
    indicators = pd.DataFrame([
        {'Indicator': '20-day SMA %', 'Value': sma_20_pct, 'Interpretation': sma_20_interpret},
        {'Indicator': '50-day SMA %', 'Value': sma_50_pct, 'Interpretation': sma_50_interpret},
        {'Indicator': '200-day SMA %', 'Value': sma_200_pct, 'Interpretation': sma_200_interpret},
        {'Indicator': '14-day RSI', 'Value': rsi_14, 'Interpretation': rsi_14_interpret},
        {'Indicator': '50-day RSI', 'Value': rsi_50, 'Interpretation': rsi_50_interpret},
        {'Indicator': '14-day ATR %', 'Value': atr_14_pct, 'Interpretation': atr_14_interpret},
        {'Indicator': '50-day ATR %', 'Value': atr_50_pct, 'Interpretation': atr_50_interpret},
        {'Indicator': '14-day ROC', 'Value': roc_14, 'Interpretation': roc_14_interpret},
        {'Indicator': '50-day ROC', 'Value': roc_50, 'Interpretation': roc_50_interpret},
        {'Indicator': 'Overall Sentiment', 'Value': '-', 'Interpretation': overall_interpret}
    ])
    indicators['Value'] = indicators['Value'].apply(lambda x: safe_format(x, '{:.2f}') if isinstance(x, (int, float)) else x)
    st.dataframe(indicators[['Indicator', 'Value', 'Interpretation']].style.set_properties(**{'text-align': 'left'}), width=800)

def render_market_technical_indicators(etfs: dict, sector_stocks: dict) -> None:
    """
    Render technical indicators averaged across all sector ETFs/stocks.
    
    Args:
        etfs: Dict mapping ETF tickers to sector names.
        sector_stocks: Dict of sector to list of stock tickers.
    """
    indicators_data = []
    for ticker, sector in etfs.items():
        yf_ticker = yf.Ticker(ticker)
        history = yf_ticker.history(period='1y')
        if history.empty:
            continue
        
        # Ensure history is sorted by date
        history = history.sort_index()
        
        current_price = history['Close'].iloc[-1]
        
        # SMA (20-day, 50-day, 200-day)
        sma_20 = history['Close'].rolling(window=20).mean().iloc[-1]
        sma_20_pct = ((current_price - sma_20) / sma_20 * 100) if pd.notnull(sma_20) else np.nan
        
        sma_50 = history['Close'].rolling(window=50).mean().iloc[-1]
        sma_50_pct = ((current_price - sma_50) / sma_50 * 100) if pd.notnull(sma_50) else np.nan
        
        sma_200 = history['Close'].rolling(window=200).mean().iloc[-1] if len(history) >= 200 else np.nan
        sma_200_pct = ((current_price - sma_200) / sma_200 * 100) if pd.notnull(sma_200) else np.nan
        
        # RSI (14-day, 50-day)
        delta = history['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain_14 = gain.rolling(window=14).mean().iloc[-1]
        avg_loss_14 = loss.rolling(window=14).mean().iloc[-1]
        rs_14 = avg_gain_14 / avg_loss_14 if avg_loss_14 != 0 else np.nan
        rsi_14 = 100 - (100 / (1 + rs_14)) if pd.notnull(rs_14) else np.nan
        
        avg_gain_50 = gain.rolling(window=50).mean().iloc[-1]
        avg_loss_50 = loss.rolling(window=50).mean().iloc[-1]
        rs_50 = avg_gain_50 / avg_loss_50 if avg_loss_50 != 0 else np.nan
        rsi_50 = 100 - (100 / (1 + rs_50)) if pd.notnull(rs_50) else np.nan
        
        # ATR (14-day, 50-day)
        true_range = pd.concat([
            history['High'] - history['Low'],
            (history['High'] - history['Close'].shift()).abs(),
            (history['Low'] - history['Close'].shift()).abs()
        ], axis=1).max(axis=1)
        atr_50 = true_range.rolling(window=50).mean().iloc[-1]
        atr_14 = true_range.rolling(window=14).mean().iloc[-1]
        atr_14_pct = (atr_14 / current_price * 100) if pd.notnull(atr_14) and current_price != 0 else np.nan
        atr_50_pct = (atr_50 / current_price * 100) if pd.notnull(atr_50) and current_price != 0 else np.nan
        
        # ROC
        roc_14 = ((current_price - history['Close'].shift(14).iloc[-1]) / history['Close'].shift(14).iloc[-1] * 100) if len(history) > 14 else np.nan
        roc_50 = ((current_price - history['Close'].shift(50).iloc[-1]) / history['Close'].shift(50).iloc[-1] * 100) if len(history) > 50 else np.nan
        
        indicators_data.append({
            'Ticker': ticker,
            'sma_20_pct': sma_20_pct,
            'sma_50_pct': sma_50_pct,
            'sma_200_pct': sma_200_pct,
            'rsi_14': rsi_14,
            'rsi_50': rsi_50,
            'atr_14_pct': atr_14_pct,
            'atr_50_pct': atr_50_pct,
            'roc_14': roc_14,
            'roc_50': roc_50
        })
    
    if not indicators_data:
        st.warning("No historical data available for market indicators.")
        return
    
    # Aggregate averages
    avg_df = pd.DataFrame(indicators_data).mean(numeric_only=True, skipna=True)
    
    # Interpretations
    sma_20_interpret = f"Bullish ({avg_df['sma_20_pct']:.2f}% above)" if avg_df['sma_20_pct'] > 1 else f"Bearish ({abs(avg_df['sma_20_pct']):.2f}% below)" if avg_df['sma_20_pct'] < -1 else "Neutral/mixed (within ±1% of SMA)"
    sma_50_interpret = f"Bullish ({avg_df['sma_50_pct']:.2f}% above)" if avg_df['sma_50_pct'] > 1 else f"Bearish ({abs(avg_df['sma_50_pct']):.2f}% below)" if avg_df['sma_50_pct'] < -1 else "Neutral/mixed (within ±1% of SMA)"
    sma_200_interpret = f"Bullish ({avg_df['sma_200_pct']:.2f}% above)" if avg_df['sma_200_pct'] > 1 else f"Bearish ({abs(avg_df['sma_200_pct']):.2f}% below)" if avg_df['sma_200_pct'] < -1 else "Neutral/mixed (within ±1% of SMA)"
    rsi_14_interpret = f"Overbought (sell signal, {avg_df['rsi_14']:.2f} > 70)" if avg_df['rsi_14'] > 70 else f"Oversold (buy signal, {avg_df['rsi_14']:.2f} < 30)" if avg_df['rsi_14'] < 30 else f"Neutral (momentum {'strengthening' if avg_df['rsi_14'] > 50 else 'weakening' if avg_df['rsi_14'] < 50 else 'stable'})"
    rsi_50_interpret = f"Overbought (sell signal, {avg_df['rsi_50']:.2f} > 70)" if avg_df['rsi_50'] > 70 else f"Oversold (buy signal, {avg_df['rsi_50']:.2f} < 30)" if avg_df['rsi_50'] < 30 else f"Neutral (momentum {'strong' if avg_df['rsi_50'] > 50 else 'weak' if avg_df['rsi_50'] < 50 else 'stable'})"
    atr_14_interpret = f"High volatility ({avg_df['atr_14_pct']:.2f}% of price, ATR > 50-day)" if avg_df['atr_14_pct'] > avg_df['atr_50_pct'] else f"Low volatility ({avg_df['atr_14_pct']:.2f}% of price, ATR < 50-day)" if avg_df['atr_14_pct'] < avg_df['atr_50_pct'] else f"Neutral volatility ({avg_df['atr_14_pct']:.2f}% of price)"
    atr_50_interpret = f"High volatility ({avg_df['atr_50_pct']:.2f}% of price)" if avg_df['atr_50_pct'] > avg_df['atr_14_pct'] else f"Low volatility ({avg_df['atr_50_pct']:.2f}% of price)" if avg_df['atr_50_pct'] < avg_df['atr_14_pct'] else f"Neutral volatility ({avg_df['atr_50_pct']:.2f}% of price)"
    roc_14_interpret = f"Bullish ({avg_df['roc_14']:.2f}% change)" if avg_df['roc_14'] > 0 else f"Bearish ({abs(avg_df['roc_14']):.2f}% change)" if avg_df['roc_14'] < 0 else "Neutral (no change)"
    roc_50_interpret = f"Bullish ({avg_df['roc_50']:.2f}% change)" if avg_df['roc_50'] > 0 else f"Bearish ({abs(avg_df['roc_50']):.2f}% change)" if avg_df['roc_50'] < 0 else "Neutral (no change)"
    
    # Overall Sentiment
    signals = [
        (1, 1 if avg_df['sma_20_pct'] > 1 else -1 if avg_df['sma_20_pct'] < -1 else 0),  # Short SMA
        (0.5, 1 if avg_df['sma_50_pct'] > 1 else -1 if avg_df['sma_50_pct'] < -1 else 0),  # Mid SMA
        (0.5, 1 if avg_df['sma_200_pct'] > 1 else -1 if avg_df['sma_200_pct'] < -1 else 0),  # Long SMA
        (1, 1 if avg_df['rsi_14'] > 70 else -1 if avg_df['rsi_14'] < 30 else 1 if avg_df['rsi_14'] > 50 else -1 if avg_df['rsi_14'] < 50 else 0),  # Short RSI
        (0.5, 1 if avg_df['rsi_50'] > 70 else -1 if avg_df['rsi_50'] < 30 else 1 if avg_df['rsi_50'] > 50 else -1 if avg_df['rsi_50'] < 50 else 0),  # Long RSI
        (1, 1 if avg_df['atr_14_pct'] > avg_df['atr_50_pct'] else -1 if avg_df['atr_14_pct'] < avg_df['atr_50_pct'] else 0),  # Short ATR
        (0.5, 1 if avg_df['atr_50_pct'] > avg_df['atr_14_pct'] else -1 if avg_df['atr_50_pct'] < avg_df['atr_14_pct'] else 0),  # Long ATR
        (1, 1 if avg_df['roc_14'] > 0 else -1 if avg_df['roc_14'] < 0 else 0),  # Short ROC
        (0.5, 1 if avg_df['roc_50'] > 0 else -1 if avg_df['roc_50'] < 0 else 0)  # Long ROC
    ]
    sentiment_score = sum(weight * signal for weight, signal in signals)
    overall_interpret = ("Bullish overall (short-term strength)" if sentiment_score > 1 else
                        "Bearish overall (long-term weakness)" if sentiment_score < -1 else
                        "Mixed/neutral signals")
    
    # Create indicators table
    indicators = pd.DataFrame([
        {'Indicator': '20-day SMA %', 'Value': avg_df['sma_20_pct'], 'Interpretation': sma_20_interpret},
        {'Indicator': '50-day SMA %', 'Value': avg_df['sma_50_pct'], 'Interpretation': sma_50_interpret},
        {'Indicator': '200-day SMA %', 'Value': avg_df['sma_200_pct'], 'Interpretation': sma_200_interpret},
        {'Indicator': '14-day RSI', 'Value': avg_df['rsi_14'], 'Interpretation': rsi_14_interpret},
        {'Indicator': '50-day RSI', 'Value': avg_df['rsi_50'], 'Interpretation': rsi_50_interpret},
        {'Indicator': '14-day ATR %', 'Value': avg_df['atr_14_pct'], 'Interpretation': atr_14_interpret},
        {'Indicator': '50-day ATR %', 'Value': avg_df['atr_50_pct'], 'Interpretation': atr_50_interpret},
        {'Indicator': '14-day ROC', 'Value': avg_df['roc_14'], 'Interpretation': roc_14_interpret},
        {'Indicator': '50-day ROC', 'Value': avg_df['roc_50'], 'Interpretation': roc_50_interpret},
        {'Indicator': 'Overall Sentiment', 'Value': '-', 'Interpretation': overall_interpret}
    ])
    indicators['Value'] = indicators['Value'].apply(lambda x: safe_format(x, '{:.2f}') if isinstance(x, (int, float)) else x)
    st.dataframe(indicators[['Indicator', 'Value', 'Interpretation']].style.set_properties(**{'text-align': 'left'}), width=800)