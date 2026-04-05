"""
European option implementation.
"""

from enum import Enum
from risk_engine.instruments.base import Instrument, MarketData
from risk_engine.core import blackscholes as bs
from risk_engine.core import binomial
from risk_engine.core import jump_diffusion as jd


class OptionType(Enum):
    CALL = "call"
    PUT = "put"


class PricingModel(Enum):
    BLACKSCHOLES = "blackscholes"
    BINOMIAL = "binomial"
    MERTON_JUMP_DIFFUSION = "jumpdiffusion"


class EuropeanOption(Instrument):
    """
    European option that can be priced using different models.

    Supports:
    - Black-Scholes (default)
    - Binomial tree
    - Merton Jump Diffusion
    """

    def __init__(
        self,
        option_type: OptionType,
        strike: float,
        time_to_expiry: float,
        asset_id: str,
        pricing_model: PricingModel = PricingModel.BLACKSCHOLES,
        binomial_steps: int = 100,
        jump_intensity: float = 2.0,
        jump_mean: float = -0.05,
        jump_vol: float = 0.15,
    ):
        """
        Initialize a European option.

        Args:
            option_type: CALL or PUT
            strike: Strike price
            time_to_expiry: Time to expiry in years
            asset_id: Underlying asset identifier
            pricing_model: Pricing model to use (default BlackScholes)
            binomial_steps: Number of steps for binomial model (default 100)
            jump_intensity: Jump intensity for Merton model (default 2.0)
            jump_mean: Mean log jump size for Merton model (default -0.05)
            jump_vol: Jump volatility for Merton model (default 0.15)
        """
        self.option_type = option_type
        self.strike = strike
        self.time_to_expiry = time_to_expiry
        self.asset_id = asset_id.strip()
        self.pricing_model = pricing_model
        self.binomial_steps = binomial_steps
        self.jump_intensity = jump_intensity
        self.jump_mean = jump_mean
        self.jump_vol = jump_vol

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
        if self.jump_intensity < 0:
            raise ValueError(
                f"Jump intensity cannot be negative, got {self.jump_intensity}"
            )

    def get_asset_id(self) -> str:
        """Get the underlying asset identifier."""
        return self.asset_id

    def get_instrument_type(self) -> str:
        """Get the type of instrument."""
        return "EuropeanOption"

    def price(self, md: MarketData) -> float:
        """Calculate the option price."""
        self._validate_market_data(md)

        if self.time_to_expiry <= 0:
            if self.option_type == OptionType.CALL:
                return max(0.0, md.spot - self.strike)
            else:
                return max(0.0, self.strike - md.spot)

        is_call = self.option_type == OptionType.CALL

        if self.pricing_model == PricingModel.BLACKSCHOLES:
            if is_call:
                return bs.call_price(
                    md.spot, self.strike, md.rate, self.time_to_expiry, md.vol
                )
            else:
                return bs.put_price(
                    md.spot, self.strike, md.rate, self.time_to_expiry, md.vol
                )

        elif self.pricing_model == PricingModel.BINOMIAL:
            opt_type = binomial.OptionType.CALL if is_call else binomial.OptionType.PUT
            return binomial.european_option_price(
                md.spot,
                self.strike,
                md.rate,
                self.time_to_expiry,
                md.vol,
                opt_type,
                self.binomial_steps,
            )

        else:  # Merton Jump Diffusion
            return jd.merton_option_price(
                md.spot,
                self.strike,
                md.rate,
                self.time_to_expiry,
                md.vol,
                jd.OptionType.CALL if is_call else jd.OptionType.PUT,
                self.jump_intensity,
                self.jump_mean,
                self.jump_vol,
            )

    def delta(self, md: MarketData) -> float:
        """Calculate delta (sensitivity to spot)."""
        self._validate_market_data(md)

        if self.pricing_model == PricingModel.BLACKSCHOLES:
            is_call = self.option_type == OptionType.CALL
            if is_call:
                return bs.call_delta(
                    md.spot, self.strike, md.rate, self.time_to_expiry, md.vol
                )
            else:
                return bs.put_delta(
                    md.spot, self.strike, md.rate, self.time_to_expiry, md.vol
                )
        else:
            return self._numerical_derivative(self.price, md)

    def gamma(self, md: MarketData) -> float:
        """Calculate gamma (second derivative to spot)."""
        self._validate_market_data(md)

        if self.pricing_model == PricingModel.BLACKSCHOLES:
            return bs.gamma(md.spot, self.strike, md.rate, self.time_to_expiry, md.vol)
        else:
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
        """Calculate vega (sensitivity to volatility)."""
        self._validate_market_data(md)

        if self.pricing_model == PricingModel.BLACKSCHOLES:
            return bs.vega(md.spot, self.strike, md.rate, self.time_to_expiry, md.vol)
        else:
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
        """Calculate theta (time decay per day)."""
        self._validate_market_data(md)

        if self.pricing_model == PricingModel.BLACKSCHOLES:
            is_call = self.option_type == OptionType.CALL
            if is_call:
                return bs.call_theta(
                    md.spot, self.strike, md.rate, self.time_to_expiry, md.vol
                )
            else:
                return bs.put_theta(
                    md.spot, self.strike, md.rate, self.time_to_expiry, md.vol
                )
        else:
            bump = 1.0 / 365.0

            if self.time_to_expiry < bump:
                return 0.0

            current_price = self.price(md)

            temp_option = EuropeanOption(
                self.option_type,
                self.strike,
                max(0.0, self.time_to_expiry - bump),
                self.asset_id,
                self.pricing_model,
                self.binomial_steps,
                self.jump_intensity,
                self.jump_mean,
                self.jump_vol,
            )

            future_price = temp_option.price(md)

            return (future_price - current_price) / bump

    def set_pricing_model(self, model: PricingModel) -> None:
        """Set the pricing model."""
        self.pricing_model = model

    def set_binomial_steps(self, steps: int) -> None:
        """Set number of binomial steps."""
        if steps < 1 or steps > 10000:
            raise ValueError(f"Binomial steps must be between 1 and 10000, got {steps}")
        self.binomial_steps = steps

    def set_jump_parameters(self, intensity: float, mean: float, vol: float) -> None:
        """Set jump diffusion parameters."""
        if intensity < 0:
            raise ValueError(f"Jump intensity must be non-negative, got {intensity}")
        if vol < 0:
            raise ValueError(f"Jump volatility must be non-negative, got {vol}")
        self.jump_intensity = intensity
        self.jump_mean = mean
        self.jump_vol = vol
