from market_data import get_candles
from ob_fvg import (
    select_ob_near_fvg,
    format_ob_fvg_selection
)

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
        print(
            f"OB + FVG TEST: "
            f"{symbol} | {timeframe}"
        )
        print("=" * 60)

        try:
            data = get_candles(
                symbol,
                interval=timeframe,
                outputsize=200
            )

            if "values" not in data:
                print("❌ No market data")
                continue

            from order_block import prepare_candles

            df = prepare_candles(
                data["values"]
            )

            setup = select_ob_near_fvg(df)

            if setup:

                print("✅ OB + FVG setup found\n")

                print(
                    format_ob_fvg_selection(
                        symbol,
                        timeframe,
                        setup
                    )
                )

            else:
                print(
                    "No valid OB + FVG setup found."
                )

        except Exception as e:

            print(
                f"⚠️ Skipped "
                f"{symbol} | {timeframe}"
            )

            print(f"Reason: {e}")
