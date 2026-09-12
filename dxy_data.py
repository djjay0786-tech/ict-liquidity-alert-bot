import requests
import pandas as pd

BASE_URL = "https://biquote.io/api/DXY/ohlc"


def get_dxy_candles(interval="1h", limit=500):

    params = {
        "interval": interval,
        "limit": limit
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    if "bars" not in data:
        raise Exception(
            data.get("message", "DXY data not available")
        )

    return data


def prepare_dxy_candles(data):

    df = pd.DataFrame(data["bars"])

    if df.empty:
        return df

    df["datetime"] = pd.to_datetime(
        df["openTime"],
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


if __name__ == "__main__":

    data = get_dxy_candles(
        interval="1h",
        limit=10
    )

    df = prepare_dxy_candles(data)

    print("\nDXY DATA")
    print("=" * 50)

    print(
        df[
            [
                "datetime",
                "open",
                "high",
                "low",
                "close"
            ]
        ].tail(10)
    )
