import json
from pathlib import Path
from datetime import date

import pandas as pd

import alert_state

from weekly_report_live import (
    get_weekly_alert_history,
    get_week_ohlc
)


TEST_STATE_FILE = Path(
    "alert_state_weekly_test.json"
)


def setup_test_state():

    state = {
        (
            "PDH_PDL|EUR/USD|H1|"
            "2026-09-14T05:00:00+00:00|PDL"
        ): {
            "sent": True,
            "details": {
                "type":
                    "BULLISH LIQUIDITY GRAB",
                "time":
                    "2026-09-14T05:00:00+00:00"
            }
        },

        (
            "SESSION_LIQUIDITY|EUR/USD|H1|"
            "2026-09-15T08:00:00+00:00|LONDON"
        ): {
            "sent": True,
            "details": {
                "type":
                    "BEARISH LIQUIDITY GRAB",
                "time":
                    "2026-09-15T08:00:00+00:00"
            }
        },

        (
            "CRT|EUR/USD|H1|"
            "2026-09-16T07:00:00+00:00|"
            "BULLISH CRT"
        ): {
            "sent": True,
            "details": {
                "type": "BULLISH CRT",
                "second_candle_time":
                    "2026-09-16T07:00:00+00:00"
            }
        },

        (
            "FVG|EUR/USD|H1|"
            "2026-09-17T08:00:00+00:00|"
            "BULLISH FVG"
        ): {
            "sent": True,
            "details": {
                "type": "BULLISH FVG",
                "time":
                    "2026-09-17T08:00:00+00:00"
            }
        },

        (
            "OB_FVG|EUR/USD|H1|"
            "2026-09-17T08:00:00+00:00|"
            "BULLISH OB"
        ): {
            "sent": True,
            "details": {
                "ob": {
                    "type": "BULLISH OB"
                },
                "fvg": {
                    "type": "BULLISH FVG"
                }
            }
        },

        (
            "HIGH_CONFLUENCE|EUR/USD|H1|"
            "2026-09-18T09:00:00+00:00|BUY"
        ): {
            "sent": True,
            "details": {
                "trade": "BUY"
            }
        },

        # Outside requested week
        (
            "CRT|EUR/USD|H1|"
            "2026-09-21T07:00:00+00:00|"
            "BULLISH CRT"
        ): {
            "sent": True,
            "details": {
                "type": "BULLISH CRT",
                "second_candle_time":
                    "2026-09-21T07:00:00+00:00"
            }
        }
    }

    with open(
        TEST_STATE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            state,
            file,
            indent=2
        )


def cleanup():

    if TEST_STATE_FILE.exists():
        TEST_STATE_FILE.unlink()


def test_weekly_alert_history():

    history = (
        get_weekly_alert_history(
            symbol="EUR/USD",
            week_start=date(
                2026,
                9,
                14
            ),
            week_end=date(
                2026,
                9,
                18
            )
        )
    )

    assert (
        len(history["liquidity"])
        == 2
    )

    assert (
        len(history["crt"])
        == 1
    )

    assert (
        len(history["fvg"])
        == 1
    )

    assert (
        len(history["ob"])
        == 1
    )

    assert (
        len(history["confluence"])
        == 1
    )

    print(
        "✅ Weekly alert history passed"
    )


def test_week_ohlc():

    df = pd.DataFrame([
        {
            "datetime":
                "2026-09-14T00:00:00+00:00",
            "open": 1.1000,
            "high": 1.1030,
            "low": 1.0980,
            "close": 1.1020
        },

        {
            "datetime":
                "2026-09-15T06:00:00+00:00",
            "open": 1.1020,
            "high": 1.1080,
            "low": 1.1010,
            "close": 1.1060
        },

        {
            "datetime":
                "2026-09-17T12:00:00+00:00",
            "open": 1.1060,
            "high": 1.1150,
            "low": 1.1040,
            "close": 1.1120
        },

        {
            "datetime":
                "2026-09-18T15:00:00+00:00",
            "open": 1.1120,
            "high": 1.1200,
            "low": 1.1100,
            "close": 1.1180
        },

        # Outside week
        {
            "datetime":
                "2026-09-21T06:00:00+00:00",
            "open": 1.1180,
            "high": 1.1250,
            "low": 1.1170,
            "close": 1.1230
        }
    ])

    df["datetime"] = (
        pd.to_datetime(
            df["datetime"],
            utc=True
        )
    )

    result = get_week_ohlc(
        df,
        week_start=date(
            2026,
            9,
            14
        ),
        week_end=date(
            2026,
            9,
            18
        )
    )

    assert result is not None

    assert (
        result["open"]
        == 1.1000
    )

    assert (
        result["high"]
        == 1.1200
    )

    assert (
        result["low"]
        == 1.0980
    )

    assert (
        result["close"]
        == 1.1180
    )

    assert (
        result["candles"]
        == 4
    )

    print(
        "✅ Weekly OHLC passed"
    )


if __name__ == "__main__":

    cleanup()

    original_state_file = (
        alert_state.STATE_FILE
    )

    try:

        alert_state.STATE_FILE = (
            TEST_STATE_FILE
        )

        setup_test_state()

        test_weekly_alert_history()

        test_week_ohlc()

        print()

        print(
            "📊 ALL WEEKLY REPORT "
            "LIVE TESTS PASSED"
        )

    finally:

        alert_state.STATE_FILE = (
            original_state_file
        )

        cleanup()
