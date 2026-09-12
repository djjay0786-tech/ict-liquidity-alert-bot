from multi_timeframe_ob import (
    get_all_timeframe_obs,
    format_mtf_ob
)

symbols = [
    "EUR/USD",
    "GBP/USD"
]

for symbol in symbols:

    print("\n" + "=" * 60)
    print(
        f"MULTI-TIMEFRAME OB TEST: {symbol}"
    )
    print("=" * 60)

    try:

        results = get_all_timeframe_obs(
            symbol
        )

        if results:

            print(
                format_mtf_ob(
                    symbol,
                    results
                )
            )

        else:

            print(
                "No valid timeframe OB found."
            )

    except Exception as e:

        print(
            f"⚠️ {symbol} test failed"
        )

        print(
            f"Reason: {e}"
        )
