from datetime import datetime


def get_direction_from_liquidity(alert):

    if alert is None:
        return None

    alert_type = alert.get(
        "type",
        ""
    )

    if (
        alert_type
        == "BULLISH LIQUIDITY GRAB"
    ):
        return "BULLISH"

    if (
        alert_type
        == "BEARISH LIQUIDITY GRAB"
    ):
        return "BEARISH"

    return None


def get_direction_from_crt(alert):

    if alert is None:
        return None

    alert_type = alert.get(
        "type",
        ""
    )

    if alert_type == "BULLISH CRT":
        return "BULLISH"

    if alert_type == "BEARISH CRT":
        return "BEARISH"

    return None


def get_direction_from_fvg(fvg):

    if fvg is None:
        return None

    if (
        fvg.get("type")
        == "BULLISH FVG"
    ):
        return "BULLISH"

    if (
        fvg.get("type")
        == "BEARISH FVG"
    ):
        return "BEARISH"

    return None


def get_direction_from_ob(ob):

    if ob is None:
        return None

    if (
        ob.get("type")
        == "BULLISH OB"
    ):
        return "BULLISH"

    if (
        ob.get("type")
        == "BEARISH OB"
    ):
        return "BEARISH"

    return None


def build_confluence(
    symbol,
    timeframe,
    liquidity_alert,
    crt_alert,
    fvg,
    ob,
    ob_first_tap=False,
):

    liquidity_direction = (
        get_direction_from_liquidity(
            liquidity_alert
        )
    )

    crt_direction = (
        get_direction_from_crt(
            crt_alert
        )
    )

    fvg_direction = (
        get_direction_from_fvg(
            fvg
        )
    )

    ob_direction = (
        get_direction_from_ob(
            ob
        )
    )

    directions = [
        liquidity_direction,
        crt_direction,
        fvg_direction,
        ob_direction,
    ]

    # Every required signal
    # must exist.
    if any(
        direction is None
        for direction in directions
    ):
        return None

    # All signals must point
    # in the same direction.
    if len(set(directions)) != 1:
        return None

    # OB must have received
    # its first tap.
    if not ob_first_tap:
        return None

    direction = directions[0]

    if direction == "BULLISH":
        trade = "BUY"
    else:
        trade = "SELL"

    return {
        "symbol":
            symbol,

        "timeframe":
            timeframe,

        "direction":
            direction,

        "trade":
            trade,

        "liquidity":
            liquidity_alert,

        "crt":
            crt_alert,

        "fvg":
            fvg,

        "ob":
            ob,

        "ob_first_tap":
            True,

        "created_at":
            datetime.utcnow()
            .isoformat(),
    }


def format_confluence_alert(
    setup
):

    if setup is None:
        return None

    if (
        setup["direction"]
        == "BULLISH"
    ):
        emoji = "🟢"
    else:
        emoji = "🔴"

    liquidity = setup[
        "liquidity"
    ]

    crt = setup["crt"]
    fvg = setup["fvg"]
    ob = setup["ob"]

    ob_level = ob.get(
        "level",
        ob.get(
            "midpoint",
            0
        )
    )

    return (
        "🔥 HIGH CONFLUENCE SETUP\n\n"

        f"{emoji} "
        f"{setup['trade']}\n\n"

        f"Symbol: "
        f"{setup['symbol']}\n"

        f"Timeframe: "
        f"{setup['timeframe']}\n\n"

        f"✅ Liquidity Grab: "
        f"{liquidity.get('level', '-')}\n"

        f"✅ CRT: "
        f"{crt.get('type', '-')}\n"

        f"✅ FVG: "
        f"{fvg.get('type', '-')}\n"

        f"✅ Order Block: "
        f"{ob.get('type', '-')}\n"

        f"✅ OB First Tap\n\n"

        f"OB Level: "
        f"{float(ob_level):.5f}\n"

        f"FVG: "
        f"{float(fvg['bottom']):.5f}"
        f" - "
        f"{float(fvg['top']):.5f}"
    )
