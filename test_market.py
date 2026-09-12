from market_data import get_candles
import time

symbols = ["EUR/USD", "GBP/USD"]

for symbol in symbols:

    print(f"\nTesting {symbol}...")

    try:
        data = get_candles(
            symbol,
            "1h",
            5
        )

        if "values" in data:
            print(f"✅ {symbol} data received")
            print(data["values"][0])
        else:
            print(f"⚠️ {symbol} failed")
            print(data)

    except Exception as e:
        print(f"⚠️ {symbol} skipped")
        print(f"Reason: {e}")

    time.sleep(5)
