from datetime import date

from weekly_report import (
    get_week_range,
    build_symbol_weekly_report,
    format_symbol_weekly_report,
    format_weekly_report
)


def test_week_range():

    week_start, week_end = (
        get_week_range(
            date(
                2026,
                9,
                17
            )
        )
    )

    assert (
        week_start.isoformat()
        == "2026-09-14"
    )

    assert (
        week_end.isoformat()
        == "2026-09-18"
    )

    print(
        "✅ Week range test passed"
    )


def test_symbol_weekly_report():

    report = (
        build_symbol_weekly_report(
            symbol="EUR/USD",

            week_open=1.10000,
            week_high=1.12000,
            week_low=1.09500,
            week_close=1.11500,

            liquidity_events=[
                {"type": "PDL"},
                {"type": "ASIA LOW"}
            ],

            crt_events=[
                {"type": "BULLISH CRT"}
            ],

            fvg_events=[
                {"type": "BULLISH FVG"}
            ],

            ob_events=[
                {"type": "BULLISH OB"}
            ],

            confluence_events=[
                {"trade": "BUY"}
            ]
        )
    )

    assert (
        report["direction"]
        == "BULLISH"
    )

    assert (
        report["liquidity_count"]
        == 2
    )

    assert (
        report["crt_count"]
        == 1
    )

    assert (
        report["fvg_count"]
        == 1
    )

    assert (
        report["ob_count"]
        == 1
    )

    assert (
        report["confluence_count"]
        == 1
    )

    message = (
        format_symbol_weekly_report(
            report
        )
    )

    assert "EUR/USD" in message
    assert "BULLISH" in message
    assert "250.0 pips" in message

    print(
        "✅ Symbol weekly report passed"
    )

    print()
    print(message)


def test_full_weekly_report():

    eur = (
        build_symbol_weekly_report(
            symbol="EUR/USD",
            week_open=1.10000,
            week_high=1.12000,
            week_low=1.09500,
            week_close=1.11500,
            liquidity_events=[{}],
            crt_events=[{}],
            fvg_events=[{}],
            ob_events=[{}],
            confluence_events=[{}]
        )
    )

    gbp = (
        build_symbol_weekly_report(
            symbol="GBP/USD",
            week_open=1.28000,
            week_high=1.29000,
            week_low=1.26000,
            week_close=1.27000,
            liquidity_events=[{}, {}],
            crt_events=[{}],
            fvg_events=[],
            ob_events=[{}],
            confluence_events=[]
        )
    )

    dxy = (
        build_symbol_weekly_report(
            symbol="DXY",
            week_open=101.200,
            week_high=102.300,
            week_low=100.800,
            week_close=102.000,
            liquidity_events=[],
            crt_events=[],
            fvg_events=[{}],
            ob_events=[],
            confluence_events=[]
        )
    )

    rankings = [
        {
            "rank": 1,
            "symbol": "EUR/USD",
            "status": "HIGH CONFLUENCE",
            "direction": "BULLISH"
        },
        {
            "rank": 2,
            "symbol": "GBP/USD",
            "status": "WATCH",
            "direction": "BEARISH"
        },
        {
            "rank": 3,
            "symbol": "DXY",
            "status": "NO SETUP",
            "direction": None
        }
    ]

    message = (
        format_weekly_report(
            symbol_reports=[
                eur,
                gbp,
                dxy
            ],

            rankings=rankings,

            week_start="2026-09-14",
            week_end="2026-09-18"
        )
    )

    assert (
        "ICT WEEKLY REPORT"
        in message
    )

    assert (
        "EUR/USD"
        in message
    )

    assert (
        "GBP/USD"
        in message
    )

    assert (
        "DXY"
        in message
    )

    assert (
        "WEEKLY FINAL RANKING"
        in message
    )

    assert (
        "#1 EUR/USD"
        in message
    )

    print()
    print(
        "✅ Full weekly report passed"
    )

    print()
    print(message)


def test_empty_weekly_report():

    message = (
        format_weekly_report(
            symbol_reports=[],
            rankings=[],
            week_start="2026-09-14",
            week_end="2026-09-18"
        )
    )

    assert (
        "No weekly market data available."
        in message
    )

    print()
    print(
        "✅ Empty weekly report passed"
    )


if __name__ == "__main__":

    test_week_range()

    test_symbol_weekly_report()

    test_full_weekly_report()

    test_empty_weekly_report()

    print()
    print(
        "📊 ALL WEEKLY REPORT TESTS PASSED"
    )
