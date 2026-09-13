import json
from pathlib import Path
from datetime import datetime, timezone

from ranking import format_ranking_message


STATE_FILE = Path("ranking_state.json")


def load_ranking_state():

    if not STATE_FILE.exists():
        return {}

    try:

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, dict):
                return data

    except Exception as e:

        print(
            f"⚠️ Ranking state "
            f"load error: {e}"
        )

    return {}


def save_ranking_state(
    state
):

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            state,
            file,
            indent=2,
            ensure_ascii=False
        )


def make_ranking_signature(
    rankings
):

    parts = []

    for item in rankings:

        parts.append(
            "|".join([
                str(
                    item.get(
                        "rank",
                        ""
                    )
                ),
                str(
                    item.get(
                        "symbol",
                        ""
                    )
                ),
                str(
                    item.get(
                        "status",
                        ""
                    )
                ),
                str(
                    item.get(
                        "direction",
                        ""
                    )
                )
            ])
        )

    return "||".join(
        parts
    )


def process_ranking_alert(
    rankings,
    candle_time,
    send_function
):

    if not rankings:

        print(
            "🏆 No ranking data"
        )

        return {
            "sent": False,
            "reason": "no_rankings"
        }

    candle_time = str(
        candle_time
    )

    state = load_ranking_state()

    last_checked_candle = (
        state.get(
            "last_checked_candle"
        )
    )

    # --------------------------------------
    # SAME H1 CANDLE
    # --------------------------------------

    if (
        last_checked_candle
        == candle_time
    ):

        print(
            "🚫 Ranking already checked "
            "for this H1 candle"
        )

        return {
            "sent": False,
            "reason": "already_checked"
        }

    current_signature = (
        make_ranking_signature(
            rankings
        )
    )

    previous_signature = (
        state.get(
            "last_sent_signature"
        )
    )

    # --------------------------------------
    # RANKING DID NOT CHANGE
    # --------------------------------------

    if (
        previous_signature
        == current_signature
    ):

        state[
            "last_checked_candle"
        ] = candle_time

        save_ranking_state(
            state
        )

        print(
            "➖ Ranking unchanged"
        )

        return {
            "sent": False,
            "reason": "unchanged"
        }

    # --------------------------------------
    # RANKING CHANGED
    # --------------------------------------

    message = (
        format_ranking_message(
            rankings
        )
    )

    # If Telegram fails,
    # do NOT update state.
    # Next workflow run can retry.
    send_function(
        message
    )

    state[
        "last_checked_candle"
    ] = candle_time

    state[
        "last_sent_signature"
    ] = current_signature

    state[
        "last_sent_at"
    ] = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    save_ranking_state(
        state
    )

    print(
        "📲 Ranking alert sent"
    )

    return {
        "sent": True,
        "reason": "ranking_changed",
        "message": message
    }
