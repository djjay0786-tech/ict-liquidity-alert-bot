import json
from pathlib import Path


STATE_FILE = Path("ob_state.json")


def load_state():
    if not STATE_FILE.exists():
        return {}

    try:
        with open(
            STATE_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except Exception:
        return {}


def save_state(state):
    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            state,
            file,
            indent=2
        )


def get_ob_id(symbol, timeframe, ob):
    return (
        f"{symbol}_"
        f"{timeframe}_"
        f"{ob['type']}_"
        f"{ob['time']}"
    )


def register_ob(symbol, timeframe, ob):

    state = load_state()

    ob_id = get_ob_id(
        symbol,
        timeframe,
        ob
    )

    # New OB
    if ob_id not in state:

        state[ob_id] = {
            "symbol": symbol,
            "timeframe": timeframe,
            "type": ob["type"],
            "time": ob["time"],
            "high": ob["high"],
            "low": ob["low"],
            "tapped": False
        }

        save_state(state)

    return ob_id


def is_already_tapped(ob_id):

    state = load_state()

    if ob_id not in state:
        return False

    return state[ob_id].get(
        "tapped",
        False
    )


def mark_tapped(ob_id):

    state = load_state()

    if ob_id not in state:
        return

    state[ob_id]["tapped"] = True

    save_state(state)


def can_alert_first_tap(
    symbol,
    timeframe,
    ob
):

    ob_id = register_ob(
        symbol,
        timeframe,
        ob
    )

    return not is_already_tapped(
        ob_id
    )


def confirm_first_tap(ob_id):

    mark_tapped(ob_id)
