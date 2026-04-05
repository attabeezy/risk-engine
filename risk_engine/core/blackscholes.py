"""
Black-Scholes option pricing model with Greeks.

Implements the Black-Scholes-Merton model for European options.
"""

from math import sqrt, exp, log, pi, erf, isfinite


def _norm_cdf(x: float) -> float:
    """Cumulative distribution function for standard normal."""
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    """Probability density function for standard normal."""
    return exp(-0.5 * x * x) / sqrt(2.0 * pi)


def _d1(spot: float, strike: float, rate: float, time: float, vol: float) -> float:
    """Calculate d1 for Black-Scholes formula."""
    return (log(spot / strike) + (rate + 0.5 * vol * vol) * time) / (vol * sqrt(time))


def _d2(spot: float, strike: float, rate: float, time: float, vol: float) -> float:
    """Calculate d2 for Black-Scholes formula."""
    return _d1(spot, strike, rate, time, vol) - vol * sqrt(time)


def _validate_inputs(
    spot: float, strike: float, rate: float, time: float, vol: float
) -> None:
    """Validate Black-Scholes inputs."""
    if spot <= 0:
        raise ValueError(f"Spot price must be positive, got {spot}")
    if strike <= 0:
        raise ValueError(f"Strike price must be positive, got {strike}")
    if time < 0:
        raise ValueError(f"Time to expiry cannot be negative, got {time}")
    if vol < 0:
        raise ValueError(f"Volatility cannot be negative, got {vol}")
    if not (
        isfinite(spot)
        and isfinite(strike)
        and isfinite(rate)
        and isfinite(time)
        and isfinite(vol)
    ):
        raise ValueError("Inputs must be finite numbers")


def call_price(
    spot: float, strike: float, rate: float, time: float, vol: float
) -> float:
    """
    Calculate European call option price using Black-Scholes.

    Args:
        spot: Current spot price
        strike: Strike price
        rate: Risk-free interest rate (annualized)
        time: Time to expiry in years
        vol: Volatility (annualized)

    Returns:
        Call option price
    """
    _validate_inputs(spot, strike, rate, time, vol)

    if time <= 0 or vol <= 0:
        return max(0.0, spot - strike)

    d1 = _d1(spot, strike, rate, time, vol)
    d2 = _d2(spot, strike, rate, time, vol)

    return spot * _norm_cdf(d1) - strike * exp(-rate * time) * _norm_cdf(d2)


def put_price(
    spot: float, strike: float, rate: float, time: float, vol: float
) -> float:
    """
    Calculate European put option price using Black-Scholes.

    Args:
        spot: Current spot price
        strike: Strike price
        rate: Risk-free interest rate (annualized)
        time: Time to expiry in years
        vol: Volatility (annualized)

    Returns:
        Put option price
    """
    _validate_inputs(spot, strike, rate, time, vol)

    if time <= 0 or vol <= 0:
        return max(0.0, strike - spot)

    d1 = _d1(spot, strike, rate, time, vol)
    d2 = _d2(spot, strike, rate, time, vol)

    return strike * exp(-rate * time) * _norm_cdf(-d2) - spot * _norm_cdf(-d1)


def call_delta(
    spot: float, strike: float, rate: float, time: float, vol: float
) -> float:
    """
    Calculate call option delta (sensitivity to spot price).

    Args:
        spot: Current spot price
        strike: Strike price
        rate: Risk-free interest rate
        time: Time to expiry in years
        vol: Volatility

    Returns:
        Call delta (between 0 and 1)
    """
    _validate_inputs(spot, strike, rate, time, vol)

    if time <= 0 or vol <= 0:
        return 1.0 if spot > strike else 0.0

    d1 = _d1(spot, strike, rate, time, vol)
    return _norm_cdf(d1)


def put_delta(
    spot: float, strike: float, rate: float, time: float, vol: float
) -> float:
    """
    Calculate put option delta (sensitivity to spot price).

    Args:
        spot: Current spot price
        strike: Strike price
        rate: Risk-free interest rate
        time: Time to expiry in years
        vol: Volatility

    Returns:
        Put delta (between -1 and 0)
    """
    _validate_inputs(spot, strike, rate, time, vol)

    if time <= 0 or vol <= 0:
        return -1.0 if spot < strike else 0.0

    d1 = _d1(spot, strike, rate, time, vol)
    return _norm_cdf(d1) - 1.0


def gamma(spot: float, strike: float, rate: float, time: float, vol: float) -> float:
    """
    Calculate option gamma (second derivative to spot price).

    Gamma is the same for calls and puts.

    Args:
        spot: Current spot price
        strike: Strike price
        rate: Risk-free interest rate
        time: Time to expiry in years
        vol: Volatility

    Returns:
        Option gamma
    """
    _validate_inputs(spot, strike, rate, time, vol)

    if time <= 0 or vol <= 0:
        return 0.0

    d1 = _d1(spot, strike, rate, time, vol)
    return _norm_pdf(d1) / (spot * vol * sqrt(time))


def vega(spot: float, strike: float, rate: float, time: float, vol: float) -> float:
    """
    Calculate option vega (sensitivity to volatility).

    Vega is the same for calls and puts.

    Args:
        spot: Current spot price
        strike: Strike price
        rate: Risk-free interest rate
        time: Time to expiry in years
        vol: Volatility

    Returns:
        Option vega (per 1% change in volatility)
    """
    _validate_inputs(spot, strike, rate, time, vol)

    if time <= 0 or vol <= 0:
        return 0.0

    d1 = _d1(spot, strike, rate, time, vol)
    return spot * _norm_pdf(d1) * sqrt(time)


def call_theta(
    spot: float, strike: float, rate: float, time: float, vol: float
) -> float:
    """
    Calculate call option theta (time decay per day).

    Args:
        spot: Current spot price
        strike: Strike price
        rate: Risk-free interest rate
        time: Time to expiry in years
        vol: Volatility

    Returns:
        Call theta (per day)
    """
    _validate_inputs(spot, strike, rate, time, vol)

    if time <= 0 or vol <= 0:
        return 0.0

    d1 = _d1(spot, strike, rate, time, vol)
    d2 = _d2(spot, strike, rate, time, vol)

    term1 = -(spot * _norm_pdf(d1) * vol) / (2.0 * sqrt(time))
    term2 = rate * strike * exp(-rate * time) * _norm_cdf(d2)

    return (term1 - term2) / 365.0


def put_theta(
    spot: float, strike: float, rate: float, time: float, vol: float
) -> float:
    """
    Calculate put option theta (time decay per day).

    Args:
        spot: Current spot price
        strike: Strike price
        rate: Risk-free interest rate
        time: Time to expiry in years
        vol: Volatility

    Returns:
        Put theta (per day)
    """
    _validate_inputs(spot, strike, rate, time, vol)

    if time <= 0 or vol <= 0:
        return 0.0

    d1 = _d1(spot, strike, rate, time, vol)
    d2 = _d2(spot, strike, rate, time, vol)

    term1 = -(spot * _norm_pdf(d1) * vol) / (2.0 * sqrt(time))
    term2 = rate * strike * exp(-rate * time) * _norm_cdf(-d2)

    return (term1 + term2) / 365.0


def call_rho(spot: float, strike: float, rate: float, time: float, vol: float) -> float:
    """
    Calculate call option rho (sensitivity to interest rate).

    Args:
        spot: Current spot price
        strike: Strike price
        rate: Risk-free interest rate
        time: Time to expiry in years
        vol: Volatility

    Returns:
        Call rho (per 1% change in rate)
    """
    _validate_inputs(spot, strike, rate, time, vol)

    if time <= 0:
        return 0.0

    d2 = _d2(spot, strike, rate, time, vol)
    return strike * time * exp(-rate * time) * _norm_cdf(d2) / 100.0


def put_rho(spot: float, strike: float, rate: float, time: float, vol: float) -> float:
    """
    Calculate put option rho (sensitivity to interest rate).

    Args:
        spot: Current spot price
        strike: Strike price
        rate: Risk-free interest rate
        time: Time to expiry in years
        vol: Volatility

    Returns:
        Put rho (per 1% change in rate)
    """
    _validate_inputs(spot, strike, rate, time, vol)

    if time <= 0:
        return 0.0

    d2 = _d2(spot, strike, rate, time, vol)
    return -strike * time * exp(-rate * time) * _norm_cdf(-d2) / 100.0


def implied_volatility(
    market_price: float,
    spot: float,
    strike: float,
    rate: float,
    time: float,
    is_call: bool,
    initial_guess: float = 0.3,
    tolerance: float = 1e-6,
    max_iterations: int = 100,
) -> float:
    """
    Calculate implied volatility from market price using Newton-Raphson.

    Args:
        market_price: Observed market price
        spot: Current spot price
        strike: Strike price
        rate: Risk-free interest rate
        time: Time to expiry in years
        is_call: True for call, False for put
        initial_guess: Starting volatility guess
        tolerance: Convergence tolerance
        max_iterations: Maximum iterations

    Returns:
        Implied volatility

    Raises:
        ValueError: If inputs invalid or doesn't converge
    """
    _validate_inputs(spot, strike, rate, time, initial_guess)

    if market_price < 0:
        raise ValueError(f"Market price cannot be negative: {market_price}")

    if time <= 0:
        raise ValueError("Cannot calculate implied volatility for expired option")

    intrinsic = max(0.0, spot - strike) if is_call else max(0.0, strike - spot)
    if market_price < intrinsic - 1e-10:
        raise ValueError(
            f"Market price {market_price} below intrinsic value {intrinsic}"
        )

    sigma = initial_guess
    price_func = call_price if is_call else put_price

    for _ in range(max_iterations):
        try:
            price = price_func(spot, strike, rate, time, sigma)
        except Exception:
            raise RuntimeError("Failed to calculate option price during IV search")

        diff = price - market_price

        if abs(diff) < tolerance:
            return sigma

        v = vega(spot, strike, rate, time, sigma)

        if v < 1e-10:
            raise RuntimeError("Vega too small for Newton-Raphson")

        sigma = sigma - diff / v

        if sigma <= 0:
            sigma = 0.01
        if sigma > 10.0:
            sigma = 10.0

    raise RuntimeError("Implied volatility did not converge")
