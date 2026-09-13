from daily_report import (
    build_symbol_report,
    format_symbol_report,
    format_daily_report
)


def test_symbol_report():

    report = build_symbol_report(
        symbol="EUR/USD",
        day_open=1.10000,
        day_high=1.10800,
        day_low=1.09700,
        day_close=1.10500,
        liquidity_events=[
            {"type": "BULLISH LIQUIDITY GRAB"},
            {"type": "BEARISH LIQUIDITY GRAB"}
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

    assert report["symbol"] == "EUR/USD"
    assert report["direction"] == "BULLISH"
    assert report["liquidity_count"] == 2
    assert report["crt_count"] == 1
    assert report["fvg_count"] == 1
    assert report["ob_count"] == 1
    assert report["confluence_count"] == 1

    message = format_symbol_report(
        report
    )

    assert "EUR/USD" in message
    assert "BULLISH" in message
    assert "Liquidity: 2" in message

    print(
        "✅ Symbol report test passed"
    )

    print()
    print(message)


def test_full_daily_report():

    eur = build_symbol_report(
        symbol="EUR/USD",
        day_open=1.10000,
        day_high=1.10800,
        day_low=1.09700,
        day_close=1.10500,
        liquidity_events=[
            {"type": "BULLISH LIQUIDITY GRAB"}
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

    gbp = build_symbol_report(
        symbol="GBP/USD",
        day_open=1.28000,
        day_high=1.28500,
        day_low=1.27200,
        day_close=1.27500,
        liquidity_events=[
            {"type": "BEARISH LIQUIDITY GRAB"}
        ],
        crt_events=[
            {"type": "BEARISH CRT"}
        ],
        fvg_events=[],
        ob_events=[
            {"type": "BEARISH OB"}
        ],
        confluence_events=[]
    )

    dxy = build_symbol_report(
        symbol="DXY",
        day_open=101.200,
        day_high=101.900,
        day_low=100.900,
        day_close=101.650,
        liquidity_events=[],
        crt_events=[],
        fvg_events=[
            {"type": "BULLISH FVG"}
        ],
        ob_events=[],
        confluence_events=[]
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

    message = format_daily_report(
        symbol_reports=[
            eur,
            gbp,
            dxy
        ],
        rankings=rankings,
        report_date="2026-09-14"
    )

    assert "ICT DAILY REPORT" in message
    assert "EUR/USD" in message
    assert "GBP/USD" in message
    assert "DXY" in message
    assert "FINAL RANKING" in message
    assert "#1 EUR/USD" in message

    print()
    print(
        "✅ Full daily report test passed"
    )

    print()
    print(message)


def test_empty_report():

    message = format_daily_report(
        symbol_reports=[],
        rankings=[],
        report_date="2026-09-14"
    )

    assert (
        "No market data available."
        in message
    )

    print()
    print(
        "✅ Empty daily report test passed"
    )


if __name__ == "__main__":

    test_symbol_report()

    test_full_daily_report()

    test_empty_report()

    print()
    print(
        "📅 ALL DAILY REPORT TESTS PASSED"
    )
