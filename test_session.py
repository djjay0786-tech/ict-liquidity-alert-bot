from market_data import get_candles
from session_liquidity import (
    prepare_candles,
    detect_session_liquidity,
    format_session_alert
)

import time


symbols = [
    "EUR/USD",
    "GBP/USD"
]


for symbol in symbols:

    print("\n" + "=" * 60)
    print(f"SESSION LIQUIDITY: {symbol}")
    print("=" * 60)

    try:

        data = get_candles(
            symbol,
            interval="1h",
            outputsize=500
        )

        if "values" not in data:

            print("⚠️ No market data")
            print(data)
            continue

        df = prepare_candles(
            data["values"]
        )

        print(
            "\n--- LONDON → ASIA LIQUIDITY ---"
        )

        alerts = detect_session_liquidity(
            df,
            "LONDON"
        )

        if alerts:

            for alert in alerts:

                print(
                    format_session_alert(
                        symbol,
                        alert
                    )
                )

        else:

            print(
                "No Asia liquidity grab."
            )

        print(
            "\n--- NEW YORK → LONDON LIQUIDITY ---"
        )

        alerts = detect_session_liquidity(
            df,
            "NEW YORK"
        )

        if alerts:

            for alert in alerts:

                print(
                    format_session_alert(
                        symbol,
                        alert
                    )
                )

        else:

            print(
                "No London liquidity grab."
            )

    except Exception as e:

        print(
            f"⚠️ {symbol} skipped"
        )

        print(
            f"Reason: {e}"
        )

    time.sleep(8)
