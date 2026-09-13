import pandas as pd

from chart_image import (
    create_mini_chart,
    delete_chart
)

from telegram_chart_alert import (
    send_chart_alert
)


def make_test_data():

    rows = []

    base_price = 1.1000

    for i in range(50):

        open_price = (
            base_price
            + i * 0.00008
        )

        if i % 3 == 0:
            close_price = (
                open_price
                - 0.00025
            )
        else:
            close_price = (
                open_price
                + 0.00020
            )

        rows.append({
            "datetime": (
                pd.Timestamp(
                    "2026-09-14 00:00:00",
                    tz="UTC"
                )
                + pd.Timedelta(
                    hours=i
                )
            ),

            "open": open_price,

            "high": (
                max(
                    open_price,
                    close_price
                )
                + 0.00030
            ),

            "low": (
                min(
                    open_price,
                    close_price
                )
                - 0.00030
            ),

            "close": close_price
        })

    return pd.DataFrame(
        rows
    )


def main():

    df = make_test_data()

    ob = {
        "type": "BULLISH OB",
        "level": 1.10350
    }

    fvg = {
        "type": "BULLISH FVG",
        "bottom": 1.10380,
        "top": 1.10440
    }

    liquidity = {
        "type":
            "BULLISH LIQUIDITY GRAB",
        "level_price":
            1.10250
    }

    crt = {
        "type":
            "BULLISH CRT",

        "second_candle_time":
            "2026-09-15T12:00:00+00:00"
    }

    chart_path = None

    try:

        chart_path = (
            create_mini_chart(
                df=df,
                symbol="EUR/USD",
                timeframe="H1",
                ob=ob,
                fvg=fvg,
                liquidity=liquidity,
                crt=crt,
                candle_count=50
            )
        )

        message = (
            "🧪 ICT CHART TEST\n\n"
            "🟢 BUY TEST\n"
            "Symbol: EUR/USD\n"
            "Timeframe: H1\n\n"
            "✅ Liquidity Grab\n"
            "✅ CRT\n"
            "✅ FVG\n"
            "✅ Order Block\n\n"
            "This is a chart delivery test."
        )

        send_chart_alert(
            chart_path=chart_path,
            message=message,
            symbol="EUR/USD",
            timeframe="H1"
        )

        print(
            "✅ TELEGRAM CHART "
            "TEST PASSED"
        )

    finally:

        if chart_path:

            delete_chart(
                chart_path
            )


if __name__ == "__main__":
    main()
