from datetime import date, timedelta


def get_week_range(
    reference_date=None
):

    if reference_date is None:
        reference_date = date.today()

    if isinstance(
        reference_date,
        str
    ):

        reference_date = (
            date.fromisoformat(
                reference_date
            )
        )

    monday = (
        reference_date
        - timedelta(
            days=reference_date.weekday()
        )
    )

    friday = (
        monday
        + timedelta(
            days=4
        )
    )

    return monday, friday


def get_market_direction(
    week_open,
    week_close
):

    if week_close > week_open:
        return "BULLISH"

    if week_close < week_open:
        return "BEARISH"

    return "NEUTRAL"


def format_price(
    symbol,
    price
):

    if price is None:
        return "-"

    if symbol in [
        "EUR/USD",
        "GBP/USD"
    ]:

        return (
            f"{float(price):.5f}"
        )

    return (
        f"{float(price):.3f}"
    )


def get_direction_text(
    direction
):

    if direction == "BULLISH":
        return "🟢 BULLISH"

    if direction == "BEARISH":
        return "🔴 BEARISH"

    return "⚪ NEUTRAL"


def build_symbol_weekly_report(
    symbol,
    week_open,
    week_high,
    week_low,
    week_close,
    liquidity_events=None,
    crt_events=None,
    fvg_events=None,
    ob_events=None,
    confluence_events=None
):

    liquidity_events = (
        liquidity_events or []
    )

    crt_events = (
        crt_events or []
    )

    fvg_events = (
        fvg_events or []
    )

    ob_events = (
        ob_events or []
    )

    confluence_events = (
        confluence_events or []
    )

    direction = (
        get_market_direction(
            float(week_open),
            float(week_close)
        )
    )

    raw_range = (
        float(week_high)
        - float(week_low)
    )

    if symbol in [
        "EUR/USD",
        "GBP/USD"
    ]:

        range_text = (
            f"{raw_range * 10000:.1f} pips"
        )

    else:

        range_text = (
            f"{raw_range:.3f} points"
        )

    return {
        "symbol": symbol,

        "open":
            float(week_open),

        "high":
            float(week_high),

        "low":
            float(week_low),

        "close":
            float(week_close),

        "direction":
            direction,

        "range":
            range_text,

        "liquidity_count":
            len(liquidity_events),

        "crt_count":
            len(crt_events),

        "fvg_count":
            len(fvg_events),

        "ob_count":
            len(ob_events),

        "confluence_count":
            len(confluence_events),

        "liquidity_events":
            liquidity_events,

        "crt_events":
            crt_events,

        "fvg_events":
            fvg_events,

        "ob_events":
            ob_events,

        "confluence_events":
            confluence_events
    }


def format_symbol_weekly_report(
    report
):

    symbol = report[
        "symbol"
    ]

    direction_text = (
        get_direction_text(
            report[
                "direction"
            ]
        )
    )

    return (
        f"{symbol}\n"
        f"{direction_text}\n\n"

        f"Open: "
        f"{format_price(symbol, report['open'])}\n"

        f"High: "
        f"{format_price(symbol, report['high'])}\n"

        f"Low: "
        f"{format_price(symbol, report['low'])}\n"

        f"Close: "
        f"{format_price(symbol, report['close'])}\n"

        f"Range: "
        f"{report['range']}\n\n"

        f"💧 Liquidity: "
        f"{report['liquidity_count']}\n"

        f"🕯 CRT: "
        f"{report['crt_count']}\n"

        f"⬜ FVG: "
        f"{report['fvg_count']}\n"

        f"🧱 OB: "
        f"{report['ob_count']}\n"

        f"🔥 High Confluence: "
        f"{report['confluence_count']}"
    )


def format_weekly_ranking(
    rankings
):

    if not rankings:

        return (
            "🏆 WEEKLY FINAL RANKING\n"
            "No ranking data"
        )

    message = (
        "🏆 WEEKLY FINAL RANKING\n"
    )

    for item in rankings:

        rank = item.get(
            "rank",
            "-"
        )

        symbol = item.get(
            "symbol",
            "-"
        )

        status = item.get(
            "status",
            "NO SETUP"
        )

        direction = item.get(
            "direction"
        )

        if direction == "BULLISH":

            direction_text = (
                "🟢 BUY"
            )

        elif direction == "BEARISH":

            direction_text = (
                "🔴 SELL"
            )

        else:

            direction_text = (
                "⚪ NEUTRAL"
            )

        if (
            status
            == "HIGH CONFLUENCE"
        ):

            status_text = (
                "🔥 HIGH CONFLUENCE"
            )

        elif status == "WATCH":

            status_text = (
                "👀 WATCH"
            )

        else:

            status_text = (
                "➖ NO SETUP"
            )

        message += (
            f"\n#{rank} {symbol}\n"
            f"{direction_text} | "
            f"{status_text}\n"
        )

    return message.rstrip()


def format_weekly_report(
    symbol_reports,
    rankings=None,
    week_start=None,
    week_end=None
):

    if (
        week_start is None
        or week_end is None
    ):

        week_start, week_end = (
            get_week_range()
        )

    if isinstance(
        week_start,
        str
    ):

        week_start = (
            date.fromisoformat(
                week_start
            )
        )

    if isinstance(
        week_end,
        str
    ):

        week_end = (
            date.fromisoformat(
                week_end
            )
        )

    message = (
        "📊 ICT WEEKLY REPORT\n"
        f"{week_start.isoformat()} "
        f"→ {week_end.isoformat()}\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
    )

    valid_reports = [
        report
        for report in symbol_reports
        if report is not None
    ]

    if not valid_reports:

        return (
            message
            + "No weekly market data available."
        )

    for index, report in enumerate(
        valid_reports
    ):

        message += (
            format_symbol_weekly_report(
                report
            )
        )

        if index < (
            len(valid_reports) - 1
        ):

            message += (
                "\n\n"
                "━━━━━━━━━━━━━━━━━━"
                "\n\n"
            )

    message += (
        "\n\n"
        "━━━━━━━━━━━━━━━━━━"
        "\n\n"
    )

    message += (
        format_weekly_ranking(
            rankings
        )
    )

    return message
