import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta

st.set_page_config(page_title="Scanner MA50 Multi-timeframe", layout="wide")

st.markdown("""
    <style>
        h1, h2, h3 { color: #0a3d62; }
        .st-bw { background-color: white; padding: 1em; border-radius: 10px; box-shadow: 0px 2px 6px rgba(0,0,0,0.05); }
        .highlight { background-color: #f5f9ff; border-radius: 8px; padding: 0.5em }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Scanner MA50 Multi-timeframe")

with st.sidebar:
    st.header("Configuration")
    TICKERS = st.text_area("Actifs (Actions ou Cryptos ex: AAPL,BTC-USD,ETH-USD)", "AAPL,MSFT,BTC-USD,ETH-USD").split(",")

intervals = {
    "Daily": "1d",
    "Weekly": "1wk",
    "4h": "60m",
}

def fetch_data(ticker, interval):
    try:
        df = yf.download(ticker.strip(), period="6mo", interval=interval, progress=False)
        df.dropna(inplace=True)
        return df
    except:
        return None

def is_above_ma50(df):
    if df is None or "Close" not in df.columns or len(df) < 60:
        return False
    ma50 = ta.trend.sma_indicator(df["Close"], window=50)
    return df["Close"].iloc[-1] > ma50.iloc[-1]

# Construction du tableau final
results = []

for ticker in TICKERS:
    ticker = ticker.strip().upper()
    row = {"Ticker": ticker}
    score = 0
    for label, interval in intervals.items():
        df = fetch_data(ticker, interval)
        status = is_above_ma50(df)
        row[label] = "✅" if status else "❌"
        score += 1 if status else 0
    row["Score"] = score
    results.append(row)

# Affichage du tableau
st.subheader("📈 Résultats classés par force relative (MA50)")

df_results = pd.DataFrame(results)
df_results = df_results.sort_values(by="Score", ascending=False)

st.dataframe(df_results, use_container_width=True)

