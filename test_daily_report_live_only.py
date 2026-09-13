import json
from pathlib import Path
from datetime import date

import pandas as pd

import alert_state

from daily_report_live import (
    parse_alert_id,
    get_alert_history_for_day,
    get_ist_day_ohlc
)


TEST_STATE_FILE = Path(
    "alert_state_daily_test.json"
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
            "CRT|EUR/USD|H1|"
            "2026-09-14T07:00:00+00:00|"
            "BULLISH CRT"
        ): {
            "sent": True,
            "details": {
                "type": "BULLISH CRT",
                "second_candle_time":
                    "2026-09-14T07:00:00+00:00"
            }
        },

        (
            "FVG|EUR/USD|H1|"
            "2026-09-14T08:00:00+00:00|"
            "BULLISH FVG"
        ): {
            "sent": True,
            "details": {
                "type": "BULLISH FVG",
                "time":
                    "2026-09-14T08:00:00+00:00"
            }
        },

        (
            "OB_FVG|EUR/USD|H1|"
            "2026-09-14T08:00:00+00:00|"
            "BULLISH OB"
        ): {
            "sent": True,
            "details": {
                "ob": {
                    "type":
                        "BULLISH OB"
                },
                "fvg": {
                    "type":
                        "BULLISH FVG"
                }
            }
        },

        (
            "HIGH_CONFLUENCE|EUR/USD|H1|"
            "2026-09-14T09:00:00+00:00|BUY"
        ): {
            "sent": True,
            "details": {
                "trade": "BUY"
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


def test_parse_alert_id():

    result = parse_alert_id(
        "CRT|EUR/USD|H1|"
        "2026-09-14T07:00:00+00:00|"
        "BULLISH CRT"
    )

    assert (
        result["alert_type"]
        == "CRT"
    )

    assert (
        result["symbol"]
        == "EUR/USD"
    )

    assert (
        result["timeframe"]
        == "H1"
    )

    print(
        "✅ Alert ID parsing passed"
    )


def test_alert_history():

    history = (
        get_alert_history_for_day(
            symbol="EUR/USD",
            report_date=date(
                2026,
                9,
                14
            )
        )
    )

    assert (
        len(history["liquidity"])
        == 1
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
        "✅ Daily alert history passed"
    )


def test_day_ohlc():

    df = pd.DataFrame([
        {
            "datetime":
                "2026-09-14T00:00:00+00:00",
            "open": 1.1000,
            "high": 1.1020,
            "low": 1.0990,
            "close": 1.1010
        },

        {
            "datetime":
                "2026-09-14T06:00:00+00:00",
            "open": 1.1010,
            "high": 1.1050,
            "low": 1.1000,
            "close": 1.1040
        },

        {
            "datetime":
                "2026-09-14T12:00:00+00:00",
            "open": 1.1040,
            "high": 1.1080,
            "low": 1.1030,
            "close": 1.1070
        }
    ])

    df["datetime"] = (
        pd.to_datetime(
            df["datetime"],
            utc=True
        )
    )

    result = get_ist_day_ohlc(
        df,
        date(
            2026,
            9,
            14
        )
    )

    assert result is not None

    assert (
        result["open"]
        == 1.1000
    )

    assert (
        result["high"]
        == 1.1080
    )

    assert (
        result["low"]
        == 1.0990
    )

    assert (
        result["close"]
        == 1.1070
    )

    assert (
        result["candles"]
        == 3
    )

    print(
        "✅ IST daily OHLC passed"
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

        test_parse_alert_id()

        test_alert_history()

        test_day_ohlc()

        print()

        print(
            "📅 ALL DAILY REPORT "
            "LIVE TESTS PASSED"
        )

    finally:

        alert_state.STATE_FILE = (
            original_state_file
        )

        cleanup()
