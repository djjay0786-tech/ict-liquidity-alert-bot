from market_data import get_candles
from fvg import prepare_candles, detect_fvg, format_fvg_alert

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
        print(f"FVG TEST: {symbol} | {timeframe}")
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

            fvgs = detect_fvg(df)

            if fvgs:
                print(f"✅ {len(fvgs)} FVG(s) detected\n")

                # Last 3 FVGs
                for fvg in fvgs[-3:]:
                    print(
                        format_fvg_alert(
                            symbol,
                            timeframe,
                            fvg
                        )
                    )
                    print()
            else:
                print("No FVG detected.")

        except Exception as e:
            print(f"⚠️ Skipped {symbol} | {timeframe}")
            print(f"Reason: {e}")
