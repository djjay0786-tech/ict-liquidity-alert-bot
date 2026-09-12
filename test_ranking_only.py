from ranking import (
    get_alignment_status,
    rank_instruments,
    format_ranking_message
)


def test_high_confluence():

    liquidity = {
        "type": "BULLISH LIQUIDITY GRAB"
    }

    crt = {
        "type": "BULLISH CRT"
    }

    fvg = {
        "type": "BULLISH FVG"
    }

    ob = {
        "type": "BULLISH OB"
    }

    result = get_alignment_status(
        liquidity_alert=liquidity,
        crt_alert=crt,
        fvg=fvg,
        ob=ob,
        ob_first_tap=True
    )

    assert (
        result["status"]
        == "HIGH CONFLUENCE"
    )

    assert (
        result["direction"]
        == "BULLISH"
    )

    print(
        "✅ High confluence test passed"
    )


def test_watch():

    liquidity = {
        "type": "BEARISH LIQUIDITY GRAB"
    }

    crt = {
        "type": "BEARISH CRT"
    }

    fvg = {
        "type": "BEARISH FVG"
    }

    ob = {
        "type": "BEARISH OB"
    }

    result = get_alignment_status(
        liquidity_alert=liquidity,
        crt_alert=crt,
        fvg=fvg,
        ob=ob,
        ob_first_tap=False
    )

    assert (
        result["status"]
        == "WATCH"
    )

    assert (
        result["direction"]
        == "BEARISH"
    )

    print(
        "✅ Watch test passed"
    )


def test_no_setup():

    liquidity = {
        "type": "BULLISH LIQUIDITY GRAB"
    }

    crt = {
        "type": "BEARISH CRT"
    }

    result = get_alignment_status(
        liquidity_alert=liquidity,
        crt_alert=crt
    )

    assert (
        result["status"]
        == "NO SETUP"
    )

    print(
        "✅ No setup test passed"
    )


def test_ranking():

    instruments = {

        "EUR/USD": {
            "liquidity": {
                "type":
                    "BULLISH LIQUIDITY GRAB"
            },
            "crt": {
                "type":
                    "BULLISH CRT"
            },
            "fvg": {
                "type":
                    "BULLISH FVG"
            },
            "ob": {
                "type":
                    "BULLISH OB"
            },
            "ob_first_tap": True
        },

        "GBP/USD": {
            "liquidity": {
                "type":
                    "BEARISH LIQUIDITY GRAB"
            },
            "crt": {
                "type":
                    "BEARISH CRT"
            },
            "fvg": {
                "type":
                    "BEARISH FVG"
            },
            "ob": {
                "type":
                    "BEARISH OB"
            },
            "ob_first_tap": False
        },

        "DXY": {
            "liquidity": None,
            "crt": None,
            "fvg": None,
            "ob": None,
            "ob_first_tap": False
        }
    }

    rankings = rank_instruments(
        instruments
    )

    assert (
        rankings[0]["symbol"]
        == "EUR/USD"
    )

    assert (
        rankings[0]["status"]
        == "HIGH CONFLUENCE"
    )

    assert (
        rankings[1]["symbol"]
        == "GBP/USD"
    )

    assert (
        rankings[1]["status"]
        == "WATCH"
    )

    assert (
        rankings[2]["symbol"]
        == "DXY"
    )

    assert (
        rankings[2]["status"]
        == "NO SETUP"
    )

    print(
        "✅ Ranking order test passed"
    )

    print()

    print(
        format_ranking_message(
            rankings
        )
    )


if __name__ == "__main__":

    test_high_confluence()

    test_watch()

    test_no_setup()

    test_ranking()

    print()

    print(
        "🏆 ALL RANKING TESTS PASSED"
    )
