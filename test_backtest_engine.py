import pandas as pd

from backtest_engine import (
    calculate_forward_move,
    convert_move,
    summarize_backtest,
    format_backtest_summary
)


def make_test_df():

    data = [
        {
            "datetime": "2026-09-14T00:00:00+00:00",
            "open": 1.1000,
            "high": 1.1010,
            "low": 1.0990,
            "close": 1.1005
        },
        {
            "datetime": "2026-09-14T01:00:00+00:00",
            "open": 1.1005,
            "high": 1.1020,
            "low": 1.1000,
            "close": 1.1015
        },
        {
            "datetime": "2026-09-14T02:00:00+00:00",
            "open": 1.1015,
            "high": 1.1040,
            "low": 1.1010,
            "close": 1.1030
        },
        {
            "datetime": "2026-09-14T03:00:00+00:00",
            "open": 1.1030,
            "high": 1.1060,
            "low": 1.1020,
            "close": 1.1050
        },
        {
            "datetime": "2026-09-14T04:00:00+00:00",
            "open": 1.1050,
            "high": 1.1070,
            "low": 1.1040,
            "close": 1.1060
        },
    ]

    df = pd.DataFrame(data)

    df["datetime"] = pd.to_datetime(
        df["datetime"],
        utc=True
    )

    return df


def test_bullish_forward_move():

    df = make_test_df()

    result = calculate_forward_move(
        full_df=df,
        signal_index=1,
        direction="BULLISH",
        entry_price=1.1015,
        forward_candles=3
    )

    assert round(
        result["best_move"],
        4
    ) == 0.0055

    assert round(
        result["worst_move"],
        4
    ) == 0.0005

    print(
        "✅ Bullish forward move passed"
    )


def test_bearish_forward_move():

    df = make_test_df()

    result = calculate_forward_move(
        full_df=df,
        signal_index=1,
        direction="BEARISH",
        entry_price=1.1015,
        forward_candles=2
    )

    assert round(
        result["best_move"],
        4
    ) == 0.0005

    assert round(
        result["worst_move"],
        4
    ) == 0.0045

    print(
        "✅ Bearish forward move passed"
    )


def test_pip_conversion():

    result = convert_move(
        "EUR/USD",
        0.0025
    )

    assert (
        round(
            result["value"],
            1
        )
        == 25.0
    )

    assert (
        result["unit"]
        == "pips"
    )

    print(
        "✅ Forex pip conversion passed"
    )


def test_dxy_conversion():

    result = convert_move(
        "DXY",
        0.75
    )

    assert (
        result["value"]
        == 0.75
    )

    assert (
        result["unit"]
        == "points"
    )

    print(
        "✅ DXY point conversion passed"
    )


def test_summary():

    result = {
        "symbol": "EUR/USD",
        "timeframe": "H1",
        "setup_count": 2,
        "setups": [
            {
                "best_move": 30.0,
                "worst_move": 10.0,
                "unit": "pips"
            },
            {
                "best_move": 50.0,
                "worst_move": 20.0,
                "unit": "pips"
            }
        ]
    }

    summary = summarize_backtest(
        result
    )

    assert (
        summary["setup_count"]
        == 2
    )

    assert (
        summary["average_best_move"]
        == 40.0
    )

    assert (
        summary["average_worst_move"]
        == 15.0
    )

    assert (
        summary["unit"]
        == "pips"
    )

    message = (
        format_backtest_summary(
            summary
        )
    )

    assert (
        "ICT BACKTEST RESULT"
        in message
    )

    assert (
        "40.0 pips"
        in message
    )

    print(
        "✅ Backtest summary passed"
    )

    print()
    print(message)


if __name__ == "__main__":

    test_bullish_forward_move()

    test_bearish_forward_move()

    test_pip_conversion()

    test_dxy_conversion()

    test_summary()

    print()
    print(
        "🧪 ALL BACKTEST ENGINE TESTS PASSED"
    )
