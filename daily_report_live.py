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

from daily_report import (
    build_symbol_report,
    format_daily_report
)


SYMBOLS = [
    "EUR/USD",
    "GBP/USD",
    "DXY"
]


IST = ZoneInfo(
    "Asia/Kolkata"
)

UTC = ZoneInfo(
    "UTC"
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


def parse_alert_id(
    alert_id
):

    parts = str(
        alert_id
    ).split(
        "|",
        4
    )

    while len(parts) < 5:
        parts.append("")

    return {
        "alert_type": parts[0],
        "symbol": parts[1],
        "timeframe": parts[2],
        "event_time": parts[3],
        "extra": parts[4]
    }


def get_event_ist_date(
    event_time,
    details=None
):

    candidates = []

    if isinstance(
        details,
        dict
    ):

        for key in [
            "time",
            "second_candle_time",
            "event_time"
        ]:

            value = details.get(
                key
            )

            if value:
                candidates.append(
                    value
                )

    if event_time:
        candidates.append(
            event_time
        )

    for value in candidates:

        text = str(
            value
        ).strip()

        if not text:
            continue

        try:

            if (
                len(text) == 10
                and text[4] == "-"
                and text[7] == "-"
            ):

                return datetime.fromisoformat(
                    text
                ).date()

            dt = datetime.fromisoformat(
                text.replace(
                    "Z",
                    "+00:00"
                )
            )

            if dt.tzinfo is None:

                dt = dt.replace(
                    tzinfo=UTC
                )

            return (
                dt.astimezone(
                    IST
                )
                .date()
            )

        except Exception:
            continue

    return None


def get_alert_history_for_day(
    symbol,
    report_date
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

        if (
            event_date
            != report_date
        ):
            continue

        alert_type = parsed[
            "alert_type"
        ]

        event_record = {
            "alert_id": alert_id,
            "alert_type": alert_type,
            "timeframe": parsed[
                "timeframe"
            ],
            "event_time": parsed[
                "event_time"
            ],
            "details": details
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


def get_ist_day_ohlc(
    df,
    report_date
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

    day_df = temp[
        temp["datetime_ist"]
        .dt.date
        == report_date
    ].copy()

    if day_df.empty:
        return None

    day_df = (
        day_df.sort_values(
            "datetime_ist"
        )
        .reset_index(
            drop=True
        )
    )

    return {
        "open": float(
            day_df.iloc[0][
                "open"
            ]
        ),

        "high": float(
            day_df[
                "high"
            ].max()
        ),

        "low": float(
            day_df[
                "low"
            ].min()
        ),

        "close": float(
            day_df.iloc[-1][
                "close"
            ]
        ),

        "candles": len(
            day_df
        )
    }


def build_live_daily_report(
    report_date=None
):

    if report_date is None:

        report_date = (
            datetime.now(
                IST
            )
            .date()
        )

    elif isinstance(
        report_date,
        str
    ):

        report_date = (
            datetime.fromisoformat(
                report_date
            )
            .date()
        )

    symbol_reports = []

    ranking_snapshots = {}

    for symbol in SYMBOLS:

        print(
            f"\n📅 Daily Report | "
            f"{symbol}"
        )

        try:

            df = get_market_data(
                symbol,
                "H1"
            )

        except Exception as e:

            print(
                f"⚠️ Market data "
                f"error | {symbol}: "
                f"{e}"
            )

            continue

        if (
            df is None
            or df.empty
        ):

            print(
                f"⚠️ No H1 data | "
                f"{symbol}"
            )

            continue

        ohlc = get_ist_day_ohlc(
            df,
            report_date
        )

        if ohlc is None:

            print(
                f"⚠️ No candles for "
                f"{report_date} | "
                f"{symbol}"
            )

            continue

        history = (
            get_alert_history_for_day(
                symbol,
                report_date
            )
        )

        report = build_symbol_report(
            symbol=symbol,

            day_open=ohlc[
                "open"
            ],

            day_high=ohlc[
                "high"
            ],

            day_low=ohlc[
                "low"
            ],

            day_close=ohlc[
                "close"
            ],

            liquidity_events=history[
                "liquidity"
            ],

            crt_events=history[
                "crt"
            ],

            fvg_events=history[
                "fvg"
            ],

            ob_events=history[
                "ob"
            ],

            confluence_events=history[
                "confluence"
            ]
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
                f"error | {symbol}: "
                f"{e}"
            )

    rankings = None

    if all(
        symbol in ranking_snapshots
        for symbol in SYMBOLS
    ):

        rankings = (
            rank_instruments(
                ranking_snapshots
            )
        )

    message = format_daily_report(
        symbol_reports=
            symbol_reports,

        rankings=rankings,

        report_date=
            report_date.isoformat()
    )

    return message


def main():

    message = (
        build_live_daily_report()
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
        "\n✅ DAILY REPORT "
        "LIVE BUILD PASSED"
    )


if __name__ == "__main__":

    main()
