# API Reference

Python API documentation for the Risk Engine.

## Core Pricing Models

### Black-Scholes

```python
from risk_engine.core.black_scholes import black_scholes_price, black_scholes_greeks

# Price a call option
price = black_scholes_price(
    spot=100.0,      # Current stock price
    strike=100.0,    # Strike price
    rate=0.05,       # Risk-free rate (5%)
    vol=0.20,        # Volatility (20%)
    expiry=1.0,      # Time to expiry (years)
    is_call=True     # True for call, False for put
)

# Calculate Greeks
delta, gamma, vega, theta, rho = black_scholes_greeks(
    spot=100.0,
    strike=100.0,
    rate=0.05,
    vol=0.20,
    expiry=1.0,
    is_call=True
)
```

### Binomial Tree

```python
from risk_engine.core.binomial import binomial_price

# Price an American option
price = binomial_price(
    spot=100.0,
    strike=100.0,
    rate=0.05,
    vol=0.20,
    expiry=1.0,
    steps=100,           # Number of tree steps
    is_call=True,
    is_american=True     # True for American, False for European
)
```

### Jump Diffusion (Merton)

```python
from risk_engine.core.jump_diffusion import merton_jump_diffusion_price

price = merton_jump_diffusion_price(
    spot=100.0,
    strike=100.0,
    rate=0.05,
    vol=0.20,
    expiry=1.0,
    jump_intensity=2.0,  # Jumps per year
    jump_mean=-0.05,     # Mean jump size
    jump_vol=0.15,       # Jump volatility
    is_call=True
)
```

## Instruments

### European Option

```python
from risk_engine.instruments.european import EuropeanOption, OptionType
from risk_engine.market_data.market_data import MarketData

option = EuropeanOption(
    option_type=OptionType.CALL,
    strike=100.0,
    expiry=1.0,
    asset_id="AAPL"
)

market_data = MarketData(spot=105.0, rate=0.05, volatility=0.20)
price = option.price(market_data)
greeks = option.greeks(market_data)
```

### American Option

```python
from risk_engine.instruments.american import AmericanOption, OptionType

option = AmericanOption(
    option_type=OptionType.PUT,
    strike=100.0,
    expiry=1.0,
    asset_id="AAPL",
    steps=100
)
```

### Asian Option

```python
from risk_engine.instruments.asian import AsianOption, OptionType

option = AsianOption(
    option_type=OptionType.CALL,
    strike=100.0,
    expiry=1.0,
    asset_id="AAPL",
    n_steps=252,          # Averaging points
    simulations=100000    # Monte Carlo paths
)
```

### Barrier Option

```python
from risk_engine.instruments.barrier import BarrierOption, OptionType, BarrierType

option = BarrierOption(
    option_type=OptionType.CALL,
    strike=100.0,
    expiry=1.0,
    asset_id="AAPL",
    barrier=120.0,
    barrier_type=BarrierType.UP_AND_OUT
)
```

## Portfolio

### Creating a Portfolio

```python
from risk_engine.portfolio.portfolio import Portfolio
from risk_engine.instruments.european import EuropeanOption, OptionType

portfolio = Portfolio()

# Add instruments
call = EuropeanOption(OptionType.CALL, strike=100, expiry=1.0, asset_id="AAPL")
put = EuropeanOption(OptionType.PUT, strike=95, expiry=0.5, asset_id="AAPL")

portfolio.add_instrument(call, quantity=100)   # Long 100 calls
portfolio.add_instrument(put, quantity=-50)    # Short 50 puts

# Portfolio info
print(f"Size: {portfolio.size()}")
print(f"Assets: {portfolio.get_unique_assets()}")
```

### Portfolio Valuation

```python
market_data = {"AAPL": MarketData(spot=105, rate=0.05, volatility=0.25)}
total_pv = portfolio.total_pv(market_data)
```

## Risk Engine

### Calculate VaR

```python
from risk_engine.portfolio.risk_engine import RiskEngine

engine = RiskEngine(
    simulations=100000,
    confidence_level=0.95
)

results = engine.calculate_portfolio_risk(
    portfolio=portfolio,
    market_data=market_data
)

print(f"Total PV: ${results['total_pv']:.2f}")
print(f"VaR 95%: ${results['var_95']:.2f}")
print(f"VaR 99%: ${results['var_99']:.2f}")
print(f"CVaR 95%: ${results['cvar_95']:.2f}")
```

### Results Dictionary

```python
{
    "total_pv": 12345.67,           # Portfolio present value
    "total_delta": 0.65,            # Aggregate delta
    "total_gamma": 0.02,            # Aggregate gamma
    "total_vega": 456.78,           # Aggregate vega
    "total_theta": -12.34,          # Aggregate theta
    "var_95": -5678.90,             # 95% VaR
    "var_99": -7890.12,             # 99% VaR
    "cvar_95": -6543.21,            # 95% Expected Shortfall
    "cvar_99": -8901.23             # 99% Expected Shortfall
}
```

## Market Data

### MarketData Class

```python
from risk_engine.market_data.market_data import MarketData

market_data = MarketData(
    spot=175.0,          # Current price
    rate=0.05,           # Risk-free rate
    volatility=0.25,     # Annualized volatility
    dividend=0.005       # Dividend yield (optional)
)
```

### Fetching from Yahoo Finance

```python
from risk_engine.market_data.fetcher import MarketDataFetcher

fetcher = MarketDataFetcher()

# Single ticker
data = fetcher.fetch_single("AAPL")

# Multiple tickers
data_dict = fetcher.fetch_multiple(["AAPL", "GOOGL", "MSFT"])

# Force refresh (bypass cache)
data = fetcher.fetch_single("AAPL", force_refresh=True)
```

### Market Data Cache

```python
from risk_engine.market_data.cache import MarketDataCache

cache = MarketDataCache(db_path="market_data_cache.db")

# Get cached data
data = cache.get("AAPL")

# Save data
cache.save("AAPL", market_data_dict)

# Clear cache
cache.clear()
```

## Example: Complete Workflow

```python
from risk_engine.portfolio.portfolio import Portfolio
from risk_engine.portfolio.risk_engine import RiskEngine
from risk_engine.instruments.european import EuropeanOption, OptionType
from risk_engine.market_data.fetcher import MarketDataFetcher

# 1. Fetch market data
fetcher = MarketDataFetcher()
market_data = fetcher.fetch_multiple(["AAPL", "GOOGL"])

# 2. Build portfolio
portfolio = Portfolio()
portfolio.add_instrument(
    EuropeanOption(OptionType.CALL, 180, 1.0, "AAPL"), 
    quantity=100
)
portfolio.add_instrument(
    EuropeanOption(OptionType.PUT, 140, 0.5, "GOOGL"), 
    quantity=-50
)

# 3. Calculate risk
engine = RiskEngine(simulations=100000)
results = engine.calculate_portfolio_risk(portfolio, market_data)

# 4. Display results
print(f"Portfolio Value: ${results['total_pv']:,.2f}")
print(f"Delta: {results['total_delta']:.4f}")
print(f"VaR (95%): ${results['var_95']:,.2f}")
print(f"Expected Shortfall (95%): ${results['cvar_95']:,.2f}")
```

## Version

Current version: **4.0.0** (Pure Python)
