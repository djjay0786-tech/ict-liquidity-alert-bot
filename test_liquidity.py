from market_data import get_candles
from liquidity import (
    prepare_candles,
    detect_liquidity_grab,
    format_alert
)
import time


symbols = [
    "EUR/USD",
    "GBP/USD"
]


for symbol in symbols:

    print("\n" + "=" * 50)
    print(f"Testing Liquidity: {symbol}")
    print("=" * 50)

    try:

        data = get_candles(
            symbol,
            interval="1h",
            outputsize=100
        )

        if "values" not in data:

            print("⚠️ No market data")
            print(data)
            continue

        df = prepare_candles(
            data["values"]
        )

        alerts = detect_liquidity_grab(
            df
        )

        if alerts:

            for alert in alerts:

                print(
                    format_alert(
                        symbol,
                        alert
                    )
                )

        else:

            print(
                "No liquidity grab detected."
            )

    except Exception as e:

        print(
            f"⚠️ {symbol} skipped"
        )

        print(
            f"Reason: {e}"
        )

    # Protect Twelve Data rate limit
    time.sleep(8)
