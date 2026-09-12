from market_data import get_candles

from fvg import (
    prepare_candles,
    detect_fvg,
    get_valid_fvgs,
    get_last_fvg,
    is_fvg_mitigated
)


SYMBOL = "EUR/USD"
TIMEFRAME = "1h"


def main():

    print("=" * 60)
    print("FVG ONLY TEST")
    print("=" * 60)

    data = get_candles(
        SYMBOL,
        interval=TIMEFRAME,
        outputsize=200
    )

    if "values" not in data:
        raise Exception(
            "Market data not received"
        )

    df = prepare_candles(
        data["values"]
    )

    print(
        f"✅ Candles received: {len(df)}"
    )

    all_fvgs = detect_fvg(
        df
    )

    print(
        f"✅ Total FVGs: {len(all_fvgs)}"
    )

    valid_fvgs = get_valid_fvgs(
        df
    )

    print(
        f"✅ Valid FVGs: {len(valid_fvgs)}"
    )

    latest = get_last_fvg(
        df
    )

    if latest is None:

        print(
            "ℹ️ No current valid FVG found"
        )

    else:

        print(
            f"✅ Latest valid FVG: "
            f"{latest['type']}"
        )

        print(
            f"Top: {latest['top']}"
        )

        print(
            f"Bottom: {latest['bottom']}"
        )

        print(
            f"Mitigated: "
            f"{is_fvg_mitigated(df, latest)}"
        )

    print("=" * 60)
    print("✅ FVG ONLY TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
