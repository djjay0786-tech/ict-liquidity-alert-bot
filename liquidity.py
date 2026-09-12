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


# ==========================================
# PREVIOUS DAY HIGH / LOW
# ==========================================

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

    return {
        "date": str(previous_date),

        "PDH": float(
            previous_day["high"].max()
        ),

        "PDL": float(
            previous_day["low"].min()
        )
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


# ==========================================
# CURRENT DAY HIGH / LOW
# ==========================================

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
        data["date"] == current_date
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


def get_prior_current_day_levels(df):

    """
    Today's High/Low BEFORE
    the latest candle.
    """

    if df is None or len(df) < 2:
        return None

    data = df.copy()

    data["date"] = (
        data["datetime"].dt.date
    )

    current_date = (
        data.iloc[-1]["date"]
    )

    prior_today = data.iloc[:-1]

    prior_today = prior_today[
        prior_today["date"]
        == current_date
    ]

    if prior_today.empty:
        return None

    return {
        "date": str(current_date),

        "DH": float(
            prior_today["high"].max()
        ),

        "DL": float(
            prior_today["low"].min()
        )
    }


# ==========================================
# PDH / PDL
# FIRST SWEEP OF CURRENT DAY ONLY
# ==========================================

def detect_liquidity_grab(df):

    if df is None or len(df) < 2:
        return []

    data = df.copy()

    data["date"] = (
        data["datetime"].dt.date
    )

    levels = get_previous_day_levels(
        data
    )

    if levels is None:
        return []

    current_date = (
        data.iloc[-1]["date"]
    )

    current_day = data[
        data["date"]
        == current_date
    ].copy()

    if current_day.empty:
        return []

    latest = current_day.iloc[-1]

    prior_today = (
        current_day.iloc[:-1]
    )

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

    # Check whether PDH was already
    # swept earlier today.
    pdh_already_swept = False

    if not prior_today.empty:

        pdh_already_swept = bool(
            (
                prior_today["high"]
                > pdh
            ).any()
        )

    # Check whether PDL was already
    # swept earlier today.
    pdl_already_swept = False

    if not prior_today.empty:

        pdl_already_swept = bool(
            (
                prior_today["low"]
                < pdl
            ).any()
        )

    alerts = []

    # PDL FIRST SWEEP
    if (
        latest_low < pdl
        and
        not pdl_already_swept
    ):

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

    # PDH FIRST SWEEP
    if (
        latest_high > pdh
        and
        not pdh_already_swept
    ):

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


# ==========================================
# CURRENT DAY DH / DL
# ==========================================

def detect_daily_liquidity_grab(df):

    if df is None or len(df) < 2:
        return []

    levels = (
        get_prior_current_day_levels(
            df
        )
    )

    if levels is None:
        return []

    latest = df.iloc[-1]

    latest_high = float(
        latest["high"]
    )

    latest_low = float(
        latest["low"]
    )

    dh = float(
        levels["DH"]
    )

    dl = float(
        levels["DL"]
    )

    alerts = []

    # Prior intraday Low swept
    if latest_low < dl:

        alerts.append({
            "type":
                "BULLISH LIQUIDITY GRAB",

            "source":
                "CURRENT DAY",

            "level":
                "DL",

            "level_date":
                levels["date"],

            "liquidity":
                dl,

            "price":
                latest_low,

            "time":
                str(
                    latest["datetime"]
                )
        })

    # Prior intraday High swept
    if latest_high > dh:

        alerts.append({
            "type":
                "BEARISH LIQUIDITY GRAB",

            "source":
                "CURRENT DAY",

            "level":
                "DH",

            "level_date":
                levels["date"],

            "liquidity":
                dh,

            "price":
                latest_high,

            "time":
                str(
                    latest["datetime"]
                )
        })

    return alerts


# ==========================================
# TELEGRAM FORMAT
# ==========================================

def format_alert(
    symbol,
    alert
):

    if (
        alert["type"]
        == "BULLISH LIQUIDITY GRAB"
    ):

        emoji = "🟢"

    else:

        emoji = "🔴"

    return (
        f"{emoji} LIQUIDITY GRAB\n\n"

        f"Symbol: {symbol}\n"

        f"Source: "
        f"{alert['source']}\n"

        f"Level: "
        f"{alert['level']}\n"

        f"Level Date: "
        f"{alert['level_date']}\n\n"

        f"Liquidity Level: "
        f"{alert['liquidity']:.5f}\n"

        f"Sweep Price: "
        f"{alert['price']:.5f}\n\n"

        f"Time: "
        f"{alert['time']}"
    )
