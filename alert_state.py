import json
from pathlib import Path


STATE_FILE = Path("alert_state.json")


def load_alert_state():

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


def save_alert_state(state):

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


def make_alert_id(
    alert_type,
    symbol="GLOBAL",
    timeframe="GLOBAL",
    event_time="",
    extra=""
):

    return (
        f"{alert_type}|"
        f"{symbol}|"
        f"{timeframe}|"
        f"{event_time}|"
        f"{extra}"
    )


def was_alert_sent(alert_id):

    state = load_alert_state()

    return alert_id in state


def mark_alert_sent(
    alert_id,
    details=None
):

    state = load_alert_state()

    state[alert_id] = {
        "sent": True,
        "details": details
    }

    save_alert_state(state)


def can_send_alert(alert_id):

    return not was_alert_sent(
        alert_id
    )


def register_alert(
    alert_id,
    details=None
):

    if was_alert_sent(alert_id):

        return False

    mark_alert_sent(
        alert_id,
        details
    )

    return True
