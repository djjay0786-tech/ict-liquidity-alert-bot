import pandas as pd


def prepare_candles(values):

    df = pd.DataFrame(values)

    if df.empty:
        return df

    df["datetime"] = pd.to_datetime(
        df["datetime"],
        utc=True
    )

    for column in [
        "open",
        "high",
        "low",
        "close"
    ]:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.dropna(
        subset=[
            "datetime",
            "open",
            "high",
            "low",
            "close"
        ]
    )

    df = df.sort_values(
        "datetime"
    )

    df = df.reset_index(
        drop=True
    )

    return df


def detect_order_blocks(df):

    """
    Refined Order Block logic.

    Bullish OB:
    - Bearish candle
    - Next candle shows displacement upward
    - Next candle closes above OB high

    Bearish OB:
    - Bullish candle
    - Next candle shows displacement downward
    - Next candle closes below OB low
    """

    if df is None or len(df) < 3:
        return []

    order_blocks = []

    for i in range(
        0,
        len(df) - 1
    ):

        candle = df.iloc[i]
        next_candle = df.iloc[i + 1]

        candle_open = float(
            candle["open"]
        )

        candle_close = float(
            candle["close"]
        )

        candle_high = float(
            candle["high"]
        )

        candle_low = float(
            candle["low"]
        )

        next_open = float(
            next_candle["open"]
        )

        next_close = float(
            next_candle["close"]
        )

        next_high = float(
            next_candle["high"]
        )

        next_low = float(
            next_candle["low"]
        )

        candle_range = max(
            candle_high - candle_low,
            0.0000001
        )

        next_body = abs(
            next_close - next_open
        )

        strong_displacement = (
            next_body
            >=
            candle_range * 0.5
        )

        # =====================================
        # BULLISH ORDER BLOCK
        # =====================================

        bearish_candle = (
            candle_close
            <
            candle_open
        )

        bullish_break = (
            next_close
            >
            candle_high
        )

        bullish_displacement = (
            next_close
            >
            next_open
        )

        if (
            bearish_candle
            and bullish_break
            and bullish_displacement
            and strong_displacement
        ):

            order_blocks.append({
                "type": "BULLISH OB",
                "time": str(
                    candle["datetime"]
                ),
                "index": i,
                "high": candle_high,
                "low": candle_low,
                "open": candle_open,
                "close": candle_close,
                "midpoint": (
                    candle_high
                    +
                    candle_low
                ) / 2
            })

        # =====================================
        # BEARISH ORDER BLOCK
        # =====================================

        bullish_candle = (
            candle_close
            >
            candle_open
        )

        bearish_break = (
            next_close
            <
            candle_low
        )

        bearish_displacement = (
            next_close
            <
            next_open
        )

        if (
            bullish_candle
            and bearish_break
            and bearish_displacement
            and strong_displacement
        ):

            order_blocks.append({
                "type": "BEARISH OB",
                "time": str(
                    candle["datetime"]
                ),
                "index": i,
                "high": candle_high,
                "low": candle_low,
                "open": candle_open,
                "close": candle_close,
                "midpoint": (
                    candle_high
                    +
                    candle_low
                ) / 2
            })

    return order_blocks


def is_ob_mitigated(
    df,
    ob
):

    """
    Full mitigation rule.

    Bullish OB:
    price trades through OB low.

    Bearish OB:
    price trades through OB high.

    OB creation candle is ignored.
    """

    if (
        df is None
        or df.empty
        or ob is None
    ):
        return False

    start_index = (
        int(ob["index"]) + 1
    )

    if start_index >= len(df):
        return False

    future = df.iloc[
        start_index:
    ]

    if (
        ob["type"]
        == "BULLISH OB"
    ):

        for _, candle in future.iterrows():

            if (
                float(candle["low"])
                <=
                float(ob["low"])
            ):

                return True

    elif (
        ob["type"]
        == "BEARISH OB"
    ):

        for _, candle in future.iterrows():

            if (
                float(candle["high"])
                >=
                float(ob["high"])
            ):

                return True

    return False


def get_valid_order_blocks(
    df,
    direction=None
):

    """
    Return only unmitigated OBs.

    direction:
    BULLISH
    BEARISH
    """

    order_blocks = (
        detect_order_blocks(
            df
        )
    )

    valid = []

    for ob in order_blocks:

        if direction:

            wanted_type = (
                f"{direction.upper()} OB"
            )

            if (
                ob["type"]
                != wanted_type
            ):
                continue

        if not is_ob_mitigated(
            df,
            ob
        ):

            valid.append(
                ob
            )

    return valid


def get_last_order_block(
    df,
    direction=None,
    valid_only=True
):

    if valid_only:

        order_blocks = (
            get_valid_order_blocks(
                df,
                direction
            )
        )

    else:

        order_blocks = (
            detect_order_blocks(
                df
            )
        )

        if direction:

            wanted_type = (
                f"{direction.upper()} OB"
            )

            order_blocks = [
                ob
                for ob in order_blocks
                if ob["type"]
                == wanted_type
            ]

    if not order_blocks:
        return None

    return order_blocks[-1]


def format_ob_alert(
    symbol,
    timeframe,
    ob
):

    if (
        ob["type"]
        == "BULLISH OB"
    ):

        emoji = "🟢"

    else:

        emoji = "🔴"

    return (
        f"{emoji} {ob['type']}\n\n"
        f"Symbol: {symbol}\n"
        f"Timeframe: {timeframe}\n\n"
        f"OB High: "
        f"{ob['high']:.5f}\n"
        f"OB Low: "
        f"{ob['low']:.5f}\n"
        f"OB Midpoint: "
        f"{ob['midpoint']:.5f}\n\n"
        f"OB Time: "
        f"{ob['time']}"
    )
