from pathlib import Path
from uuid import uuid4

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pandas as pd


CHART_DIR = Path("charts")


def _safe_float(value):

    try:
        return float(value)

    except (TypeError, ValueError):
        return None


def _get_liquidity_price(
    liquidity
):

    if not isinstance(
        liquidity,
        dict
    ):
        return None

    for key in [
        "price",
        "level_price",
        "value",
        "liquidity_price"
    ]:

        price = _safe_float(
            liquidity.get(key)
        )

        if price is not None:
            return price

    level = _safe_float(
        liquidity.get("level")
    )

    return level


def _find_candle_index(
    df,
    event_time
):

    if not event_time:
        return None

    try:

        target = pd.to_datetime(
            event_time,
            utc=True
        )

    except Exception:
        return None

    times = pd.to_datetime(
        df["datetime"],
        utc=True
    )

    differences = (
        times - target
    ).abs()

    if differences.empty:
        return None

    return int(
        differences.argmin()
    )


def create_mini_chart(
    df,
    symbol,
    timeframe,
    ob=None,
    fvg=None,
    liquidity=None,
    crt=None,
    candle_count=50
):

    if df is None or df.empty:

        raise ValueError(
            "No candle data available"
        )

    required_columns = {
        "datetime",
        "open",
        "high",
        "low",
        "close"
    }

    missing = (
        required_columns
        - set(df.columns)
    )

    if missing:

        raise ValueError(
            "Missing candle columns: "
            + ", ".join(
                sorted(missing)
            )
        )

    candles = (
        df.tail(
            candle_count
        )
        .copy()
        .reset_index(
            drop=True
        )
    )

    candles[
        "datetime"
    ] = pd.to_datetime(
        candles["datetime"],
        utc=True
    )

    for column in [
        "open",
        "high",
        "low",
        "close"
    ]:

        candles[
            column
        ] = pd.to_numeric(
            candles[column],
            errors="coerce"
        )

    candles = (
        candles.dropna(
            subset=[
                "open",
                "high",
                "low",
                "close"
            ]
        )
        .reset_index(
            drop=True
        )
    )

    if candles.empty:

        raise ValueError(
            "No valid candle data"
        )

    CHART_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = (
        f"{symbol.replace('/', '')}_"
        f"{timeframe}_"
        f"{uuid4().hex[:10]}.png"
    )

    output_path = (
        CHART_DIR
        / filename
    )

    fig, ax = plt.subplots(
        figsize=(10, 5.6),
        dpi=120
    )

    candle_width = 0.62

    for index, candle in (
        candles.iterrows()
    ):

        open_price = float(
            candle["open"]
        )

        high_price = float(
            candle["high"]
        )

        low_price = float(
            candle["low"]
        )

        close_price = float(
            candle["close"]
        )

        bullish = (
            close_price
            >= open_price
        )

        candle_color = (
            "#22c55e"
            if bullish
            else "#ef4444"
        )

        ax.vlines(
            index,
            low_price,
            high_price,
            color=candle_color,
            linewidth=1.0
        )

        body_bottom = min(
            open_price,
            close_price
        )

        body_height = abs(
            close_price
            - open_price
        )

        if body_height == 0:

            body_height = (
                max(
                    high_price
                    - low_price,
                    0.00001
                )
                * 0.02
            )

        rectangle = Rectangle(
            (
                index
                - candle_width / 2,
                body_bottom
            ),
            candle_width,
            body_height,
            facecolor=candle_color,
            edgecolor=candle_color,
            linewidth=0.8
        )

        ax.add_patch(
            rectangle
        )

    # ======================================
    # ORDER BLOCK
    # ======================================

    if isinstance(
        ob,
        dict
    ):

        ob_level = _safe_float(
            ob.get(
                "level",
                ob.get(
                    "midpoint"
                )
            )
        )

        if ob_level is not None:

            ax.axhline(
                ob_level,
                linestyle="--",
                linewidth=1.3,
                alpha=0.9,
                label="OB"
            )

    # ======================================
    # FVG
    # ======================================

    if isinstance(
        fvg,
        dict
    ):

        bottom = _safe_float(
            fvg.get("bottom")
        )

        top = _safe_float(
            fvg.get("top")
        )

        if (
            bottom is not None
            and top is not None
        ):

            low = min(
                bottom,
                top
            )

            high = max(
                bottom,
                top
            )

            ax.axhspan(
                low,
                high,
                alpha=0.12,
                label="FVG"
            )

    # ======================================
    # LIQUIDITY LEVEL
    # ======================================

    liquidity_price = (
        _get_liquidity_price(
            liquidity
        )
    )

    if liquidity_price is not None:

        ax.axhline(
            liquidity_price,
            linestyle=":",
            linewidth=1.2,
            alpha=0.9,
            label="Liquidity"
        )

    # ======================================
    # CRT CONFIRMATION
    # ======================================

    if isinstance(
        crt,
        dict
    ):

        crt_time = crt.get(
            "second_candle_time"
        )

        crt_index = (
            _find_candle_index(
                candles,
                crt_time
            )
        )

        if crt_index is not None:

            ax.axvline(
                crt_index,
                linestyle="--",
                linewidth=1.0,
                alpha=0.7,
                label="CRT"
            )

    # ======================================
    # LAST PRICE
    # ======================================

    last_close = float(
        candles.iloc[-1][
            "close"
        ]
    )

    ax.axhline(
        last_close,
        linewidth=0.8,
        alpha=0.35
    )

    # ======================================
    # X AXIS
    # ======================================

    step = max(
        1,
        len(candles) // 6
    )

    tick_positions = list(
        range(
            0,
            len(candles),
            step
        )
    )

    tick_labels = []

    for position in tick_positions:

        dt = candles.iloc[
            position
        ]["datetime"]

        tick_labels.append(
            dt.strftime(
                "%d %b\n%H:%M"
            )
        )

    ax.set_xticks(
        tick_positions
    )

    ax.set_xticklabels(
        tick_labels,
        fontsize=8
    )

    ax.set_title(
        f"{symbol} • {timeframe}",
        fontsize=13,
        fontweight="bold"
    )

    ax.set_ylabel(
        "Price"
    )

    ax.grid(
        True,
        alpha=0.15
    )

    handles, labels = (
        ax.get_legend_handles_labels()
    )

    if handles:

        unique = {}

        for handle, label in zip(
            handles,
            labels
        ):

            if label not in unique:
                unique[label] = handle

        ax.legend(
            unique.values(),
            unique.keys(),
            loc="best",
            fontsize=8
        )

    fig.tight_layout()

    fig.savefig(
        output_path,
        bbox_inches="tight"
    )

    plt.close(
        fig
    )

    return str(
        output_path
    )


def delete_chart(
    chart_path
):

    if not chart_path:
        return

    try:

        path = Path(
            chart_path
        )

        if path.exists():
            path.unlink()

    except Exception:
        pass
