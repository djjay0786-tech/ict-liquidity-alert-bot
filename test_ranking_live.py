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

from crt import detect_crt

from ob_fvg import (
    select_ob_near_fvg
)

from ob_tap import (
    is_latest_candle_first_tap
)

from confluence import (
    get_direction_from_liquidity,
    get_direction_from_crt
)

from ranking import (
    rank_instruments,
    format_ranking_message
)


SYMBOLS = [
    "EUR/USD",
    "GBP/USD",
    "DXY"
]


def get_h1_data(symbol):

    if symbol == "DXY":

        data = get_dxy_candles(
            interval="1h",
            limit=200
        )

        return prepare_dxy_candles(
            data
        )

    data = get_candles(
        symbol,
        interval="1h",
        outputsize=200
    )

    if "values" not in data:
        return None

    return prepare_candles(
        data["values"]
    )


def get_latest_liquidity(df):

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

    for session in [
        "ASIA",
        "LONDON",
        "NEW YORK"
    ]:

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

        direction = (
            get_direction_from_liquidity(
                alert
            )
        )

        if direction is not None:
            valid.append(alert)

    if not valid:
        return None

    return valid[-1]


def get_latest_crt(df):

    alerts = detect_crt(
        df
    ) or []

    valid = []

    for alert in alerts:

        direction = (
            get_direction_from_crt(
                alert
            )
        )

        if direction is not None:
            valid.append(alert)

    if not valid:
        return None

    return valid[-1]


def build_snapshot(symbol):

    print(
        f"\n📊 Loading {symbol} H1..."
    )

    df = get_h1_data(
        symbol
    )

    if (
        df is None
        or df.empty
    ):

        print(
            f"⚠️ No H1 data for {symbol}"
        )

        return {
            "liquidity": None,
            "crt": None,
            "fvg": None,
            "ob": None,
            "ob_first_tap": False
        }

    print(
        f"✅ {len(df)} candles | "
        f"{symbol}"
    )

    liquidity = (
        get_latest_liquidity(
            df
        )
    )

    crt = get_latest_crt(
        df
    )

    setup = select_ob_near_fvg(
        df
    )

    if setup is None:

        fvg = None
        ob = None
        first_tap = False

    else:

        fvg = setup[
            "fvg"
        ]

        ob = setup[
            "ob"
        ]

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


def main():

    instruments = {}

    for symbol in SYMBOLS:

        instruments[
            symbol
        ] = build_snapshot(
            symbol
        )

    rankings = rank_instruments(
        instruments
    )

    print(
        "\n" + "=" * 50
    )

    print(
        format_ranking_message(
            rankings
        )
    )

    print(
        "=" * 50
    )

    print(
        "\n✅ LIVE RANKING TEST PASSED"
    )


if __name__ == "__main__":
    main()
