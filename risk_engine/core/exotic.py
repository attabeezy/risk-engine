"""
Exotic options pricing - Monte Carlo fallbacks.

Pure Python implementation for Barrier and Asian options.
"""

from enum import Enum
from math import exp, sqrt, log
import numpy as np


class BarrierTypeEnum(Enum):
    DOWN_IN = "down_in"
    DOWN_OUT = "down_out"
    UP_IN = "up_in"
    UP_OUT = "up_out"


class AverageTypeEnum(Enum):
    ARITHMETIC = "arithmetic"
    GEOMETRIC = "geometric"


def _mc_barrier_price(
    spot,
    strike,
    barrier,
    rate,
    time,
    vol,
    is_call,
    barrier_type,
    rebate=0.0,
    n_sims=10000,
):
    """Monte Carlo pricing for barrier options."""
    dt = time / 50
    n_steps = 50

    payoffs = []

    for _ in range(n_sims):
        S = spot
        breached = False

        for _ in range(n_steps):
            z = np.random.normal()
            S = S * exp((rate - 0.5 * vol**2) * dt + vol * sqrt(dt) * z)

            if barrier_type in [BarrierTypeEnum.DOWN_IN, BarrierTypeEnum.DOWN_OUT]:
                if S <= barrier:
                    breached = True
                    break
            else:
                if S >= barrier:
                    breached = True
                    break

        if barrier_type in [BarrierTypeEnum.DOWN_IN, BarrierTypeEnum.UP_IN]:
            if breached:
                payoff = max(0.0, S - strike) if is_call else max(0.0, strike - S)
                payoffs.append(payoff + rebate)
            else:
                payoffs.append(rebate)
        else:
            if not breached:
                payoff = max(0.0, S - strike) if is_call else max(0.0, strike - S)
                payoffs.append(payoff)
            else:
                payoffs.append(rebate)

    discount = exp(-rate * time)
    return discount * np.mean(payoffs)


def barrier_option_price(
    spot: float,
    strike: float,
    barrier: float,
    rate: float,
    time: float,
    vol: float,
    is_call: bool,
    barrier_type: BarrierTypeEnum,
    rebate: float = 0.0,
) -> float:
    """Price a barrier option using Monte Carlo."""
    if spot <= 0:
        raise ValueError(f"Spot price must be positive, got {spot}")
    if strike <= 0:
        raise ValueError(f"Strike price must be positive, got {strike}")
    if barrier <= 0:
        raise ValueError(f"Barrier level must be positive, got {barrier}")
    if time < 0:
        raise ValueError(f"Time to expiry cannot be negative, got {time}")
    if vol < 0:
        raise ValueError(f"Volatility cannot be negative, got {vol}")
    if rebate < 0:
        raise ValueError(f"Rebate cannot be negative, got {rebate}")

    if time == 0:
        return max(0.0, spot - strike) if is_call else max(0.0, strike - spot)

    return _mc_barrier_price(
        spot, strike, barrier, rate, time, vol, is_call, barrier_type, rebate
    )


def asian_option_price(
    spot: float,
    strike: float,
    rate: float,
    time: float,
    vol: float,
    is_call: bool,
    average_type: AverageTypeEnum = AverageTypeEnum.ARITHMETIC,
    past_fixings: int = 0,
    running_sum: float = 0.0,
) -> float:
    """Price an Asian option using Monte Carlo."""
    if spot <= 0:
        raise ValueError(f"Spot price must be positive, got {spot}")
    if strike <= 0:
        raise ValueError(f"Strike price must be positive, got {strike}")
    if time < 0:
        raise ValueError(f"Time to expiry cannot be negative, got {time}")
    if vol < 0:
        raise ValueError(f"Volatility cannot be negative, got {vol}")
    if past_fixings < 0:
        raise ValueError(f"Past fixings cannot be negative, got {past_fixings}")

    if time == 0:
        return max(0.0, spot - strike) if is_call else max(0.0, strike - spot)

    n_sims = 10000
    n_steps = 50
    dt = time / n_steps

    payoffs = []

    for _ in range(n_sims):
        prices = [spot]
        for _ in range(n_steps):
            z = np.random.normal()
            S = prices[-1] * exp((rate - 0.5 * vol**2) * dt + vol * sqrt(dt) * z)
            prices.append(S)

        avg_price = np.mean(prices[1:])

        if is_call:
            payoff = max(0.0, avg_price - strike)
        else:
            payoff = max(0.0, strike - avg_price)
        payoffs.append(payoff)

    discount = exp(-rate * time)
    return discount * np.mean(payoffs)
