# Frequently Asked Questions

Common questions about the Risk Engine.

## General Questions

### What is the Risk Engine?

A pure Python quantitative finance platform for portfolio risk management and options pricing. It features:
- Black-Scholes, Binomial, and Jump Diffusion pricing models
- Monte Carlo VaR calculations with Numba acceleration
- Real-time market data via Yahoo Finance
- Interactive Streamlit dashboard

### Who should use this?

- Quantitative analysts and traders
- Portfolio managers
- Students learning quantitative finance
- Researchers in financial mathematics
- Developers building fintech applications

### What platforms are supported?

Any platform that runs Python 3.9+:
- Windows 10/11
- macOS 11+
- Linux (Ubuntu, Debian, etc.)

## Features

### What option types are supported?

**Option Styles:**
- European options (exercise at expiry only)
- American options (exercise any time)
- Asian options (average price)
- Barrier options (knock-in/knock-out)

**Option Types:**
- Call options
- Put options

### What pricing models are available?

1. **Black-Scholes** - Analytical solution for European options
2. **Binomial Tree** - Numerical method for American options
3. **Monte Carlo** - For path-dependent exotic options
4. **Merton Jump Diffusion** - Incorporates price jumps

### What risk metrics are calculated?

**Greeks:**
- Delta, Gamma, Vega, Theta, Rho

**Risk Measures:**
- Value at Risk (VaR) at 95% and 99% confidence
- Expected Shortfall (CVaR)
- Portfolio present value

### How accurate are the calculations?

- **Black-Scholes**: Exact analytical solution
- **Binomial Tree**: Converges as steps increase (default: 100 steps)
- **Monte Carlo VaR**: Statistical accuracy improves with simulations (default: 100,000)

## Market Data

### Where does market data come from?

Yahoo Finance via the `yfinance` Python library. Data includes:
- Current spot prices
- Historical prices (for volatility calculation)
- Dividend yields
- Risk-free rate (10-year Treasury)

### Is the market data real-time?

Near real-time during market hours (15-20 minute delay typical). Outside market hours, uses last closing prices.

### Can I use my own market data?

Yes. Provide data directly:

```python
from risk_engine.market_data.market_data import MarketData

market_data = MarketData(
    spot=175.0,
    volatility=0.28,
    rate=0.045,
    dividend=0.005
)
```

### How is volatility calculated?

Historical volatility from 252 trading days:
1. Fetch daily prices
2. Calculate log returns
3. Compute standard deviation
4. Annualize: `σ_annual = σ_daily * sqrt(252)`

## Usage

### How do I price a single option?

```python
from risk_engine.core.black_scholes import black_scholes_price

price = black_scholes_price(
    spot=105, strike=100, rate=0.05,
    vol=0.25, expiry=1.0, is_call=True
)
```

### How do I calculate portfolio risk?

```python
from risk_engine.portfolio.risk_engine import RiskEngine
from risk_engine.portfolio.portfolio import Portfolio

portfolio = Portfolio()
# Add instruments...

engine = RiskEngine(simulations=100000)
results = engine.calculate_portfolio_risk(portfolio, market_data_dict)
```

### Can I run calculations offline?

Yes, if you provide market data directly instead of relying on Yahoo Finance fetching.

## Performance

### How fast are calculations?

Typical performance:
- Single option pricing: < 1 millisecond
- Portfolio (100 options): < 10 milliseconds
- VaR (100K simulations): 1-3 seconds

Numba JIT compilation makes first run slower, subsequent runs are fast.

### How can I improve performance?

1. Reduce VaR simulations for testing
2. Use smaller portfolios when developing
3. Cache market data to avoid repeated fetches
4. First run triggers Numba compilation (be patient)

## Troubleshooting

### See Also

- [Troubleshooting Guide](troubleshooting_guide.md) - Detailed solutions
- [Installation Guide](INSTALLATION.md) - Setup help

## Support

- GitHub Issues: Report bugs or ask questions
- Documentation: Check guides in this folder
