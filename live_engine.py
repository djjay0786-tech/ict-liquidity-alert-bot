import time
from datetime import datetime
from zoneinfo import ZoneInfo

from market_data import get_candles

from dxy_data import (
    get_dxy_candles,
    prepare_dxy_candles
)

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
    get_valid_fvgs,
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

from alert_state import (
    make_alert_id,
    can_send_alert,
    mark_alert_sent
)

from telegram_alert import (
    send_alert
)


# ==========================================
# SYMBOLS
# ==========================================

SYMBOLS = [
    "EUR/USD",
    "GBP/USD",
    "DXY"
]


# ==========================================
# TIMEFRAMES
#
# Twelve Data Daily = 1day
# Biquote DXY Daily = 1d
# ==========================================

TIMEFRAMES = {
    "H1": {
        "twelve": "1h",
        "dxy": "1h"
    },
    "H4": {
        "twelve": "4h",
        "dxy": "4h"
    },
    "DAILY": {
        "twelve": "1day",
        "dxy": "1d"
    }
}


UTC = ZoneInfo("UTC")


# ==========================================
# MARKET DATA
# ==========================================

def get_market_data(
    symbol,
    timeframe
):

    config = TIMEFRAMES[
        timeframe
    ]

    if symbol == "DXY":

        data = get_dxy_candles(
            interval=config["dxy"],
            limit=200
        )

        return prepare_dxy_candles(
            data
        )

    data = get_candles(
        symbol,
        interval=config["twelve"],
        outputsize=200
    )

    if "values" not in data:
        return None

    return prepare_candles(
        data["values"]
    )


# ==========================================
# TELEGRAM
# ==========================================

def send_message(
    message,
    label
):

    try:

        send_alert(
            message
        )

        print(
            f"📲 Telegram "
            f"{label} alert sent"
        )

        return True

    except Exception as e:

        print(
            f"⚠️ Telegram error: {e}"
        )

        return False


def send_once(
    alert_id,
    message,
    label,
    details=None
):

    if not can_send_alert(
        alert_id
    ):

        print(
            f"🚫 Duplicate "
            f"{label} alert blocked"
        )

        return False

    sent = send_message(
        message,
        label
    )

    if sent:

        mark_alert_sent(
            alert_id,
            details
        )

        return True

    return False


# ==========================================
# SESSION OPEN / CLOSE
# ==========================================

def check_session_open_close():

    current_utc = datetime.now(
        UTC
    )

    events = get_session_events(
        current_utc
    )

    if not events:

        print(
            "🕒 No session "
            "open/close event"
        )

        return

    for event in events:

        session = event[
            "session"
        ]

        event_type = event[
            "event"
        ]

        alert_id = make_alert_id(
            "SESSION_EVENT",
            session,
            "GLOBAL",
            event["local_time"],
            event_type
        )

        message = (
            format_session_event(
                event
            )
        )

        print(
            f"\n🚨 {session} "
            f"SESSION {event_type}"
        )

        send_once(
            alert_id,
            message,
            "Session Open/Close",
            event
        )


# ==========================================
# PDH / PDL LIQUIDITY
#
# H1 ONLY
# Prevent duplicate H1/H4/Daily alerts.
# ==========================================

def check_liquidity(
    symbol,
    timeframe,
    df
):

    if timeframe != "H1":
        return

    alerts = (
        detect_liquidity_grab(
            df
        )
    )

    if not alerts:

        print(
            f"💧 No PDH/PDL grab | "
            f"{symbol} | {timeframe}"
        )

        return

    for alert in alerts:

        alert_id = make_alert_id(
            "LIQUIDITY",
            symbol,
            timeframe,
            alert.get(
                "time",
                ""
            ),
            (
                f"{alert.get('type', '')}|"
                f"{alert.get('level', '')}"
            )
        )

        message = format_alert(
            symbol,
            alert
        )

        message += (
            f"\nTimeframe: "
            f"{timeframe}"
        )

        print(
            "\n🚨 LIQUIDITY GRAB"
        )

        send_once(
            alert_id,
            message,
            "Liquidity",
            alert
        )


# ==========================================
# SESSION LIQUIDITY
#
# H1 ONLY
# ==========================================

def check_session_liquidity(
    symbol,
    timeframe,
    df
):

    if timeframe != "H1":
        return

    for session in [
        "LONDON",
        "NEW YORK"
    ]:

        alerts = (
            detect_session_liquidity(
                df,
                session
            )
        )

        if not alerts:
            continue

        for alert in alerts:

            alert_id = (
                make_alert_id(
                    "SESSION_LIQUIDITY",
                    symbol,
                    timeframe,
                    alert.get(
                        "time",
                        ""
                    ),
                    (
                        f"{session}|"
                        f"{alert.get('level', '')}|"
                        f"{alert.get('type', '')}"
                    )
                )
            )

            message = (
                format_session_alert(
                    symbol,
                    alert
                )
            )

            message += (
                f"\nTimeframe: "
                f"{timeframe}"
            )

            print(
                "\n🚨 SESSION "
                "LIQUIDITY"
            )

            send_once(
                alert_id,
                message,
                "Session Liquidity",
                alert
            )


# ==========================================
# CRT
#
# H1 + H4 ONLY
# ==========================================

def check_crt(
    symbol,
    timeframe,
    df
):

    if timeframe not in [
        "H1",
        "H4"
    ]:
        return

    alerts = detect_crt(
        df
    )

    if not alerts:

        print(
            f"🕯️ No CRT | "
            f"{symbol} | {timeframe}"
        )

        return

    for alert in alerts:

        alert_id = make_alert_id(
            "CRT",
            symbol,
            timeframe,
            alert.get(
                "second_candle_time",
                ""
            ),
            alert.get(
                "type",
                ""
            )
        )

        message = (
            format_crt_alert(
                symbol,
                timeframe,
                alert
            )
        )

        print(
            "\n🚨 CRT DETECTED"
        )

        send_once(
            alert_id,
            message,
            "CRT",
            alert
        )


# ==========================================
# VALID FVG
#
# H1 + H4 + DAILY
# ==========================================

def check_fvg(
    symbol,
    timeframe,
    df
):

    valid_fvgs = (
        get_valid_fvgs(
            df
        )
    )

    if not valid_fvgs:

        print(
            f"🟩 No valid FVG | "
            f"{symbol} | {timeframe}"
        )

        return

    latest_fvg = (
        valid_fvgs[-1]
    )

    alert_id = make_alert_id(
        "FVG",
        symbol,
        timeframe,
        latest_fvg.get(
            "time",
            ""
        ),
        latest_fvg.get(
            "type",
            ""
        )
    )

    message = (
        format_fvg_alert(
            symbol,
            timeframe,
            latest_fvg
        )
    )

    print(
        "\n🚨 VALID FVG"
    )

    send_once(
        alert_id,
        message,
        "FVG",
        latest_fvg
    )


# ==========================================
# OB + FVG
#
# VALID FVG + VALID OB
# H1 + H4 + DAILY
# ==========================================

def check_ob_fvg(
    symbol,
    timeframe,
    df
):

    setup = (
        select_ob_near_fvg(
            df
        )
    )

    if setup is None:

        print(
            f"📦 No valid OB + FVG | "
            f"{symbol} | {timeframe}"
        )

        return

    ob = setup["ob"]
    fvg = setup["fvg"]

    alert_id = make_alert_id(
        "OB_FVG",
        symbol,
        timeframe,
        ob.get(
            "time",
            ""
        ),
        (
            f"{ob.get('type', '')}|"
            f"{fvg.get('time', '')}"
        )
    )

    message = (
        format_ob_fvg_selection(
            symbol,
            timeframe,
            setup
        )
    )

    print(
        "\n🚨 OB + FVG SETUP"
    )

    print(
        f"OB: {ob['type']}"
    )

    print(
        f"FVG: {fvg['type']}"
    )

    print(
        f"Distance: "
        f"{setup['distance']}"
    )

    send_once(
        alert_id,
        message,
        "OB + FVG",
        {
            "ob": ob,
            "fvg": fvg
        }
    )


# ==========================================
# ORDER BLOCK FIRST TAP
# ==========================================

def check_ob_first_tap(
    symbol,
    timeframe,
    df
):

    setup = (
        select_ob_near_fvg(
            df
        )
    )

    if setup is None:

        print(
            f"👆 No valid OB | "
            f"{symbol} | {timeframe}"
        )

        return

    ob = setup["ob"]

    if not can_alert_first_tap(
        symbol,
        timeframe,
        ob
    ):

        print(
            f"🚫 OB already tapped | "
            f"{symbol} | {timeframe}"
        )

        return

    if not is_latest_candle_first_tap(
        df,
        ob
    ):

        print(
            f"⏳ No new first OB tap | "
            f"{symbol} | {timeframe}"
        )

        return

    candle = df.iloc[-1]

    message = (
        create_tap_alert(
            symbol,
            timeframe,
            ob,
            candle
        )
    )

    print(
        "\n🚨 ORDER BLOCK "
        "FIRST TAP"
    )

    sent = send_message(
        message,
        "OB First Tap"
    )

    if sent:

        confirm_first_tap(
            symbol,
            timeframe
        )


# ==========================================
# MAIN ENGINE
# ==========================================

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

    # Session Open / Close
    check_session_open_close()

    for symbol in SYMBOLS:

        for timeframe in TIMEFRAMES:

            print(
                "\n" + "-" * 60
            )

            print(
                f"Checking "
                f"{symbol} | "
                f"{timeframe}"
            )

            print(
                "-" * 60
            )

            try:

                df = (
                    get_market_data(
                        symbol,
                        timeframe
                    )
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

                # H1 only
                check_liquidity(
                    symbol,
                    timeframe,
                    df
                )

                # H1 only
                check_session_liquidity(
                    symbol,
                    timeframe,
                    df
                )

                # H1 + H4 only
                check_crt(
                    symbol,
                    timeframe,
                    df
                )

                # H1 + H4 + Daily
                check_fvg(
                    symbol,
                    timeframe,
                    df
                )

                # H1 + H4 + Daily
                check_ob_fvg(
                    symbol,
                    timeframe,
                    df
                )

                # H1 + H4 + Daily
                check_ob_first_tap(
                    symbol,
                    timeframe,
                    df
                )

            except Exception as e:

                print(
                    f"⚠️ Error | "
                    f"{symbol} | "
                    f"{timeframe}: {e}"
                )

            # Avoid rapid requests
            time.sleep(3)


if __name__ == "__main__":

    run_engine()
