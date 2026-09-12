from confluence import (
    get_direction_from_liquidity,
    get_direction_from_crt,
    get_direction_from_fvg,
    get_direction_from_ob
)


def get_alignment_status(
    liquidity_alert=None,
    crt_alert=None,
    fvg=None,
    ob=None,
    ob_first_tap=False
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
        ob_direction
    ]

    valid_directions = [
        direction
        for direction in directions
        if direction is not None
    ]

    if not valid_directions:

        return {
            "status": "NO SETUP",
            "direction": None,
            "priority": 0
        }

    bullish_count = (
        valid_directions.count(
            "BULLISH"
        )
    )

    bearish_count = (
        valid_directions.count(
            "BEARISH"
        )
    )

    if bullish_count > bearish_count:
        direction = "BULLISH"

    elif bearish_count > bullish_count:
        direction = "BEARISH"

    else:
        direction = None

    all_present = all(
        direction_item is not None
        for direction_item in directions
    )

    all_same = (
        all_present
        and len(set(directions)) == 1
    )

    if (
        all_same
        and ob_first_tap
    ):

        return {
            "status": "HIGH CONFLUENCE",
            "direction": direction,
            "priority": 3
        }

    if all_same:

        return {
            "status": "WATCH",
            "direction": direction,
            "priority": 2
        }

    same_direction_count = max(
        bullish_count,
        bearish_count
    )

    if (
        direction is not None
        and same_direction_count >= 3
    ):

        return {
            "status": "WATCH",
            "direction": direction,
            "priority": 1
        }

    return {
        "status": "NO SETUP",
        "direction": direction,
        "priority": 0
    }


def rank_instruments(
    instruments
):

    results = []

    for symbol, data in instruments.items():

        alignment = (
            get_alignment_status(
                liquidity_alert=data.get(
                    "liquidity"
                ),
                crt_alert=data.get(
                    "crt"
                ),
                fvg=data.get(
                    "fvg"
                ),
                ob=data.get(
                    "ob"
                ),
                ob_first_tap=data.get(
                    "ob_first_tap",
                    False
                )
            )
        )

        results.append({
            "symbol": symbol,
            "status": alignment[
                "status"
            ],
            "direction": alignment[
                "direction"
            ],
            "priority": alignment[
                "priority"
            ]
        })

    results.sort(
        key=lambda item: (
            item["priority"]
        ),
        reverse=True
    )

    for index, item in enumerate(
        results,
        start=1
    ):
        item["rank"] = index

    return results


def format_ranking_message(
    rankings
):

    message = (
        "🏆 ICT MARKET RANKING\n"
        "H1 SETUP PRIORITY\n\n"
    )

    for item in rankings:

        rank = item["rank"]
        symbol = item["symbol"]
        status = item["status"]
        direction = item[
            "direction"
        ]

        if direction == "BULLISH":
            direction_text = "🟢 BUY"

        elif direction == "BEARISH":
            direction_text = "🔴 SELL"

        else:
            direction_text = "⚪ NEUTRAL"

        if status == "HIGH CONFLUENCE":
            status_text = (
                "🔥 HIGH CONFLUENCE"
            )

        elif status == "WATCH":
            status_text = "👀 WATCH"

        else:
            status_text = "➖ NO SETUP"

        message += (
            f"#{rank} {symbol}\n"
            f"{direction_text}\n"
            f"{status_text}\n\n"
        )

    message += (
        "Priority only — "
        "not a setup score."
    )

    return message
