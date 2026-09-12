import pandas as pd

from fvg import (
    detect_fvg,
    get_valid_fvgs,
    get_last_fvg,
    is_fvg_mitigated
)


def build_test_data():

    data = [
        {
            "datetime": "2026-09-12 00:00:00+00:00",
            "open": 1.1000,
            "high": 1.1010,
            "low": 1.0990,
            "close": 1.1005,
        },
        {
            "datetime": "2026-09-12 01:00:00+00:00",
            "open": 1.1005,
            "high": 1.1030,
            "low": 1.1000,
            "close": 1.1025,
        },
        {
            "datetime": "2026-09-12 02:00:00+00:00",
            "open": 1.1025,
            "high": 1.1040,
            "low": 1.1020,
            "close": 1.1035,
        },
        {
            "datetime": "2026-09-12 03:00:00+00:00",
            "open": 1.1035,
            "high": 1.1050,
            "low": 1.1030,
            "close": 1.1045,
        },
        {
            "datetime": "2026-09-12 04:00:00+00:00",
            "open": 1.1045,
            "high": 1.1060,
            "low": 1.1040,
            "close": 1.1055,
        },
    ]

    df = pd.DataFrame(data)

    df["datetime"] = pd.to_datetime(
        df["datetime"],
        utc=True
    )

    return df


def main():

    print("=" * 60)
    print("FVG LOCAL LOGIC TEST")
    print("=" * 60)

    df = build_test_data()

    print(
        f"✅ Test candles: {len(df)}"
    )

    all_fvgs = detect_fvg(
        df
    )

    print(
        f"✅ Total FVGs detected: {len(all_fvgs)}"
    )

    if not all_fvgs:
        raise Exception(
            "No FVG detected in local test data"
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
        raise Exception(
            "No valid latest FVG returned"
        )

    print(
        f"✅ Latest FVG: {latest['type']}"
    )

    print(
        f"Top: {latest['top']}"
    )

    print(
        f"Bottom: {latest['bottom']}"
    )

    mitigated = is_fvg_mitigated(
        df,
        latest
    )

    print(
        f"Mitigated: {mitigated}"
    )

    print("=" * 60)
    print("✅ FVG LOCAL TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
