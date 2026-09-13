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


# ==========================================
# EVENT COLLECTION
# ==========================================

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

    valid = []

    for alert in alerts:

        if (
            get_direction_from_liquidity(
                alert
            )
            is not None
        ):
            valid.append(
                alert
            )

    return valid


def get_crt_alerts(df):

    alerts = (
        detect_crt(df)
        or []
    )

    valid = []

    for alert in alerts:

        if (
            get_direction_from_crt(
                alert
            )
            is not None
        ):
            valid.append(
                alert
            )

    return valid


def make_liquidity_key(
    alert
):

    return "|".join([
        str(
            alert.get(
                "type",
                ""
            )
        ),
        str(
            alert.get(
                "time",
                ""
            )
        ),
        str(
            alert.get(
                "level",
                ""
            )
        ),
        str(
            alert.get(
                "session",
                ""
            )
        ),
        str(
            alert.get(
                "session_date",
                ""
            )
        ),
        str(
            alert.get(
                "level_date",
                ""
            )
        )
    ])


def make_crt_key(
    alert
):

    return "|".join([
        str(
            alert.get(
                "type",
                ""
            )
        ),
        str(
            alert.get(
                "first_candle_time",
                ""
            )
        ),
        str(
            alert.get(
                "second_candle_time",
                ""
            )
        )
    ])


# ==========================================
# FORWARD MOVE
# ==========================================

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


# ==========================================
# SEQUENCE BACKTEST
# ==========================================

def backtest_symbol(
    df,
    symbol,
    timeframe="H1",
    minimum_candles=60,
    forward_candles=6,
    liquidity_lookback=6,
    crt_lookback=4
):

    if (
        df is None
        or df.empty
    ):

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "setup_count": 0,
            "setups": [],
            "stats": {
                "candles": 0,
                "liquidity_events": 0,
                "crt_events": 0,
                "ob_first_taps": 0,
                "confluence_setups": 0
            }
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

    seen_setups = set()
    seen_liquidity = set()
    seen_crt = set()
    seen_taps = set()

    liquidity_history = []
    crt_history = []

    stats = {
        "candles":
            len(data),

        "liquidity_events":
            0,

        "crt_events":
            0,

        "ob_first_taps":
            0,

        "confluence_setups":
            0
    }

    for index in range(
        minimum_candles,
        len(data)
    ):

        history = (
            data.iloc[
                :index + 1
            ]
            .copy()
        )

        # ==================================
        # 1. RECORD LIQUIDITY EVENTS
        # ==================================

        current_liquidity = (
            get_liquidity_alerts(
                history
            )
        )

        for alert in current_liquidity:

            key = (
                make_liquidity_key(
                    alert
                )
            )

            if key in seen_liquidity:
                continue

            seen_liquidity.add(
                key
            )

            direction = (
                get_direction_from_liquidity(
                    alert
                )
            )

            liquidity_history.append({
                "index":
                    index,

                "direction":
                    direction,

                "alert":
                    alert
            })

            stats[
                "liquidity_events"
            ] += 1

        # ==================================
        # 2. RECORD CRT EVENTS
        # ==================================

        current_crt = (
            get_crt_alerts(
                history
            )
        )

        for alert in current_crt:

            key = (
                make_crt_key(
                    alert
                )
            )

            if key in seen_crt:
                continue

            seen_crt.add(
                key
            )

            direction = (
                get_direction_from_crt(
                    alert
                )
            )

            crt_history.append({
                "index":
                    index,

                "direction":
                    direction,

                "alert":
                    alert
            })

            stats[
                "crt_events"
            ] += 1

        # ==================================
        # 3. CURRENT VALID OB + FVG
        # ==================================

        setup = (
            select_ob_near_fvg(
                history
            )
        )

        if setup is None:
            continue

        ob = setup[
            "ob"
        ]

        fvg = setup[
            "fvg"
        ]

        # ==================================
        # 4. FIRST TAP
        # ==================================

        first_tap = (
            is_latest_candle_first_tap(
                history,
                ob
            )
        )

        if not first_tap:
            continue

        tap_key = "|".join([
            str(
                ob.get(
                    "type",
                    ""
                )
            ),
            str(
                ob.get(
                    "time",
                    ""
                )
            ),
            str(
                history.iloc[-1][
                    "datetime"
                ]
            )
        ])

        if tap_key not in seen_taps:

            seen_taps.add(
                tap_key
            )

            stats[
                "ob_first_taps"
            ] += 1

        # ==================================
        # 5. RECENT LIQUIDITY WINDOW
        # ==================================

        recent_liquidity = [
            item
            for item
            in liquidity_history
            if (
                0
                <= index
                - item["index"]
                <= liquidity_lookback
            )
        ]

        if not recent_liquidity:
            continue

        # ==================================
        # 6. RECENT CRT WINDOW
        # ==================================

        recent_crt = [
            item
            for item
            in crt_history
            if (
                0
                <= index
                - item["index"]
                <= crt_lookback
            )
        ]

        if not recent_crt:
            continue

        # ==================================
        # 7. SEQUENCE:
        # LIQUIDITY -> CRT -> OB TAP
        # ==================================

        final_setup = None
        final_liquidity = None
        final_crt = None

        for crt_item in reversed(
            recent_crt
        ):

            for liquidity_item in reversed(
                recent_liquidity
            ):

                # Liquidity must happen
                # before or at CRT.
                if (
                    liquidity_item[
                        "index"
                    ]
                    >
                    crt_item[
                        "index"
                    ]
                ):
                    continue

                # Directions must agree
                # before building final
                # confluence.
                if (
                    liquidity_item[
                        "direction"
                    ]
                    !=
                    crt_item[
                        "direction"
                    ]
                ):
                    continue

                candidate = (
                    build_confluence(
                        symbol=symbol,
                        timeframe=timeframe,
                        liquidity_alert=
                            liquidity_item[
                                "alert"
                            ],
                        crt_alert=
                            crt_item[
                                "alert"
                            ],
                        fvg=fvg,
                        ob=ob,
                        ob_first_tap=True
                    )
                )

                if candidate is None:
                    continue

                final_setup = (
                    candidate
                )

                final_liquidity = (
                    liquidity_item[
                        "alert"
                    ]
                )

                final_crt = (
                    crt_item[
                        "alert"
                    ]
                )

                break

            if (
                final_setup
                is not None
            ):
                break

        if final_setup is None:
            continue

        # ==================================
        # 8. UNIQUE SETUP
        # ==================================

        candle = (
            history.iloc[-1]
        )

        signal_time = str(
            candle[
                "datetime"
            ]
        )

        direction = (
            final_setup[
                "direction"
            ]
        )

        unique_id = "|".join([
            signal_time,
            direction,
            str(
                ob.get(
                    "time",
                    ""
                )
            ),
            str(
                fvg.get(
                    "time",
                    ""
                )
            )
        ])

        if unique_id in seen_setups:
            continue

        seen_setups.add(
            unique_id
        )

        entry_price = float(
            candle[
                "close"
            ]
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
                best[
                    "value"
                ],

            "worst_move":
                worst[
                    "value"
                ],

            "unit":
                best[
                    "unit"
                ],

            "liquidity":
                final_liquidity,

            "crt":
                final_crt,

            "ob":
                ob,

            "fvg":
                fvg
        })

        stats[
            "confluence_setups"
        ] += 1

    return {
        "symbol":
            symbol,

        "timeframe":
            timeframe,

        "setup_count":
            len(setups),

        "setups":
            setups,

        "stats":
            stats
    }


# ==========================================
# SUMMARY
# ==========================================

def summarize_backtest(
    result
):

    setups = (
        result.get(
            "setups",
            []
        )
    )

    stats = (
        result.get(
            "stats",
            {}
        )
    )

    if not setups:

        return {
            "symbol":
                result[
                    "symbol"
                ],

            "setup_count":
                0,

            "average_best_move":
                0.0,

            "average_worst_move":
                0.0,

            "unit":
                (
                    "pips"
                    if result[
                        "symbol"
                    ]
                    in [
                        "EUR/USD",
                        "GBP/USD"
                    ]
                    else "points"
                ),

            "stats":
                stats
        }

    average_best = (
        sum(
            item[
                "best_move"
            ]
            for item in setups
        )
        / len(setups)
    )

    average_worst = (
        sum(
            item[
                "worst_move"
            ]
            for item in setups
        )
        / len(setups)
    )

    return {
        "symbol":
            result[
                "symbol"
            ],

        "setup_count":
            len(setups),

        "average_best_move":
            average_best,

        "average_worst_move":
            average_worst,

        "unit":
            setups[0][
                "unit"
            ],

        "stats":
            stats
    }


def format_backtest_summary(
    summary
):

    stats = (
        summary.get(
            "stats",
            {}
        )
    )

    message = (
        "🧪 ICT BACKTEST RESULT\n\n"

        f"Symbol: "
        f"{summary['symbol']}\n"

        f"High Confluence Setups: "
        f"{summary['setup_count']}\n\n"
    )

    if stats:

        message += (
            "🔎 Sequence Funnel\n"
            f"Liquidity Events: "
            f"{stats.get('liquidity_events', 0)}\n"

            f"CRT Events: "
            f"{stats.get('crt_events', 0)}\n"

            f"OB First Taps: "
            f"{stats.get('ob_first_taps', 0)}\n\n"
        )

    message += (
        f"📈 Average Favorable Move: "
        f"{summary['average_best_move']:.1f} "
        f"{summary['unit']}\n"

        f"📉 Average Adverse Move: "
        f"{summary['average_worst_move']:.1f} "
        f"{summary['unit']}\n\n"

        "Sequence: "
        "Liquidity → CRT → "
        "OB/FVG First Tap"
    )

    return message
