from market_data import get_candles
from crt import prepare_candles, detect_crt, format_crt_alert


symbols = [
    "EUR/USD",
    "GBP/USD"
]


timeframes = [
    "1h",
    "4h"
]


for symbol in symbols:

    for timeframe in timeframes:

        print("\n" + "=" * 60)
        print(f"CRT TEST: {symbol} | {timeframe}")
        print("=" * 60)

        data = get_candles(
            symbol,
            interval=timeframe,
            outputsize=100
        )

        if "values" not in data:

            print("❌ No market data")
            continue

        df = prepare_candles(
            data["values"]
        )

        alerts = detect_crt(df)

        if alerts:

            for alert in alerts:

                print(
                    format_crt_alert(
                        symbol,
                        timeframe,
                        alert
                    )
                )

        else:

            print("No CRT setup detected.")
