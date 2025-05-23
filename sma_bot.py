import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

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

