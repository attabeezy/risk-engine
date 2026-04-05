"""
Tests for Black-Scholes module.
"""

import pytest
from risk_engine.core import blackscholes as bs


class TestNormalDistribution:
    def test_norm_cdf_at_zero(self):
        assert abs(bs._norm_cdf(0.0) - 0.5) < 1e-10

    def test_norm_cdf_symmetry(self):
        z = 1.5
        assert abs(bs._norm_cdf(z) + bs._norm_cdf(-z) - 1.0) < 1e-10


class TestCallPrice:
    def test_call_atm(self):
        price = bs.call_price(100.0, 100.0, 0.05, 1.0, 0.2)
        assert abs(price - 10.4506) < 0.01

    def test_call_itm(self):
        price = bs.call_price(110.0, 100.0, 0.05, 1.0, 0.2)
        assert abs(price - 17.6630) < 0.01

    def test_call_otm(self):
        price = bs.call_price(90.0, 100.0, 0.05, 1.0, 0.2)
        assert abs(price - 5.0912) < 0.01

    def test_call_intrinsic_at_expiry(self):
        price = bs.call_price(110.0, 100.0, 0.05, 0.0, 0.2)
        assert price == 10.0


class TestPutPrice:
    def test_put_atm(self):
        price = bs.put_price(100.0, 100.0, 0.05, 1.0, 0.2)
        assert abs(price - 5.5735) < 0.01

    def test_put_intrinsic_at_expiry(self):
        price = bs.put_price(90.0, 100.0, 0.05, 0.0, 0.2)
        assert price == 10.0


class TestPutCallParity:
    def test_parity_atm(self):
        S = K = 100.0
        r = 0.05
        T = 1.0
        sigma = 0.2
        call = bs.call_price(S, K, r, T, sigma)
        put = bs.put_price(S, K, r, T, sigma)
        lhs = call - put
        from math import exp

        rhs = S - K * exp(-r * T)
        assert abs(lhs - rhs) < 1e-6


class TestDelta:
    def test_call_delta_atm(self):
        delta = bs.call_delta(100.0, 100.0, 0.05, 1.0, 0.2)
        assert 0.0 <= delta <= 1.0
        assert abs(delta - 0.6368) < 0.01

    def test_put_delta_atm(self):
        delta = bs.put_delta(100.0, 100.0, 0.05, 1.0, 0.2)
        assert -1.0 <= delta <= 0.0
        assert abs(delta - (-0.3632)) < 0.01


class TestGamma:
    def test_gamma_positive(self):
        gamma = bs.gamma(100.0, 100.0, 0.05, 1.0, 0.2)
        assert gamma >= 0.0

    def test_gamma_zero_at_expiry(self):
        gamma = bs.gamma(100.0, 100.0, 0.05, 0.0, 0.2)
        assert gamma == 0.0


class TestVega:
    def test_vega_positive(self):
        vega = bs.vega(100.0, 100.0, 0.05, 1.0, 0.2)
        assert vega >= 0.0


class TestTheta:
    def test_call_theta_negative(self):
        theta = bs.call_theta(100.0, 100.0, 0.05, 1.0, 0.2)
        assert theta < 0.0


class TestInputValidation:
    def test_negative_spot(self):
        with pytest.raises(ValueError):
            bs.call_price(-100.0, 100.0, 0.05, 1.0, 0.2)

    def test_negative_strike(self):
        with pytest.raises(ValueError):
            bs.call_price(100.0, -100.0, 0.05, 1.0, 0.2)

    def test_negative_time(self):
        with pytest.raises(ValueError):
            bs.call_price(100.0, 100.0, 0.05, -1.0, 0.2)

    def test_negative_vol(self):
        with pytest.raises(ValueError):
            bs.call_price(100.0, 100.0, 0.05, 1.0, -0.2)
