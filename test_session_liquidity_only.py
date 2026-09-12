import pandas as pd

from session_liquidity import (
    get_last_completed_session,
    detect_session_liquidity,
    format_session_alert
)


def make_df(rows):

    df = pd.DataFrame(rows)

    df["datetime"] = pd.to_datetime(
        df["datetime"],
        utc=True
    )

    return df


def test_asia_high_sweep():

    df = make_df([
        {
            "datetime": "2026-09-12 15:00:00+00:00",
            "open": 100.0,
            "high": 101.0,
            "low": 99.5,
            "close": 100.5,
        },
        {
            "datetime": "2026-09-12 18:00:00+00:00",
            "open": 100.5,
            "high": 102.0,
            "low": 100.0,
            "close": 101.5,
        },
        {
            "datetime": "2026-09-12 23:00:00+00:00",
            "open": 101.5,
            "high": 101.8,
            "low": 100.2,
            "close": 101.0,
        },
        {
            "datetime": "2026-09-13 00:30:00+00:00",
            "open": 101.0,
            "high": 102.5,
            "low": 100.8,
            "close": 102.0,
        }
    ])

    session = get_last_completed_session(
        df,
        "ASIA"
    )

    assert session is not None

    assert round(
        session["high"],
        2
    ) == 102.00

    alerts = detect_session_liquidity(
        df,
        "ASIA"
    )

    assert len(alerts) == 1

    assert (
        alerts[0]["level"]
        == "ASIA HIGH"
    )

    print(
        "\n✅ ASIA HIGH SWEEP TEST PASSED"
    )

    print(
        format_session_alert(
            "DXY",
            alerts[0]
        )
    )


def test_london_low_sweep():

    df = make_df([
        {
            "datetime": "2026-09-12 07:00:00+00:00",
            "open": 1.1700,
            "high": 1.1710,
            "low": 1.1685,
            "close": 1.1705,
        },
        {
            "datetime": "2026-09-12 10:00:00+00:00",
            "open": 1.1705,
            "high": 1.1730,
            "low": 1.1670,
            "close": 1.1710,
        },
        {
            "datetime": "2026-09-12 15:00:00+00:00",
            "open": 1.1710,
            "high": 1.1720,
            "low": 1.1680,
            "close": 1.1690,
        },
        {
            "datetime": "2026-09-12 17:30:00+00:00",
            "open": 1.1690,
            "high": 1.1700,
            "low": 1.1660,
            "close": 1.1670,
        }
    ])

    alerts = detect_session_liquidity(
        df,
        "LONDON"
    )

    assert len(alerts) == 1

    assert (
        alerts[0]["level"]
        == "LONDON LOW"
    )

    print(
        "\n✅ LONDON LOW SWEEP TEST PASSED"
    )


def test_new_york_high_sweep():

    df = make_df([
        {
            "datetime": "2026-09-12 12:00:00+00:00",
            "open": 1.3500,
            "high": 1.3520,
            "low": 1.3480,
            "close": 1.3510,
        },
        {
            "datetime": "2026-09-12 16:00:00+00:00",
            "open": 1.3510,
            "high": 1.3550,
            "low": 1.3490,
            "close": 1.3530,
        },
        {
            "datetime": "2026-09-12 20:00:00+00:00",
            "open": 1.3530,
            "high": 1.3540,
            "low": 1.3500,
            "close": 1.3520,
        },
        {
            "datetime": "2026-09-12 22:30:00+00:00",
            "open": 1.3520,
            "high": 1.3560,
            "low": 1.3510,
            "close": 1.3550,
        }
    ])

    alerts = detect_session_liquidity(
        df,
        "NEW YORK"
    )

    assert len(alerts) == 1

    assert (
        alerts[0]["level"]
        == "NEW YORK HIGH"
    )

    print(
        "\n✅ NEW YORK HIGH SWEEP TEST PASSED"
    )


def test_no_session_sweep():

    df = make_df([
        {
            "datetime": "2026-09-12 07:00:00+00:00",
            "open": 1.1700,
            "high": 1.1720,
            "low": 1.1680,
            "close": 1.1710,
        },
        {
            "datetime": "2026-09-12 12:00:00+00:00",
            "open": 1.1710,
            "high": 1.1740,
            "low": 1.1690,
            "close": 1.1720,
        },
        {
            "datetime": "2026-09-12 17:30:00+00:00",
            "open": 1.1720,
            "high": 1.1730,
            "low": 1.1700,
            "close": 1.1710,
        }
    ])

    alerts = detect_session_liquidity(
        df,
        "LONDON"
    )

    assert len(alerts) == 0

    print(
        "\n✅ NO SESSION SWEEP TEST PASSED"
    )


if __name__ == "__main__":

    test_asia_high_sweep()

    test_london_low_sweep()

    test_new_york_high_sweep()

    test_no_session_sweep()

    print(
        "\n🔥 ALL SESSION LIQUIDITY TESTS PASSED"
    )
