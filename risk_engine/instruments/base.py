"""
Base instrument class for all derivatives.
"""

from abc import ABC, abstractmethod
from typing import Optional

from risk_engine.market_data.market_data import MarketData


class Instrument(ABC):
    """Abstract base class for all financial instruments."""

    @abstractmethod
    def price(self, md: MarketData) -> float:
        """Calculate the price of the instrument."""
        pass

    @abstractmethod
    def delta(self, md: MarketData) -> float:
        """Calculate the delta (sensitivity to spot price)."""
        pass

    @abstractmethod
    def gamma(self, md: MarketData) -> float:
        """Calculate the gamma (second derivative to spot)."""
        pass

    @abstractmethod
    def vega(self, md: MarketData) -> float:
        """Calculate the vega (sensitivity to volatility)."""
        pass

    @abstractmethod
    def theta(self, md: MarketData) -> float:
        """Calculate the theta (time decay per day)."""
        pass

    @abstractmethod
    def get_asset_id(self) -> str:
        """Get the underlying asset identifier."""
        pass

    @abstractmethod
    def get_instrument_type(self) -> str:
        """Get the type of instrument (e.g., 'EuropeanOption')."""
        pass

    def is_valid(self) -> bool:
        """Check if instrument parameters are valid."""
        try:
            self._validate_parameters()
            return True
        except Exception:
            return False

    @abstractmethod
    def _validate_parameters(self) -> None:
        """Validate instrument-specific parameters."""
        pass

    def _validate_market_data(self, md: MarketData) -> None:
        """Validate market data for pricing."""
        if md.spot <= 0:
            raise ValueError(f"Spot price must be positive, got {md.spot}")
        if md.vol < 0:
            raise ValueError(f"Volatility cannot be negative, got {md.vol}")

    @staticmethod
    def _numerical_derivative(func, md: MarketData, bump: float = 0.01) -> float:
        """
        Calculate numerical derivative using central difference.

        Args:
            func: Pricing function to differentiate
            md: Market data
            bump: Relative bump size (default 1%)

        Returns:
            Numerical derivative
        """
        spot = md.spot
        abs_bump = spot * bump

        md_up = MarketData(
            asset_id=md.asset_id,
            spot=spot + abs_bump,
            rate=md.rate,
            vol=md.vol,
            dividend=md.dividend,
        )

        md_down = MarketData(
            asset_id=md.asset_id,
            spot=spot - abs_bump,
            rate=md.rate,
            vol=md.vol,
            dividend=md.dividend,
        )

        return (func(md_up) - func(md_down)) / (2.0 * abs_bump)
