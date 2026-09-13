import pandas as pd


def is_price_in_ob(
    price,
    ob
):

    return (
        float(ob["low"])
        <=
        float(price)
        <=
        float(ob["high"])
    )


def detect_first_tap(
    candle,
    ob
):

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

    return (
        candle_low <= ob_high
        and
        candle_high >= ob_low
    )


def get_tap_start_index(
    ob
):

    """
    First legitimate tap can only
    happen AFTER the OB confirmation
    / displacement candle.
    """

    if (
        "confirmation_index"
        in ob
    ):

        return (
            int(
                ob[
                    "confirmation_index"
                ]
            )
            + 1
        )

    # Compatibility with older OB data.
    return (
        int(
            ob.get(
                "index",
                0
            )
        )
        + 2
    )


def get_first_tap_after_ob(
    df,
    ob
):

    """
    Find first real retracement/tap.

    OB candle is ignored.
    Confirmation/displacement candle
    is also ignored.
    """

    if (
        df is None
        or df.empty
        or ob is None
    ):
        return None

    start_index = (
        get_tap_start_index(
            ob
        )
    )

    if start_index >= len(df):
        return None

    future = df.iloc[
        start_index:
    ]

    for _, candle in future.iterrows():

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

    first_tap = (
        get_first_tap_after_ob(
            df,
            ob
        )
    )

    if first_tap is None:
        return False

    if not latest_candle_only:
        return True

    latest_time = pd.to_datetime(
        df.iloc[-1][
            "datetime"
        ],
        utc=True
    )

    tap_time = pd.to_datetime(
        first_tap[
            "datetime"
        ],
        utc=True
    )

    return (
        tap_time
        <
        latest_time
    )


def is_latest_candle_first_tap(
    df,
    ob
):

    """
    True only when the latest candle
    is the first REAL retracement
    into the OB after confirmation.
    """

    if (
        df is None
        or df.empty
        or ob is None
    ):
        return False

    first_tap = (
        get_first_tap_after_ob(
            df,
            ob
        )
    )

    if first_tap is None:
        return False

    latest_time = pd.to_datetime(
        df.iloc[-1][
            "datetime"
        ],
        utc=True
    )

    tap_time = pd.to_datetime(
        first_tap[
            "datetime"
        ],
        utc=True
    )

    return (
        tap_time
        ==
        latest_time
    )


def create_tap_alert(
    symbol,
    timeframe,
    ob,
    candle
):

    if (
        ob["type"]
        ==
        "BULLISH OB"
    ):

        emoji = "🟢"

    else:

        emoji = "🔴"

    return (
        f"{emoji} ORDER BLOCK FIRST TAP\n\n"

        f"Symbol: "
        f"{symbol}\n"

        f"Timeframe: "
        f"{timeframe}\n\n"

        f"Type: "
        f"{ob['type']}\n"

        f"OB High: "
        f"{float(ob['high']):.5f}\n"

        f"OB Low: "
        f"{float(ob['low']):.5f}\n\n"

        f"Tap Price: "
        f"{float(candle['close']):.5f}\n"

        f"Tap Time: "
        f"{candle['datetime']}"
    )
