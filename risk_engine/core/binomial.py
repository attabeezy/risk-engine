"""
Binomial tree option pricing model.

Implements the Cox-Ross-Rubinstein (CRR) binomial model for European and American options.
"""

from math import exp, sqrt
from enum import Enum
from typing import List, Tuple


class OptionType(Enum):
    CALL = "call"
    PUT = "put"


def _validate_inputs(
    spot: float, strike: float, rate: float, time: float, vol: float, steps: int
) -> None:
    """Validate binomial tree inputs."""
    if spot <= 0:
        raise ValueError(f"Spot price must be positive, got {spot}")
    if strike <= 0:
        raise ValueError(f"Strike price must be positive, got {strike}")
    if time < 0:
        raise ValueError(f"Time to expiry cannot be negative, got {time}")
    if vol < 0:
        raise ValueError(f"Volatility cannot be negative, got {vol}")
    if steps < 1:
        raise ValueError(f"Steps must be positive, got {steps}")


def european_option_price(
    spot: float,
    strike: float,
    rate: float,
    time: float,
    vol: float,
    option_type: OptionType,
    steps: int = 100,
) -> float:
    """
    Price a European option using the binomial tree method.

    Args:
        spot: Current spot price
        strike: Strike price
        rate: Risk-free interest rate (annualized)
        time: Time to expiry in years
        vol: Volatility (annualized)
        option_type: OptionType.CALL or OptionType.PUT
        steps: Number of time steps (default 100)

    Returns:
        European option price
    """
    _validate_inputs(spot, strike, rate, time, vol, steps)

    if time == 0:
        if option_type == OptionType.CALL:
            return max(0.0, spot - strike)
        else:
            return max(0.0, strike - spot)

    dt = time / steps
    u = exp(vol * sqrt(dt))
    d = 1.0 / u
    p = (exp(rate * dt) - d) / (u - d)
    discount = exp(-rate * dt)

    if not 0 <= p <= 1:
        raise RuntimeError(f"Invalid probability in binomial tree: {p}")

    prices = [0.0] * (steps + 1)

    for i in range(steps + 1):
        spot_at_maturity = spot * (u ** (steps - i)) * (d**i)
        if option_type == OptionType.CALL:
            prices[i] = max(0.0, spot_at_maturity - strike)
        else:
            prices[i] = max(0.0, strike - spot_at_maturity)

    for step in range(steps - 1, -1, -1):
        for i in range(step + 1):
            prices[i] = discount * (p * prices[i] + (1.0 - p) * prices[i + 1])

    return prices[0]


def american_option_price(
    spot: float,
    strike: float,
    rate: float,
    time: float,
    vol: float,
    option_type: OptionType,
    steps: int = 100,
) -> float:
    """
    Price an American option using the binomial tree method with early exercise.

    Args:
        spot: Current spot price
        strike: Strike price
        rate: Risk-free interest rate (annualized)
        time: Time to expiry in years
        vol: Volatility (annualized)
        option_type: OptionType.CALL or OptionType.PUT
        steps: Number of time steps (default 100)

    Returns:
        American option price
    """
    _validate_inputs(spot, strike, rate, time, vol, steps)

    if time == 0:
        if option_type == OptionType.CALL:
            return max(0.0, spot - strike)
        else:
            return max(0.0, strike - spot)

    dt = time / steps
    u = exp(vol * sqrt(dt))
    d = 1.0 / u
    p = (exp(rate * dt) - d) / (u - d)
    discount = exp(-rate * dt)

    if not 0 <= p <= 1:
        raise RuntimeError(f"Invalid probability in binomial tree: {p}")

    prices = [0.0] * (steps + 1)
    spots = [0.0] * (steps + 1)

    for i in range(steps + 1):
        spots[i] = spot * (u ** (steps - i)) * (d**i)
        if option_type == OptionType.CALL:
            prices[i] = max(0.0, spots[i] - strike)
        else:
            prices[i] = max(0.0, strike - spots[i])

    for step in range(steps - 1, -1, -1):
        for i in range(step + 1):
            spots[i] = spot * (u ** (step - i)) * (d**i)

            hold_value = discount * (p * prices[i] + (1.0 - p) * prices[i + 1])

            if option_type == OptionType.CALL:
                exercise_value = max(0.0, spots[i] - strike)
            else:
                exercise_value = max(0.0, strike - spots[i])

            prices[i] = max(hold_value, exercise_value)

    return prices[0]


def build_tree(
    spot: float,
    strike: float,
    rate: float,
    time: float,
    vol: float,
    option_type: OptionType,
    steps: int,
    is_american: bool,
) -> List[List[Tuple[float, float, bool]]]:
    """
    Build a binomial tree for visualization.

    Returns:
        List of time steps, each containing list of nodes as
        (stock_price, option_value, is_early_exercise_optimal)
    """
    _validate_inputs(spot, strike, rate, time, vol, steps)

    dt = time / steps
    u = exp(vol * sqrt(dt))
    d = 1.0 / u
    p = (exp(rate * dt) - d) / (u - d)
    discount = exp(-rate * dt)

    tree: List[List[Tuple[float, float, bool]]] = []

    for step in range(steps + 1):
        nodes = []
        for i in range(step + 1):
            stock_price = spot * (u ** (step - i)) * (d**i)
            nodes.append((stock_price, 0.0, False))
        tree.append(nodes)

    for i in range(steps + 1):
        spot_at_maturity = tree[steps][i][0]
        if option_type == OptionType.CALL:
            option_value = max(0.0, spot_at_maturity - strike)
        else:
            option_value = max(0.0, strike - spot_at_maturity)
        tree[steps][i] = (spot_at_maturity, option_value, False)

    for step in range(steps - 1, -1, -1):
        for i in range(step + 1):
            hold_value = discount * (
                p * tree[step + 1][i][1] + (1.0 - p) * tree[step + 1][i + 1][1]
            )

            stock_price = tree[step][i][0]
            if option_type == OptionType.CALL:
                exercise_value = max(0.0, stock_price - strike)
            else:
                exercise_value = max(0.0, strike - stock_price)

            if is_american and exercise_value > hold_value:
                tree[step][i] = (stock_price, exercise_value, True)
            else:
                tree[step][i] = (stock_price, hold_value, False)

    return tree
