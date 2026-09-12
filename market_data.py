import os
import requests

API_KEY = os.getenv("TWELVE_DATA_API_KEY")

BASE_URL = "https://api.twelvedata.com/time_series"


def get_candles(symbol, interval="1h", outputsize=100):
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": API_KEY,
    }

    response = requests.get(BASE_URL, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()

    if "status" in data and data["status"] == "error":
        raise Exception(data.get("message", "Twelve Data API error"))

    return data


if __name__ == "__main__":
    for symbol in ["EUR/USD", "GBP/USD"]:
        print(f"\n{symbol}")
        data = get_candles(symbol, "1h", 5)
        print(data)
