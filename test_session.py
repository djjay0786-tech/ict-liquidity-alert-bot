from market_data import get_candles

from session_liquidity import (
    prepare_candles,
    detect_session_liquidity,
    format_session_alert
)


symbols = [
    "EUR/USD",
    "GBP/USD"
]


for symbol in symbols:

    print("\n" + "=" * 60)
    print(f"SESSION LIQUIDITY: {symbol}")
    print("=" * 60)

    data = get_candles(
        symbol,
        interval="1h",
        outputsize=500
    )

    if "values" not in data:

        print("❌ No market data")
        continue

    df = prepare_candles(
        data["values"]
    )

    # ---------------------------------------
    # LONDON checks ASIA liquidity
    # ---------------------------------------

    print("\n--- LONDON → ASIA LIQUIDITY ---")

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


    # ---------------------------------------
    # NEW YORK checks LONDON liquidity
    # ---------------------------------------

    print("\n--- NEW YORK → LONDON LIQUIDITY ---")

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
