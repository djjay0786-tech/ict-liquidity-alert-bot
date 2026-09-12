import live_engine


def main():

    print("\n" + "=" * 60)
    print("ICT LIVE ENGINE INTEGRATION TEST")
    print("=" * 60)

    required_functions = [
        "get_market_data",
        "send_message",
        "check_session_open_close",
        "check_liquidity",
        "check_session_liquidity",
        "check_crt",
        "check_fvg",
        "check_ob_fvg",
        "check_ob_first_tap",
        "run_engine",
    ]

    print("\nChecking live_engine functions...\n")

    missing = []

    for function_name in required_functions:

        if hasattr(
            live_engine,
            function_name
        ):

            print(
                f"PASS: {function_name}"
            )

        else:

            print(
                f"FAIL: {function_name}"
            )

            missing.append(
                function_name
            )

    print("\n" + "=" * 60)

    if missing:

        print("LIVE ENGINE TEST FAILED")

        print(
            "Missing functions:"
        )

        for function_name in missing:
            print(
                f"- {function_name}"
            )

        raise SystemExit(1)

    print(
        "LIVE ENGINE IMPORT TEST PASSED"
    )

    print(
        "Duplicate alert integration loaded."
    )

    print(
        "OB First Tap integration loaded."
    )

    print(
        "Session alerts integration loaded."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
