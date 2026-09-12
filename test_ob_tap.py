from market_data import get_candles
from order_block import prepare_candles
from ob_fvg import select_ob_near_fvg
from ob_tap import detect_first_tap, create_tap_alert


symbols = [
    "EUR/USD",
    "GBP/USD"
]

timeframes = [
    "1h",
    "4h"
]


for symbol in symbols:
    for timeframe in timeframes:

        print("\n" + "=" * 60)
        print(
            f"OB FIRST TAP TEST: "
            f"{symbol} | {timeframe}"
        )
        print("=" * 60)

        try:

            data = get_candles(
                symbol,
                interval=timeframe,
                outputsize=200
            )

            if "values" not in data:
                print("❌ No market data")
                continue

            df = prepare_candles(
                data["values"]
            )

            setup = select_ob_near_fvg(df)

            if setup is None:
                print(
                    "No valid OB + FVG setup."
                )
                continue

            ob = setup["ob"]

            tapped = False

            # Check candles after OB creation
            for i in range(len(df)):

                candle = df.iloc[i]

                if str(candle["datetime"]) <= ob["time"]:
                    continue

                if detect_first_tap(
                    candle,
                    ob
                ):

                    print(
                        "\n🚨 FIRST TAP DETECTED\n"
                    )

                    print(
                        create_tap_alert(
                            symbol,
                            timeframe,
                            ob,
                            candle
                        )
                    )

                    tapped = True
                    break

            if not tapped:
                print(
                    "No first tap detected."
                )

        except Exception as e:

            print(
                f"⚠️ Skipped "
                f"{symbol} | {timeframe}"
            )

            print(
                f"Reason: {e}"
            )
