import time

from market_data import get_candles
from dxy_data import get_dxy_candles, prepare_dxy_candles

from liquidity import (
    prepare_candles,
    detect_liquidity_grab,
    format_alert
)

from session_liquidity import (
    detect_session_liquidity,
    format_session_alert
)

from crt import (
    detect_crt,
    format_crt_alert
)

from telegram_alert import send_alert


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


def send_liquidity_alert(
    symbol,
    timeframe,
    alert
):

    message = format_alert(
        symbol,
        alert
    )

    message += (
        f"\nTimeframe: {timeframe}"
    )

    try:

        send_alert(message)

        print(
            "📲 Telegram liquidity alert sent"
        )

    except Exception as e:

        print(
            f"⚠️ Telegram error: {e}"
        )


def send_session_alert(
    symbol,
    timeframe,
    alert
):

    message = format_session_alert(
        symbol,
        alert
    )

    message += (
        f"\nTimeframe: {timeframe}"
    )

    try:

        send_alert(message)

        print(
            "📲 Telegram session alert sent"
        )

    except Exception as e:

        print(
            f"⚠️ Telegram error: {e}"
        )


def send_crt_alert(
    symbol,
    timeframe,
    alert
):

    message = format_crt_alert(
        symbol,
        timeframe,
        alert
    )

    try:

        send_alert(message)

        print(
            "📲 Telegram CRT alert sent"
        )

    except Exception as e:

        print(
            f"⚠️ Telegram error: {e}"
        )


def check_liquidity(
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

    for alert in alerts:

        print(
            f"\n🚨 LIQUIDITY GRAB"
        )

        print(
            f"{symbol} | {timeframe}"
        )

        send_liquidity_alert(
            symbol,
            timeframe,
            alert
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
            continue

        for alert in alerts:

            print(
                "\n🚨 SESSION LIQUIDITY"
            )

            print(
                f"{symbol} | {timeframe}"
            )

            send_session_alert(
                symbol,
                timeframe,
                alert
            )


def check_crt(
    symbol,
    timeframe,
    df
):

    alerts = detect_crt(df)

    if not alerts:

        print(
            f"🕯️ No CRT | "
            f"{symbol} | {timeframe}"
        )

        return

    for alert in alerts:

        print(
            "\n🚨 CRT DETECTED"
        )

        print(
            f"{symbol} | {timeframe}"
        )

        print(
            f"Type: {alert['type']}"
        )

        print(
            f"Confirmation: "
            f"{alert['confirmation_close']}"
        )

        print(
            f"Entry Reference: "
            f"{alert['entry_price']}"
        )

        send_crt_alert(
            symbol,
            timeframe,
            alert
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

                # 1️⃣ Previous Day Liquidity
                check_liquidity(
                    symbol,
                    timeframe,
                    df
                )

                # 2️⃣ Session Liquidity
                check_session_liquidity(
                    symbol,
                    timeframe,
                    df
                )

                # 3️⃣ CRT
                check_crt(
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
