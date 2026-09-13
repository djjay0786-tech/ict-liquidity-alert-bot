from market_data import get_candles

from dxy_data import (
    get_dxy_candles,
    prepare_dxy_candles
)

from liquidity import prepare_candles

from order_block import (
    detect_order_blocks,
    get_valid_order_blocks
)

from fvg import (
    get_valid_fvgs
)

from ob_fvg import (
    select_ob_near_fvg
)

from ob_tap import (
    is_latest_candle_first_tap
)


SYMBOLS = [
    "EUR/USD",
    "GBP/USD",
    "DXY"
]


def get_h1(symbol):

    if symbol == "DXY":

        raw = get_dxy_candles(
            interval="1h",
            limit=200
        )

        return prepare_dxy_candles(
            raw
        )

    raw = get_candles(
        symbol,
        interval="1h",
        outputsize=200
    )

    return prepare_candles(
        raw["values"]
    )


def debug_symbol(
    df,
    symbol
):

    stats = {
        "replay_candles": 0,
        "detected_obs": 0,
        "valid_obs": 0,
        "valid_fvgs": 0,
        "ob_fvg_selections": 0,
        "selected_first_taps": 0
    }

    seen_obs = set()
    seen_valid_obs = set()
    seen_fvg = set()
    seen_selection = set()
    seen_tap = set()

    for index in range(
        60,
        len(df)
    ):

        history = (
            df.iloc[:index + 1]
            .copy()
        )

        stats[
            "replay_candles"
        ] += 1

        # -------------------------
        # ALL DETECTED OBs
        # -------------------------

        obs = detect_order_blocks(
            history
        )

        for ob in obs:

            key = (
                f"{ob['type']}|"
                f"{ob['time']}"
            )

            if key not in seen_obs:

                seen_obs.add(
                    key
                )

                stats[
                    "detected_obs"
                ] += 1

        # -------------------------
        # VALID OBs
        # -------------------------

        valid_obs = (
            get_valid_order_blocks(
                history
            )
        )

        for ob in valid_obs:

            key = (
                f"{ob['type']}|"
                f"{ob['time']}"
            )

            if key not in seen_valid_obs:

                seen_valid_obs.add(
                    key
                )

                stats[
                    "valid_obs"
                ] += 1

        # -------------------------
        # VALID FVGs
        # -------------------------

        fvgs = get_valid_fvgs(
            history
        )

        for fvg in fvgs:

            key = (
                f"{fvg['type']}|"
                f"{fvg['time']}"
            )

            if key not in seen_fvg:

                seen_fvg.add(
                    key
                )

                stats[
                    "valid_fvgs"
                ] += 1

        # -------------------------
        # SELECTED OB + FVG
        # -------------------------

        setup = select_ob_near_fvg(
            history
        )

        if setup is None:
            continue

        ob = setup["ob"]
        fvg = setup["fvg"]

        selection_key = (
            f"{ob['type']}|"
            f"{ob['time']}|"
            f"{fvg['time']}"
        )

        if (
            selection_key
            not in seen_selection
        ):

            seen_selection.add(
                selection_key
            )

            stats[
                "ob_fvg_selections"
            ] += 1

        # -------------------------
        # FIRST TAP OF SELECTED OB
        # -------------------------

        if (
            is_latest_candle_first_tap(
                history,
                ob
            )
        ):

            candle_time = str(
                history.iloc[-1][
                    "datetime"
                ]
            )

            tap_key = (
                f"{selection_key}|"
                f"{candle_time}"
            )

            if tap_key not in seen_tap:

                seen_tap.add(
                    tap_key
                )

                stats[
                    "selected_first_taps"
                ] += 1

                print(
                    "\n🔥 FIRST TAP FOUND"
                )

                print(
                    f"Symbol: {symbol}"
                )

                print(
                    f"OB: {ob['type']}"
                )

                print(
                    f"OB Time: {ob['time']}"
                )

                print(
                    f"FVG Time: {fvg['time']}"
                )

                print(
                    f"Tap Time: "
                    f"{candle_time}"
                )

    return stats


def main():

    print(
        "\n"
        + "=" * 60
    )

    print(
        "🔎 OB / FVG FUNNEL DEBUG"
    )

    print(
        "=" * 60
    )

    for symbol in SYMBOLS:

        print(
            f"\n📊 Loading {symbol}..."
        )

        try:

            df = get_h1(
                symbol
            )

            print(
                f"✅ {len(df)} candles"
            )

            stats = debug_symbol(
                df,
                symbol
            )

            print()
            print(
                f"===== {symbol} ====="
            )

            print(
                "Detected OBs: "
                f"{stats['detected_obs']}"
            )

            print(
                "Valid OBs: "
                f"{stats['valid_obs']}"
            )

            print(
                "Valid FVGs: "
                f"{stats['valid_fvgs']}"
            )

            print(
                "OB + FVG Selections: "
                f"{stats['ob_fvg_selections']}"
            )

            print(
                "Selected OB First Taps: "
                f"{stats['selected_first_taps']}"
            )

        except Exception as e:

            print(
                f"❌ {symbol}: {e}"
            )

    print()
    print(
        "✅ DEBUG COMPLETED"
    )


if __name__ == "__main__":
    main()
