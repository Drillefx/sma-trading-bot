import os
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import telegram

# Telegram bot setup
bot = telegram.Bot(token=os.getenv("TELEGRAM_TOKEN"))
chat_id = os.getenv("TELEGRAM_CHAT_ID")

# List of symbols to analyze
symbols = ['AAPL', 'BTC-USD', 'GC=F']  # Apple, Bitcoin, Gold Futures

# SMA parameters
short_window = 20
long_window = 50

for symbol in symbols:
    print(f"🔍 Analyzing {symbol}")
    data = yf.download(symbol, start="2023-01-01", end="2024-12-31")

    if data.empty:
        print(f"❌ Failed to download data for {symbol}")
        bot.send_message(chat_id=chat_id, text=f"❌ Failed to fetch data for {symbol}")
        continue

    # Calculate moving averages
    data['ShortMA'] = data['Close'].rolling(window=short_window).mean()
    data['LongMA'] = data['Close'].rolling(window=long_window).mean()
    data['Signal'] = 0
    data.loc[data.index[long_window:], 'Signal'] = (
        data['ShortMA'][long_window:] > data['LongMA'][long_window:]
    )

    # Identify signals
    buy_signals = data[(data['Signal'] == 1) & (data['Signal'].shift(1) == 0)]
    sell_signals = data[(data['Signal'] == 0) & (data['Signal'].shift(1) == 1)]

    print("📈 Buy Signals:")
    print(buy_signals[['Close']])
    print("📉 Sell Signals:")
    print(sell_signals[['Close']])

    # Telegram alerts
    if not buy_signals.empty:
        latest_price = buy_signals['Close'].iloc[-1]
        bot.send_message(chat_id=chat_id, text=f"📈 BUY signal for {symbol} at ${latest_price:.2f}")
    elif not sell_signals.empty:
        latest_price = sell_signals['Close'].iloc[-1]
        bot.send_message(chat_id=chat_id, text=f"📉 SELL signal for {symbol} at ${latest_price:.2f}")
    else:
        bot.send_message(chat_id=chat_id, text=f"⏱ No signal for {symbol} this hour. SMA bot ran successfully.")



    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(data['Close'], label='Close Price', alpha=0.5)
    plt.plot(data['ShortMA'], label=f'{short_window}-day SMA')
    plt.plot(data['LongMA'], label=f'{long_window}-day SMA')
    plt.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', label='Buy Signal', s=100)
    plt.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', label='Sell Signal', s=100)
    plt.title(f'{symbol} Buy/Sell Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

