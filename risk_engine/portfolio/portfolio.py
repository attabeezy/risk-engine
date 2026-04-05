"""
Portfolio management for risk calculations.
"""

from typing import List, Tuple, Dict
from risk_engine.instruments.base import Instrument, MarketData


class Portfolio:
    """
    Portfolio of financial instruments.

    Holds multiple instruments with their quantities and provides
    aggregation methods for risk metrics.
    """

    def __init__(self):
        """Initialize an empty portfolio."""
        self._instruments: List[Tuple[Instrument, int]] = []

    def add_instrument(self, instrument: Instrument, quantity: int) -> None:
        """
        Add an instrument to the portfolio.

        Args:
            instrument: The financial instrument
            quantity: Number of contracts (can be negative for short positions)
        """
        if instrument is None:
            raise ValueError("Cannot add null instrument to portfolio")

        asset_id = instrument.get_asset_id()
        if not asset_id:
            raise ValueError("Instrument must have a valid asset ID")

        self._instruments.append((instrument, quantity))

    def get_instruments(self) -> List[Tuple[Instrument, int]]:
        """Get all instruments in the portfolio."""
        return self._instruments.copy()

    def size(self) -> int:
        """Get the number of positions in the portfolio."""
        return len(self._instruments)

    def is_empty(self) -> bool:
        """Check if portfolio is empty."""
        return len(self._instruments) == 0

    def clear(self) -> None:
        """Remove all instruments from the portfolio."""
        self._instruments.clear()

    def get_total_quantity_for_asset(self, asset_id: str) -> int:
        """
        Get total quantity for a specific asset.

        Args:
            asset_id: Asset identifier

        Returns:
            Net quantity for the asset
        """
        if not asset_id:
            raise ValueError("Asset ID cannot be empty")

        total = 0
        for instrument, quantity in self._instruments:
            if instrument.get_asset_id() == asset_id:
                total += quantity

        return total

    def remove_instrument(self, index: int) -> None:
        """Remove instrument at the given index."""
        if index < 0 or index >= len(self._instruments):
            raise IndexError(
                f"Index {index} out of range. Portfolio size: {len(self._instruments)}"
            )
        self._instruments.pop(index)

    def update_quantity(self, index: int, new_quantity: int) -> None:
        """Update the quantity of an instrument at the given index."""
        if index < 0 or index >= len(self._instruments):
            raise IndexError(
                f"Index {index} out of range. Portfolio size: {len(self._instruments)}"
            )
        self._instruments[index] = (self._instruments[index][0], new_quantity)

    def __len__(self) -> int:
        """Get portfolio size."""
        return len(self._instruments)

    def __iter__(self):
        """Iterate over instruments."""
        return iter(self._instruments)

    def get_unique_assets(self) -> set:
        """Get set of unique asset IDs in portfolio."""
        return {inst.get_asset_id() for inst, _ in self._instruments}
