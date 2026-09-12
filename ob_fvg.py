from fvg import detect_fvg
from order_block import detect_order_blocks


def select_ob_near_fvg(df):

    if df.empty:
        return None

    fvgs = detect_fvg(df)
    obs = detect_order_blocks(df)

    if not fvgs or not obs:
        return None

    # Latest FVG
    last_fvg = fvgs[-1]

    matching_obs = []

    for ob in obs:

        # ==========================================
        # SAME DIRECTION ONLY
        # ==========================================

        if last_fvg["type"] == "BULLISH FVG":

            if ob["type"] != "BULLISH OB":
                continue

        elif last_fvg["type"] == "BEARISH FVG":

            if ob["type"] != "BEARISH OB":
                continue

        # ==========================================
        # OB MUST FORM BEFORE FVG
        # ==========================================

        if ob["time"] >= last_fvg["time"]:
            continue

        # ==========================================
        # OB CENTER
        # ==========================================

        ob_center = (
            ob["high"] + ob["low"]
        ) / 2

        # ==========================================
        # FVG CENTER
        # ==========================================

        fvg_center = (
            last_fvg["top"] + last_fvg["bottom"]
        ) / 2

        # ==========================================
        # DISTANCE
        # ==========================================

        distance = abs(
            ob_center - fvg_center
        )

        matching_obs.append({
            "ob": ob,
            "distance": distance
        })

    if not matching_obs:
        return None

    # ==========================================
    # CLOSEST VALID OB
    # ==========================================

    selected = min(
        matching_obs,
        key=lambda x: x["distance"]
    )

    return {
        "fvg": last_fvg,
        "ob": selected["ob"],
        "distance": selected["distance"]
    }


def format_ob_fvg_selection(
    symbol,
    timeframe,
    setup
):

    ob = setup["ob"]
    fvg = setup["fvg"]

    if ob["type"] == "BULLISH OB":
        emoji = "🟢"
    else:
        emoji = "🔴"

    message = (
        f"{emoji} OB + FVG SETUP\n\n"

        f"Symbol: {symbol}\n"
        f"Timeframe: {timeframe}\n\n"

        f"Order Block: {ob['type']}\n"
        f"OB High: {ob['high']:.5f}\n"
        f"OB Low: {ob['low']:.5f}\n\n"

        f"FVG: {fvg['type']}\n"
        f"FVG Top: {fvg['top']:.5f}\n"
        f"FVG Bottom: {fvg['bottom']:.5f}\n\n"

        f"OB-FVG Distance: "
        f"{setup['distance']:.5f}\n\n"

        f"OB Time: {ob['time']}\n"
        f"FVG Time: {fvg['time']}"
    )

    return message
