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


def detect_crt(df):

    """
    CRT Logic

    Bullish CRT:
    1. Candle 1 sweeps previous candle LOW.
    2. Candle 2 closes above Candle 1 HIGH.
    3. Entry reference = Candle 3 OPEN.

    Bearish CRT:
    1. Candle 1 sweeps previous candle HIGH.
    2. Candle 2 closes below Candle 1 LOW.
    3. Entry reference = Candle 3 OPEN.
    """

    if df is None or len(df) < 4:
        return []

    alerts = []

    previous = df.iloc[-4]
    first = df.iloc[-3]
    second = df.iloc[-2]
    third = df.iloc[-1]

    # ==========================================
    # BULLISH CRT
    # ==========================================

    bullish_sweep = (
        float(first["low"])
        <
        float(previous["low"])
    )

    bullish_close = (
        float(second["close"])
        >
        float(first["high"])
    )

    if (
        bullish_sweep
        and bullish_close
    ):

        alerts.append({
            "type": "BULLISH CRT",

            "liquidity_side":
                "LOW SWEEP",

            "previous_low":
                float(previous["low"]),

            "first_candle_time":
                str(first["datetime"]),

            "first_high":
                float(first["high"]),

            "first_low":
                float(first["low"]),

            "second_candle_time":
                str(second["datetime"]),

            "confirmation_close":
                float(second["close"]),

            "entry_time":
                str(third["datetime"]),

            "entry_price":
                float(third["open"])
        })

    # ==========================================
    # BEARISH CRT
    # ==========================================

    bearish_sweep = (
        float(first["high"])
        >
        float(previous["high"])
    )

    bearish_close = (
        float(second["close"])
        <
        float(first["low"])
    )

    if (
        bearish_sweep
        and bearish_close
    ):

        alerts.append({
            "type": "BEARISH CRT",

            "liquidity_side":
                "HIGH SWEEP",

            "previous_high":
                float(previous["high"]),

            "first_candle_time":
                str(first["datetime"]),

            "first_high":
                float(first["high"]),

            "first_low":
                float(first["low"]),

            "second_candle_time":
                str(second["datetime"]),

            "confirmation_close":
                float(second["close"]),

            "entry_time":
                str(third["datetime"]),

            "entry_price":
                float(third["open"])
        })

    return alerts


def format_crt_alert(
    symbol,
    timeframe,
    alert
):

    if (
        alert["type"]
        == "BULLISH CRT"
    ):

        emoji = "🟢"

    else:

        emoji = "🔴"

    message = (
        f"{emoji} {alert['type']}\n\n"
        f"Symbol: {symbol}\n"
        f"Timeframe: {timeframe}\n\n"
        f"Liquidity: "
        f"{alert['liquidity_side']}\n\n"
        f"First Candle High: "
        f"{alert['first_high']:.5f}\n"
        f"First Candle Low: "
        f"{alert['first_low']:.5f}\n\n"
        f"Confirmation Close: "
        f"{alert['confirmation_close']:.5f}\n\n"
        f"Entry Reference "
        f"(3rd Candle Open): "
        f"{alert['entry_price']:.5f}\n\n"
        f"Confirmation Time: "
        f"{alert['second_candle_time']}\n"
        f"Entry Time: "
        f"{alert['entry_time']}"
    )

    return message
