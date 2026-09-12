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


def get_previous_day_levels(df):

    if df is None or df.empty:
        return None

    data = df.copy()

    data["date"] = (
        data["datetime"].dt.date
    )

    current_date = (
        data.iloc[-1]["date"]
    )

    previous_data = data[
        data["date"] < current_date
    ]

    if previous_data.empty:
        return None

    previous_date = (
        previous_data.iloc[-1]["date"]
    )

    previous_day = previous_data[
        previous_data["date"]
        == previous_date
    ]

    if previous_day.empty:
        return None

    pdh = float(
        previous_day["high"].max()
    )

    pdl = float(
        previous_day["low"].min()
    )

    return {
        "date": str(previous_date),
        "PDH": pdh,
        "PDL": pdl
    }


def previous_day_levels(df):

    levels = get_previous_day_levels(
        df
    )

    if levels is None:
        return None

    return {
        "PDH": levels["PDH"],
        "PDL": levels["PDL"]
    }


def current_day_levels(df):

    if df is None or df.empty:
        return None

    data = df.copy()

    data["date"] = (
        data["datetime"].dt.date
    )

    current_date = (
        data.iloc[-1]["date"]
    )

    current_day = data[
        data["date"]
        == current_date
    ]

    if current_day.empty:
        return None

    return {
        "DH": float(
            current_day["high"].max()
        ),
        "DL": float(
            current_day["low"].min()
        )
    }


def detect_liquidity_grab(df):

    if df is None or len(df) < 2:
        return []

    levels = get_previous_day_levels(
        df
    )

    if levels is None:
        return []

    latest = df.iloc[-1]

    pdh = float(
        levels["PDH"]
    )

    pdl = float(
        levels["PDL"]
    )

    latest_high = float(
        latest["high"]
    )

    latest_low = float(
        latest["low"]
    )

    alerts = []

    # ==================================
    # PDL SWEEP
    # ==================================

    if latest_low < pdl:

        alerts.append({
            "type":
                "BULLISH LIQUIDITY GRAB",

            "source":
                "PREVIOUS DAY",

            "level":
                "PDL",

            "level_date":
                levels["date"],

            "liquidity":
                pdl,

            "price":
                latest_low,

            "time":
                str(
                    latest["datetime"]
                )
        })

    # ==================================
    # PDH SWEEP
    # ==================================

    if latest_high > pdh:

        alerts.append({
            "type":
                "BEARISH LIQUIDITY GRAB",

            "source":
                "PREVIOUS DAY",

            "level":
                "PDH",

            "level_date":
                levels["date"],

            "liquidity":
                pdh,

            "price":
                latest_high,

            "time":
                str(
                    latest["datetime"]
                )
        })

    return alerts


def format_alert(
    symbol,
    alert
):

    if (
        alert["type"]
        ==
        "BULLISH LIQUIDITY GRAB"
    ):

        emoji = "🟢"

    else:

        emoji = "🔴"

    return (
        f"{emoji} PDH/PDL "
        f"LIQUIDITY GRAB\n\n"

        f"Symbol: {symbol}\n"

        f"Type: "
        f"{alert['type']}\n"

        f"Level: "
        f"{alert['level']}\n"

        f"Previous Day: "
        f"{alert['level_date']}\n\n"

        f"Liquidity Level: "
        f"{alert['liquidity']:.5f}\n"

        f"Sweep Price: "
        f"{alert['price']:.5f}\n\n"

        f"Time: "
        f"{alert['time']}"
    )
