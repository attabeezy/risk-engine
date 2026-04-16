"""Tests for the Portfolio class."""

import pytest
from risk_engine.portfolio.portfolio import Portfolio
from risk_engine.instruments.european import EuropeanOption, OptionType, PricingModel


def _make_option(strike=100.0, expiry=1.0, asset="AAPL", opt_type=OptionType.CALL):
    return EuropeanOption(opt_type, strike, expiry, asset)


class TestPortfolioBasics:
    def test_empty_on_init(self):
        p = Portfolio()
        assert p.is_empty()
        assert p.size() == 0

    def test_add_instrument(self):
        p = Portfolio()
        p.add_instrument(_make_option(), 10)
        assert p.size() == 1
        assert not p.is_empty()

    def test_add_multiple(self):
        p = Portfolio()
        p.add_instrument(_make_option(asset="AAPL"), 5)
        p.add_instrument(_make_option(asset="MSFT"), 3)
        assert p.size() == 2

    def test_add_null_raises(self):
        p = Portfolio()
        with pytest.raises(ValueError):
            p.add_instrument(None, 1)

    def test_clear(self):
        p = Portfolio()
        p.add_instrument(_make_option(), 10)
        p.clear()
        assert p.is_empty()

    def test_len(self):
        p = Portfolio()
        p.add_instrument(_make_option(), 10)
        assert len(p) == 1


class TestPortfolioQuantities:
    def test_get_total_quantity_single(self):
        p = Portfolio()
        p.add_instrument(_make_option(asset="AAPL"), 10)
        assert p.get_total_quantity_for_asset("AAPL") == 10

    def test_get_total_quantity_multiple_same_asset(self):
        p = Portfolio()
        p.add_instrument(_make_option(asset="AAPL", strike=100.0), 10)
        p.add_instrument(_make_option(asset="AAPL", strike=110.0), 5)
        assert p.get_total_quantity_for_asset("AAPL") == 15

    def test_get_total_quantity_missing_asset(self):
        p = Portfolio()
        p.add_instrument(_make_option(asset="AAPL"), 10)
        assert p.get_total_quantity_for_asset("MSFT") == 0

    def test_get_total_quantity_empty_id_raises(self):
        p = Portfolio()
        with pytest.raises(ValueError):
            p.get_total_quantity_for_asset("")

    def test_update_quantity(self):
        p = Portfolio()
        p.add_instrument(_make_option(), 10)
        p.update_quantity(0, 20)
        assert p.get_instruments()[0][1] == 20

    def test_update_quantity_out_of_range(self):
        p = Portfolio()
        with pytest.raises(IndexError):
            p.update_quantity(0, 5)

    def test_negative_quantity_short(self):
        """Negative quantity represents a short position — should be allowed."""
        p = Portfolio()
        p.add_instrument(_make_option(), -5)
        assert p.get_total_quantity_for_asset("AAPL") == -5


class TestPortfolioRemove:
    def test_remove_instrument(self):
        p = Portfolio()
        p.add_instrument(_make_option(asset="AAPL"), 10)
        p.add_instrument(_make_option(asset="MSFT"), 5)
        p.remove_instrument(0)
        assert p.size() == 1
        assert p.get_instruments()[0][0].get_asset_id() == "MSFT"

    def test_remove_out_of_range_raises(self):
        p = Portfolio()
        with pytest.raises(IndexError):
            p.remove_instrument(0)


class TestPortfolioAssets:
    def test_unique_assets(self):
        p = Portfolio()
        p.add_instrument(_make_option(asset="AAPL"), 1)
        p.add_instrument(_make_option(asset="AAPL"), 2)
        p.add_instrument(_make_option(asset="MSFT"), 1)
        assert p.get_unique_assets() == {"AAPL", "MSFT"}
