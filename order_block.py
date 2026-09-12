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


def detect_order_blocks(df):

    if len(df) < 5:
        return []

    order_blocks = []

    for i in range(1, len(df) - 2):

        candle = df.iloc[i]
        next_candle = df.iloc[i + 1]

        # =====================================
        # BULLISH ORDER BLOCK
        # Last bearish candle before
        # strong bullish displacement
        # =====================================

        if (
            candle["close"] < candle["open"]
            and
            next_candle["close"] > candle["high"]
        ):

            order_blocks.append({
                "type": "BULLISH OB",
                "time": str(candle["datetime"]),
                "high": float(candle["high"]),
                "low": float(candle["low"]),
                "open": float(candle["open"]),
                "close": float(candle["close"])
            })

        # =====================================
        # BEARISH ORDER BLOCK
        # Last bullish candle before
        # strong bearish displacement
        # =====================================

        if (
            candle["close"] > candle["open"]
            and
            next_candle["close"] < candle["low"]
        ):

            order_blocks.append({
                "type": "BEARISH OB",
                "time": str(candle["datetime"]),
                "high": float(candle["high"]),
                "low": float(candle["low"]),
                "open": float(candle["open"]),
                "close": float(candle["close"])
            })

    return order_blocks


def get_last_order_block(df):

    order_blocks = detect_order_blocks(df)

    if not order_blocks:
        return None

    return order_blocks[-1]


def format_ob_alert(symbol, timeframe, ob):

    if ob["type"] == "BULLISH OB":
        emoji = "🟢"
    else:
        emoji = "🔴"

    message = (
        f"{emoji} {ob['type']}\n\n"
        f"Symbol: {symbol}\n"
        f"Timeframe: {timeframe}\n\n"
        f"OB High: {ob['high']:.5f}\n"
        f"OB Low: {ob['low']:.5f}\n\n"
        f"OB Time: {ob['time']}"
    )

    return message
