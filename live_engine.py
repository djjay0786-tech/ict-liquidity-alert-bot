import time

from market_data import get_candles
from dxy_data import get_dxy_candles, prepare_dxy_candles
from liquidity import prepare_candles, detect_liquidity_grab


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

        return prepare_candles(
            data["values"]
        )


def check_liquidity(symbol, timeframe, df):

    alerts = detect_liquidity_grab(df)

    if not alerts:

        print(
            f"💧 No liquidity grab | "
            f"{symbol} | {timeframe}"
        )

        return

    for alert in alerts:

        print(
            f"\n🚨 LIQUIDITY GRAB DETECTED"
        )

        print(
            f"Symbol: {symbol}"
        )

        print(
            f"Timeframe: {timeframe}"
        )

        print(
            f"Type: {alert['type']}"
        )

        print(
            f"Level: {alert['level']}"
        )

        print(
            f"Liquidity: {alert['liquidity']}"
        )

        print(
            f"Grab Price: {alert['price']}"
        )

        print(
            f"Time: {alert['time']}"
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

                check_liquidity(
                    symbol,
                    timeframe,
                    df
                )

            except Exception as e:

                print(
                    f"⚠️ Error: {e}"
                )

            time.sleep(2)


if __name__ == "__main__":

    run_engine()
