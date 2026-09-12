from market_data import get_candles
from session_liquidity import (
    prepare_candles,
    calculate_session_levels,
    detect_session_liquidity_grab,
    format_session_alert
)


symbols = [
    "EUR/USD",
    "GBP/USD"
]


for symbol in symbols:

    print("\n" + "=" * 60)
    print(f"SESSION LIQUIDITY TEST: {symbol}")
    print("=" * 60)

    data = get_candles(
        symbol,
        interval="1h",
        outputsize=200
    )

    if "values" not in data:
        print("❌ No market data")
        continue

    df = prepare_candles(data["values"])

    for session in [
        "ASIA",
        "LONDON",
        "NEW YORK"
    ]:

        print(f"\n--- {session} ---")

        levels = calculate_session_levels(
            df,
            session
        )

        if levels:

            print(
                f"High: {levels['high']}"
            )

            print(
                f"Low: {levels['low']}"
            )

            alerts = detect_session_liquidity_grab(
                df,
                session
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
                    "No liquidity grab detected."
                )

        else:

            print(
                "Session data not available."
            )
