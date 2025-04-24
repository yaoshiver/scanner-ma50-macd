import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import cryptocompare

st.set_page_config(page_title="Scanner MA50 + MACD", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #f7f9fa; }
        h1, h2, h3 { color: #083759; }
        .st-bw { background-color: white; padding: 1em; border-radius: 10px; box-shadow: 0px 2px 6px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

st.title("Scanner Technique : MA50 + MACD")

with st.sidebar:
    st.header("Configuration")
    TICKERS_STOCKS = st.text_area("Actions (ex: AAPL,MSFT,GOOGL)", "AAPL,MSFT,NVDA").split(",")
    TICKERS_CRYPTOS = st.text_area("Cryptos (ex: BTC,ETH,SOL)", "BTC,ETH,SOL").split(",")

def get_stock_data(ticker):
    try:
        df = yf.download(ticker.strip(), period="3mo", interval="1d")
        df.dropna(inplace=True)
        return df
    except:
        return None

def get_crypto_data(symbol):
    try:
        hist = cryptocompare.get_historical_price_day(symbol.strip(), currency='USD', limit=90)
        df = pd.DataFrame(hist)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df.set_index("time", inplace=True)
        df.rename(columns={"close": "Close"}, inplace=True)
        return df
    except:
        return None

def check_conditions(df):
    if "Close" not in df.columns or len(df) < 60:
        return False

    try:
        ma50_indicator = ta.trend.SMAIndicator(close=df["Close"], window=50)
        df["MA50"] = ma50_indicator.sma_indicator()
        macd = ta.trend.MACD(close=df["Close"])
        df["MACD"] = macd.macd()
        df["MACD_SIGNAL"] = macd.macd_signal()

        if df[["MA50", "MACD", "MACD_SIGNAL"]].isna().any().any():
            return False

        is_above_ma = df["Close"].iloc[-1] > df["MA50"].iloc[-1]
        macd_now, macd_prev = df["MACD"].iloc[-1], df["MACD"].iloc[-2]
        signal_now, signal_prev = df["MACD_SIGNAL"].iloc[-1], df["MACD_SIGNAL"].iloc[-2]

        cross_up = macd_prev < signal_prev and macd_now > signal_now
        is_positive_zone = macd_now > 0 and signal_now > 0

        return is_above_ma and cross_up and is_positive_zone
    except:
        return False

st.header("Résultats du Scanner")

TIMEFRAMES = {
    "1d": "Daily",
    "1wk": "Weekly",
    "4h": "4h"
}

results = []

def process_ticker(ticker, is_crypto=False):
    result = {"Ticker": ticker.strip()}
    for interval, label in TIMEFRAMES.items():
        if is_crypto:
            df = get_crypto_data(ticker)
        else:
            try:
                df = yf.download(ticker.strip(), period="3mo", interval=interval)
                df.dropna(inplace=True)
            except:
                df = None

        if df is None or df.empty:
            result[label] = "❌"
        else:
            try:
                result[label] = "✅" if check_conditions(df) else "❌"
            except:
                result[label] = "❌"

    score = sum([1 for tf in TIMEFRAMES.values() if result.get(tf) == "✅"])
    result["Score"] = score
    return result

# Traiter tous les tickers
for ticker in TICKERS_STOCKS:
    if ticker.strip():
        results.append(process_ticker(ticker.strip(), is_crypto=False))

for crypto in TICKERS_CRYPTOS:
    if crypto.strip():
        results.append(process_ticker(crypto.strip(), is_crypto=True))

# Afficher le tableau
if results:
    df_results = pd.DataFrame(results).sort_values(by="Score", ascending=False)
    st.dataframe(df_results, use_container_width=True)
else:
    st.warning("Aucun actif n’a pu être analysé. Vérifiez vos tickers.")
