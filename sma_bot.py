import yfinance as yf
import pandas as pd
import os
import asyncio
from telegram import Bot

# Load environment variables (from GitHub Secrets)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Define async function to send a Telegram message
async def send_telegram_message(message: str):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

# Stock symbol to analyze
symbol = "AAPL"

# SMA window settings
short_window = 20
long_window = 50

print(f"🔍 Analyzing {symbol}")
data = yf.download(symbol, period="6mo")  # Fetch recent data

if data.empty:
    print(f"❌ No data for {symbol}")
    asyncio.run(send_telegram_message(f"❌ No data found for {symbol}"))
    exit()

# Calculate moving averages
data["ShortMA"] = data["Close"].rolling(window=short_window).mean()
data["LongMA"] = data["Close"].rolling(window=long_window).mean()
data["Signal"] = 0
data.loc[data.index[long_window:], "Signal"] = (
    data["ShortMA"][long_window:] > data["LongMA"][long_window:]
).astype(int)

# Find buy and sell points
buy_signals = data[(data["Signal"] == 1) & (data["Signal"].shift(1) == 0)]
sell_signals = data[(data["Signal"] == 0) & (data["Signal"].shift(1) == 1)]

# Check and notify
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
    print("ℹ️ No signals today.")
    asyncio.run(send_telegram_message(f"ℹ️ No signals for {symbol} today. Bot ran successfully ✅"))
   
    asyncio.run(send_telegram_message("✅ Bot ran! Test message from GitHub Action."))


print(f"Using token: {TELEGRAM_TOKEN[:10]}... and chat_id: {TELEGRAM_CHAT_ID}")

