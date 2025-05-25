import yfinance as yf
import pandas as pd
import os
import asyncio
from telegram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_telegram_message(message: str):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

# Add your favorite symbols here:
symbols = ["AAPL", "BTC-USD", "GC=F"]  # Apple, Bitcoin, Gold Futures

short_window = 20
long_window = 50

for symbol in symbols:
    print(f"🔍 Analyzing {symbol}")
    data = yf.download(symbol, period="6mo")

    if data.empty:
        print(f"❌ No data for {symbol}")
        asyncio.run(send_telegram_message(f"❌ No data found for {symbol}"))
        continue

    data["ShortMA"] = data["Close"].rolling(window=short_window).mean()
    data["LongMA"] = data["Close"].rolling(window=long_window).mean()
    data["Signal"] = 0
    data.loc[data.index[long_window:], "Signal"] = (
        data["ShortMA"][long_window:] > data["LongMA"][long_window:]
    ).astype(int)

    buy_signals = data[(data["Signal"] == 1) & (data["Signal"].shift(1) == 0)]
    sell_signals = data[(data["Signal"] == 0) & (data["Signal"].shift(1) == 1)]

    if not buy_signals.empty:
        latest = buy_signals.iloc[-1]
        message = f"📈 BUY signal for {symbol} at ${float(latest['Close']):.2f} on {latest.name.strftime('%Y-%m-%d')}"
        print(message)
        asyncio.run(send_telegram_message(message))
    elif not sell_signals.empty:
        latest = sell_signals.iloc[-1]
        message = f"📉 SELL signal for {symbol} at ${float(latest['Close']):.2f} on {latest.name.strftime('%Y-%m-%d')}"
        print(message)
        asyncio.run(send_telegram_message(message))
    else:
        print(f"ℹ️ No signals for {symbol} today.")
        asyncio.run(send_telegram_message(f"ℹ️ No signals for {symbol} today. ✅"))
