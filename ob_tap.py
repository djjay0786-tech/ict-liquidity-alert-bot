def is_price_in_ob(price, ob):
    return (
        ob["low"] <= price <= ob["high"]
    )


def detect_first_tap(candle, ob):
    """
    Detect first price entry into the
    selected Order Block zone.
    """

    if ob is None:
        return False

    candle_high = float(candle["high"])
    candle_low = float(candle["low"])

    # Price touched the OB zone
    touched = (
        candle_low <= ob["high"]
        and
        candle_high >= ob["low"]
    )

    return touched


def create_tap_alert(
    symbol,
    timeframe,
    ob,
    candle
):

    if ob["type"] == "BULLISH OB":
        emoji = "🟢"
    else:
        emoji = "🔴"

    return (
        f"{emoji} ORDER BLOCK FIRST TAP\n\n"
        f"Symbol: {symbol}\n"
        f"Timeframe: {timeframe}\n\n"
        f"Type: {ob['type']}\n"
        f"OB High: {ob['high']:.5f}\n"
        f"OB Low: {ob['low']:.5f}\n\n"
        f"Tap Price: "
        f"{float(candle['close']):.5f}\n"
        f"Tap Time: "
        f"{candle['datetime']}"
    )
