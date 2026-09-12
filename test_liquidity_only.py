import pandas as pd

from liquidity import (
    get_previous_day_levels,
    detect_liquidity_grab,
    format_alert
)


def make_df(rows):
    df = pd.DataFrame(rows)

    df["datetime"] = pd.to_datetime(
        df["datetime"],
        utc=True
    )

    return df


def test_pdh_sweep():

    df = make_df([
        {
            "datetime": "2026-09-11 00:00:00+00:00",
            "open": 1.1700,
            "high": 1.1750,
            "low": 1.1680,
            "close": 1.1720,
        },
        {
            "datetime": "2026-09-11 12:00:00+00:00",
            "open": 1.1720,
            "high": 1.1740,
            "low": 1.1690,
            "close": 1.1710,
        },
        {
            "datetime": "2026-09-12 00:00:00+00:00",
            "open": 1.1730,
            "high": 1.1765,
            "low": 1.1710,
            "close": 1.1755,
        }
    ])

    levels = get_previous_day_levels(
        df
    )

    assert round(
        levels["PDH"],
        5
    ) == 1.17500

    alerts = detect_liquidity_grab(
        df
    )

    assert len(alerts) == 1

    assert (
        alerts[0]["level"]
        == "PDH"
    )

    assert (
        alerts[0]["type"]
        == "BEARISH LIQUIDITY GRAB"
    )

    print(
        "\n✅ PDH SWEEP TEST PASSED"
    )

    print(
        format_alert(
            "EUR/USD",
            alerts[0]
        )
    )


def test_pdl_sweep():

    df = make_df([
        {
            "datetime": "2026-09-11 00:00:00+00:00",
            "open": 1.1700,
            "high": 1.1750,
            "low": 1.1680,
            "close": 1.1720,
        },
        {
            "datetime": "2026-09-11 12:00:00+00:00",
            "open": 1.1720,
            "high": 1.1740,
            "low": 1.1690,
            "close": 1.1710,
        },
        {
            "datetime": "2026-09-12 00:00:00+00:00",
            "open": 1.1690,
            "high": 1.1700,
            "low": 1.1665,
            "close": 1.1680,
        }
    ])

    alerts = detect_liquidity_grab(
        df
    )

    assert len(alerts) == 1

    assert (
        alerts[0]["level"]
        == "PDL"
    )

    assert (
        alerts[0]["type"]
        == "BULLISH LIQUIDITY GRAB"
    )

    print(
        "\n✅ PDL SWEEP TEST PASSED"
    )

    print(
        format_alert(
            "GBP/USD",
            alerts[0]
        )
    )


def test_no_sweep():

    df = make_df([
        {
            "datetime": "2026-09-11 00:00:00+00:00",
            "open": 1.1700,
            "high": 1.1750,
            "low": 1.1680,
            "close": 1.1720,
        },
        {
            "datetime": "2026-09-12 00:00:00+00:00",
            "open": 1.1710,
            "high": 1.1740,
            "low": 1.1690,
            "close": 1.1720,
        }
    ])

    alerts = detect_liquidity_grab(
        df
    )

    assert len(alerts) == 0

    print(
        "\n✅ NO SWEEP TEST PASSED"
    )


if __name__ == "__main__":

    test_pdh_sweep()

    test_pdl_sweep()

    test_no_sweep()

    print(
        "\n🔥 ALL PDH/PDL TESTS PASSED"
    )
