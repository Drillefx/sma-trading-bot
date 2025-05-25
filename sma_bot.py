import yfinance as yf
import pandas as pd
import os
import telegram

# Load Telegram bot credentials from environment variables
token = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

bot = telegram.Bot(token=token)

symbols = ['AAPL', 'BTC-USD', 'GC=F']  # Apple, Bitcoin, Gold

short_window = 20
long_window = 50
has_signal = False

for symbol in symbols:
    print(f"🔍 Analyzing {symbol}")
    data = yf.download(symbol, start="2023-01-01", end="2024-12-31")

    if data.empty:
        print(f"❌ Failed to download data for {symbol}")
        continue

    # Calculate moving averages
    data['ShortMA'] = data['Close'].rolling(window=short_window).mean()
    data['LongMA'] = data['Close'].rolling(window=long_window).mean()
    data['Signal'] = 0
    data.loc[data.index[long_window:], 'Signal'] = (
        data['ShortMA'][long_window:] > data['LongMA'][long_window:]
    ).astype(int)

    # Find buy/sell signals
    buy_signals = data[(data['Signal'] == 1) & (data['Signal'].shift(1) == 0)]
    sell_signals = data[(data['Signal'] == 0) & (data['Signal'].shift(1) == 1)]

    # ✅ Extract latest close as float safely
    latest_price = float(data['Close'].iloc[-1])

    if not buy_signals.empty:
        has_signal = True
        bot.send_message(chat_id=chat_id, text=f"📈 BUY signal for {symbol} at ${latest_price:.2f}")

    if not sell_signals.empty:
        has_signal = True
        bot.send_message(chat_id=chat_id, text=f"📉 SELL signal for {symbol} at ${latest_price:.2f}")

# ✅ Fallback if nothing detected
if not has_signal:
    bot.send_message(chat_id=chat_id, text="📭 No trading signals found in this run.")
