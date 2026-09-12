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


def detect_fvg(df):

    """
    Standard 3-candle FVG detection.

    Bullish FVG:
    Candle 1 HIGH < Candle 3 LOW

    Bearish FVG:
    Candle 1 LOW > Candle 3 HIGH
    """

    if df is None or len(df) < 3:
        return []

    fvgs = []

    for i in range(
        2,
        len(df)
    ):

        first = df.iloc[i - 2]
        middle = df.iloc[i - 1]
        third = df.iloc[i]

        # =====================================
        # BULLISH FVG
        # =====================================

        if (
            float(first["high"])
            <
            float(third["low"])
        ):

            bottom = float(
                first["high"]
            )

            top = float(
                third["low"]
            )

            fvgs.append({
                "type": "BULLISH FVG",
                "time": str(
                    third["datetime"]
                ),
                "index": i,
                "top": top,
                "bottom": bottom,
                "midpoint": (
                    top + bottom
                ) / 2,
                "size": (
                    top - bottom
                ),
                "middle_candle": str(
                    middle["datetime"]
                )
            })

        # =====================================
        # BEARISH FVG
        # =====================================

        if (
            float(first["low"])
            >
            float(third["high"])
        ):

            top = float(
                first["low"]
            )

            bottom = float(
                third["high"]
            )

            fvgs.append({
                "type": "BEARISH FVG",
                "time": str(
                    third["datetime"]
                ),
                "index": i,
                "top": top,
                "bottom": bottom,
                "midpoint": (
                    top + bottom
                ) / 2,
                "size": (
                    top - bottom
                ),
                "middle_candle": str(
                    middle["datetime"]
                )
            })

    return fvgs


def is_fvg_mitigated(
    df,
    fvg
):

    """
    FULL mitigation rule.

    Bullish FVG:
    Price must trade through the
    FVG bottom to fully mitigate it.

    Bearish FVG:
    Price must trade through the
    FVG top to fully mitigate it.

    FVG creation candle is ignored.
    """

    if (
        df is None
        or df.empty
        or fvg is None
    ):
        return False

    start_index = (
        int(fvg["index"]) + 1
    )

    if start_index >= len(df):
        return False

    future = df.iloc[
        start_index:
    ]

    if (
        fvg["type"]
        == "BULLISH FVG"
    ):

        for _, candle in future.iterrows():

            if (
                float(candle["low"])
                <=
                float(fvg["bottom"])
            ):

                return True

    elif (
        fvg["type"]
        == "BEARISH FVG"
    ):

        for _, candle in future.iterrows():

            if (
                float(candle["high"])
                >=
                float(fvg["top"])
            ):

                return True

    return False


def get_valid_fvgs(
    df,
    direction=None
):

    """
    Return FVGs that have NOT been
    fully mitigated.

    direction examples:
    BULLISH
    BEARISH
    """

    fvgs = detect_fvg(
        df
    )

    valid = []

    for fvg in fvgs:

        if direction:

            wanted_type = (
                f"{direction.upper()} FVG"
            )

            if (
                fvg["type"]
                != wanted_type
            ):
                continue

        if not is_fvg_mitigated(
            df,
            fvg
        ):

            valid.append(
                fvg
            )

    return valid


def get_last_fvg(
    df,
    direction=None,
    valid_only=True
):

    """
    Get latest relevant FVG.

    By default only an unmitigated
    FVG is returned.
    """

    if valid_only:

        fvgs = get_valid_fvgs(
            df,
            direction
        )

    else:

        fvgs = detect_fvg(
            df
        )

        if direction:

            wanted_type = (
                f"{direction.upper()} FVG"
            )

            fvgs = [
                fvg
                for fvg in fvgs
                if fvg["type"]
                == wanted_type
            ]

    if not fvgs:
        return None

    return fvgs[-1]


def format_fvg_alert(
    symbol,
    timeframe,
    fvg
):

    if (
        fvg["type"]
        == "BULLISH FVG"
    ):

        emoji = "🟢"

    else:

        emoji = "🔴"

    return (
        f"{emoji} {fvg['type']}\n\n"
        f"Symbol: {symbol}\n"
        f"Timeframe: {timeframe}\n\n"
        f"FVG Top: "
        f"{fvg['top']:.5f}\n"
        f"FVG Bottom: "
        f"{fvg['bottom']:.5f}\n"
        f"FVG Midpoint: "
        f"{fvg['midpoint']:.5f}\n"
        f"FVG Size: "
        f"{fvg['size']:.5f}\n\n"
        f"FVG Time: "
        f"{fvg['time']}"
    )
