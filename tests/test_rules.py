"""Rule checks on small hand-built price series."""

import numpy as np
import pandas as pd

from deeter.config import Config
from deeter.outcomes import add_outcomes
from deeter.rules import find_setups

IGNITION = 100  # session index of the planted ignition day


def make_prices(ignition_move: float, consol_moves: list[float],
                friday_move: float = 0.0) -> tuple[dict, pd.Timestamp]:
    """One stock plus SPY: random noise, then a planted ignition, consolidation days and the
    day after the screen date."""
    rng = np.random.default_rng(0)
    dates = pd.bdate_range("2024-01-01", periods=IGNITION + len(consol_moves) + 5)
    spy = rng.normal(0, 0.01, len(dates))
    stock = spy + rng.normal(0, 0.015, len(dates))
    volume = np.full(len(dates), 1e6)

    days = range(IGNITION, IGNITION + len(consol_moves) + 2)
    spy[days] = 0.0  # quiet market over the setup, so raw and excess moves match
    stock[days] = [ignition_move, *consol_moves, friday_move]
    volume[IGNITION] = 5e6

    close = pd.DataFrame({"SPY": 400 * np.cumprod(1 + spy), "AAA": 100 * np.cumprod(1 + stock)},
                         index=dates)
    volumes = pd.DataFrame({"SPY": 1e8, "AAA": volume}, index=dates)
    prices = {"open": close, "high": close * 1.005, "low": close * 0.995, "close": close,
              "volume": volumes}
    return prices, dates[IGNITION + len(consol_moves)]


def test_finds_planted_setup():
    p, screen_date = make_prices(0.10, [0.001, -0.001, 0.001])
    df = find_setups(p, Config(), [screen_date])
    assert list(df["ticker"]) == ["AAA"]
    assert df.loc[0, "direction"] == 1 and df.loc[0, "consol_days"] == 3


def test_down_move_mirrors_up_move():
    # Drifts down and closes at the low: every lean vote should favour "goes again" (down)
    p, screen_date = make_prices(-0.10, [-0.005, -0.005, -0.005])
    p["volume"].iloc[IGNITION + 1:, 1] = 2e6  # consolidation volume under half of ignition
    df = find_setups(p, Config(), [screen_date])
    assert df.loc[0, "direction"] == -1
    assert df.loc[0, "votes"] == 3


def test_rejects_setup_that_gives_back_the_move():
    # Each day is quiet (< 1 sigma), but together they give back ~60% of a 6% move
    p, screen_date = make_prices(0.06, [-0.012, -0.012, -0.012])
    assert find_setups(p, Config(), [screen_date]).empty


def test_no_look_ahead():
    # Deleting everything after the screen date must not change the result
    p, screen_date = make_prices(0.10, [0.001, -0.001, 0.001])
    truncated = {field: f.loc[:screen_date] for field, f in p.items()}
    pd.testing.assert_frame_equal(find_setups(p, Config(), [screen_date]),
                                  find_setups(truncated, Config(), [screen_date]))


def friday_outcome(friday_move: float) -> pd.Series:
    p, screen_date = make_prices(0.10, [0.001, -0.001, 0.001], friday_move)
    friday = p["close"].index[IGNITION + 4]
    setups = find_setups(p, Config(), [screen_date])
    return add_outcomes(setups, p, pd.Series([friday], index=[screen_date])).iloc[0]


def test_outcome_labels():
    assert friday_outcome(0.05)["outcome"] == "goes again"
    assert friday_outcome(0.0)["outcome"] == "stalls"
    assert friday_outcome(-0.05)["outcome"] == "reverses"
    assert friday_outcome(0.05)["close_to_close"] > 0.04
