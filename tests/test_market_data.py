"""Tests for MarketData dataclass."""

import pytest
from risk_engine.market_data.market_data import MarketData


class TestMarketDataValidation:
    def test_valid_construction(self):
        md = MarketData(asset_id="AAPL", spot=150.0, rate=0.05, vol=0.2)
        assert md.asset_id == "AAPL"
        assert md.spot == 150.0
        assert md.dividend == 0.0  # default

    def test_empty_asset_id_raises(self):
        with pytest.raises(ValueError):
            MarketData(asset_id="", spot=100.0, rate=0.05, vol=0.2)

    def test_whitespace_asset_id_raises(self):
        with pytest.raises(ValueError):
            MarketData(asset_id="   ", spot=100.0, rate=0.05, vol=0.2)

    def test_negative_spot_raises(self):
        with pytest.raises(ValueError):
            MarketData(asset_id="AAPL", spot=-1.0, rate=0.05, vol=0.2)

    def test_zero_spot_raises(self):
        with pytest.raises(ValueError):
            MarketData(asset_id="AAPL", spot=0.0, rate=0.05, vol=0.2)

    def test_negative_vol_raises(self):
        with pytest.raises(ValueError):
            MarketData(asset_id="AAPL", spot=100.0, rate=0.05, vol=-0.1)

    def test_zero_vol_allowed(self):
        """Zero volatility is technically valid (no uncertainty)."""
        md = MarketData(asset_id="AAPL", spot=100.0, rate=0.05, vol=0.0)
        assert md.vol == 0.0

    def test_negative_rate_allowed(self):
        """Negative risk-free rates are valid (e.g., ZIRP/NIRP environments)."""
        md = MarketData(asset_id="AAPL", spot=100.0, rate=-0.01, vol=0.2)
        assert md.rate == -0.01

    def test_negative_dividend_raises(self):
        with pytest.raises(ValueError):
            MarketData(asset_id="AAPL", spot=100.0, rate=0.05, vol=0.2, dividend=-0.01)

    def test_positive_dividend_allowed(self):
        md = MarketData(asset_id="AAPL", spot=100.0, rate=0.05, vol=0.2, dividend=0.03)
        assert md.dividend == 0.03


class TestMarketDataSerialization:
    def test_to_dict(self):
        md = MarketData(asset_id="AAPL", spot=150.0, rate=0.05, vol=0.25, dividend=0.01)
        d = md.to_dict()
        assert d["asset_id"] == "AAPL"
        assert d["spot"] == 150.0
        assert d["rate"] == 0.05
        assert d["vol"] == 0.25
        assert d["dividend"] == 0.01

    def test_from_dict_round_trip(self):
        md = MarketData(asset_id="MSFT", spot=300.0, rate=0.04, vol=0.18, dividend=0.02)
        restored = MarketData.from_dict(md.to_dict())
        assert restored.asset_id == md.asset_id
        assert restored.spot == md.spot
        assert restored.rate == md.rate
        assert restored.vol == md.vol
        assert restored.dividend == md.dividend

    def test_from_dict_missing_dividend_defaults_zero(self):
        d = {"asset_id": "TSLA", "spot": 200.0, "rate": 0.05, "vol": 0.4}
        md = MarketData.from_dict(d)
        assert md.dividend == 0.0

    def test_from_dict_string_values_coerced(self):
        d = {"asset_id": "GOOG", "spot": "2800.0", "rate": "0.05", "vol": "0.22"}
        md = MarketData.from_dict(d)
        assert isinstance(md.spot, float)
        assert md.spot == 2800.0
