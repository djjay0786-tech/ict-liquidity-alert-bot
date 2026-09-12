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


def get_ob_key(
    symbol,
    timeframe
):

    return (
        f"{symbol}_"
        f"{timeframe}"
    )


def register_current_ob(
    symbol,
    timeframe,
    ob
):

    state = load_state()

    key = get_ob_key(
        symbol,
        timeframe
    )

    current = state.get(key)

    new_ob_id = (
        f"{ob['type']}_"
        f"{ob['time']}"
    )

    # New OB → replace old OB
    if current is None or current.get(
        "ob_id"
    ) != new_ob_id:

        state[key] = {
            "ob_id": new_ob_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "type": ob["type"],
            "time": ob["time"],
            "high": ob["high"],
            "low": ob["low"],
            "tapped": False
        }

        save_state(state)

    return key


def is_already_tapped(
    symbol,
    timeframe
):

    state = load_state()

    key = get_ob_key(
        symbol,
        timeframe
    )

    if key not in state:
        return False

    return state[key].get(
        "tapped",
        False
    )


def mark_tapped(
    symbol,
    timeframe
):

    state = load_state()

    key = get_ob_key(
        symbol,
        timeframe
    )

    if key not in state:
        return

    state[key]["tapped"] = True

    save_state(state)


def can_alert_first_tap(
    symbol,
    timeframe,
    ob
):

    register_current_ob(
        symbol,
        timeframe,
        ob
    )

    return not is_already_tapped(
        symbol,
        timeframe
    )


def confirm_first_tap(
    symbol,
    timeframe
):

    mark_tapped(
        symbol,
        timeframe
    )
