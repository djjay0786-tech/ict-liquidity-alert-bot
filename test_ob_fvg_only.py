import pandas as pd

from ob_fvg import (
    select_ob_near_fvg,
    format_ob_fvg_selection
)


def build_test_data():

    data = [
        {
            "datetime": "2026-09-12 00:00:00+00:00",
            "open": 1.1050,
            "high": 1.1060,
            "low": 1.1020,
            "close": 1.1030,
        },
        {
            "datetime": "2026-09-12 01:00:00+00:00",
            "open": 1.1030,
            "high": 1.1080,
            "low": 1.1025,
            "close": 1.1075,
        },
        {
            "datetime": "2026-09-12 02:00:00+00:00",
            "open": 1.1075,
            "high": 1.1100,
            "low": 1.1070,
            "close": 1.1090,
        },
        {
            "datetime": "2026-09-12 03:00:00+00:00",
            "open": 1.1090,
            "high": 1.1120,
            "low": 1.1085,
            "close": 1.1110,
        },
        {
            "datetime": "2026-09-12 04:00:00+00:00",
            "open": 1.1110,
            "high": 1.1140,
            "low": 1.1105,
            "close": 1.1130,
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
    print("OB + FVG LOCAL TEST")
    print("=" * 60)

    df = build_test_data()

    setup = select_ob_near_fvg(
        df
    )

    if setup is None:
        raise Exception(
            "No valid OB + FVG setup found"
        )

    print(
        format_ob_fvg_selection(
            "TEST",
            "H1",
            setup
        )
    )

    print("=" * 60)
    print("✅ OB + FVG LOCAL TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
