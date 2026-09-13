from datetime import datetime
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")


def get_market_direction(
    day_open,
    day_close
):

    if day_close > day_open:
        return "BULLISH"

    if day_close < day_open:
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
        return f"{float(price):.5f}"

    return f"{float(price):.3f}"


def get_direction_text(
    direction
):

    if direction == "BULLISH":
        return "🟢 BULLISH"

    if direction == "BEARISH":
        return "🔴 BEARISH"

    return "⚪ NEUTRAL"


def build_symbol_report(
    symbol,
    day_open,
    day_high,
    day_low,
    day_close,
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
            float(day_open),
            float(day_close)
        )
    )

    return {
        "symbol": symbol,

        "open": float(day_open),
        "high": float(day_high),
        "low": float(day_low),
        "close": float(day_close),

        "direction": direction,

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


def format_symbol_report(
    report
):

    symbol = report[
        "symbol"
    ]

    direction_text = (
        get_direction_text(
            report["direction"]
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
        f"{format_price(symbol, report['close'])}\n\n"

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


def format_ranking_section(
    rankings
):

    if not rankings:

        return (
            "🏆 FINAL RANKING\n"
            "No ranking data"
        )

    message = (
        "🏆 FINAL RANKING\n"
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
            direction_text = "🟢 BUY"

        elif direction == "BEARISH":
            direction_text = "🔴 SELL"

        else:
            direction_text = "⚪ NEUTRAL"

        if status == "HIGH CONFLUENCE":

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


def format_daily_report(
    symbol_reports,
    rankings=None,
    report_date=None
):

    if report_date is None:

        report_date = (
            datetime.now(
                IST
            )
            .date()
            .isoformat()
        )

    message = (
        "📅 ICT DAILY REPORT\n"
        f"Date: {report_date}\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
    )

    valid_reports = [
        report
        for report in symbol_reports
        if report is not None
    ]

    if not valid_reports:

        message += (
            "No market data available."
        )

        return message

    for index, report in enumerate(
        valid_reports
    ):

        message += (
            format_symbol_report(
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
        format_ranking_section(
            rankings
        )
    )

    return message
