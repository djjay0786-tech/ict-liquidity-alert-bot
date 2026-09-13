import pandas as pd

from session_summary import (
    calculate_session_summary,
    format_session_summary,
    format_combined_session_summary
)


def make_test_df():

    data = [
        {
            "datetime": "2026-09-14T00:00:00+00:00",
            "open": 1.1000,
            "high": 1.1010,
            "low": 1.0995,
            "close": 1.1005,
        },
        {
            "datetime": "2026-09-14T01:00:00+00:00",
            "open": 1.1005,
            "high": 1.1020,
            "low": 1.1000,
            "close": 1.1015,
        },
        {
            "datetime": "2026-09-14T02:00:00+00:00",
            "open": 1.1015,
            "high": 1.1030,
            "low": 1.1010,
            "close": 1.1025,
        },
        {
            "datetime": "2026-09-14T03:00:00+00:00",
            "open": 1.1025,
            "high": 1.1040,
            "low": 1.1020,
            "close": 1.1035,
        },
        {
            "datetime": "2026-09-14T04:00:00+00:00",
            "open": 1.1035,
            "high": 1.1050,
            "low": 1.1030,
            "close": 1.1045,
        },
        {
            "datetime": "2026-09-14T05:00:00+00:00",
            "open": 1.1045,
            "high": 1.1060,
            "low": 1.1040,
            "close": 1.1055,
        },
        {
            "datetime": "2026-09-14T06:00:00+00:00",
            "open": 1.1055,
            "high": 1.1070,
            "low": 1.1050,
            "close": 1.1065,
        },
        {
            "datetime": "2026-09-14T07:00:00+00:00",
            "open": 1.1065,
            "high": 1.1080,
            "low": 1.1060,
            "close": 1.1075,
        },
        {
            "datetime": "2026-09-14T08:00:00+00:00",
            "open": 1.1075,
            "high": 1.1090,
            "low": 1.1070,
            "close": 1.1085,
        },
        {
            "datetime": "2026-09-14T09:00:00+00:00",
            "open": 1.1085,
            "high": 1.1100,
            "low": 1.1080,
            "close": 1.1095,
        },
    ]

    df = pd.DataFrame(data)

    df["datetime"] = pd.to_datetime(
        df["datetime"],
        utc=True
    )

    return df


def test_session_summary():

    df = make_test_df()

    summary = calculate_session_summary(
        symbol="EUR/USD",
        session="LONDON",
        df=df
    )

    assert summary is not None
    assert summary["symbol"] == "EUR/USD"
    assert summary["session"] == "LONDON"
    assert summary["direction"] in [
        "BULLISH",
        "BEARISH",
        "NEUTRAL"
    ]

    assert summary["high"] >= summary["low"]
    assert summary["candles"] > 0

    print(
        "✅ Session summary calculation passed"
    )

    print()

    print(
        format_session_summary(
            summary
        )
    )


def test_combined_summary():

    df = make_test_df()

    eur = calculate_session_summary(
        symbol="EUR/USD",
        session="LONDON",
        df=df
    )

    gbp = calculate_session_summary(
        symbol="GBP/USD",
        session="LONDON",
        df=df
    )

    dxy = calculate_session_summary(
        symbol="DXY",
        session="LONDON",
        df=df
    )

    message = (
        format_combined_session_summary(
            "LONDON",
            [
                eur,
                gbp,
                dxy
            ]
        )
    )

    assert "EUR/USD" in message
    assert "GBP/USD" in message
    assert "DXY" in message
    assert "LONDON" in message

    print()
    print(
        "✅ Combined summary passed"
    )

    print()
    print(message)


def test_invalid_session():

    df = make_test_df()

    try:

        calculate_session_summary(
            symbol="EUR/USD",
            session="INVALID",
            df=df
        )

        raise AssertionError(
            "Invalid session was not blocked"
        )

    except ValueError:

        print()
        print(
            "✅ Invalid session correctly blocked"
        )


if __name__ == "__main__":

    test_session_summary()

    test_combined_summary()

    test_invalid_session()

    print()
    print(
        "📊 ALL SESSION SUMMARY TESTS PASSED"
    )
