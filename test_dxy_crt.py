from dxy_data import get_dxy_candles, prepare_dxy_candles
from crt import detect_crt, format_crt_alert
import time

timeframes = [
    "1h",
    "4h"
]

for timeframe in timeframes:

    print("\n" + "=" * 60)
    print(f"DXY CRT TEST | {timeframe}")
    print("=" * 60)

    try:
        data = get_dxy_candles(
            interval=timeframe,
            limit=100
        )

        df = prepare_dxy_candles(data)

        if df.empty:
            print("❌ No DXY data")
            continue

        alerts = detect_crt(df)

        if alerts:
            for alert in alerts:
                print(
                    format_crt_alert(
                        "DXY",
                        timeframe,
                        alert
                    )
                )
        else:
            print("No CRT setup detected.")

    except Exception as e:
        print(f"⚠️ DXY {timeframe} skipped")
        print(f"Reason: {e}")

    time.sleep(3)
