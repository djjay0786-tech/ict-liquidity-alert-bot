import pandas as pd


def is_price_in_ob(price, ob):

    return (
        float(ob["low"])
        <= float(price)
        <= float(ob["high"])
    )


def detect_first_tap(candle, ob):
    """
    Check whether a candle touches
    the Order Block zone.
    """

    if ob is None:
        return False

    candle_high = float(
        candle["high"]
    )

    candle_low = float(
        candle["low"]
    )

    ob_high = float(
        ob["high"]
    )

    ob_low = float(
        ob["low"]
    )

    touched = (
        candle_low <= ob_high
        and
        candle_high >= ob_low
    )

    return touched


def get_first_tap_after_ob(df, ob):
    """
    Find the FIRST candle that touched
    the OB AFTER the OB was created.

    This prevents candles before the OB
    from being counted as a first tap.
    """

    if df is None or df.empty:
        return None

    if ob is None:
        return None

    ob_time = pd.to_datetime(
        ob["time"],
        utc=True
    )

    for _, candle in df.iterrows():

        candle_time = pd.to_datetime(
            candle["datetime"],
            utc=True
        )

        # Ignore OB creation candle
        # and all older candles
        if candle_time <= ob_time:
            continue

        if detect_first_tap(
            candle,
            ob
        ):
            return candle

    return None


def has_historical_tap(
    df,
    ob,
    latest_candle_only=False
):
    """
    Check whether the selected OB was
    already touched after its creation.

    If the first touch happened before
    the latest candle, then the OB is
    already historically tapped.
    """

    first_tap = get_first_tap_after_ob(
        df,
        ob
    )

    if first_tap is None:
        return False

    if not latest_candle_only:
        return True

    latest_time = pd.to_datetime(
        df.iloc[-1]["datetime"],
        utc=True
    )

    tap_time = pd.to_datetime(
        first_tap["datetime"],
        utc=True
    )

    return tap_time < latest_time


def is_latest_candle_first_tap(
    df,
    ob
):
    """
    True ONLY when the latest candle
    is the first candle to touch the OB
    after the OB was created.
    """

    if df is None or df.empty:
        return False

    first_tap = get_first_tap_after_ob(
        df,
        ob
    )

    if first_tap is None:
        return False

    latest_time = pd.to_datetime(
        df.iloc[-1]["datetime"],
        utc=True
    )

    tap_time = pd.to_datetime(
        first_tap["datetime"],
        utc=True
    )

    return tap_time == latest_time


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
        f"OB High: {float(ob['high']):.5f}\n"
        f"OB Low: {float(ob['low']):.5f}\n\n"
        f"Tap Price: "
        f"{float(candle['close']):.5f}\n"
        f"Tap Time: "
        f"{candle['datetime']}"
    )
