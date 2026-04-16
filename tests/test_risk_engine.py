"""Tests for RiskEngine and PortfolioRiskResult."""

import pytest
import numpy as np
from risk_engine.portfolio.portfolio import Portfolio
from risk_engine.portfolio.risk_engine import RiskEngine, PortfolioRiskResult
from risk_engine.instruments.european import EuropeanOption, OptionType, PricingModel
from risk_engine.market_data.market_data import MarketData


def _md(asset="AAPL", spot=100.0, rate=0.05, vol=0.2, dividend=0.0):
    return MarketData(asset_id=asset, spot=spot, rate=rate, vol=vol, dividend=dividend)


def _call(strike=100.0, expiry=1.0, asset="AAPL"):
    return EuropeanOption(OptionType.CALL, strike, expiry, asset)


def _put(strike=100.0, expiry=1.0, asset="AAPL"):
    return EuropeanOption(OptionType.PUT, strike, expiry, asset)


class TestPortfolioRiskResult:
    def test_is_valid_all_finite(self):
        r = PortfolioRiskResult(
            total_pv=100.0, total_delta=0.5, total_gamma=0.01,
            total_vega=10.0, total_theta=-0.05,
            value_at_risk_95=5.0, value_at_risk_99=8.0,
            expected_shortfall_95=6.0, expected_shortfall_99=9.0,
        )
        assert r.is_valid()

    def test_is_valid_nan_fails(self):
        r = PortfolioRiskResult(total_pv=float("nan"))
        assert not r.is_valid()

    def test_is_valid_inf_fails(self):
        r = PortfolioRiskResult(total_pv=float("inf"))
        assert not r.is_valid()


class TestRiskEngineBasics:
    def test_empty_portfolio_returns_zero_result(self):
        engine = RiskEngine()
        result = engine.calculate_portfolio_risk(Portfolio(), {"AAPL": _md()})
        assert result.portfolio_size == 0
        assert result.total_pv == 0.0

    def test_single_call_produces_finite_metrics(self):
        p = Portfolio()
        p.add_instrument(_call(), 10)
        engine = RiskEngine(var_simulations=1000)
        engine.set_random_seed(42)
        result = engine.calculate_portfolio_risk(p, {"AAPL": _md()})
        assert result.is_valid()
        assert result.total_pv > 0
        assert result.portfolio_size == 1

    def test_var_95_le_var_99(self):
        p = Portfolio()
        p.add_instrument(_call(), 10)
        engine = RiskEngine(var_simulations=2000)
        engine.set_random_seed(0)
        result = engine.calculate_portfolio_risk(p, {"AAPL": _md()})
        assert result.value_at_risk_95 <= result.value_at_risk_99

    def test_put_var_differs_from_call_var(self):
        """Regression test for bug fix: put VaR should differ from call VaR."""
        md = {"AAPL": _md()}
        engine = RiskEngine(var_simulations=5000)
        engine.set_random_seed(7)

        p_call = Portfolio()
        p_call.add_instrument(_call(), 10)
        result_call = engine.calculate_portfolio_risk(p_call, md)

        engine.set_random_seed(7)
        p_put = Portfolio()
        p_put.add_instrument(_put(), 10)
        result_put = engine.calculate_portfolio_risk(p_put, md)

        # Call and put VaR should not be identical
        assert abs(result_call.value_at_risk_95 - result_put.value_at_risk_95) > 0.01

    def test_missing_market_data_raises(self):
        p = Portfolio()
        p.add_instrument(_call(asset="TSLA"), 1)
        engine = RiskEngine()
        with pytest.raises(ValueError, match="Missing market data"):
            engine.calculate_portfolio_risk(p, {"AAPL": _md()})

    def test_pnl_distribution_stored(self):
        p = Portfolio()
        p.add_instrument(_call(), 5)
        engine = RiskEngine(var_simulations=500)
        engine.set_random_seed(1)
        result = engine.calculate_portfolio_risk(p, {"AAPL": _md()})
        assert result.pnl_distribution is not None
        assert len(result.pnl_distribution) == 500


class TestRiskEngineValidation:
    def test_zero_simulations_raises(self):
        engine = RiskEngine()
        with pytest.raises(ValueError):
            engine.set_var_simulations(0)

    def test_too_many_simulations_raises(self):
        engine = RiskEngine()
        with pytest.raises(ValueError):
            engine.set_var_simulations(2_000_000)

    def test_zero_time_horizon_raises(self):
        engine = RiskEngine()
        with pytest.raises(ValueError):
            engine.set_var_time_horizon_days(0)

    def test_time_horizon_exceeds_max_raises(self):
        engine = RiskEngine()
        with pytest.raises(ValueError):
            engine.set_var_time_horizon_days(300)
