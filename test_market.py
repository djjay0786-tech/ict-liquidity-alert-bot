from market_data import get_candles, get_dxy_candles

symbols = ["EUR/USD", "GBP/USD"]

for symbol in symbols:
    print(f"\nTesting {symbol}...")

    data = get_candles(symbol, "1h", 5)

    if "values" in data:
        print(f"✅ {symbol} data received")
        print(data["values"][0])
    else:
        print(f"❌ {symbol} failed")
        print(data)


print("\nTesting DXY...")

dxy = get_dxy_candles("1h", 5)

if "bars" in dxy:
    print("✅ DXY data received")
    print(dxy["bars"][0])
else:
    print("❌ DXY failed")
    print(dxy)
