"""Tests for exotic options: barrier and Asian."""

import pytest
import numpy as np
from risk_engine.core.exotic import (
    barrier_option_price,
    asian_option_price,
    BarrierTypeEnum,
    AverageTypeEnum,
)
from risk_engine.core.blackscholes import call_price, put_price


class TestBarrierOption:
    S, K, r, T, sigma = 100.0, 100.0, 0.05, 1.0, 0.2

    def test_down_out_le_vanilla_call(self):
        """Down-and-out call <= vanilla call (barrier can only reduce value)."""
        np.random.seed(0)
        vanilla = call_price(self.S, self.K, self.r, self.T, self.sigma)
        barrier = barrier_option_price(
            self.S, self.K, 80.0, self.r, self.T, self.sigma,
            True, BarrierTypeEnum.DOWN_OUT,
        )
        assert barrier <= vanilla + 0.5  # allow small MC noise

    def test_up_out_le_vanilla_call(self):
        """Up-and-out call <= vanilla call."""
        np.random.seed(1)
        vanilla = call_price(self.S, self.K, self.r, self.T, self.sigma)
        barrier = barrier_option_price(
            self.S, self.K, 120.0, self.r, self.T, self.sigma,
            True, BarrierTypeEnum.UP_OUT,
        )
        assert barrier <= vanilla + 0.5

    def test_down_in_positive(self):
        np.random.seed(2)
        price = barrier_option_price(
            self.S, self.K, 80.0, self.r, self.T, self.sigma,
            True, BarrierTypeEnum.DOWN_IN,
        )
        assert price >= 0

    def test_barrier_put_positive(self):
        np.random.seed(3)
        price = barrier_option_price(
            self.S, self.K, 80.0, self.r, self.T, self.sigma,
            False, BarrierTypeEnum.DOWN_OUT,
        )
        assert price >= 0

    def test_at_expiry_itm_call(self):
        price = barrier_option_price(110.0, 100.0, 90.0, 0.05, 0.0, 0.2, True, BarrierTypeEnum.DOWN_OUT)
        assert price == 10.0

    def test_at_expiry_otm_call(self):
        price = barrier_option_price(90.0, 100.0, 80.0, 0.05, 0.0, 0.2, True, BarrierTypeEnum.DOWN_OUT)
        assert price == 0.0

    def test_negative_spot_raises(self):
        with pytest.raises(ValueError):
            barrier_option_price(-100.0, 100.0, 80.0, 0.05, 1.0, 0.2, True, BarrierTypeEnum.DOWN_OUT)

    def test_negative_strike_raises(self):
        with pytest.raises(ValueError):
            barrier_option_price(100.0, -100.0, 80.0, 0.05, 1.0, 0.2, True, BarrierTypeEnum.DOWN_OUT)

    def test_negative_barrier_raises(self):
        with pytest.raises(ValueError):
            barrier_option_price(100.0, 100.0, -80.0, 0.05, 1.0, 0.2, True, BarrierTypeEnum.DOWN_OUT)

    def test_negative_rebate_raises(self):
        with pytest.raises(ValueError):
            barrier_option_price(100.0, 100.0, 80.0, 0.05, 1.0, 0.2, True, BarrierTypeEnum.DOWN_OUT, rebate=-1.0)


class TestAsianOption:
    S, K, r, T, sigma = 100.0, 100.0, 0.05, 1.0, 0.2

    def test_asian_call_le_vanilla_call(self):
        """Asian call <= vanilla call (averaging reduces effective vol)."""
        np.random.seed(42)
        vanilla = call_price(self.S, self.K, self.r, self.T, self.sigma)
        asian = asian_option_price(
            self.S, self.K, self.r, self.T, self.sigma, is_call=True,
            average_type=AverageTypeEnum.ARITHMETIC,
        )
        assert asian <= vanilla + 0.5  # allow MC noise

    def test_asian_call_positive(self):
        np.random.seed(10)
        price = asian_option_price(
            self.S, self.K, self.r, self.T, self.sigma, is_call=True,
        )
        assert price > 0

    def test_asian_put_positive(self):
        np.random.seed(11)
        price = asian_option_price(
            self.S, self.K, self.r, self.T, self.sigma, is_call=False,
        )
        assert price > 0

    def test_at_expiry_itm_call(self):
        price = asian_option_price(110.0, 100.0, 0.05, 0.0, 0.2, is_call=True)
        assert price == 10.0

    def test_at_expiry_itm_put(self):
        price = asian_option_price(90.0, 100.0, 0.05, 0.0, 0.2, is_call=False)
        assert price == 10.0

    def test_negative_spot_raises(self):
        with pytest.raises(ValueError):
            asian_option_price(-100.0, 100.0, 0.05, 1.0, 0.2, is_call=True)

    def test_negative_strike_raises(self):
        with pytest.raises(ValueError):
            asian_option_price(100.0, -100.0, 0.05, 1.0, 0.2, is_call=True)

    def test_negative_past_fixings_raises(self):
        with pytest.raises(ValueError):
            asian_option_price(100.0, 100.0, 0.05, 1.0, 0.2, is_call=True, past_fixings=-1)
