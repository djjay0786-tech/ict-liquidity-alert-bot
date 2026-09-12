from market_data import get_candles
from order_block import (
    prepare_candles,
    detect_order_blocks,
    format_ob_alert
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
            f"ORDER BLOCK TEST: "
            f"{symbol} | {timeframe}"
        )
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

            order_blocks = detect_order_blocks(df)

            if order_blocks:
                print(
                    f"✅ {len(order_blocks)} "
                    f"Order Block(s) detected\n"
                )

                # Last 3 Order Blocks
                for ob in order_blocks[-3:]:

                    print(
                        format_ob_alert(
                            symbol,
                            timeframe,
                            ob
                        )
                    )

                    print()

            else:
                print(
                    "No Order Block detected."
                )

        except Exception as e:

            print(
                f"⚠️ Skipped "
                f"{symbol} | {timeframe}"
            )

            print(f"Reason: {e}")
