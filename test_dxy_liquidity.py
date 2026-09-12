from dxy_data import get_dxy_candles, prepare_dxy_candles
from liquidity import detect_liquidity_grab


print("\n" + "=" * 60)
print("DXY LIQUIDITY TEST")
print("=" * 60)


try:

    data = get_dxy_candles(
        interval="1h",
        limit=500
    )

    df = prepare_dxy_candles(data)

    if df.empty:

        print("❌ No DXY data")
    
    else:

        print("✅ DXY candles received")
        print()

        alerts = detect_liquidity_grab(df)

        if alerts:

            for alert in alerts:

                print("\n🚨 LIQUIDITY GRAB")

                print(
                    f"Type: {alert['type']}"
                )

                print(
                    f"Level: {alert['level']}"
                )

                print(
                    f"Liquidity: "
                    f"{alert['liquidity']:.3f}"
                )

                print(
                    f"Grab Price: "
                    f"{alert['price']:.3f}"
                )

                print(
                    f"Time: {alert['time']}"
                )

        else:

            print(
                "No Previous Day liquidity grab detected."
            )


except Exception as e:

    print("❌ DXY liquidity test failed")
    print(str(e))
