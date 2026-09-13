from pathlib import Path

import pandas as pd

from chart_image import (
    create_mini_chart,
    delete_chart
)


def make_test_data():

    rows = []

    base_price = 1.1000

    for i in range(60):

        open_price = (
            base_price
            + i * 0.0001
        )

        if i % 2 == 0:

            close_price = (
                open_price
                + 0.00025
            )

        else:

            close_price = (
                open_price
                - 0.00020
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

            "open":
                open_price,

            "high":
                max(
                    open_price,
                    close_price
                )
                + 0.00030,

            "low":
                min(
                    open_price,
                    close_price
                )
                - 0.00030,

            "close":
                close_price
        })

    return pd.DataFrame(
        rows
    )


def main():

    df = make_test_data()

    ob = {
        "type": "BULLISH OB",
        "level": 1.10450
    }

    fvg = {
        "type": "BULLISH FVG",
        "bottom": 1.10500,
        "top": 1.10560
    }

    liquidity = {
        "type":
            "BULLISH LIQUIDITY GRAB",
        "level_price":
            1.10350
    }

    crt = {
        "type": "BULLISH CRT",
        "second_candle_time":
            "2026-09-16T06:00:00+00:00"
    }

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

    path = Path(
        chart_path
    )

    assert path.exists()

    assert (
        path.suffix.lower()
        == ".png"
    )

    assert (
        path.stat().st_size
        > 1000
    )

    print(
        "✅ Mini chart created"
    )

    print(
        f"📈 Chart: {chart_path}"
    )

    print(
        f"📦 Size: "
        f"{path.stat().st_size} bytes"
    )

    delete_chart(
        chart_path
    )

    assert (
        not path.exists()
    )

    print(
        "✅ Temporary chart cleanup passed"
    )

    print()
    print(
        "📊 ALL CHART IMAGE TESTS PASSED"
    )


if __name__ == "__main__":
    main()
