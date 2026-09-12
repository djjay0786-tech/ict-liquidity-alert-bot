import pandas as pd


def prepare_candles(values):
    df = pd.DataFrame(values)

    if df.empty:
        return df

    df["datetime"] = pd.to_datetime(
        df["datetime"],
        utc=True
    )

    for column in ["open", "high", "low", "close"]:
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

    df = df.sort_values("datetime")
    df = df.reset_index(drop=True)

    return df


def detect_fvg(df):

    if len(df) < 3:
        return []

    fvgs = []

    for i in range(2, len(df)):

        first = df.iloc[i - 2]
        middle = df.iloc[i - 1]
        third = df.iloc[i]

        # =====================================
        # BULLISH FVG
        # First candle HIGH < Third candle LOW
        # =====================================

        if first["high"] < third["low"]:

            fvgs.append({
                "type": "BULLISH FVG",
                "time": str(third["datetime"]),
                "top": float(third["low"]),
                "bottom": float(first["high"]),
                "middle_candle": str(
                    middle["datetime"]
                )
            })

        # =====================================
        # BEARISH FVG
        # First candle LOW > Third candle HIGH
        # =====================================

        if first["low"] > third["high"]:

            fvgs.append({
                "type": "BEARISH FVG",
                "time": str(third["datetime"]),
                "top": float(first["low"]),
                "bottom": float(third["high"]),
                "middle_candle": str(
                    middle["datetime"]
                )
            })

    return fvgs


def get_last_fvg(df):

    fvgs = detect_fvg(df)

    if not fvgs:
        return None

    return fvgs[-1]


def format_fvg_alert(symbol, timeframe, fvg):

    if fvg["type"] == "BULLISH FVG":
        emoji = "🟢"
    else:
        emoji = "🔴"

    message = (
        f"{emoji} {fvg['type']}\n\n"
        f"Symbol: {symbol}\n"
        f"Timeframe: {timeframe}\n\n"
        f"FVG Top: "
        f"{fvg['top']:.5f}\n"
        f"FVG Bottom: "
        f"{fvg['bottom']:.5f}\n\n"
        f"FVG Time: "
        f"{fvg['time']}"
    )

    return message
