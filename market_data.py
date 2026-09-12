import os
import requests

API_KEY = os.getenv("TWELVE_DATA_API_KEY")

TWELVE_URL = "https://api.twelvedata.com/time_series"
BIQUOTE_URL = "https://biquote.io/api"


def get_candles(symbol, interval="1h", outputsize=100):
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": API_KEY,
    }

    response = requests.get(TWELVE_URL, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()

    if data.get("status") == "error":
        raise Exception(data.get("message", "Twelve Data API error"))

    return data


def get_dxy_candles(interval="1h", limit=100):
    params = {
        "interval": interval,
        "limit": limit,
    }

    response = requests.get(
        f"{BIQUOTE_URL}/DXY/ohlc",
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    if "bars" not in data:
        raise Exception(f"DXY API error: {data}")

    return data


if __name__ == "__main__":
    print("\nEUR/USD")
    print(get_candles("EUR/USD", "1h", 5))

    print("\nGBP/USD")
    print(get_candles("GBP/USD", "1h", 5))

    print("\nDXY")
    print(get_dxy_candles("1h", 5))
