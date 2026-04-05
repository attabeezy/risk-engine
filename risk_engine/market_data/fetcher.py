"""
Market data fetcher using YFinance.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from risk_engine.market_data.cache import MarketDataCache
from risk_engine.market_data.market_data import MarketData

try:
    import yfinance as yf

    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_RISK_FREE_RATE = 0.045


class MarketDataFetcher:
    """Fetches live market data using YFinance with caching."""

    def __init__(self, cache: Optional[MarketDataCache] = None):
        self.cache = cache or MarketDataCache()

    def fetch_single(self, ticker: str, force_refresh: bool = False) -> Dict:
        """Fetch market data for a single ticker."""
        if not YFINANCE_AVAILABLE:
            raise ImportError(
                "yfinance is not installed. Install with: pip install yfinance"
            )

        ticker = ticker.upper().strip()

        if not ticker:
            raise ValueError("Ticker symbol cannot be empty")

        if not force_refresh:
            cached_data = self.cache.get(ticker)
            if cached_data:
                logger.info(f"Using cached data for {ticker}")
                return cached_data

        try:
            stock = yf.Ticker(ticker)

            info = stock.info
            spot_price = info.get("currentPrice") or info.get("regularMarketPrice")

            if not spot_price:
                hist = stock.history(period="1d")
                if hist.empty:
                    raise ValueError(f"No price data available for {ticker}")
                spot_price = hist["Close"].iloc[-1]

            dividend_yield = info.get("dividendYield", 0.0) or 0.0

            volatility = self._calculate_volatility(stock)

            risk_free_rate = self._get_risk_free_rate()

            result = {
                "asset_id": ticker,
                "spot": float(spot_price),
                "vol": float(volatility),
                "rate": float(risk_free_rate),
                "dividend": float(dividend_yield),
                "last_updated": datetime.now().isoformat(),
                "source": "yfinance",
            }

            self.cache.set(
                ticker,
                result["spot"],
                result["vol"],
                result["rate"],
                result["dividend"],
            )

            logger.info(f"Successfully fetched data for {ticker}")
            return result

        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")

    def fetch_multiple(
        self, tickers: List[str], force_refresh: bool = False
    ) -> Tuple[Dict, List]:
        """Fetch market data for multiple tickers."""
        successful = {}
        failed = []

        for ticker in tickers:
            try:
                data = self.fetch_single(ticker, force_refresh)
                successful[ticker] = data
            except Exception as e:
                logger.warning(f"Failed to fetch {ticker}: {str(e)}")
                failed.append({"ticker": ticker, "error": str(e)})

        return successful, failed

    def _calculate_volatility(self, stock, window_days: int = 252) -> float:
        """Calculate annualized historical volatility."""
        try:
            hist = stock.history(period="1y")

            if hist.empty or len(hist) < 30:
                logger.warning("Insufficient historical data, using default volatility")
                return 0.25

            returns = hist["Close"].pct_change().dropna()

            if len(returns) < 2:
                return 0.25

            volatility = returns.std() * (252**0.5)

            volatility = max(0.01, min(2.0, volatility))

            return volatility

        except Exception as e:
            logger.warning(f"Error calculating volatility: {str(e)}, using default")
            return 0.25

    def _get_risk_free_rate(self) -> float:
        """Get current risk-free rate from 10-year Treasury."""
        try:
            treasury = yf.Ticker("^TNX")
            hist = treasury.history(period="1d")

            if not hist.empty:
                rate = hist["Close"].iloc[-1] / 100.0
                return float(rate)
        except Exception:
            pass

        return DEFAULT_RISK_FREE_RATE


_market_data_fetcher = None


def get_market_data_fetcher() -> MarketDataFetcher:
    """Get or create global MarketDataFetcher instance."""
    global _market_data_fetcher
    if _market_data_fetcher is None:
        _market_data_fetcher = MarketDataFetcher()
    return _market_data_fetcher
