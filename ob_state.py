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


# --------------------------------
# OLD / COMPATIBILITY OB ID
# --------------------------------

def get_ob_id(symbol, timeframe, ob):

    return (
        f"{symbol}_"
        f"{timeframe}_"
        f"{ob['type']}_"
        f"{ob['time']}"
    )


# --------------------------------
# SYMBOL + TIMEFRAME KEY
# --------------------------------

def get_ob_key(symbol, timeframe):

    return (
        f"{symbol}_"
        f"{timeframe}"
    )


# --------------------------------
# REGISTER CURRENT OB
# --------------------------------

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

    new_ob_id = get_ob_id(
        symbol,
        timeframe,
        ob
    )

    current = state.get(key)

    # New OB → replace old OB
    if (
        current is None
        or current.get("ob_id") != new_ob_id
    ):

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


# --------------------------------
# FIND STATE BY OLD OB ID
# --------------------------------

def _find_key_by_ob_id(ob_id):

    state = load_state()

    for key, value in state.items():

        if value.get("ob_id") == ob_id:
            return key

    return None


# --------------------------------
# CHECK TAPPED
# --------------------------------

def is_already_tapped(*args):

    state = load_state()

    # New format:
    # is_already_tapped(symbol, timeframe)
    if len(args) == 2:

        symbol = args[0]
        timeframe = args[1]

        key = get_ob_key(
            symbol,
            timeframe
        )

    # Old format:
    # is_already_tapped(ob_id)
    elif len(args) == 1:

        ob_id = args[0]

        key = _find_key_by_ob_id(
            ob_id
        )

    else:
        return False

    if key not in state:
        return False

    return state[key].get(
        "tapped",
        False
    )


# --------------------------------
# MARK TAPPED
# --------------------------------

def mark_tapped(*args):

    state = load_state()

    # New format
    if len(args) == 2:

        symbol = args[0]
        timeframe = args[1]

        key = get_ob_key(
            symbol,
            timeframe
        )

    # Old format
    elif len(args) == 1:

        ob_id = args[0]

        key = _find_key_by_ob_id(
            ob_id
        )

    else:
        return

    if key not in state:
        return

    state[key]["tapped"] = True

    save_state(state)


# --------------------------------
# FIRST TAP CHECK
# --------------------------------

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


# --------------------------------
# CONFIRM FIRST TAP
# --------------------------------

def confirm_first_tap(*args):

    # Supports both:
    #
    # confirm_first_tap(ob_id)
    #
    # AND
    #
    # confirm_first_tap(symbol, timeframe)

    mark_tapped(*args)
