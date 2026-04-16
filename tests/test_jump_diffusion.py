"""Tests for Merton jump diffusion pricing."""

import pytest
from risk_engine.core import jump_diffusion as jd
from risk_engine.core import blackscholes as bs


class TestMertonCallPrice:
    def test_converges_to_bs_when_no_jumps(self):
        """With zero jump intensity, Merton price should match Black-Scholes."""
        S, K, r, T, sigma = 100.0, 100.0, 0.05, 1.0, 0.2
        merton = jd.merton_call_price(S, K, r, T, sigma, jump_intensity=0.0, jump_mean=0.0, jump_vol=0.0)
        black_scholes = bs.call_price(S, K, r, T, sigma)
        assert abs(merton - black_scholes) < 0.01

    def test_jumps_increase_call_price(self):
        """Positive jump intensity should increase option price vs no-jump case."""
        S, K, r, T, sigma = 100.0, 100.0, 0.05, 1.0, 0.2
        no_jump = jd.merton_call_price(S, K, r, T, sigma, jump_intensity=0.0, jump_mean=0.0, jump_vol=0.0)
        with_jump = jd.merton_call_price(S, K, r, T, sigma, jump_intensity=1.0, jump_mean=0.0, jump_vol=0.2)
        assert with_jump > no_jump

    def test_call_at_expiry(self):
        price = jd.merton_call_price(110.0, 100.0, 0.05, 0.0, 0.2, 1.0, -0.05, 0.15)
        assert price == 10.0

    def test_call_positive(self):
        price = jd.merton_call_price(100.0, 100.0, 0.05, 1.0, 0.2, 2.0, -0.05, 0.15)
        assert price > 0

    def test_negative_spot_raises(self):
        with pytest.raises(ValueError):
            jd.merton_call_price(-100.0, 100.0, 0.05, 1.0, 0.2, 1.0, 0.0, 0.1)

    def test_negative_jump_intensity_raises(self):
        with pytest.raises(ValueError):
            jd.merton_call_price(100.0, 100.0, 0.05, 1.0, 0.2, -1.0, 0.0, 0.1)


class TestMertonPutPrice:
    def test_converges_to_bs_when_no_jumps(self):
        S, K, r, T, sigma = 100.0, 100.0, 0.05, 1.0, 0.2
        merton = jd.merton_put_price(S, K, r, T, sigma, jump_intensity=0.0, jump_mean=0.0, jump_vol=0.0)
        black_scholes = bs.put_price(S, K, r, T, sigma)
        assert abs(merton - black_scholes) < 0.01

    def test_put_at_expiry(self):
        price = jd.merton_put_price(90.0, 100.0, 0.05, 0.0, 0.2, 1.0, -0.05, 0.15)
        assert price == 10.0


class TestMertonOptionPrice:
    def test_call_dispatch(self):
        price = jd.merton_option_price(100.0, 100.0, 0.05, 1.0, 0.2, jd.OptionType.CALL)
        expected = jd.merton_call_price(100.0, 100.0, 0.05, 1.0, 0.2, 2.0, -0.05, 0.15)
        assert abs(price - expected) < 1e-10

    def test_put_dispatch(self):
        price = jd.merton_option_price(100.0, 100.0, 0.05, 1.0, 0.2, jd.OptionType.PUT)
        expected = jd.merton_put_price(100.0, 100.0, 0.05, 1.0, 0.2, 2.0, -0.05, 0.15)
        assert abs(price - expected) < 1e-10

    def test_put_call_parity_no_jumps(self):
        """Put-call parity should hold approximately with no jumps."""
        from math import exp
        S, K, r, T, sigma = 100.0, 100.0, 0.05, 1.0, 0.2
        call = jd.merton_option_price(S, K, r, T, sigma, jd.OptionType.CALL, jump_intensity=0.0, jump_mean=0.0, jump_vol=0.0)
        put = jd.merton_option_price(S, K, r, T, sigma, jd.OptionType.PUT, jump_intensity=0.0, jump_mean=0.0, jump_vol=0.0)
        assert abs((call - put) - (S - K * exp(-r * T))) < 0.01
