from confluence import (
    build_confluence,
    format_confluence_alert,
)


def test_bullish():

    liquidity = {
        "type": "BULLISH LIQUIDITY GRAB",
        "level": "PDL",
    }

    crt = {
        "type": "BULLISH CRT",
    }

    fvg = {
        "type": "BULLISH FVG",
        "bottom": 1.10000,
        "top": 1.10100,
    }

    ob = {
        "type": "BULLISH OB",
        "level": 1.09950,
    }

    setup = build_confluence(
        symbol="EUR/USD",
        timeframe="H1",
        liquidity_alert=liquidity,
        crt_alert=crt,
        fvg=fvg,
        ob=ob,
        ob_first_tap=True,
    )

    assert setup is not None
    assert setup["trade"] == "BUY"

    print("✅ Bullish confluence passed")
    print()
    print(
        format_confluence_alert(
            setup
        )
    )


def test_bearish():

    liquidity = {
        "type": "BEARISH LIQUIDITY GRAB",
        "level": "PDH",
    }

    crt = {
        "type": "BEARISH CRT",
    }

    fvg = {
        "type": "BEARISH FVG",
        "bottom": 1.10500,
        "top": 1.10600,
    }

    ob = {
        "type": "BEARISH OB",
        "level": 1.10650,
    }

    setup = build_confluence(
        symbol="EUR/USD",
        timeframe="H1",
        liquidity_alert=liquidity,
        crt_alert=crt,
        fvg=fvg,
        ob=ob,
        ob_first_tap=True,
    )

    assert setup is not None
    assert setup["trade"] == "SELL"

    print("✅ Bearish confluence passed")


def test_mixed_direction():

    liquidity = {
        "type": "BULLISH LIQUIDITY GRAB",
        "level": "PDL",
    }

    crt = {
        "type": "BEARISH CRT",
    }

    fvg = {
        "type": "BULLISH FVG",
        "bottom": 1.10000,
        "top": 1.10100,
    }

    ob = {
        "type": "BULLISH OB",
        "level": 1.09950,
    }

    setup = build_confluence(
        symbol="EUR/USD",
        timeframe="H1",
        liquidity_alert=liquidity,
        crt_alert=crt,
        fvg=fvg,
        ob=ob,
        ob_first_tap=True,
    )

    assert setup is None

    print(
        "✅ Mixed direction correctly blocked"
    )


def test_without_ob_tap():

    liquidity = {
        "type": "BULLISH LIQUIDITY GRAB",
        "level": "PDL",
    }

    crt = {
        "type": "BULLISH CRT",
    }

    fvg = {
        "type": "BULLISH FVG",
        "bottom": 1.10000,
        "top": 1.10100,
    }

    ob = {
        "type": "BULLISH OB",
        "level": 1.09950,
    }

    setup = build_confluence(
        symbol="EUR/USD",
        timeframe="H1",
        liquidity_alert=liquidity,
        crt_alert=crt,
        fvg=fvg,
        ob=ob,
        ob_first_tap=False,
    )

    assert setup is None

    print(
        "✅ Setup without OB tap correctly blocked"
    )


if __name__ == "__main__":

    test_bullish()
    test_bearish()
    test_mixed_direction()
    test_without_ob_tap()

    print()
    print(
        "🔥 ALL CONFLUENCE TESTS PASSED"
    )
