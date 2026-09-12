import time
from datetime import datetime
from zoneinfo import ZoneInfo

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

from session_alerts import (
    get_session_events,
    format_session_event
)

from crt import (
    detect_crt,
    format_crt_alert
)

from fvg import (
    detect_fvg,
    format_fvg_alert
)

from ob_fvg import (
    select_ob_near_fvg,
    format_ob_fvg_selection
)

from ob_tap import (
    is_latest_candle_first_tap,
    create_tap_alert
)

from ob_state import (
    can_alert_first_tap,
    confirm_first_tap
)

from telegram_alert import send_alert


SYMBOLS = [
    "EUR/USD",
    "GBP/USD",
    "DXY"
]


TIMEFRAMES = [
    "1h",
    "4h",
    "1day"
]


UTC = ZoneInfo("UTC")


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


def send_message(message, label):

    try:

        send_alert(message)

        print(
            f"📲 Telegram {label} alert sent"
        )

    except Exception as e:

        print(
            f"⚠️ Telegram error: {e}"
        )


def check_session_open_close():

    current_utc = datetime.now(UTC)

    events = get_session_events(
        current_utc
    )

    if not events:

        print(
            "🕒 No session open/close event"
        )

        return

    for event in events:

        print(
            f"\n🚨 SESSION "
            f"{event['event']}"
        )

        message = format_session_event(
            event
        )

        send_message(
            message,
            "Session Open/Close"
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

    send_message(
        message,
        "liquidity"
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

    send_message(
        message,
        "session liquidity"
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

    send_message(
        message,
        "CRT"
    )


def send_fvg_alert(
    symbol,
    timeframe,
    fvg
):

    message = format_fvg_alert(
        symbol,
        timeframe,
        fvg
    )

    send_message(
        message,
        "FVG"
    )


def send_ob_fvg_alert(
    symbol,
    timeframe,
    setup
):

    message = format_ob_fvg_selection(
        symbol,
        timeframe,
        setup
    )

    send_message(
        message,
        "OB + FVG"
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
            "\n🚨 LIQUIDITY GRAB"
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

        send_crt_alert(
            symbol,
            timeframe,
            alert
        )


def check_fvg(
    symbol,
    timeframe,
    df
):

    fvgs = detect_fvg(df)

    if not fvgs:

        print(
            f"🟩 No FVG | "
            f"{symbol} | {timeframe}"
        )

        return

    latest_fvg = fvgs[-1]

    print(
        "\n🚨 FVG DETECTED"
    )

    send_fvg_alert(
        symbol,
        timeframe,
        latest_fvg
    )


def check_ob_fvg(
    symbol,
    timeframe,
    df
):

    setup = select_ob_near_fvg(df)

    if setup is None:

        print(
            f"📦 No OB + FVG setup | "
            f"{symbol} | {timeframe}"
        )

        return

    print(
        "\n🚨 OB + FVG SETUP"
    )

    ob = setup["ob"]
    fvg = setup["fvg"]

    print(
        f"OB: {ob['type']}"
    )

    print(
        f"OB High: {ob['high']}"
    )

    print(
        f"OB Low: {ob['low']}"
    )

    print(
        f"FVG: {fvg['type']}"
    )

    print(
        f"Distance: "
        f"{setup['distance']}"
    )

    send_ob_fvg_alert(
        symbol,
        timeframe,
        setup
    )


def check_ob_first_tap(
    symbol,
    timeframe,
    df
):

    setup = select_ob_near_fvg(df)

    if setup is None:

        print(
            f"👆 No OB for First Tap | "
            f"{symbol} | {timeframe}"
        )

        return

    ob = setup["ob"]

    can_alert = can_alert_first_tap(
        symbol,
        timeframe,
        ob
    )

    if not can_alert:

        print(
            f"🚫 OB already tapped | "
            f"{symbol} | {timeframe}"
        )

        return

    first_tap_now = (
        is_latest_candle_first_tap(
            df,
            ob
        )
    )

    if not first_tap_now:

        print(
            f"⏳ No new first OB tap | "
            f"{symbol} | {timeframe}"
        )

        return

    candle = df.iloc[-1]

    print(
        "\n🚨 ORDER BLOCK FIRST TAP"
    )

    message = create_tap_alert(
        symbol,
        timeframe,
        ob,
        candle
    )

    send_message(
        message,
        "OB First Tap"
    )

    confirm_first_tap(
        symbol,
        timeframe
    )


def run_engine():

    print(
        "\n" + "=" * 60
    )

    print(
        "🚀 ICT LIVE ALERT ENGINE"
    )

    print(
        "=" * 60
    )

    # Session open / close check
    check_session_open_close()

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

                if (
                    df is None
                    or df.empty
                ):

                    print(
                        "⚠️ No market data"
                    )

                    continue

                print(
                    f"✅ {len(df)} "
                    f"candles received"
                )

                check_liquidity(
                    symbol,
                    timeframe,
                    df
                )

                check_session_liquidity(
                    symbol,
                    timeframe,
                    df
                )

                check_crt(
                    symbol,
                    timeframe,
                    df
                )

                check_fvg(
                    symbol,
                    timeframe,
                    df
                )

                check_ob_fvg(
                    symbol,
                    timeframe,
                    df
                )

                check_ob_first_tap(
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
