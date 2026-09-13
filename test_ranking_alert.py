from pathlib import Path

import ranking_alert


TEST_STATE_FILE = Path(
    "ranking_state_test.json"
)

ranking_alert.STATE_FILE = (
    TEST_STATE_FILE
)


sent_messages = []


def fake_send(
    message
):

    sent_messages.append(
        message
    )


def cleanup():

    if TEST_STATE_FILE.exists():
        TEST_STATE_FILE.unlink()


def get_rankings():

    return [
        {
            "rank": 1,
            "symbol": "EUR/USD",
            "status": "HIGH CONFLUENCE",
            "direction": "BULLISH",
            "priority": 3
        },
        {
            "rank": 2,
            "symbol": "GBP/USD",
            "status": "WATCH",
            "direction": "BEARISH",
            "priority": 2
        },
        {
            "rank": 3,
            "symbol": "DXY",
            "status": "NO SETUP",
            "direction": None,
            "priority": 0
        }
    ]


def test_first_alert():

    rankings = get_rankings()

    result = (
        ranking_alert
        .process_ranking_alert(
            rankings=rankings,
            candle_time=(
                "2026-09-13 10:00:00"
            ),
            send_function=fake_send
        )
    )

    assert (
        result["sent"]
        is True
    )

    assert (
        result["reason"]
        == "ranking_changed"
    )

    assert len(
        sent_messages
    ) == 1

    print(
        "✅ First ranking alert passed"
    )


def test_same_candle_blocked():

    rankings = get_rankings()

    result = (
        ranking_alert
        .process_ranking_alert(
            rankings=rankings,
            candle_time=(
                "2026-09-13 10:00:00"
            ),
            send_function=fake_send
        )
    )

    assert (
        result["sent"]
        is False
    )

    assert (
        result["reason"]
        == "already_checked"
    )

    assert len(
        sent_messages
    ) == 1

    print(
        "✅ Same H1 candle blocked"
    )


def test_unchanged_ranking():

    rankings = get_rankings()

    result = (
        ranking_alert
        .process_ranking_alert(
            rankings=rankings,
            candle_time=(
                "2026-09-13 11:00:00"
            ),
            send_function=fake_send
        )
    )

    assert (
        result["sent"]
        is False
    )

    assert (
        result["reason"]
        == "unchanged"
    )

    assert len(
        sent_messages
    ) == 1

    print(
        "✅ Unchanged ranking blocked"
    )


def test_changed_ranking():

    rankings = get_rankings()

    rankings[0] = {
        "rank": 1,
        "symbol": "GBP/USD",
        "status": "HIGH CONFLUENCE",
        "direction": "BEARISH",
        "priority": 3
    }

    rankings[1] = {
        "rank": 2,
        "symbol": "EUR/USD",
        "status": "WATCH",
        "direction": "BULLISH",
        "priority": 2
    }

    result = (
        ranking_alert
        .process_ranking_alert(
            rankings=rankings,
            candle_time=(
                "2026-09-13 12:00:00"
            ),
            send_function=fake_send
        )
    )

    assert (
        result["sent"]
        is True
    )

    assert (
        result["reason"]
        == "ranking_changed"
    )

    assert len(
        sent_messages
    ) == 2

    print(
        "✅ Changed ranking alert passed"
    )


if __name__ == "__main__":

    cleanup()

    try:

        test_first_alert()

        test_same_candle_blocked()

        test_unchanged_ranking()

        test_changed_ranking()

        print()

        print(
            "🏆 ALL RANKING ALERT "
            "TESTS PASSED"
        )

    finally:

        cleanup()
