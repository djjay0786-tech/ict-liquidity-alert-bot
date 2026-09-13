from urllib.parse import quote


SYMBOL_MAP = {
    "EUR/USD": "OANDA:EURUSD",
    "GBP/USD": "OANDA:GBPUSD",
    "DXY": "TVC:DXY",
}


TIMEFRAME_MAP = {
    "H1": "60",
    "H4": "240",
    "DAILY": "1D",
}


BASE_URL = (
    "https://www.tradingview.com/chart/"
)


def get_tradingview_symbol(
    symbol
):

    return SYMBOL_MAP.get(
        symbol
    )


def get_tradingview_interval(
    timeframe
):

    return TIMEFRAME_MAP.get(
        timeframe
    )


def get_tradingview_link(
    symbol,
    timeframe=None
):

    tv_symbol = (
        get_tradingview_symbol(
            symbol
        )
    )

    if tv_symbol is None:

        return None

    encoded_symbol = quote(
        tv_symbol,
        safe=""
    )

    url = (
        f"{BASE_URL}"
        f"?symbol={encoded_symbol}"
    )

    if timeframe:

        interval = (
            get_tradingview_interval(
                timeframe
            )
        )

        if interval:

            url += (
                f"&interval={interval}"
            )

    return url


def format_tradingview_link(
    symbol,
    timeframe=None
):

    url = get_tradingview_link(
        symbol,
        timeframe
    )

    if url is None:
        return ""

    return (
        f"📈 TradingView Chart:\n"
        f"{url}"
    )


def add_tradingview_link(
    message,
    symbol,
    timeframe=None
):

    chart = (
        format_tradingview_link(
            symbol,
            timeframe
        )
    )

    if not chart:
        return message

    return (
        f"{message}\n\n"
        f"{chart}"
    )
