# Quick Start Guide

Get the Quant Enthusiasts Risk Engine running in under 5 minutes.

## Prerequisites

- Python 3.11+

## Quick Setup

### 1. Install Dependencies

```bash
# Clone repository
git clone https://github.com/Quant-Enthusiasts/Quant-Enthusiasts-Risk-Engine.git
cd Quant-Enthusiasts-Risk-Engine

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in editable mode
pip install -e .
```

### 2. Run the Dashboard

```bash
streamlit run dashboard/app.py
```

Dashboard is now running at `http://localhost:8501`

## Test Your Installation

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

## Dashboard Features

The Streamlit dashboard provides:

1. **Portfolio Builder** - Add European/American options with various pricing models
2. **Risk Analysis** - View Greeks, VaR, Expected Shortfall with live market data
3. **Market Data** - Fetch data from Yahoo Finance with historical charts
4. **Visualizations** - Option payoff diagrams and Greeks exposure
5. **Greeks Analysis** - Delta/Gamma/Vega heatmaps and 3D IV surface

## Common Issues

### "ModuleNotFoundError: risk_engine"

**Fix**: Install the package in editable mode
```bash
pip install -e .
```

### "yfinance not installed"

**Fix**: Install yfinance
```bash
pip install yfinance
```

## Next Steps

- **API Reference**: See [api_reference.md](api_reference.md) for REST API docs
- **Market Data**: Read [market_data_guide.md](market_data_guide.md) for YFinance integration
- **Development**: Check [development_guide.md](development_guide.md) to contribute

---

**Setup complete!** You now have a working quantitative finance risk engine.
