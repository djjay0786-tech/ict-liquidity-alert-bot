from dxy_data import get_dxy_candles, prepare_dxy_candles


print("\n" + "=" * 60)
print("DXY MARKET DATA TEST")
print("=" * 60)


try:

    data = get_dxy_candles(
        interval="1h",
        limit=20
    )

    df = prepare_dxy_candles(data)

    if df.empty:
        print("❌ No DXY data received")

    else:

        print("✅ DXY data received")
        print()

        print(
            df[
                [
                    "datetime",
                    "open",
                    "high",
                    "low",
                    "close"
                ]
            ].tail(10)
        )


except Exception as e:

    print("❌ DXY test failed")
    print(str(e))
