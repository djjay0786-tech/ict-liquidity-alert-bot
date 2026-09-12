from market_data import get_candles
from order_block import prepare_candles
from ob_fvg import select_ob_near_fvg


TIMEFRAMES = {
    "H1": "1h",
    "H4": "4h",
    "DAILY": "1day"
}


def get_timeframe_ob(symbol, timeframe):

    interval = TIMEFRAMES[timeframe]

    data = get_candles(
        symbol,
        interval=interval,
        outputsize=200
    )

    if "values" not in data:
        return None

    df = prepare_candles(
        data["values"]
    )

    if df.empty:
        return None

    setup = select_ob_near_fvg(df)

    if setup is None:
        return None

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "ob": setup["ob"],
        "fvg": setup["fvg"],
        "distance": setup["distance"]
    }


def get_all_timeframe_obs(symbol):

    results = {}

    for timeframe in TIMEFRAMES:

        try:
            setup = get_timeframe_ob(
                symbol,
                timeframe
            )

            if setup is not None:
                results[timeframe] = setup

        except Exception as e:

            results[timeframe] = {
                "error": str(e)
            }

    return results


def format_mtf_ob(symbol, results):

    message = (
        f"📊 MULTI-TIMEFRAME OB\n\n"
        f"Symbol: {symbol}\n"
    )

    for timeframe, setup in results.items():

        message += (
            f"\n━━━━━━━━━━━━━━\n"
            f"⏱ {timeframe}\n"
        )

        if "error" in setup:
            message += (
                f"⚠️ Error: "
                f"{setup['error']}\n"
            )
            continue

        ob = setup["ob"]
        fvg = setup["fvg"]

        message += (
            f"OB: {ob['type']}\n"
            f"High: {ob['high']:.5f}\n"
            f"Low: {ob['low']:.5f}\n"
            f"OB Time: {ob['time']}\n\n"
            f"FVG: {fvg['type']}\n"
            f"FVG Top: {fvg['top']:.5f}\n"
            f"FVG Bottom: {fvg['bottom']:.5f}\n"
        )

    return message
