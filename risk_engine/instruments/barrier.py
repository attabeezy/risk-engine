"""
Barrier option implementation.
"""

from risk_engine.instruments.base import Instrument, MarketData
from risk_engine.core.exotic import BarrierTypeEnum, barrier_option_price
from risk_engine.core.binomial import OptionType


class BarrierOption(Instrument):
    """
    Barrier option that activates/deactivates when price hits barrier.

    Types:
    - DownIn: Activates when price drops below barrier
    - DownOut: Deactivates when price drops below barrier
    - UpIn: Activates when price rises above barrier
    - UpOut: Deactivates when price rises above barrier
    """

    def __init__(
        self,
        option_type: OptionType,
        strike: float,
        barrier: float,
        barrier_type: BarrierTypeEnum,
        time_to_expiry: float,
        asset_id: str,
        rebate: float = 0.0,
    ):
        self.option_type = option_type
        self.strike = strike
        self.barrier = barrier
        self.barrier_type = barrier_type
        self.time_to_expiry = time_to_expiry
        self.asset_id = asset_id.strip()
        self.rebate = rebate

        self._validate_parameters()

    def _validate_parameters(self) -> None:
        if self.strike <= 0:
            raise ValueError(f"Strike price must be positive, got {self.strike}")
        if self.barrier <= 0:
            raise ValueError(f"Barrier level must be positive, got {self.barrier}")
        if self.time_to_expiry < 0:
            raise ValueError(
                f"Time to expiry cannot be negative, got {self.time_to_expiry}"
            )
        if not self.asset_id:
            raise ValueError("Asset ID cannot be empty")
        if self.rebate < 0:
            raise ValueError(f"Rebate cannot be negative, got {self.rebate}")

    def get_asset_id(self) -> str:
        return self.asset_id

    def get_instrument_type(self) -> str:
        return "BarrierOption"

    def price(self, md: MarketData) -> float:
        self._validate_market_data(md)
        is_call = self.option_type == OptionType.CALL
        return barrier_option_price(
            md.spot,
            self.strike,
            self.barrier,
            md.rate,
            self.time_to_expiry,
            md.vol,
            is_call,
            self.barrier_type,
            self.rebate,
        )

    def delta(self, md: MarketData) -> float:
        self._validate_market_data(md)
        bump = md.spot * 0.01
        md_up = MarketData(md.asset_id, md.spot + bump, md.rate, md.vol, md.dividend)
        md_down = MarketData(md.asset_id, md.spot - bump, md.rate, md.vol, md.dividend)
        return (self.price(md_up) - self.price(md_down)) / (2.0 * bump)

    def gamma(self, md: MarketData) -> float:
        self._validate_market_data(md)
        bump = md.spot * 0.01
        md_up = MarketData(md.asset_id, md.spot + bump, md.rate, md.vol, md.dividend)
        md_down = MarketData(md.asset_id, md.spot - bump, md.rate, md.vol, md.dividend)
        return (self.delta(md_up) - self.delta(md_down)) / (2.0 * bump)

    def vega(self, md: MarketData) -> float:
        self._validate_market_data(md)
        bump = 0.01
        md_up = MarketData(md.asset_id, md.spot, md.rate, md.vol + bump, md.dividend)
        md_down = MarketData(
            md.asset_id, md.spot, md.rate, max(0.0, md.vol - bump), md.dividend
        )
        return (self.price(md_up) - self.price(md_down)) / (2.0 * bump)

    def theta(self, md: MarketData) -> float:
        self._validate_market_data(md)
        bump = 1.0 / 365.0
        if self.time_to_expiry < bump:
            return 0.0
        current_price = self.price(md)
        temp = BarrierOption(
            self.option_type,
            self.strike,
            self.barrier,
            self.barrier_type,
            max(0.0, self.time_to_expiry - bump),
            self.asset_id,
            self.rebate,
        )
        future_price = temp.price(md)
        return (future_price - current_price) / bump
