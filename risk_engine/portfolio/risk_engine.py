"""
Risk engine with Monte Carlo VaR using Numba JIT compilation.
"""

from dataclasses import dataclass
from math import sqrt, erf
from typing import Dict, List, Tuple, Optional
import numpy as np
from numba import njit, prange
from risk_engine.instruments.base import Instrument, MarketData
from risk_engine.portfolio.portfolio import Portfolio


@dataclass
class PortfolioRiskResult:
    """Result of portfolio risk calculation."""

    total_pv: float = 0.0
    total_delta: float = 0.0
    total_gamma: float = 0.0
    total_vega: float = 0.0
    total_theta: float = 0.0
    value_at_risk_95: float = 0.0
    value_at_risk_99: float = 0.0
    expected_shortfall_95: float = 0.0
    expected_shortfall_99: float = 0.0
    portfolio_size: int = 0

    def is_valid(self) -> bool:
        """Check if all values are finite."""
        return all(
            np.isfinite(v)
            for v in [
                self.total_pv,
                self.total_delta,
                self.total_gamma,
                self.total_vega,
                self.total_theta,
                self.value_at_risk_95,
                self.value_at_risk_99,
                self.expected_shortfall_95,
                self.expected_shortfall_99,
            ]
        )


@njit(parallel=True)
def _monte_carlo_var_numba(
    initial_pv: float,
    spots: np.ndarray,
    vols: np.ndarray,
    rates: np.ndarray,
    quantities: np.ndarray,
    strikes: np.ndarray,
    times: np.ndarray,
    option_types: np.ndarray,
    is_americans: np.ndarray,
    binomial_steps_arr: np.ndarray,
    n_sims: int,
    time_horizon: float,
    seed: int,
) -> np.ndarray:
    """Numba-accelerated Monte Carlo VaR calculation."""
    np.random.seed(seed)
    n_assets = len(spots)

    pnl = np.zeros(n_sims)

    dt = time_horizon / 252.0
    sqrt_dt = sqrt(dt)

    for sim in prange(n_sims):
        simulated_pv = 0.0

        for i in range(n_assets):
            S0 = spots[i]
            sigma = vols[i]
            r = rates[i]
            K = strikes[i]
            T = times[i]
            qty = quantities[i]
            opt_type = option_types[i]
            is_american = is_americans[i]
            steps = binomial_steps_arr[i]

            random_shock = np.random.normal(0.0, 1.0)
            drift = (r - 0.5 * sigma * sigma) * dt
            diffusion = sigma * sqrt_dt * random_shock
            S_sim = S0 * np.exp(drift + diffusion)

            if S_sim <= 0.0 or np.isnan(S_sim) or np.isinf(S_sim):
                S_sim = S0

            price = _price_option_numba(
                S_sim, K, r, T, sigma, opt_type, is_american, steps
            )
            simulated_pv += price * qty

        pnl[sim] = simulated_pv - initial_pv

    return pnl


@njit
def _price_option_numba(
    spot: float,
    strike: float,
    rate: float,
    time: float,
    vol: float,
    option_type: int,
    is_american: int,
    steps: int,
) -> float:
    """Price a single option (simplified Black-Scholes for Numba)."""
    if time <= 0.0 or vol <= 0.0:
        if option_type == 1:
            return max(0.0, spot - strike)
        else:
            return max(0.0, strike - spot)

    d1 = (np.log(spot / strike) + (rate + 0.5 * vol * vol) * time) / (vol * sqrt(time))
    d2 = d1 - vol * sqrt(time)

    if option_type == 1:
        return spot * _norm_cdf(d1) - strike * np.exp(-rate * time) * _norm_cdf(d2)
    else:
        return strike * np.exp(-rate * time) * _norm_cdf(-d2) - spot * _norm_cdf(-d1)


@njit
def _norm_cdf(x: float) -> float:
    """Standard normal CDF."""
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def _calculate_var_metrics(
    pnl: np.ndarray, n_sims: int
) -> Tuple[float, float, float, float]:
    """Calculate VaR and Expected Shortfall from P&L distribution."""
    sorted_pnl = np.sort(pnl)

    index_95 = int((1.0 - 0.95) * n_sims)
    index_99 = int((1.0 - 0.99) * n_sims)

    var_95 = float(-sorted_pnl[index_95])
    var_99 = float(-sorted_pnl[index_99])
    es_95 = float(-np.mean(sorted_pnl[: index_95 + 1]))
    es_99 = float(-np.mean(sorted_pnl[: index_99 + 1]))

    return var_95, var_99, es_95, es_99


class RiskEngine:
    """Risk engine for portfolio risk calculations with VaR."""

    def __init__(self, var_simulations: int = 10000):
        self.var_simulations = var_simulations
        self.time_horizon_days = 1.0
        self.random_seed: Optional[int] = None
        self.use_fixed_seed = False

    def set_var_simulations(self, simulations: int) -> None:
        if simulations <= 0:
            raise ValueError("VaR simulations must be positive")
        if simulations > 1000000:
            raise ValueError("VaR simulations cannot exceed 1,000,000")
        self.var_simulations = simulations

    def set_var_time_horizon_days(self, days: float) -> None:
        if days <= 0:
            raise ValueError("Time horizon must be positive")
        if days > 252:
            raise ValueError("Time horizon cannot exceed 252 trading days")
        self.time_horizon_days = days

    def set_random_seed(self, seed: int) -> None:
        self.random_seed = seed
        self.use_fixed_seed = True

    def set_use_fixed_seed(self, use_fixed: bool) -> None:
        self.use_fixed_seed = use_fixed

    def calculate_portfolio_risk(
        self, portfolio: Portfolio, market_data_map: Dict[str, MarketData]
    ) -> PortfolioRiskResult:
        """Calculate portfolio risk metrics."""
        if portfolio.is_empty():
            return PortfolioRiskResult(portfolio_size=0)

        result = PortfolioRiskResult()
        result.portfolio_size = portfolio.size()

        for instrument, quantity in portfolio.get_instruments():
            asset_id = instrument.get_asset_id()

            if asset_id not in market_data_map:
                raise ValueError(f"Missing market data for asset: {asset_id}")

            md = market_data_map[asset_id]

            result.total_pv += instrument.price(md) * quantity
            result.total_delta += instrument.delta(md) * quantity
            result.total_gamma += instrument.gamma(md) * quantity
            result.total_vega += instrument.vega(md) * quantity
            result.total_theta += instrument.theta(md) * quantity

        if not result.is_valid():
            raise RuntimeError("Portfolio risk calculation produced invalid results")

        var_result = self._calculate_var_monte_carlo(portfolio, market_data_map)
        result.value_at_risk_95 = var_result[0]
        result.value_at_risk_99 = var_result[1]
        result.expected_shortfall_95 = var_result[2]
        result.expected_shortfall_99 = var_result[3]

        return result

    def _calculate_var_monte_carlo(
        self, portfolio: Portfolio, market_data_map: Dict[str, MarketData]
    ) -> Tuple[float, float, float, float]:
        """Calculate VaR using Monte Carlo simulation."""
        instruments_data = portfolio.get_instruments()

        n_positions = len(instruments_data)
        n_sims = self.var_simulations

        spots = np.zeros(n_positions, dtype=np.float64)
        vols = np.zeros(n_positions, dtype=np.float64)
        rates = np.zeros(n_positions, dtype=np.float64)
        quantities = np.zeros(n_positions, dtype=np.float64)
        strikes = np.zeros(n_positions, dtype=np.float64)
        times = np.zeros(n_positions, dtype=np.float64)
        option_types = np.zeros(n_positions, dtype=np.float64)
        is_americans = np.zeros(n_positions, dtype=np.float64)
        binomial_steps_arr = np.zeros(n_positions, dtype=np.float64)

        initial_pv = 0.0

        for i, (instrument, quantity) in enumerate(instruments_data):
            asset_id = instrument.get_asset_id()
            md = market_data_map[asset_id]

            spots[i] = md.spot
            vols[i] = md.vol
            rates[i] = md.rate
            quantities[i] = quantity

            strikes[i] = getattr(instrument, "strike", 0)
            times[i] = getattr(instrument, "time_to_expiry", 1.0)

            option_types[i] = 1.0
            is_americans[i] = 0.0
            binomial_steps_arr[i] = 100.0

            initial_pv += instrument.price(md) * quantity

        seed = (
            self.random_seed
            if self.use_fixed_seed
            else int(np.random.randint(0, 2**31))
        )

        pnl = _monte_carlo_var_numba(
            initial_pv,
            spots,
            vols,
            rates,
            quantities,
            strikes,
            times,
            option_types,
            is_americans,
            binomial_steps_arr,
            n_sims,
            self.time_horizon_days,
            seed,
        )

        return _calculate_var_metrics(pnl, n_sims)
