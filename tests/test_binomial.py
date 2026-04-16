"""Tests for binomial tree option pricing."""

import pytest
from risk_engine.core import binomial
from risk_engine.core import blackscholes as bs


class TestEuropeanBinomial:
    def test_call_converges_to_black_scholes(self):
        """European binomial price should approach B-S as steps increase."""
        S, K, r, T, sigma = 100.0, 100.0, 0.05, 1.0, 0.2
        bs_price = bs.call_price(S, K, r, T, sigma)
        bin_price = binomial.european_option_price(S, K, r, T, sigma, binomial.OptionType.CALL, steps=500)
        assert abs(bin_price - bs_price) < 0.05

    def test_put_converges_to_black_scholes(self):
        S, K, r, T, sigma = 100.0, 100.0, 0.05, 1.0, 0.2
        bs_price = bs.put_price(S, K, r, T, sigma)
        bin_price = binomial.european_option_price(S, K, r, T, sigma, binomial.OptionType.PUT, steps=500)
        assert abs(bin_price - bs_price) < 0.05

    def test_call_intrinsic_at_expiry(self):
        price = binomial.european_option_price(110.0, 100.0, 0.05, 0.0, 0.2, binomial.OptionType.CALL)
        assert price == 10.0

    def test_put_intrinsic_at_expiry(self):
        price = binomial.european_option_price(90.0, 100.0, 0.05, 0.0, 0.2, binomial.OptionType.PUT)
        assert price == 10.0

    def test_call_positive(self):
        price = binomial.european_option_price(100.0, 100.0, 0.05, 1.0, 0.2, binomial.OptionType.CALL)
        assert price > 0

    def test_dividend_reduces_call(self):
        S, K, r, T, sigma = 100.0, 100.0, 0.05, 1.0, 0.2
        price_no_div = binomial.european_option_price(S, K, r, T, sigma, binomial.OptionType.CALL, dividend=0.0)
        price_with_div = binomial.european_option_price(S, K, r, T, sigma, binomial.OptionType.CALL, dividend=0.03)
        assert price_with_div < price_no_div


class TestAmericanBinomial:
    def test_american_call_ge_european_call(self):
        """American call should be >= European call (ignoring dividends)."""
        S, K, r, T, sigma = 100.0, 100.0, 0.05, 1.0, 0.2
        american = binomial.american_option_price(S, K, r, T, sigma, binomial.OptionType.CALL)
        european = binomial.european_option_price(S, K, r, T, sigma, binomial.OptionType.CALL)
        assert american >= european - 1e-6

    def test_american_put_ge_european_put(self):
        """American put should be >= European put due to early exercise premium."""
        S, K, r, T, sigma = 100.0, 100.0, 0.05, 1.0, 0.2
        american = binomial.american_option_price(S, K, r, T, sigma, binomial.OptionType.PUT)
        european = binomial.european_option_price(S, K, r, T, sigma, binomial.OptionType.PUT)
        assert american >= european - 1e-6

    def test_american_put_early_exercise_premium(self):
        """Deep ITM American put should have meaningful early exercise premium."""
        S, K, r, T, sigma = 60.0, 100.0, 0.05, 1.0, 0.2
        american = binomial.american_option_price(S, K, r, T, sigma, binomial.OptionType.PUT)
        european = binomial.european_option_price(S, K, r, T, sigma, binomial.OptionType.PUT)
        assert american > european

    def test_american_call_intrinsic_at_expiry(self):
        price = binomial.american_option_price(110.0, 100.0, 0.05, 0.0, 0.2, binomial.OptionType.CALL)
        assert price == 10.0

    def test_invalid_steps(self):
        with pytest.raises(ValueError):
            binomial.american_option_price(100.0, 100.0, 0.05, 1.0, 0.2, binomial.OptionType.CALL, steps=0)

    def test_negative_spot_raises(self):
        with pytest.raises(ValueError):
            binomial.american_option_price(-100.0, 100.0, 0.05, 1.0, 0.2, binomial.OptionType.CALL)
