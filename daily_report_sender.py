from datetime import datetime
from zoneinfo import ZoneInfo

from daily_report_live import (
    build_live_daily_report
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


def send_daily_report():

    report_date = (
        datetime.now(
            IST
        )
        .date()
        .isoformat()
    )

    alert_id = make_alert_id(
        "DAILY_REPORT",
        "GLOBAL",
        "DAILY",
        report_date,
        "IST"
    )

    if not can_send_alert(
        alert_id
    ):

        print(
            "🚫 Daily Report "
            "already sent today"
        )

        return False

    print(
        f"📅 Building Daily Report | "
        f"{report_date}"
    )

    message = (
        build_live_daily_report(
            report_date
        )
    )

    send_telegram_message(
        message
    )

    mark_alert_sent(
        alert_id,
        {
            "report_date":
                report_date,
            "timezone":
                "Asia/Kolkata"
        }
    )

    print(
        "✅ Daily Report sent "
        "to Telegram"
    )

    return True


if __name__ == "__main__":

    send_daily_report()
