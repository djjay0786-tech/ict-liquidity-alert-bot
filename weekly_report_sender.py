from datetime import datetime
from zoneinfo import ZoneInfo

from weekly_report import (
    get_week_range
)

from weekly_report_live import (
    build_live_weekly_report
)

from telegram_alert import (
    send_telegram_message
)

from alert_state import (
    make_alert_id,
    can_send_alert,
    mark_alert_sent
)


IST = ZoneInfo(
    "Asia/Kolkata"
)


def send_weekly_report():

    today = (
        datetime.now(
            IST
        )
        .date()
    )

    week_start, week_end = (
        get_week_range(
            today
        )
    )

    alert_id = make_alert_id(
        "WEEKLY_REPORT",
        "GLOBAL",
        "WEEKLY",
        week_end.isoformat(),
        week_start.isoformat()
    )

    if not can_send_alert(
        alert_id
    ):

        print(
            "🚫 Weekly Report "
            "already sent"
        )

        return False

    print(
        "📊 Building Weekly Report | "
        f"{week_start} → {week_end}"
    )

    message = (
        build_live_weekly_report(
            reference_date=today
        )
    )

    send_telegram_message(
        message
    )

    mark_alert_sent(
        alert_id,
        {
            "week_start":
                week_start.isoformat(),

            "week_end":
                week_end.isoformat(),

            "timezone":
                "Asia/Kolkata"
        }
    )

    print(
        "✅ Weekly Report sent "
        "to Telegram"
    )

    return True


if __name__ == "__main__":

    send_weekly_report()
