import pandas as pd

from backtest_engine import (
    calculate_forward_move,
    convert_move,
    summarize_backtest,
    format_backtest_summary
)

from order_block import (
    detect_order_blocks,
    get_valid_order_blocks
)

from ob_tap import (
    is_latest_candle_first_tap
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


def make_ob_tap_test_df():

    data = [
        # Candle 0 = Bullish OB candle
        {
            "datetime": "2026-09-15T00:00:00+00:00",
            "open": 1.1000,
            "high": 1.1010,
            "low": 1.0990,
            "close": 1.0995
        },

        # Candle 1 = Confirmation /
        # displacement candle.
        # It overlaps the OB but MUST NOT
        # count as First Tap.
        {
            "datetime": "2026-09-15T01:00:00+00:00",
            "open": 1.0995,
            "high": 1.1025,
            "low": 1.0994,
            "close": 1.1020
        },

        # Candle 2 = Price moves away
        {
            "datetime": "2026-09-15T02:00:00+00:00",
            "open": 1.1020,
            "high": 1.1030,
            "low": 1.1015,
            "close": 1.1025
        },

        # Candle 3 = First REAL retracement
        # into the OB.
        {
            "datetime": "2026-09-15T03:00:00+00:00",
            "open": 1.1025,
            "high": 1.1030,
            "low": 1.1005,
            "close": 1.1015
        }
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


def test_ob_confirmation_not_first_tap():

    df = make_ob_tap_test_df()

    order_blocks = (
        detect_order_blocks(
            df
        )
    )

    bullish_obs = [
        ob
        for ob in order_blocks
        if (
            ob["type"]
            ==
            "BULLISH OB"
            and
            ob["index"]
            == 0
        )
    ]

    assert bullish_obs, (
        "Bullish OB was not detected"
    )

    ob = bullish_obs[0]

    assert (
        ob["confirmation_index"]
        == 1
    )

    # Up to confirmation candle:
    # MUST NOT count as First Tap.
    confirmation_df = (
        df.iloc[:2]
        .copy()
    )

    assert (
        is_latest_candle_first_tap(
            confirmation_df,
            ob
        )
        is False
    )

    # Price moved away:
    # still no First Tap.
    away_df = (
        df.iloc[:3]
        .copy()
    )

    assert (
        is_latest_candle_first_tap(
            away_df,
            ob
        )
        is False
    )

    # Candle 3 retraces into OB:
    # THIS must be the First Tap.
    tap_df = (
        df.iloc[:4]
        .copy()
    )

    assert (
        is_latest_candle_first_tap(
            tap_df,
            ob
        )
        is True
    )

    # The retracement touched the OB
    # but did not break through OB low,
    # so the OB should remain valid.
    valid_obs = (
        get_valid_order_blocks(
            tap_df
        )
    )

    valid_match = [
        item
        for item in valid_obs
        if (
            item["type"]
            ==
            "BULLISH OB"
            and
            item["index"]
            == 0
        )
    ]

    assert valid_match, (
        "Tapped OB should still be valid"
    )

    print(
        "✅ OB confirmation candle ignored"
    )

    print(
        "✅ Real retracement detected as First Tap"
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
        summary[
            "average_best_move"
        ]
        == 40.0
    )

    assert (
        summary[
            "average_worst_move"
        ]
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

    test_ob_confirmation_not_first_tap()

    test_summary()

    print()

    print(
        "🧪 ALL BACKTEST ENGINE TESTS PASSED"
    )
