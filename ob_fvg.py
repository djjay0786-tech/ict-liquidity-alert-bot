from fvg import get_valid_fvgs
from order_block import get_valid_order_blocks


def select_ob_near_fvg(df):

    """
    Select the most relevant valid OB
    near the latest valid FVG.

    Rules:
    1. FVG must be valid / unmitigated.
    2. OB must be valid / unmitigated.
    3. OB and FVG must have same direction.
    4. OB must form before the FVG.
    5. Latest valid FVG gets priority.
    6. Closest OB to that FVG is selected.
    """

    if df is None or df.empty:
        return None

    valid_fvgs = get_valid_fvgs(
        df
    )

    valid_obs = get_valid_order_blocks(
        df
    )

    if (
        not valid_fvgs
        or not valid_obs
    ):
        return None

    # Latest valid FVG first
    sorted_fvgs = sorted(
        valid_fvgs,
        key=lambda x: x["index"],
        reverse=True
    )

    for fvg in sorted_fvgs:

        candidates = []

        if (
            fvg["type"]
            == "BULLISH FVG"
        ):
            required_ob_type = (
                "BULLISH OB"
            )

        else:
            required_ob_type = (
                "BEARISH OB"
            )

        for ob in valid_obs:

            # Same direction
            if (
                ob["type"]
                != required_ob_type
            ):
                continue

            # OB must exist before FVG
            if (
                int(ob["index"])
                >=
                int(fvg["index"])
            ):
                continue

            ob_center = (
                float(ob["high"])
                +
                float(ob["low"])
            ) / 2

            fvg_center = (
                float(fvg["top"])
                +
                float(fvg["bottom"])
            ) / 2

            distance = abs(
                ob_center
                -
                fvg_center
            )

            candidates.append({
                "ob": ob,
                "distance": distance
            })

        if not candidates:
            continue

        # Closest valid OB
        selected = min(
            candidates,
            key=lambda x: (
                x["distance"],
                -int(x["ob"]["index"])
            )
        )

        return {
            "fvg": fvg,
            "ob": selected["ob"],
            "distance":
                selected["distance"]
        }

    return None


def format_ob_fvg_selection(
    symbol,
    timeframe,
    setup
):

    ob = setup["ob"]
    fvg = setup["fvg"]

    if (
        ob["type"]
        == "BULLISH OB"
    ):
        emoji = "🟢"

    else:
        emoji = "🔴"

    return (
        f"{emoji} OB + FVG SETUP\n\n"
        f"Symbol: {symbol}\n"
        f"Timeframe: {timeframe}\n\n"

        f"Order Block: "
        f"{ob['type']}\n"
        f"OB High: "
        f"{ob['high']:.5f}\n"
        f"OB Low: "
        f"{ob['low']:.5f}\n"
        f"OB Midpoint: "
        f"{ob['midpoint']:.5f}\n\n"

        f"FVG: "
        f"{fvg['type']}\n"
        f"FVG Top: "
        f"{fvg['top']:.5f}\n"
        f"FVG Bottom: "
        f"{fvg['bottom']:.5f}\n"
        f"FVG Midpoint: "
        f"{fvg['midpoint']:.5f}\n\n"

        f"OB-FVG Distance: "
        f"{setup['distance']:.5f}\n\n"

        f"OB Time: "
        f"{ob['time']}\n"
        f"FVG Time: "
        f"{fvg['time']}"
    )
