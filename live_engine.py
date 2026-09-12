import time
from datetime import datetime, timedelta
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

from telegram_alert import send_alert


SYMBOLS = [
    "EUR/USD",
    "GBP/USD",
    "DXY"
]


TIMEFRAMES = {
    "H1": {
        "twelve": "1h",
        "dxy": "1h",
        "fresh_hours": 2
    },

    "H4": {
        "twelve": "4h",
        "dxy": "4h",
        "fresh_hours": 8
    },

    "DAILY": {
        "twelve": "1day",
        "dxy": "1d",
        "fresh_hours": 48
    }
}


UTC = ZoneInfo("UTC")


def is_fresh(
    event_time,
    timeframe
):

    if not event_time:
        return False

    try:

        event_dt = datetime.fromisoformat(
            str(event_time).replace(
                "Z",
                "+00:00"
            )
        )

        if event_dt.tzinfo is None:

            event_dt = event_dt.replace(
                tzinfo=UTC
            )

        event_dt = event_dt.astimezone(
            UTC
        )

    except Exception:

        return False

    now = datetime.now(
        UTC
    )

    max_age = timedelta(
        hours=TIMEFRAMES[
            timeframe
        ]["fresh_hours"]
    )

    age = now - event_dt

    return (
        timedelta(0)
        <= age
        <= max_age
    )


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

        event_date = event[
            "event_date"
        ]

        scheduled_time = event[
            "scheduled_time"
        ]

        stable_event_time = (
            f"{event_date}|"
            f"{scheduled_time}"
        )

        alert_id = make_alert_id(
            "SESSION_EVENT",
            session,
            "GLOBAL",
            stable_event_time,
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


def check_liquidity(
    symbol,
    timeframe,
    df
):

    if timeframe != "H1":
        return

    alerts = detect_liquidity_grab(
        df
    )

    for alert in alerts:

        event_time = alert.get(
            "time",
            ""
        )

        if not is_fresh(
            event_time,
            timeframe
        ):

            print(
                f"🕰️ Old liquidity ignored | "
                f"{symbol} | {event_time}"
            )

            continue

        alert_id = make_alert_id(
            "LIQUIDITY",
            symbol,
            timeframe,
            event_time,
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

        send_once(
            alert_id,
            message,
            "Liquidity",
            alert
        )


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

        for alert in alerts:

            event_time = alert.get(
                "time",
                ""
            )

            if not is_fresh(
                event_time,
                timeframe
            ):

                print(
                    f"🕰️ Old session "
                    f"liquidity ignored | "
                    f"{symbol} | "
                    f"{event_time}"
                )

                continue

            alert_id = make_alert_id(
                "SESSION_LIQUIDITY",
                symbol,
                timeframe,
                event_time,
                (
                    f"{session}|"
                    f"{alert.get('level', '')}|"
                    f"{alert.get('type', '')}"
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

            send_once(
                alert_id,
                message,
                "Session Liquidity",
                alert
            )


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

    for alert in alerts:

        confirmation_time = (
            alert.get(
                "second_candle_time",
                ""
            )
        )

        if not is_fresh(
            confirmation_time,
            timeframe
        ):

            print(
                f"🕰️ Old CRT ignored | "
                f"{symbol} | "
                f"{timeframe}"
            )

            continue

        alert_id = make_alert_id(
            "CRT",
            symbol,
            timeframe,
            confirmation_time,
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

        send_once(
            alert_id,
            message,
            "CRT",
            alert
        )


def check_fvg(
    symbol,
    timeframe,
    df
):

    valid_fvgs = get_valid_fvgs(
        df
    )

    if not valid_fvgs:
        return

    latest_fvg = valid_fvgs[-1]

    fvg_time = latest_fvg.get(
        "time",
        ""
    )

    if not is_fresh(
        fvg_time,
        timeframe
    ):

        print(
            f"🕰️ Old FVG ignored | "
            f"{symbol} | "
            f"{timeframe} | "
            f"{fvg_time}"
        )

        return

    alert_id = make_alert_id(
        "FVG",
        symbol,
        timeframe,
        fvg_time,
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

    send_once(
        alert_id,
        message,
        "FVG",
        latest_fvg
    )


def check_ob_fvg(
    symbol,
    timeframe,
    df
):

    setup = select_ob_near_fvg(
        df
    )

    if setup is None:
        return

    ob = setup["ob"]
    fvg = setup["fvg"]

    fvg_time = fvg.get(
        "time",
        ""
    )

    if not is_fresh(
        fvg_time,
        timeframe
    ):

        print(
            f"🕰️ Old OB+FVG "
            f"setup ignored | "
            f"{symbol} | "
            f"{timeframe}"
        )

        return

    alert_id = make_alert_id(
        "OB_FVG",
        symbol,
        timeframe,
        fvg_time,
        (
            f"{ob.get('type', '')}|"
            f"{ob.get('time', '')}"
        )
    )

    message = (
        format_ob_fvg_selection(
            symbol,
            timeframe,
            setup
        )
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


def check_ob_first_tap(
    symbol,
    timeframe,
    df
):

    setup = select_ob_near_fvg(
        df
    )

    if setup is None:
        return

    ob = setup["ob"]

    if not can_alert_first_tap(
        symbol,
        timeframe,
        ob
    ):
        return

    if not is_latest_candle_first_tap(
        df,
        ob
    ):
        return

    candle = df.iloc[-1]

    candle_time = str(
        candle["datetime"]
    )

    if not is_fresh(
        candle_time,
        timeframe
    ):

        print(
            f"🕰️ Old OB tap ignored | "
            f"{symbol} | "
            f"{timeframe}"
        )

        return

    message = create_tap_alert(
        symbol,
        timeframe,
        ob,
        candle
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
                    f"⚠️ Error | "
                    f"{symbol} | "
                    f"{timeframe}: {e}"
                )

            time.sleep(3)


if __name__ == "__main__":
    run_engine()
