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
    detect_daily_liquidity_grab,
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

from session_summary import (
    calculate_session_summary,
    format_combined_session_summary
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

from ranking import (
    rank_instruments
)

from ranking_alert import (
    process_ranking_alert
)


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
            f"📸 Telegram "
            f"{label} chart alert sent"
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

        return []

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

        send_once(
            alert_id,
            message,
            "Session Open/Close",
            event
        )

    return events


# ==========================================
# SESSION CLOSE SUMMARY
# ==========================================

def check_session_summaries(
    session_events,
    h1_market_data
):

    if not session_events:
        return

    for event in session_events:

        event_type = str(
            event.get(
                "event",
                ""
            )
        ).upper()

        if "CLOSE" not in event_type:
            continue

        session = event.get(
            "session",
            ""
        )

        if session not in [
            "ASIA",
            "LONDON",
            "NEW YORK"
        ]:
            continue

        event_date = event.get(
            "event_date",
            ""
        )

        scheduled_time = event.get(
            "scheduled_time",
            ""
        )

        stable_event_time = (
            f"{event_date}|"
            f"{scheduled_time}"
        )

        summaries = []

        for symbol in SYMBOLS:

            df = h1_market_data.get(
                symbol
            )

            if (
                df is None
                or df.empty
            ):
                continue

            try:

                summary = (
                    calculate_session_summary(
                        symbol=symbol,
                        session=session,
                        df=df
                    )
                )

                if summary is not None:

                    summaries.append(
                        summary
                    )

            except Exception as e:

                print(
                    f"⚠️ Session summary "
                    f"error | {symbol} | "
                    f"{session}: {e}"
                )

        if not summaries:
            continue

        message = (
            format_combined_session_summary(
                session,
                summaries
            )
        )

        alert_id = make_alert_id(
            "SESSION_SUMMARY",
            session,
            "H1",
            stable_event_time,
            "COMBINED"
        )

        send_once(
            alert_id,
            message,
            "Session Summary",
            {
                "session": session,
                "event_date": event_date,
                "scheduled_time":
                    scheduled_time
            }
        )


# ==========================================
# PDH / PDL
# ==========================================

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

    if not alerts:
        return

    for alert in alerts:

        event_time = alert.get(
            "time",
            ""
        )

        if not is_fresh(
            event_time,
            timeframe
        ):
            continue

        alert_id = make_alert_id(
            "PDH_PDL",
            symbol,
            timeframe,
            event_time,
            (
                f"{alert.get('level', '')}|"
                f"{alert.get('level_date', '')}"
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
            "PDH/PDL",
            alert
        )


# ==========================================
# DH / DL
# ==========================================

def check_daily_liquidity(
    symbol,
    timeframe,
    df
):

    if timeframe != "H1":
        return

    alerts = (
        detect_daily_liquidity_grab(
            df
        )
    )

    if not alerts:
        return

    for alert in alerts:

        event_time = alert.get(
            "time",
            ""
        )

        if not is_fresh(
            event_time,
            timeframe
        ):
            continue

        alert_id = make_alert_id(
            "DH_DL",
            symbol,
            timeframe,
            event_time,
            (
                f"{alert.get('level', '')}|"
                f"{alert.get('level_date', '')}"
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
            "DH/DL",
            alert
        )


# ==========================================
# SESSION LIQUIDITY
# ==========================================

def check_session_liquidity(
    symbol,
    timeframe,
    df
):

    if timeframe != "H1":
        return

    for session in [
        "ASIA",
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

            event_time = alert.get(
                "time",
                ""
            )

            if not is_fresh(
                event_time,
                timeframe
            ):
                continue

            alert_id = make_alert_id(
                "SESSION_LIQUIDITY",
                symbol,
                timeframe,
                event_time,
                (
                    f"{session}|"
                    f"{alert.get('level', '')}|"
                    f"{alert.get('session_date', '')}"
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


# ==========================================
# CRT
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
# FVG
# ==========================================

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

    message = format_fvg_alert(
        symbol,
        timeframe,
        latest_fvg
    )

    send_once(
        alert_id,
        message,
        "FVG",
        latest_fvg
    )


# ==========================================
# OB + FVG
# ==========================================

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


# ==========================================
# OB FIRST TAP
# WITH CHART
# ==========================================

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
    fvg = setup["fvg"]

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
        return

    message = create_tap_alert(
        symbol,
        timeframe,
        ob,
        candle
    )

    sent = send_chart_or_text(
        df=df,
        symbol=symbol,
        timeframe=timeframe,
        message=message,
        label="OB First Tap",
        ob=ob,
        fvg=fvg
    )

    if sent:

        confirm_first_tap(
            symbol,
            timeframe
        )


# ==========================================
# HIGH CONFLUENCE
# WITH CHART
# ==========================================

def check_high_confluence(
    symbol,
    timeframe,
    df
):

    if timeframe != "H1":
        return

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
        return

    if not is_latest_candle_first_tap(
        df,
        ob
    ):
        return

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

    crt_alerts = (
        detect_crt(
            df
        ) or []
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
                    liquidity_alert=liquidity_alert,
                    crt_alert=crt_alert,
                    fvg=fvg,
                    ob=ob,
                    ob_first_tap=True
                )
            )

            if candidate is not None:

                final_setup = candidate
                final_liquidity = (
                    liquidity_alert
                )
                final_crt = crt_alert
                break

        if final_setup is not None:
            break

    if final_setup is None:
        return

    candle = df.iloc[-1]

    candle_time = str(
        candle["datetime"]
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
        ) or []
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

        crt = valid_crt[-1]

    setup = select_ob_near_fvg(
        df
    )

    if setup is None:

        return {
            "liquidity": liquidity,
            "crt": crt,
            "fvg": None,
            "ob": None,
            "ob_first_tap": False
        }

    fvg = setup["fvg"]
    ob = setup["ob"]

    if not is_fresh(
        fvg.get(
            "time",
            ""
        ),
        "H1"
    ):

        return {
            "liquidity": liquidity,
            "crt": crt,
            "fvg": None,
            "ob": None,
            "ob_first_tap": False
        }

    first_tap = (
        is_latest_candle_first_tap(
            df,
            ob
        )
    )

    return {
        "liquidity": liquidity,
        "crt": crt,
        "fvg": fvg,
        "ob": ob,
        "ob_first_tap": first_tap
    }


# ==========================================
# MARKET RANKING
# ==========================================

def send_market_ranking(
    snapshots
):

    missing = [
        symbol
        for symbol in SYMBOLS
        if symbol not in snapshots
    ]

    if missing:

        print(
            "⚠️ Ranking skipped. "
            "Missing H1 data: "
            + ", ".join(missing)
        )

        return

    rankings = rank_instruments(
        snapshots
    )

    ranking_cycle = (
        datetime.now(
            UTC
        )
        .replace(
            minute=0,
            second=0,
            microsecond=0
        )
        .isoformat()
    )

    def ranking_sender(
        message
    ):

        sent = send_message(
            message,
            "Market Ranking"
        )

        if not sent:

            raise Exception(
                "Ranking Telegram "
                "send failed"
            )

    result = (
        process_ranking_alert(
            rankings=rankings,
            candle_time=ranking_cycle,
            send_function=ranking_sender
        )
    )

    print(
        "🏆 Ranking result: "
        f"{result.get('reason')}"
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

    session_events = (
        check_session_open_close()
    )

    ranking_snapshots = {}

    h1_market_data = {}

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

                if timeframe == "H1":

                    h1_market_data[
                        symbol
                    ] = df

                check_liquidity(
                    symbol,
                    timeframe,
                    df
                )

                check_daily_liquidity(
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

                # High Confluence first,
                # before OB tap is confirmed.
                check_high_confluence(
                    symbol,
                    timeframe,
                    df
                )

                if timeframe == "H1":

                    ranking_snapshots[
                        symbol
                    ] = (
                        build_ranking_snapshot(
                            df
                        )
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

    print(
        "\n" + "=" * 60
    )

    print(
        "📊 CHECKING SESSION SUMMARIES"
    )

    print(
        "=" * 60
    )

    try:

        check_session_summaries(
            session_events,
            h1_market_data
        )

    except Exception as e:

        print(
            f"⚠️ Session summary error: {e}"
        )

    print(
        "\n" + "=" * 60
    )

    print(
        "🏆 CHECKING MARKET RANKING"
    )

    print(
        "=" * 60
    )

    try:

        send_market_ranking(
            ranking_snapshots
        )

    except Exception as e:

        print(
            f"⚠️ Ranking error: {e}"
        )


if __name__ == "__main__":

    run_engine()
