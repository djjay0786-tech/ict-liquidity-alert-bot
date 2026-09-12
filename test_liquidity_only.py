import pandas as pd

from liquidity import (
    get_previous_day_levels,
    get_prior_current_day_levels,
    detect_liquidity_grab,
    detect_daily_liquidity_grab,
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


def test_pdh_first_sweep_only():

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

        # First PDH sweep
        {
            "datetime": "2026-09-12 01:00:00+00:00",
            "open": 1.1730,
            "high": 1.1760,
            "low": 1.1720,
            "close": 1.1755,
        },

        # Still above PDH
        # This must NOT create another alert
        {
            "datetime": "2026-09-12 02:00:00+00:00",
            "open": 1.1755,
            "high": 1.1770,
            "low": 1.1740,
            "close": 1.1760,
        }
    ])

    alerts = detect_liquidity_grab(
        df
    )

    assert len(alerts) == 0

    print(
        "\n✅ PDH FIRST-SWEEP PROTECTION PASSED"
    )


def test_pdl_first_sweep_only():

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

        # First PDL sweep
        {
            "datetime": "2026-09-12 01:00:00+00:00",
            "open": 1.1690,
            "high": 1.1700,
            "low": 1.1670,
            "close": 1.1680,
        },

        # Still below PDL
        # This must NOT create another alert
        {
            "datetime": "2026-09-12 02:00:00+00:00",
            "open": 1.1680,
            "high": 1.1690,
            "low": 1.1660,
            "close": 1.1670,
        }
    ])

    alerts = detect_liquidity_grab(
        df
    )

    assert len(alerts) == 0

    print(
        "\n✅ PDL FIRST-SWEEP PROTECTION PASSED"
    )


def test_dh_sweep():

    df = make_df([
        {
            "datetime": "2026-09-12 00:00:00+00:00",
            "open": 1.1700,
            "high": 1.1720,
            "low": 1.1690,
            "close": 1.1710,
        },
        {
            "datetime": "2026-09-12 01:00:00+00:00",
            "open": 1.1710,
            "high": 1.1730,
            "low": 1.1700,
            "close": 1.1720,
        },
        {
            "datetime": "2026-09-12 02:00:00+00:00",
            "open": 1.1720,
            "high": 1.1745,
            "low": 1.1710,
            "close": 1.1740,
        }
    ])

    levels = get_prior_current_day_levels(
        df
    )

    assert round(
        levels["DH"],
        5
    ) == 1.17300

    alerts = detect_daily_liquidity_grab(
        df
    )

    assert len(alerts) == 1

    assert (
        alerts[0]["level"]
        == "DH"
    )

    assert (
        alerts[0]["type"]
        == "BEARISH LIQUIDITY GRAB"
    )

    print(
        "\n✅ DH SWEEP TEST PASSED"
    )

    print(
        format_alert(
            "EUR/USD",
            alerts[0]
        )
    )


def test_dl_sweep():

    df = make_df([
        {
            "datetime": "2026-09-12 00:00:00+00:00",
            "open": 1.1700,
            "high": 1.1720,
            "low": 1.1680,
            "close": 1.1710,
        },
        {
            "datetime": "2026-09-12 01:00:00+00:00",
            "open": 1.1710,
            "high": 1.1730,
            "low": 1.1690,
            "close": 1.1700,
        },
        {
            "datetime": "2026-09-12 02:00:00+00:00",
            "open": 1.1700,
            "high": 1.1710,
            "low": 1.1665,
            "close": 1.1680,
        }
    ])

    alerts = detect_daily_liquidity_grab(
        df
    )

    assert len(alerts) == 1

    assert (
        alerts[0]["level"]
        == "DL"
    )

    assert (
        alerts[0]["type"]
        == "BULLISH LIQUIDITY GRAB"
    )

    print(
        "\n✅ DL SWEEP TEST PASSED"
    )

    print(
        format_alert(
            "GBP/USD",
            alerts[0]
        )
    )


def test_no_daily_sweep():

    df = make_df([
        {
            "datetime": "2026-09-12 00:00:00+00:00",
            "open": 1.1700,
            "high": 1.1740,
            "low": 1.1680,
            "close": 1.1710,
        },
        {
            "datetime": "2026-09-12 01:00:00+00:00",
            "open": 1.1710,
            "high": 1.1730,
            "low": 1.1690,
            "close": 1.1720,
        }
    ])

    alerts = detect_daily_liquidity_grab(
        df
    )

    assert len(alerts) == 0

    print(
        "\n✅ NO DH/DL SWEEP TEST PASSED"
    )


if __name__ == "__main__":

    test_pdh_sweep()

    test_pdl_sweep()

    test_pdh_first_sweep_only()

    test_pdl_first_sweep_only()

    test_dh_sweep()

    test_dl_sweep()

    test_no_daily_sweep()

    print(
        "\n🔥 ALL LIQUIDITY + FIRST-SWEEP TESTS PASSED"
    )
