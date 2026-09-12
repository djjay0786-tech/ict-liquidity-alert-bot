import time

from market_data import get_candles
from dxy_data import get_dxy_candles, prepare_dxy_candles

SYMBOLS = [
    "EUR/USD",
    "GBP/USD",
    "DXY"
]

TIMEFRAMES = [
    "1h",
    "4h"
]


def get_market_data(symbol, timeframe):

    if symbol == "DXY":

        data = get_dxy_candles(
            interval=timeframe,
            limit=200
        )

        return prepare_dxy_candles(data)

    else:

        data = get_candles(
            symbol,
            interval=timeframe,
            outputsize=200
        )

        if "values" not in data:
            return None

        from order_block import prepare_candles

        return prepare_candles(
            data["values"]
        )


def run_engine():

    print("\n" + "=" * 60)
    print("🚀 ICT LIVE ALERT ENGINE")
    print("=" * 60)

    for symbol in SYMBOLS:

        for timeframe in TIMEFRAMES:

            print(
                f"\nChecking "
                f"{symbol} | {timeframe}"
            )

            try:

                df = get_market_data(
                    symbol,
                    timeframe
                )

                if df is None or df.empty:

                    print(
                        "⚠️ No market data"
                    )

                    continue

                print(
                    f"✅ {len(df)} candles received"
                )

            except Exception as e:

                print(
                    f"⚠️ Error: {e}"
                )


if __name__ == "__main__":

    run_engine()
