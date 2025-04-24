import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import cryptocompare
from datetime import datetime, timedelta

st.set_page_config(page_title="Scanner MA50 + MACD", layout="wide")

st.title("Scanner d'opportunités - MA50 + MACD")

TICKERS_STOCKS = st.text_area("Liste des actions (séparées par des virgules)", "AAPL,MSFT,GOOGL,NVDA").split(",")
TICKERS_CRYPTOS = st.text_area("Liste des cryptos (séparées par des virgules)", "BTC,ETH,SOL,BNB").split(",")

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

    df["MA50"] = ta.trend.sma_indicator(df["Close"], window=50)
    macd = ta.trend.macd(df["Close"])
    signal = ta.trend.macd_signal(df["Close"])
    
    if macd.isna().sum() > 0 or signal.isna().sum() > 0:
        return False

    is_above_ma = df["Close"].iloc[-1] > df["MA50"].iloc[-1]
    macd_now, macd_prev = macd.iloc[-1], macd.iloc[-2]
    signal_now, signal_prev = signal.iloc[-1], signal.iloc[-2]

    cross_up = macd_prev < signal_prev and macd_now > signal_now
    is_positive_zone = macd_now > 0 and signal_now > 0

    return is_above_ma and cross_up and is_positive_zone
