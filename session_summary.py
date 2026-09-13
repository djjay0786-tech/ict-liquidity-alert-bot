from datetime import time


SESSION_CONFIG = {
    "ASIA": {
        "timezone": "Asia/Tokyo",
        "start": time(0, 0),
        "end": time(9, 0),
    },

    "LONDON": {
        "timezone": "Europe/London",
        "start": time(8, 0),
        "end": time(17, 0),
    },

    "NEW YORK": {
        "timezone": "America/New_York",
        "start": time(8, 0),
        "end": time(17, 0),
    },
}


def get_session_candles(
    df,
    session
):

    if session not in SESSION_CONFIG:
        raise ValueError(
            f"Unknown session: {session}"
        )

    if df is None or df.empty:
        return None

    config = SESSION_CONFIG[
        session
    ]

    timezone_name = config[
        "timezone"
    ]

    start_time = config[
        "start"
    ]

    end_time = config[
        "end"
    ]

    temp = df.copy()

    temp["datetime"] = (
        temp["datetime"]
        .dt.tz_convert(
            timezone_name
        )
    )

    latest_date = (
        temp["datetime"]
        .dt.date
        .max()
    )

    session_df = temp[
        (
            temp["datetime"]
            .dt.date
            == latest_date
        )
        &
        (
            temp["datetime"]
            .dt.time
            >= start_time
        )
        &
        (
            temp["datetime"]
            .dt.time
            < end_time
        )
    ]

    if session_df.empty:
        return None

    return session_df.copy()


def calculate_session_summary(
    symbol,
    session,
    df
):

    session_df = (
        get_session_candles(
            df,
            session
        )
    )

    if (
        session_df is None
        or session_df.empty
    ):
        return None

    first = session_df.iloc[0]
    last = session_df.iloc[-1]

    session_open = float(
        first["open"]
    )

    session_close = float(
        last["close"]
    )

    session_high = float(
        session_df["high"].max()
    )

    session_low = float(
        session_df["low"].min()
    )

    if session_close > session_open:

        direction = "BULLISH"

    elif session_close < session_open:

        direction = "BEARISH"

    else:

        direction = "NEUTRAL"

    raw_range = (
        session_high
        - session_low
    )

    if symbol in [
        "EUR/USD",
        "GBP/USD"
    ]:

        range_value = (
            raw_range
            * 10000
        )

        range_label = (
            f"{range_value:.1f} pips"
        )

    else:

        range_label = (
            f"{raw_range:.3f} points"
        )

    return {
        "symbol": symbol,
        "session": session,
        "date": str(
            first["datetime"].date()
        ),
        "open": session_open,
        "high": session_high,
        "low": session_low,
        "close": session_close,
        "direction": direction,
        "range": range_label,
        "candles": len(
            session_df
        ),
    }


def format_price(
    symbol,
    price
):

    if symbol in [
        "EUR/USD",
        "GBP/USD"
    ]:

        return f"{price:.5f}"

    return f"{price:.3f}"


def format_session_summary(
    summary
):

    if summary is None:
        return None

    direction = summary[
        "direction"
    ]

    if direction == "BULLISH":

        direction_text = (
            "🟢 BULLISH"
        )

    elif direction == "BEARISH":

        direction_text = (
            "🔴 BEARISH"
        )

    else:

        direction_text = (
            "⚪ NEUTRAL"
        )

    symbol = summary[
        "symbol"
    ]

    return (
        f"📊 {summary['session']} "
        f"SESSION SUMMARY\n\n"

        f"Symbol: {symbol}\n"
        f"Date: {summary['date']}\n\n"

        f"{direction_text}\n\n"

        f"Open: "
        f"{format_price(symbol, summary['open'])}\n"

        f"High: "
        f"{format_price(symbol, summary['high'])}\n"

        f"Low: "
        f"{format_price(symbol, summary['low'])}\n"

        f"Close: "
        f"{format_price(symbol, summary['close'])}\n\n"

        f"📏 Range: "
        f"{summary['range']}\n"

        f"🕯 Candles: "
        f"{summary['candles']}"
    )


def format_combined_session_summary(
    session,
    summaries
):

    message = (
        f"📊 {session} SESSION "
        f"SUMMARY\n\n"
    )

    valid = [
        item
        for item in summaries
        if item is not None
    ]

    if not valid:

        return (
            message
            + "No session data available."
        )

    for summary in valid:

        symbol = summary[
            "symbol"
        ]

        direction = summary[
            "direction"
        ]

        if direction == "BULLISH":
            emoji = "🟢"

        elif direction == "BEARISH":
            emoji = "🔴"

        else:
            emoji = "⚪"

        message += (
            f"{emoji} {symbol}\n"
            f"High: "
            f"{format_price(symbol, summary['high'])}\n"
            f"Low: "
            f"{format_price(symbol, summary['low'])}\n"
            f"Close: "
            f"{format_price(symbol, summary['close'])}\n"
            f"Range: "
            f"{summary['range']}\n\n"
        )

    return message.rstrip()
