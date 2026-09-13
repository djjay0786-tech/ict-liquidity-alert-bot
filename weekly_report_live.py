from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

from alert_state import (
    load_alert_state
)

from live_engine import (
    get_market_data,
    build_ranking_snapshot
)

from ranking import (
    rank_instruments
)

from daily_report_live import (
    parse_alert_id,
    get_event_ist_date
)

from weekly_report import (
    get_week_range,
    build_symbol_weekly_report,
    format_weekly_report
)


SYMBOLS = [
    "EUR/USD",
    "GBP/USD",
    "DXY"
]


IST = ZoneInfo(
    "Asia/Kolkata"
)


LIQUIDITY_TYPES = {
    "PDH_PDL",
    "DH_DL",
    "SESSION_LIQUIDITY"
}

CRT_TYPES = {
    "CRT"
}

FVG_TYPES = {
    "FVG"
}

OB_TYPES = {
    "OB_FVG"
}

CONFLUENCE_TYPES = {
    "HIGH_CONFLUENCE"
}


def get_weekly_alert_history(
    symbol,
    week_start,
    week_end
):

    state = load_alert_state()

    history = {
        "liquidity": [],
        "crt": [],
        "fvg": [],
        "ob": [],
        "confluence": []
    }

    for alert_id, record in state.items():

        parsed = parse_alert_id(
            alert_id
        )

        if (
            parsed["symbol"]
            != symbol
        ):
            continue

        details = None

        if isinstance(
            record,
            dict
        ):

            details = record.get(
                "details"
            )

        event_date = (
            get_event_ist_date(
                parsed["event_time"],
                details
            )
        )

        if event_date is None:
            continue

        if not (
            week_start
            <= event_date
            <= week_end
        ):
            continue

        alert_type = parsed[
            "alert_type"
        ]

        event_record = {
            "alert_id":
                alert_id,

            "alert_type":
                alert_type,

            "timeframe":
                parsed["timeframe"],

            "event_time":
                parsed["event_time"],

            "details":
                details
        }

        if (
            alert_type
            in LIQUIDITY_TYPES
        ):

            history[
                "liquidity"
            ].append(
                event_record
            )

        elif (
            alert_type
            in CRT_TYPES
        ):

            history[
                "crt"
            ].append(
                event_record
            )

        elif (
            alert_type
            in FVG_TYPES
        ):

            history[
                "fvg"
            ].append(
                event_record
            )

        elif (
            alert_type
            in OB_TYPES
        ):

            history[
                "ob"
            ].append(
                event_record
            )

        elif (
            alert_type
            in CONFLUENCE_TYPES
        ):

            history[
                "confluence"
            ].append(
                event_record
            )

    return history


def get_week_ohlc(
    df,
    week_start,
    week_end
):

    if (
        df is None
        or df.empty
    ):

        return None

    temp = df.copy()

    temp["datetime"] = (
        pd.to_datetime(
            temp["datetime"],
            utc=True
        )
    )

    temp["datetime_ist"] = (
        temp["datetime"]
        .dt.tz_convert(
            "Asia/Kolkata"
        )
    )

    week_df = temp[
        (
            temp["datetime_ist"]
            .dt.date
            >= week_start
        )
        &
        (
            temp["datetime_ist"]
            .dt.date
            <= week_end
        )
    ].copy()

    if week_df.empty:
        return None

    week_df = (
        week_df.sort_values(
            "datetime_ist"
        )
        .reset_index(
            drop=True
        )
    )

    return {
        "open":
            float(
                week_df.iloc[0][
                    "open"
                ]
            ),

        "high":
            float(
                week_df[
                    "high"
                ].max()
            ),

        "low":
            float(
                week_df[
                    "low"
                ].min()
            ),

        "close":
            float(
                week_df.iloc[-1][
                    "close"
                ]
            ),

        "candles":
            len(
                week_df
            )
    }


def build_live_weekly_report(
    reference_date=None
):

    if reference_date is None:

        reference_date = (
            datetime.now(
                IST
            )
            .date()
        )

    elif isinstance(
        reference_date,
        str
    ):

        reference_date = (
            datetime.fromisoformat(
                reference_date
            )
            .date()
        )

    week_start, week_end = (
        get_week_range(
            reference_date
        )
    )

    print(
        "\n📊 Weekly Report"
    )

    print(
        f"Week: {week_start} "
        f"→ {week_end}"
    )

    symbol_reports = []

    ranking_snapshots = {}

    for symbol in SYMBOLS:

        print(
            f"\n📈 Loading "
            f"{symbol} H1..."
        )

        try:

            df = get_market_data(
                symbol,
                "H1"
            )

        except Exception as e:

            print(
                f"⚠️ Market data error | "
                f"{symbol}: {e}"
            )

            continue

        if (
            df is None
            or df.empty
        ):

            print(
                f"⚠️ No market data | "
                f"{symbol}"
            )

            continue

        ohlc = get_week_ohlc(
            df,
            week_start,
            week_end
        )

        if ohlc is None:

            print(
                f"⚠️ No weekly candles | "
                f"{symbol}"
            )

            continue

        history = (
            get_weekly_alert_history(
                symbol,
                week_start,
                week_end
            )
        )

        report = (
            build_symbol_weekly_report(
                symbol=symbol,

                week_open=
                    ohlc["open"],

                week_high=
                    ohlc["high"],

                week_low=
                    ohlc["low"],

                week_close=
                    ohlc["close"],

                liquidity_events=
                    history[
                        "liquidity"
                    ],

                crt_events=
                    history[
                        "crt"
                    ],

                fvg_events=
                    history[
                        "fvg"
                    ],

                ob_events=
                    history[
                        "ob"
                    ],

                confluence_events=
                    history[
                        "confluence"
                    ]
            )
        )

        symbol_reports.append(
            report
        )

        try:

            ranking_snapshots[
                symbol
            ] = (
                build_ranking_snapshot(
                    df
                )
            )

        except Exception as e:

            print(
                f"⚠️ Ranking snapshot "
                f"error | {symbol}: {e}"
            )

    rankings = None

    if all(
        symbol
        in ranking_snapshots
        for symbol in SYMBOLS
    ):

        rankings = (
            rank_instruments(
                ranking_snapshots
            )
        )

    message = format_weekly_report(
        symbol_reports=
            symbol_reports,

        rankings=
            rankings,

        week_start=
            week_start,

        week_end=
            week_end
    )

    return message


def main():

    message = (
        build_live_weekly_report()
    )

    print(
        "\n"
        + "=" * 60
    )

    print(
        message
    )

    print(
        "=" * 60
    )

    print(
        "\n✅ WEEKLY REPORT "
        "LIVE BUILD PASSED"
    )


if __name__ == "__main__":

    main()
