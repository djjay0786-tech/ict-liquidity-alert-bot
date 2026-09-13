import pandas as pd

from liquidity import (
    detect_liquidity_grab,
    detect_daily_liquidity_grab
)

from session_liquidity import (
    detect_session_liquidity
)

from crt import (
    detect_crt
)

from ob_fvg import (
    select_ob_near_fvg
)

from ob_tap import (
    is_latest_candle_first_tap
)

from confluence import (
    build_confluence,
    get_direction_from_liquidity,
    get_direction_from_crt
)


SESSIONS = [
    "ASIA",
    "LONDON",
    "NEW YORK"
]


def get_liquidity_alerts(df):

    alerts = []

    try:
        alerts.extend(
            detect_liquidity_grab(df)
            or []
        )
    except Exception:
        pass

    try:
        alerts.extend(
            detect_daily_liquidity_grab(df)
            or []
        )
    except Exception:
        pass

    for session in SESSIONS:

        try:
            alerts.extend(
                detect_session_liquidity(
                    df,
                    session
                )
                or []
            )
        except Exception:
            pass

    return [
        alert
        for alert in alerts
        if get_direction_from_liquidity(
            alert
        ) is not None
    ]


def get_crt_alerts(df):

    alerts = detect_crt(
        df
    ) or []

    return [
        alert
        for alert in alerts
        if get_direction_from_crt(
            alert
        ) is not None
    ]


def calculate_forward_move(
    full_df,
    signal_index,
    direction,
    entry_price,
    forward_candles=6
):

    start = (
        signal_index + 1
    )

    end = min(
        len(full_df),
        start + forward_candles
    )

    future = full_df.iloc[
        start:end
    ]

    if future.empty:

        return {
            "best_move": 0.0,
            "worst_move": 0.0
        }

    future_high = float(
        future["high"].max()
    )

    future_low = float(
        future["low"].min()
    )

    if direction == "BULLISH":

        best_move = (
            future_high
            - entry_price
        )

        worst_move = (
            entry_price
            - future_low
        )

    else:

        best_move = (
            entry_price
            - future_low
        )

        worst_move = (
            future_high
            - entry_price
        )

    return {
        "best_move":
            max(
                0.0,
                best_move
            ),

        "worst_move":
            max(
                0.0,
                worst_move
            )
    }


def convert_move(
    symbol,
    move
):

    if symbol in [
        "EUR/USD",
        "GBP/USD"
    ]:

        return {
            "value":
                move * 10000,

            "unit":
                "pips"
        }

    return {
        "value":
            move,

        "unit":
            "points"
    }


def backtest_symbol(
    df,
    symbol,
    timeframe="H1",
    minimum_candles=60,
    forward_candles=6
):

    if (
        df is None
        or df.empty
    ):

        return {
            "symbol": symbol,
            "setups": [],
            "setup_count": 0
        }

    data = (
        df.copy()
        .sort_values(
            "datetime"
        )
        .reset_index(
            drop=True
        )
    )

    setups = []

    seen = set()

    for index in range(
        minimum_candles,
        len(data)
    ):

        history = data.iloc[
            :index + 1
        ].copy()

        liquidity_alerts = (
            get_liquidity_alerts(
                history
            )
        )

        if not liquidity_alerts:
            continue

        crt_alerts = (
            get_crt_alerts(
                history
            )
        )

        if not crt_alerts:
            continue

        ob_fvg = (
            select_ob_near_fvg(
                history
            )
        )

        if ob_fvg is None:
            continue

        ob = ob_fvg[
            "ob"
        ]

        fvg = ob_fvg[
            "fvg"
        ]

        first_tap = (
            is_latest_candle_first_tap(
                history,
                ob
            )
        )

        if not first_tap:
            continue

        final_setup = None

        for liquidity in reversed(
            liquidity_alerts
        ):

            for crt in reversed(
                crt_alerts
            ):

                candidate = (
                    build_confluence(
                        symbol=symbol,
                        timeframe=timeframe,
                        liquidity_alert=liquidity,
                        crt_alert=crt,
                        fvg=fvg,
                        ob=ob,
                        ob_first_tap=True
                    )
                )

                if candidate is not None:

                    final_setup = candidate
                    break

            if final_setup is not None:
                break

        if final_setup is None:
            continue

        candle = history.iloc[-1]

        signal_time = str(
            candle["datetime"]
        )

        direction = final_setup[
            "direction"
        ]

        unique_id = (
            f"{signal_time}|"
            f"{direction}|"
            f"{ob.get('time', '')}|"
            f"{fvg.get('time', '')}"
        )

        if unique_id in seen:
            continue

        seen.add(
            unique_id
        )

        entry_price = float(
            candle["close"]
        )

        movement = (
            calculate_forward_move(
                full_df=data,
                signal_index=index,
                direction=direction,
                entry_price=entry_price,
                forward_candles=
                    forward_candles
            )
        )

        best = convert_move(
            symbol,
            movement[
                "best_move"
            ]
        )

        worst = convert_move(
            symbol,
            movement[
                "worst_move"
            ]
        )

        setups.append({
            "symbol":
                symbol,

            "timeframe":
                timeframe,

            "time":
                signal_time,

            "direction":
                direction,

            "trade":
                final_setup[
                    "trade"
                ],

            "entry":
                entry_price,

            "best_move":
                best["value"],

            "worst_move":
                worst["value"],

            "unit":
                best["unit"],

            "ob":
                ob,

            "fvg":
                fvg
        })

    return {
        "symbol":
            symbol,

        "timeframe":
            timeframe,

        "setup_count":
            len(setups),

        "setups":
            setups
    }


def summarize_backtest(
    result
):

    setups = result[
        "setups"
    ]

    if not setups:

        return {
            "symbol":
                result["symbol"],

            "setup_count":
                0,

            "average_best_move":
                0.0,

            "average_worst_move":
                0.0,

            "unit":
                (
                    "pips"
                    if result["symbol"]
                    in [
                        "EUR/USD",
                        "GBP/USD"
                    ]
                    else "points"
                )
        }

    average_best = (
        sum(
            item["best_move"]
            for item in setups
        )
        / len(setups)
    )

    average_worst = (
        sum(
            item["worst_move"]
            for item in setups
        )
        / len(setups)
    )

    return {
        "symbol":
            result["symbol"],

        "setup_count":
            len(setups),

        "average_best_move":
            average_best,

        "average_worst_move":
            average_worst,

        "unit":
            setups[0][
                "unit"
            ]
    }


def format_backtest_summary(
    summary
):

    return (
        "🧪 ICT BACKTEST RESULT\n\n"

        f"Symbol: "
        f"{summary['symbol']}\n"

        f"High Confluence Setups: "
        f"{summary['setup_count']}\n\n"

        f"📈 Average Favorable Move: "
        f"{summary['average_best_move']:.1f} "
        f"{summary['unit']}\n"

        f"📉 Average Adverse Move: "
        f"{summary['average_worst_move']:.1f} "
        f"{summary['unit']}\n\n"

        "Forward window: configurable"
    )
