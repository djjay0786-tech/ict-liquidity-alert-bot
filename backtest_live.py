from market_data import get_candles

from dxy_data import (
    get_dxy_candles,
    prepare_dxy_candles
)

from liquidity import (
    prepare_candles
)

from backtest_engine import (
    backtest_symbol,
    summarize_backtest,
    format_backtest_summary
)


SYMBOLS = [
    "EUR/USD",
    "GBP/USD",
    "DXY"
]


def get_historical_h1(
    symbol
):

    if symbol == "DXY":

        data = get_dxy_candles(
            interval="1h",
            limit=200
        )

        return prepare_dxy_candles(
            data
        )

    data = get_candles(
        symbol,
        interval="1h",
        outputsize=200
    )

    if "values" not in data:

        raise RuntimeError(
            f"No candle data for {symbol}"
        )

    return prepare_candles(
        data["values"]
    )


def run_backtest():

    print(
        "\n"
        + "=" * 60
    )

    print(
        "🧪 ICT HISTORICAL BACKTEST"
    )

    print(
        "=" * 60
    )

    all_summaries = []

    for symbol in SYMBOLS:

        print(
            f"\n📊 Loading {symbol}..."
        )

        try:

            df = get_historical_h1(
                symbol
            )

            if (
                df is None
                or df.empty
            ):

                print(
                    f"⚠️ No data | {symbol}"
                )

                continue

            print(
                f"✅ {len(df)} "
                f"H1 candles loaded"
            )

            result = backtest_symbol(
                df=df,
                symbol=symbol,
                timeframe="H1",
                minimum_candles=60,
                forward_candles=6
            )

            summary = summarize_backtest(
                result
            )

            all_summaries.append(
                summary
            )

            print()
            print(
                format_backtest_summary(
                    summary
                )
            )

            if result["setups"]:

                print(
                    "\n📋 Recent setups:"
                )

                for setup in (
                    result["setups"][-5:]
                ):

                    print(
                        "• "
                        f"{setup['time']} | "
                        f"{setup['trade']} | "
                        f"Best "
                        f"{setup['best_move']:.1f} "
                        f"{setup['unit']} | "
                        f"Adverse "
                        f"{setup['worst_move']:.1f} "
                        f"{setup['unit']}"
                    )

        except Exception as e:

            print(
                f"⚠️ Backtest error | "
                f"{symbol}: {e}"
            )

    print(
        "\n"
        + "=" * 60
    )

    print(
        "📊 BACKTEST OVERVIEW"
    )

    print(
        "=" * 60
    )

    for summary in all_summaries:

        print(
            f"{summary['symbol']} | "
            f"Setups: "
            f"{summary['setup_count']} | "
            f"Avg favorable: "
            f"{summary['average_best_move']:.1f} "
            f"{summary['unit']} | "
            f"Avg adverse: "
            f"{summary['average_worst_move']:.1f} "
            f"{summary['unit']}"
        )

    print()
    print(
        "✅ HISTORICAL BACKTEST COMPLETED"
    )


if __name__ == "__main__":

    run_backtest()
