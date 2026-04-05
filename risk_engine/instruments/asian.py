"""
Asian option implementation using Monte Carlo simulation.
"""

from risk_engine.instruments.base import Instrument, MarketData
from risk_engine.core.exotic import AverageTypeEnum, asian_option_price
from risk_engine.core.binomial import OptionType


class AsianOption(Instrument):
    """
    Asian option with payoff based on average underlying price.

    Types:
    - Arithmetic: Average of prices
    - Geometric: Geometric average of prices
    """

    def __init__(
        self,
        option_type: OptionType,
        strike: float,
        time_to_expiry: float,
        asset_id: str,
        average_type: AverageTypeEnum,
        num_fixings: int,
        running_sum: float = 0.0,
        past_fixings: int = 0,
    ):
        """
        Initialize an Asian option.

        Args:
            option_type: OptionType.CALL or OptionType.PUT
            strike: Strike price
            time_to_expiry: Time to expiry in years
            asset_id: Underlying asset identifier
            average_type: Type of averaging (arithmetic, geometric)
            num_fixings: Number of price observations
            running_sum: Running sum of past fixings (default 0)
            past_fixings: Number of already observed fixings (default 0)
        """
        self.option_type = option_type
        self.strike = strike
        self.time_to_expiry = time_to_expiry
        self.asset_id = asset_id.strip()
        self.average_type = average_type
        self.num_fixings = num_fixings
        self.running_sum = running_sum
        self.past_fixings = past_fixings

        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """Validate option parameters."""
        if self.strike <= 0:
            raise ValueError(f"Strike price must be positive, got {self.strike}")
        if self.time_to_expiry < 0:
            raise ValueError(
                f"Time to expiry cannot be negative, got {self.time_to_expiry}"
            )
        if not self.asset_id:
            raise ValueError("Asset ID cannot be empty")
        if self.num_fixings < 1:
            raise ValueError(
                f"Number of fixings must be positive, got {self.num_fixings}"
            )
        if self.past_fixings < 0 or self.past_fixings > self.num_fixings:
            raise ValueError(
                f"Past fixings must be between 0 and {self.num_fixings}, "
                f"got {self.past_fixings}"
            )

    def get_asset_id(self) -> str:
        """Get the underlying asset identifier."""
        return self.asset_id

    def get_instrument_type(self) -> str:
        """Get the type of instrument."""
        return "AsianOption"

    def price(self, md: MarketData) -> float:
        """Calculate the Asian option price."""
        self._validate_market_data(md)

        is_call = self.option_type == OptionType.CALL

        return asian_option_price(
            md.spot,
            self.strike,
            md.rate,
            self.time_to_expiry,
            md.vol,
            is_call,
            self.average_type,
            self.past_fixings,
            self.running_sum,
        )

    def delta(self, md: MarketData) -> float:
        """Calculate delta using numerical differentiation."""
        self._validate_market_data(md)

        bump = md.spot * 0.01

        md_up = MarketData(
            asset_id=md.asset_id,
            spot=md.spot + bump,
            rate=md.rate,
            vol=md.vol,
            dividend=md.dividend,
        )

        md_down = MarketData(
            asset_id=md.asset_id,
            spot=md.spot - bump,
            rate=md.rate,
            vol=md.vol,
            dividend=md.dividend,
        )

        return (self.price(md_up) - self.price(md_down)) / (2.0 * bump)

    def gamma(self, md: MarketData) -> float:
        """Calculate gamma using numerical differentiation."""
        self._validate_market_data(md)

        bump = md.spot * 0.01

        md_up = MarketData(
            asset_id=md.asset_id,
            spot=md.spot + bump,
            rate=md.rate,
            vol=md.vol,
            dividend=md.dividend,
        )

        md_down = MarketData(
            asset_id=md.asset_id,
            spot=md.spot - bump,
            rate=md.rate,
            vol=md.vol,
            dividend=md.dividend,
        )

        return (self.delta(md_up) - self.delta(md_down)) / (2.0 * bump)

    def vega(self, md: MarketData) -> float:
        """Calculate vega using numerical differentiation."""
        self._validate_market_data(md)

        bump = 0.01

        md_up = MarketData(
            asset_id=md.asset_id,
            spot=md.spot,
            rate=md.rate,
            vol=md.vol + bump,
            dividend=md.dividend,
        )

        md_down = MarketData(
            asset_id=md.asset_id,
            spot=md.spot,
            rate=md.rate,
            vol=max(0.0, md.vol - bump),
            dividend=md.dividend,
        )

        return (self.price(md_up) - self.price(md_down)) / (2.0 * bump)

    def theta(self, md: MarketData) -> float:
        """Calculate theta using numerical differentiation."""
        self._validate_market_data(md)

        bump = 1.0 / 365.0

        if self.time_to_expiry < bump:
            return 0.0

        current_price = self.price(md)

        temp_option = AsianOption(
            self.option_type,
            self.strike,
            max(0.0, self.time_to_expiry - bump),
            self.asset_id,
            self.average_type,
            self.num_fixings,
            self.running_sum,
            self.past_fixings,
        )

        future_price = temp_option.price(md)

        return (future_price - current_price) / bump
