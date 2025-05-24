import os
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import telegram

# Telegram bot setup
bot = telegram.Bot(token=os.getenv("TELEGRAM_TOKEN"))
chat_id = os.getenv("TELEGRAM_CHAT_ID")
from telegram import Bot
import os

# Telegram setup
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = Bot(token=TELEGRAM_TOKEN)

# Symbols to track
symbols = ['AAPL', 'BTC-USD', 'GC=F']
short_window = 20
long_window = 50

for symbol in symbols:
    print(f"🔍 Analyzing {symbol}")
    data = yf.download(symbol, start="2023-01-01", end="2024-12-31")

    if data.empty:
        print(f"❌ Failed to download data for {symbol}")
        bot.send_message(chat_id=chat_id, text=f"❌ Failed to fetch data for {symbol}")
    data = yf.download(symbol, start="2023-01-01")

    if data.empty:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⚠️ Failed to get data for {symbol}")
        continue

    data['ShortMA'] = data['Close'].rolling(window=short_window).mean()
    data['LongMA'] = data['Close'].rolling(window=long_window).mean()
    data['Signal'] = 0
    data.loc[data.index[long_window:], 'Signal'] = (
        data['ShortMA'][long_window:] > data['LongMA'][long_window:]
    ).astype(int)

    # Detect Buy/Sell
    buy_signals = data[(data['Signal'] == 1) & (data['Signal'].shift(1) == 0)]
    sell_signals = data[(data['Signal'] == 0) & (data['Signal'].shift(1) == 1)]

    latest_price = data['Close'].iloc[-1]

    # Telegram alerts
    if not buy_signals.empty:
        latest_price = buy_signals['Close'].iloc[-1]
        bot.send_message(chat_id=chat_id, text=f"📈 BUY signal for {symbol} at ${latest_price:.2f}")
    elif not sell_signals.empty:
        latest_price = sell_signals['Close'].iloc[-1]
        bot.send_message(chat_id=chat_id, text=f"📉 SELL signal for {symbol} at ${latest_price:.2f}")
    else:
        bot.send_message(chat_id=chat_id, text=f"⏱ No signal for {symbol} this hour. SMA bot ran successfully.")


    if not buy_signals.empty:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"📈 BUY signal for {symbol} at ${latest_price:.2f}")
    elif not sell_signals.empty:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"📉 SELL signal for {symbol} at ${latest_price:.2f}")
    else:
        # ✅ Fallback message if no signals
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⏳ No signals for {symbol}. Last price: ${latest_price:.2f}")

