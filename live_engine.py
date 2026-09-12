import time

from market_data import get_candles
from dxy_data import get_dxy_candles, prepare_dxy_candles

from liquidity import (
    prepare_candles,
    detect_liquidity_grab
)

from session_liquidity import (
    detect_session_liquidity,
    format_session_alert
)


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


def check_previous_day_liquidity(
    symbol,
    timeframe,
    df
):

    alerts = detect_liquidity_grab(df)

    if not alerts:

        print(
            f"💧 No PDH/PDL grab | "
            f"{symbol} | {timeframe}"
        )

        return

    for alert in alerts:

        print(
            f"\n🚨 PREVIOUS DAY "
            f"LIQUIDITY GRAB"
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
            f"Liquidity: "
            f"{alert['liquidity']}"
        )

        print(
            f"Grab Price: "
            f"{alert['price']}"
        )


def check_session_liquidity(
    symbol,
    timeframe,
    df
):

    for session in [
        "LONDON",
        "NEW YORK"
    ]:

        alerts = detect_session_liquidity(
            df,
            session
        )

        if not alerts:

            print(
                f"💧 No {session} "
                f"session grab | "
                f"{symbol} | {timeframe}"
            )

            continue

        for alert in alerts:

            print(
                "\n🚨 SESSION "
                "LIQUIDITY GRAB"
            )

            print(
                format_session_alert(
                    symbol,
                    alert
                )
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
                    f"✅ {len(df)} "
                    f"candles received"
                )

                # Previous Day Liquidity
                check_previous_day_liquidity(
                    symbol,
                    timeframe,
                    df
                )

                # Session Liquidity
                check_session_liquidity(
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
