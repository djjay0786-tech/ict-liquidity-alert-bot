from market_data import get_candles
from crt import prepare_candles, detect_crt, format_crt_alert
import time

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

        try:
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

        except Exception as e:
            print(f"⚠️ Skipped {symbol} | {timeframe}")
            print(f"Reason: {e}")

        # API rate-limit protection
        time.sleep(5)
