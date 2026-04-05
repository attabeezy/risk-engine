# Quant Enthusiasts Risk Engine

A high-performance pure Python quantitative finance platform for portfolio risk management and options pricing.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)

## Overview

Pure Python quantitative finance platform offering:

- **Multiple Pricing Models**: Black-Scholes, Binomial Tree, Merton Jump Diffusion
- **Exotic Options**: Barrier and Asian options via Monte Carlo simulation
- **Risk Analytics**: Greeks calculation, Value at Risk (Monte Carlo with Numba), Portfolio aggregation
- **Live Market Data**: Automatic fetching from Yahoo Finance with SQLite caching
- **Web Dashboard**: Interactive Streamlit-based portfolio builder and risk visualizer

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Install the package in editable mode (required for imports)
pip install -e .

# Run the Streamlit dashboard
streamlit run dashboard/app.py
```

Server runs at `http://localhost:8501`

## Architecture

```
Streamlit Dashboard
        |
        | (direct Python calls)
        v
  risk_engine/          # Core Python package
  ├── core/             # Pricing models (BS, Binomial, Jump Diffusion)
  ├── instruments/      # Option classes
  ├── portfolio/        # Risk engine with Numba VaR
  └── market_data/      # YFinance fetcher + SQLite cache
```

## Core Features

| Model | Type | Options | Key Features |
|-------|------|---------|--------------|
| Black-Scholes | Analytical | European | Fast, Greeks calculation |
| Binomial Tree | Numerical | European/American | Early exercise, configurable steps |
| Merton Jump Diffusion | Analytical | European | Discontinuous jumps |
| QuantLib | Monte Carlo | Barrier/Asian | Exotic options |

### Risk Metrics

- **Greeks**: Delta, Gamma, Vega, Theta, Rho
- **VaR**: Monte Carlo simulation with Numba JIT acceleration
- **Expected Shortfall**: 95%/99% confidence levels
- **Portfolio Analytics**: Net positions, PV aggregation

### Market Data Integration

- Automatic fetching from Yahoo Finance
- SQLite-based caching (24-hour expiration)
- Volatility calculation from historical data

## Usage Example

```python
from risk_engine import (
    EuropeanOption,
    Portfolio,
    RiskEngine,
    MarketData,
    OptionType,
    PricingModel,
)

# Create an option
option = EuropeanOption(
    OptionType.CALL,
    strike=180.0,
    time_to_expiry=1.0,
    asset_id="AAPL",
    pricing_model=PricingModel.BLACKSCHOLES
)

# Create market data
md = MarketData(
    asset_id="AAPL",
    spot=175.0,
    rate=0.05,
    vol=0.25
)

# Price the option
price = option.price(md)
print(f"Option price: ${price:.2f}")

# Build portfolio and calculate risk
portfolio = Portfolio()
portfolio.add_instrument(option, quantity=100)

engine = RiskEngine(var_simulations=10000)
result = engine.calculate_portfolio_risk(portfolio, {"AAPL": md})

print(f"Total PV: ${result.total_pv:,.2f}")
print(f"VaR 95%: ${result.value_at_risk_95:,.2f}")
```

## Dashboard

The Streamlit dashboard provides:

1. **Portfolio Builder** - Add European/American options with various pricing models, view portfolio allocation
2. **Risk Analysis** - View Greeks, VaR, Expected Shortfall with auto-fetch market data
3. **Market Data** - Fetch live stock data from Yahoo Finance with historical price charts
4. **Visualizations** - Option payoff diagrams and Greeks exposure charts
5. **Greeks Analysis** - Delta/Gamma/Vega heatmaps and 3D implied volatility surface

Run with:
```bash
streamlit run dashboard/app.py
```

## Testing

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Dependencies

- **numpy**, **scipy** - Numerical computing
- **numba** - JIT compilation for Monte Carlo VaR
- **QuantLib-Python** - Exotic option pricing
- **yfinance** - Market data fetching
- **streamlit** - Web dashboard
- **plotly** - Interactive charts

## License

MIT License - See [LICENSE](LICENSE) for details.

---

**Made by Quant Enthusiasts**
