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
    detect_daily_liquidity_grab
)

from session_liquidity import (
    detect_session_liquidity
)

from crt import (
    detect_crt,
    format_crt_alert
)

from ob_fvg import (
    select_ob_near_fvg
)

from ob_tap import (
    is_latest_candle_first_tap
)

from alert_state import (
    make_alert_id,
    can_send_alert,
    mark_alert_sent
)

from telegram_alert import (
    send_alert
)

from telegram_chart_alert import (
    send_chart_alert
)

from chart_image import (
    create_mini_chart,
    delete_chart
)

from confluence import (
    build_confluence,
    format_confluence_alert,
    get_direction_from_liquidity,
    get_direction_from_crt
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
# ==========================================

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

    # Keep DAILY available for
    # report modules / compatibility.
    "DAILY": {
        "twelve": "1day",
        "dxy": "1d",
        "fresh_hours": 48
    }
}


# Live Clean Mode only needs H1 + H4.
LIVE_TIMEFRAMES = [
    "H1",
    "H4"
]


UTC = ZoneInfo(
    "UTC"
)


# ==========================================
# FRESH EVENT CHECK
# ==========================================

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

    age = (
        now
        -
        event_dt
    )

    return (
        timedelta(0)
        <= age
        <= max_age
    )


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
            interval=config[
                "dxy"
            ],
            limit=200
        )

        return prepare_dxy_candles(
            data
        )

    data = get_candles(
        symbol,
        interval=config[
            "twelve"
        ],
        outputsize=200
    )

    if "values" not in data:

        return None

    return prepare_candles(
        data["values"]
    )


# ==========================================
# MESSAGE SEND
# Telegram Personal
# Telegram Group
# Discord
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
            f"📲 {label} alert sent "
            f"to Telegram + Discord"
        )

        return True

    except Exception as e:

        print(
            f"⚠️ {label} send error: "
            f"{e}"
        )

        return False


# ==========================================
# CHART SEND
# ==========================================

def send_chart_or_text(
    df,
    symbol,
    timeframe,
    message,
    label,
    ob=None,
    fvg=None,
    liquidity=None,
    crt=None
):

    chart_path = None

    try:

        chart_path = (
            create_mini_chart(
                df=df,
                symbol=symbol,
                timeframe=timeframe,
                ob=ob,
                fvg=fvg,
                liquidity=liquidity,
                crt=crt,
                candle_count=50
            )
        )

        send_chart_alert(
            chart_path=chart_path,
            message=message,
            symbol=symbol,
            timeframe=timeframe
        )

        print(
            f"📸 {label} chart "
            f"alert sent"
        )

        return True

    except Exception as e:

        print(
            f"⚠️ Chart alert error | "
            f"{label}: {e}"
        )

        print(
            "↪️ Falling back "
            "to text alert"
        )

        return send_message(
            message,
            label
        )

    finally:

        if chart_path:

            delete_chart(
                chart_path
            )


# ==========================================
# DUPLICATE SAFE TEXT ALERT
# ==========================================

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
            f"{label} blocked"
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
# CRT
# ONLY H1 + H4
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

    alerts = (
        detect_crt(
            df
        )
        or []
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


# ==========================================
# H4 ORDER BLOCK
# TAP OR PRICE INSIDE ZONE
# ONE ALERT PER OB
# ==========================================

def latest_candle_touches_ob(
    df,
    ob
):

    if (
        df is None
        or df.empty
        or ob is None
    ):

        return False

    candle = df.iloc[-1]

    candle_low = float(
        candle[
            "low"
        ]
    )

    candle_high = float(
        candle[
            "high"
        ]
    )

    ob_low = float(
        ob[
            "low"
        ]
    )

    ob_high = float(
        ob[
            "high"
        ]
    )

    return (
        candle_low
        <= ob_high
        and
        candle_high
        >= ob_low
    )


def latest_price_inside_ob(
    df,
    ob
):

    if (
        df is None
        or df.empty
        or ob is None
    ):

        return False

    price = float(
        df.iloc[-1][
            "close"
        ]
    )

    return (
        float(
            ob["low"]
        )
        <= price
        <= float(
            ob["high"]
        )
    )


def format_h4_ob_alert(
    symbol,
    ob,
    fvg,
    candle,
    price_inside
):

    if (
        ob["type"]
        ==
        "BULLISH OB"
    ):

        emoji = "🟢"

    else:

        emoji = "🔴"

    if price_inside:

        status = (
            "PRICE INSIDE H4 OB ZONE"
        )

    else:

        status = (
            "H4 OB TAPPED"
        )

    return (
        f"{emoji} H4 ORDER BLOCK ALERT\n\n"

        f"Symbol: {symbol}\n"
        f"Timeframe: H4\n\n"

        f"Type: {ob['type']}\n"

        f"OB High: "
        f"{float(ob['high']):.5f}\n"

        f"OB Low: "
        f"{float(ob['low']):.5f}\n"

        f"OB Midpoint: "
        f"{float(ob['midpoint']):.5f}\n\n"

        f"Current Price: "
        f"{float(candle['close']):.5f}\n"

        f"Status: {status}\n\n"

        f"OB Time: "
        f"{ob.get('time', '')}\n"

        f"Related FVG: "
        f"{fvg.get('type', '')}\n"

        f"FVG Time: "
        f"{fvg.get('time', '')}"
    )


def check_h4_ob_zone(
    symbol,
    timeframe,
    df
):

    if timeframe != "H4":
        return

    setup = (
        select_ob_near_fvg(
            df
        )
    )

    if setup is None:

        print(
            f"ℹ️ No relevant H4 "
            f"OB + FVG | {symbol}"
        )

        return

    ob = setup[
        "ob"
    ]

    fvg = setup[
        "fvg"
    ]

    touched = (
        latest_candle_touches_ob(
            df,
            ob
        )
    )

    price_inside = (
        latest_price_inside_ob(
            df,
            ob
        )
    )

    if not (
        touched
        or price_inside
    ):

        return

    candle = (
        df.iloc[-1]
    )

    candle_time = str(
        candle[
            "datetime"
        ]
    )

    if not is_fresh(
        candle_time,
        "H4"
    ):

        return

    # Stable ID based on the OB itself.
    # Same H4 OB will alert only once,
    # even if price stays inside during
    # several 15-minute workflow runs.
    alert_id = make_alert_id(
        "H4_OB_ZONE",
        symbol,
        "H4",
        ob.get(
            "time",
            ""
        ),
        (
            f"{ob.get('type', '')}|"
            f"{float(ob['high']):.5f}|"
            f"{float(ob['low']):.5f}"
        )
    )

    message = (
        format_h4_ob_alert(
            symbol,
            ob,
            fvg,
            candle,
            price_inside
        )
    )

    send_once(
        alert_id,
        message,
        "H4 OB Zone",
        {
            "symbol":
                symbol,

            "timeframe":
                "H4",

            "ob":
                ob,

            "fvg":
                fvg,

            "tap_time":
                candle_time,

            "price_inside":
                price_inside
        }
    )


# ==========================================
# HIGH CONFLUENCE
# H1 ONLY
# CHART + TRADINGVIEW LINK
# ==========================================

def check_high_confluence(
    symbol,
    timeframe,
    df
):

    if timeframe != "H1":
        return

    setup = (
        select_ob_near_fvg(
            df
        )
    )

    if setup is None:
        return

    ob = setup[
        "ob"
    ]

    fvg = setup[
        "fvg"
    ]

    fvg_time = (
        fvg.get(
            "time",
            ""
        )
    )

    if not is_fresh(
        fvg_time,
        timeframe
    ):

        return

    if not is_latest_candle_first_tap(
        df,
        ob
    ):

        return

    # ======================================
    # BACKGROUND LIQUIDITY
    # NO STANDALONE ALERT
    # ======================================

    liquidity_alerts = []

    try:

        liquidity_alerts.extend(
            detect_liquidity_grab(
                df
            ) or []
        )

    except Exception:
        pass

    try:

        liquidity_alerts.extend(
            detect_daily_liquidity_grab(
                df
            ) or []
        )

    except Exception:
        pass

    for session in [
        "ASIA",
        "LONDON",
        "NEW YORK"
    ]:

        try:

            liquidity_alerts.extend(
                detect_session_liquidity(
                    df,
                    session
                ) or []
            )

        except Exception:
            pass

    fresh_liquidity = []

    for alert in liquidity_alerts:

        if not is_fresh(
            alert.get(
                "time",
                ""
            ),
            timeframe
        ):

            continue

        if (
            get_direction_from_liquidity(
                alert
            )
            is not None
        ):

            fresh_liquidity.append(
                alert
            )

    if not fresh_liquidity:
        return

    # ======================================
    # BACKGROUND CRT
    # ======================================

    crt_alerts = (
        detect_crt(
            df
        )
        or []
    )

    fresh_crt = []

    for alert in crt_alerts:

        if not is_fresh(
            alert.get(
                "second_candle_time",
                ""
            ),
            timeframe
        ):

            continue

        if (
            get_direction_from_crt(
                alert
            )
            is not None
        ):

            fresh_crt.append(
                alert
            )

    if not fresh_crt:
        return

    final_setup = None
    final_liquidity = None
    final_crt = None

    for liquidity_alert in reversed(
        fresh_liquidity
    ):

        for crt_alert in reversed(
            fresh_crt
        ):

            candidate = (
                build_confluence(
                    symbol=symbol,
                    timeframe=timeframe,
                    liquidity_alert=
                        liquidity_alert,
                    crt_alert=
                        crt_alert,
                    fvg=fvg,
                    ob=ob,
                    ob_first_tap=True
                )
            )

            if candidate is not None:

                final_setup = (
                    candidate
                )

                final_liquidity = (
                    liquidity_alert
                )

                final_crt = (
                    crt_alert
                )

                break

        if final_setup is not None:
            break

    if final_setup is None:
        return

    candle = (
        df.iloc[-1]
    )

    candle_time = str(
        candle[
            "datetime"
        ]
    )

    alert_id = make_alert_id(
        "HIGH_CONFLUENCE",
        symbol,
        timeframe,
        candle_time,
        (
            f"{final_setup['direction']}|"
            f"{ob.get('time', '')}|"
            f"{fvg.get('time', '')}"
        )
    )

    if not can_send_alert(
        alert_id
    ):

        print(
            "🚫 Duplicate High "
            "Confluence alert blocked"
        )

        return

    message = (
        format_confluence_alert(
            final_setup
        )
    )

    sent = send_chart_or_text(
        df=df,
        symbol=symbol,
        timeframe=timeframe,
        message=message,
        label="High Confluence",
        ob=ob,
        fvg=fvg,
        liquidity=final_liquidity,
        crt=final_crt
    )

    if sent:

        mark_alert_sent(
            alert_id,
            final_setup
        )


# ==========================================
# RANKING SNAPSHOT
# KEEP FOR DAILY / WEEKLY REPORT MODULES
# NO LIVE RANKING MESSAGE
# ==========================================

def build_ranking_snapshot(
    df
):

    liquidity_alerts = []

    try:

        liquidity_alerts.extend(
            detect_liquidity_grab(
                df
            ) or []
        )

    except Exception:
        pass

    try:

        liquidity_alerts.extend(
            detect_daily_liquidity_grab(
                df
            ) or []
        )

    except Exception:
        pass

    for session in [
        "ASIA",
        "LONDON",
        "NEW YORK"
    ]:

        try:

            liquidity_alerts.extend(
                detect_session_liquidity(
                    df,
                    session
                ) or []
            )

        except Exception:
            pass

    valid_liquidity = []

    for alert in liquidity_alerts:

        if not is_fresh(
            alert.get(
                "time",
                ""
            ),
            "H1"
        ):

            continue

        if (
            get_direction_from_liquidity(
                alert
            )
            is not None
        ):

            valid_liquidity.append(
                alert
            )

    liquidity = None

    if valid_liquidity:

        liquidity = (
            valid_liquidity[-1]
        )

    crt_alerts = (
        detect_crt(
            df
        )
        or []
    )

    valid_crt = []

    for alert in crt_alerts:

        if not is_fresh(
            alert.get(
                "second_candle_time",
                ""
            ),
            "H1"
        ):

            continue

        if (
            get_direction_from_crt(
                alert
            )
            is not None
        ):

            valid_crt.append(
                alert
            )

    crt = None

    if valid_crt:

        crt = (
            valid_crt[-1]
        )

    setup = (
        select_ob_near_fvg(
            df
        )
    )

    if setup is None:

        return {
            "liquidity":
                liquidity,

            "crt":
                crt,

            "fvg":
                None,

            "ob":
                None,

            "ob_first_tap":
                False
        }

    fvg = setup[
        "fvg"
    ]

    ob = setup[
        "ob"
    ]

    if not is_fresh(
        fvg.get(
            "time",
            ""
        ),
        "H1"
    ):

        return {
            "liquidity":
                liquidity,

            "crt":
                crt,

            "fvg":
                None,

            "ob":
                None,

            "ob_first_tap":
                False
        }

    first_tap = (
        is_latest_candle_first_tap(
            df,
            ob
        )
    )

    return {
        "liquidity":
            liquidity,

        "crt":
            crt,

        "fvg":
            fvg,

        "ob":
            ob,

        "ob_first_tap":
            first_tap
    }


# ==========================================
# CLEAN MODE MAIN ENGINE
# ==========================================

def run_engine():

    print(
        "\n"
        + "=" * 60
    )

    print(
        "🧹 ICT LIVE ALERT ENGINE "
        "- CLEAN MODE"
    )

    print(
        "=" * 60
    )

    print(
        "✅ CRT: H1 + H4"
    )

    print(
        "✅ H4 OB Tap / Inside Zone"
    )

    print(
        "✅ High Confluence: H1 + Chart"
    )

    print(
        "🚫 Standalone Liquidity OFF"
    )

    print(
        "🚫 Standalone FVG OFF"
    )

    print(
        "🚫 OB + FVG message OFF"
    )

    print(
        "🚫 Session messages OFF"
    )

    print(
        "🚫 Ranking messages OFF"
    )

    for symbol in SYMBOLS:

        for timeframe in LIVE_TIMEFRAMES:

            print(
                "\n"
                + "-"
                * 60
            )

            print(
                f"Checking "
                f"{symbol} | "
                f"{timeframe}"
            )

            print(
                "-"
                * 60
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

                # --------------------------
                # 1. CRT H1 / H4
                # --------------------------

                check_crt(
                    symbol,
                    timeframe,
                    df
                )

                # --------------------------
                # 2. HIGH CONFLUENCE H1
                # --------------------------

                if timeframe == "H1":

                    check_high_confluence(
                        symbol,
                        timeframe,
                        df
                    )

                # --------------------------
                # 3. H4 OB TAP / ZONE
                # --------------------------

                if timeframe == "H4":

                    check_h4_ob_zone(
                        symbol,
                        timeframe,
                        df
                    )

            except Exception as e:

                print(
                    f"⚠️ Error | "
                    f"{symbol} | "
                    f"{timeframe}: "
                    f"{e}"
                )

            time.sleep(
                3
            )

    print(
        "\n"
        + "=" * 60
    )

    print(
        "✅ CLEAN MODE CYCLE COMPLETE"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":

    run_engine()
