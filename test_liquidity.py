from market_data import get_candles
from liquidity import prepare_candles, detect_liquidity_grab, format_alert


symbols = ["EUR/USD", "GBP/USD"]

for symbol in symbols:

    print("\n" + "=" * 50)
    print(f"Testing Liquidity: {symbol}")
    print("=" * 50)

    data = get_candles(
        symbol,
        interval="1h",
        outputsize=100
    )

    if "values" not in data:
        print("❌ No market data")
        continue

    df = prepare_candles(data["values"])

    alerts = detect_liquidity_grab(df)

    if alerts:

        for alert in alerts:
            print(format_alert(symbol, alert))

    else:
        print("No liquidity grab detected.")
