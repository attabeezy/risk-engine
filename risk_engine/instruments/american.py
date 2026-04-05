"""
American option implementation using binomial tree.
"""

from risk_engine.instruments.base import Instrument, MarketData
from risk_engine.core import binomial


class AmericanOption(Instrument):
    """
    American option using binomial tree with early exercise.

    Early exercise is allowed at any time before expiry.
    """

    def __init__(
        self,
        option_type: binomial.OptionType,
        strike: float,
        time_to_expiry: float,
        asset_id: str,
        binomial_steps: int = 100,
    ):
        """
        Initialize an American option.

        Args:
            option_type: OptionType.CALL or OptionType.PUT
            strike: Strike price
            time_to_expiry: Time to expiry in years
            asset_id: Underlying asset identifier
            binomial_steps: Number of binomial steps (default 100)
        """
        self.option_type = option_type
        self.strike = strike
        self.time_to_expiry = time_to_expiry
        self.asset_id = asset_id.strip()
        self.binomial_steps = binomial_steps

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
        if self.binomial_steps < 1 or self.binomial_steps > 10000:
            raise ValueError(
                f"Binomial steps must be between 1 and 10000, got {self.binomial_steps}"
            )

    def get_asset_id(self) -> str:
        """Get the underlying asset identifier."""
        return self.asset_id

    def get_instrument_type(self) -> str:
        """Get the type of instrument."""
        return "AmericanOption"

    def price(self, md: MarketData) -> float:
        """Calculate the American option price using binomial tree."""
        self._validate_market_data(md)

        if self.time_to_expiry <= 0:
            if self.option_type == binomial.OptionType.CALL:
                return max(0.0, md.spot - self.strike)
            else:
                return max(0.0, self.strike - md.spot)

        return binomial.american_option_price(
            md.spot,
            self.strike,
            md.rate,
            self.time_to_expiry,
            md.vol,
            self.option_type,
            self.binomial_steps,
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

        temp_option = AmericanOption(
            self.option_type,
            self.strike,
            max(0.0, self.time_to_expiry - bump),
            self.asset_id,
            self.binomial_steps,
        )

        future_price = temp_option.price(md)

        return (future_price - current_price) / bump

    def set_binomial_steps(self, steps: int) -> None:
        """Set number of binomial steps."""
        if steps < 1 or steps > 10000:
            raise ValueError(f"Binomial steps must be between 1 and 10000, got {steps}")
        self.binomial_steps = steps
