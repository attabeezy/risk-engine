"""
Merton Jump Diffusion option pricing model.

Implements the Merton (1976) jump-diffusion model for European options.
"""

import math
from math import exp, sqrt, log
from .binomial import OptionType
from . import blackscholes as bs


def _poisson_probability(n: int, lambda_t: float) -> float:
    """
    Calculate Poisson probability using numerically stable log-space computation.

    P(N=n) = (lambda_t)^n * exp(-lambda_t) / n!

    Args:
        n: Number of jumps
        lambda_t: Lambda * T (expected number of jumps)

    Returns:
        Probability of exactly n jumps
    """
    if lambda_t < 0:
        raise ValueError(f"Lambda * T must be non-negative, got {lambda_t}")
    if n < 0:
        raise ValueError(f"Number of jumps cannot be negative, got {n}")

    if lambda_t == 0:
        return 1.0 if n == 0 else 0.0

    log_prob = n * log(lambda_t) - lambda_t
    for i in range(2, n + 1):
        log_prob -= log(i)

    return exp(log_prob)


def merton_call_price(
    spot: float,
    strike: float,
    rate: float,
    time: float,
    vol: float,
    jump_intensity: float,
    jump_mean: float,
    jump_vol: float,
    max_jumps: int = 50,
) -> float:
    """
    Calculate European call price under Merton jump diffusion model.

    The model assumes asset prices follow:
        dS/S = (r - lambda*k) * dt + sigma * dW + J * dN

    where J ~ lognormal(mean, vol) and N is a Poisson process.

    Args:
        spot: Current spot price
        strike: Strike price
        rate: Risk-free interest rate
        time: Time to expiry in years
        vol: Diffusion volatility
        jump_intensity: Lambda (average jumps per year)
        jump_mean: Mean of log jump size
        jump_vol: Volatility of log jump size
        max_jumps: Maximum number of jumps to sum (default 50)

    Returns:
        Call option price
    """
    if spot <= 0:
        raise ValueError(f"Spot price must be positive, got {spot}")
    if strike <= 0:
        raise ValueError(f"Strike price must be positive, got {strike}")
    if time < 0:
        raise ValueError(f"Time to expiry cannot be negative, got {time}")
    if vol < 0:
        raise ValueError(f"Volatility cannot be negative, got {vol}")
    if jump_vol < 0:
        raise ValueError(f"Jump volatility cannot be negative, got {jump_vol}")
    if jump_intensity < 0:
        raise ValueError(f"Jump intensity must be non-negative, got {jump_intensity}")

    if time == 0:
        return max(0.0, spot - strike)

    k = exp(jump_mean + 0.5 * jump_vol * jump_vol) - 1.0

    option_value = 0.0
    sum_prob = 0.0

    for n in range(max_jumps + 1):
        prob = _poisson_probability(n, jump_intensity * time)

        if prob < 1e-10:
            break

        sum_prob += prob

        sigma_n = sqrt(vol * vol + n * jump_vol * jump_vol / time)

        r_n = (
            rate
            - jump_intensity * k
            + n * (jump_mean + 0.5 * jump_vol * jump_vol) / time
        )

        bs_price = bs.call_price(spot, strike, r_n, time, sigma_n)

        option_value += prob * bs_price

        if sum_prob > 0.9999 and prob < 1e-8:
            break

    if not math.isfinite(option_value):
        raise RuntimeError("Invalid Merton jump diffusion price (NaN or Inf)")

    return option_value


def merton_put_price(
    spot: float,
    strike: float,
    rate: float,
    time: float,
    vol: float,
    jump_intensity: float,
    jump_mean: float,
    jump_vol: float,
    max_jumps: int = 50,
) -> float:
    """
    Calculate European put price under Merton jump diffusion model.

    Args:
        spot: Current spot price
        strike: Strike price
        rate: Risk-free interest rate
        time: Time to expiry in years
        vol: Diffusion volatility
        jump_intensity: Lambda (average jumps per year)
        jump_mean: Mean of log jump size
        jump_vol: Volatility of log jump size
        max_jumps: Maximum number of jumps to sum (default 50)

    Returns:
        Put option price
    """
    if spot <= 0:
        raise ValueError(f"Spot price must be positive, got {spot}")
    if strike <= 0:
        raise ValueError(f"Strike price must be positive, got {strike}")
    if time < 0:
        raise ValueError(f"Time to expiry cannot be negative, got {time}")
    if vol < 0:
        raise ValueError(f"Volatility cannot be negative, got {vol}")
    if jump_vol < 0:
        raise ValueError(f"Jump volatility cannot be negative, got {jump_vol}")
    if jump_intensity < 0:
        raise ValueError(f"Jump intensity must be non-negative, got {jump_intensity}")

    if time == 0:
        return max(0.0, strike - spot)

    k = exp(jump_mean + 0.5 * jump_vol * jump_vol) - 1.0

    option_value = 0.0
    sum_prob = 0.0

    for n in range(max_jumps + 1):
        prob = _poisson_probability(n, jump_intensity * time)

        if prob < 1e-10:
            break

        sum_prob += prob

        sigma_n = sqrt(vol * vol + n * jump_vol * jump_vol / time)

        r_n = (
            rate
            - jump_intensity * k
            + n * (jump_mean + 0.5 * jump_vol * jump_vol) / time
        )

        bs_price = bs.put_price(spot, strike, r_n, time, sigma_n)

        option_value += prob * bs_price

        if sum_prob > 0.9999 and prob < 1e-8:
            break

    if not math.isfinite(option_value):
        raise RuntimeError("Invalid Merton jump diffusion price (NaN or Inf)")

    return option_value


def merton_option_price(
    spot: float,
    strike: float,
    rate: float,
    time: float,
    vol: float,
    option_type: OptionType,
    jump_intensity: float = 2.0,
    jump_mean: float = -0.05,
    jump_vol: float = 0.15,
    max_jumps: int = 50,
) -> float:
    """
    Calculate European option price under Merton jump diffusion model.

    Args:
        spot: Current spot price
        strike: Strike price
        rate: Risk-free interest rate
        time: Time to expiry in years
        vol: Diffusion volatility
        option_type: OptionType.CALL or OptionType.PUT
        jump_intensity: Lambda (average jumps per year), default 2.0
        jump_mean: Mean of log jump size, default -0.05
        jump_vol: Volatility of log jump size, default 0.15
        max_jumps: Maximum number of jumps to sum (default 50)

    Returns:
        Option price
    """
    if option_type == OptionType.CALL:
        return merton_call_price(
            spot,
            strike,
            rate,
            time,
            vol,
            jump_intensity,
            jump_mean,
            jump_vol,
            max_jumps,
        )
    else:
        return merton_put_price(
            spot,
            strike,
            rate,
            time,
            vol,
            jump_intensity,
            jump_mean,
            jump_vol,
            max_jumps,
        )
