"""
Market data types and classes.
"""

from dataclasses import dataclass


@dataclass
class MarketData:
    """Market data required for pricing."""

    asset_id: str
    spot: float
    rate: float
    vol: float
    dividend: float = 0.0

    def __post_init__(self):
        if not self.asset_id or not self.asset_id.strip():
            raise ValueError("Asset ID cannot be empty")
        if self.spot <= 0:
            raise ValueError(f"Spot price must be positive, got {self.spot}")
        if self.vol < 0:
            raise ValueError(f"Volatility cannot be negative, got {self.vol}")
        if self.dividend < 0:
            raise ValueError(f"Dividend yield cannot be negative, got {self.dividend}")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "asset_id": self.asset_id,
            "spot": self.spot,
            "rate": self.rate,
            "vol": self.vol,
            "dividend": self.dividend,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MarketData":
        """Create from dictionary."""
        return cls(
            asset_id=data["asset_id"],
            spot=float(data["spot"]),
            rate=float(data["rate"]),
            vol=float(data["vol"]),
            dividend=float(data.get("dividend", 0.0)),
        )
