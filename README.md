# Quant Enthusiasts Risk Engine

A pure Python quantitative finance platform for options pricing, Greeks calculation, and portfolio risk management.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)

---

## Overview

A self-contained options risk platform built in pure Python — from raw pricing math through exotic instrument support, portfolio-level risk aggregation, and an interactive web dashboard with live market data.

**Pricing models**
- Black-Scholes-Merton (analytical, full Greeks, implied volatility)
- Binomial tree — Cox-Ross-Rubinstein (European & American with early exercise)
- Merton Jump Diffusion (Poisson jumps, series expansion)
- Monte Carlo — barrier and Asian exotic options

**Risk engine**
- Portfolio Greeks aggregation (Δ, Γ, ν, θ, ρ)
- Monte Carlo Value at Risk (95%/99%) and Expected Shortfall, Numba JIT accelerated
- P&L distribution with histogram visualization

**Market data**
- Live prices and historical volatility via yfinance
- Real implied volatility surface computed from live option chains
- SQLite-backed cache (Peewee ORM)

---

## Quick Start

```bash
git clone https://github.com/attabeezy/risk-engine.git
cd risk-engine

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -e .
streamlit run dashboard/app.py
```

Dashboard opens at `http://localhost:8501`

---

## Usage

### Price a single option

```python
from risk_engine import EuropeanOption, MarketData, OptionType, PricingModel

option = EuropeanOption(
    OptionType.CALL,
    strike=180.0,
    time_to_expiry=1.0,
    asset_id="AAPL",
    pricing_model=PricingModel.BLACKSCHOLES,
)

md = MarketData(asset_id="AAPL", spot=175.0, rate=0.05, vol=0.25, dividend=0.005)

print(f"Price:  ${option.price(md):.2f}")
print(f"Delta:  {option.delta(md):.4f}")
print(f"Gamma:  {option.gamma(md):.4f}")
print(f"Vega:   {option.vega(md):.4f}")
print(f"Theta:  {option.theta(md):.4f}")
```

### Build a portfolio and calculate risk

```python
from risk_engine import Portfolio, RiskEngine

portfolio = Portfolio()
portfolio.add_instrument(option, quantity=100)

engine = RiskEngine(var_simulations=10000)
result = engine.calculate_portfolio_risk(portfolio, {"AAPL": md})

print(f"Total PV:   ${result.total_pv:,.2f}")
print(f"Delta:       {result.total_delta:,.2f}")
print(f"VaR  95%:   ${result.value_at_risk_95:,.2f}")
print(f"VaR  99%:   ${result.value_at_risk_99:,.2f}")
print(f"ES   95%:   ${result.expected_shortfall_95:,.2f}")
```

### Implied volatility

```python
from risk_engine.core.blackscholes import implied_volatility

iv = implied_volatility(
    market_price=12.50,
    spot=175.0,
    strike=180.0,
    rate=0.05,
    time=1.0,
    is_call=True,
    dividend=0.005,
)
print(f"Implied vol: {iv:.2%}")
```

### American and exotic options

```python
from risk_engine import AmericanOption
from risk_engine.core.binomial import OptionType as BinomialOptionType

american_put = AmericanOption(BinomialOptionType.PUT, strike=180.0, time_to_expiry=1.0, asset_id="AAPL")
print(f"American put: ${american_put.price(md):.2f}")

from risk_engine.instruments.barrier import BarrierOption
from risk_engine.core.exotic import BarrierTypeEnum
from risk_engine.core.binomial import OptionType

barrier = BarrierOption(OptionType.CALL, strike=180.0, barrier=160.0,
                        barrier_type=BarrierTypeEnum.DOWN_OUT,
                        time_to_expiry=1.0, asset_id="AAPL")
print(f"Down-out call: ${barrier.price(md):.2f}")
```

---

## Architecture

```
risk_engine/
├── core/
│   ├── blackscholes.py      # B-S pricing, Greeks, implied vol (Merton dividend adjustment)
│   ├── binomial.py          # CRR binomial tree — European & American
│   ├── jump_diffusion.py    # Merton jump diffusion
│   └── exotic.py            # Monte Carlo — barrier & Asian options
├── instruments/
│   ├── base.py              # Instrument + MarketData base classes
│   ├── european.py          # European option (B-S / Binomial / Merton)
│   ├── american.py          # American option (Binomial, numerical Greeks)
│   ├── barrier.py           # Barrier option (Down/Up In/Out)
│   └── asian.py             # Asian option (arithmetic / geometric average)
├── portfolio/
│   ├── portfolio.py         # Portfolio container
│   └── risk_engine.py       # Greeks aggregation + Numba Monte Carlo VaR
└── market_data/
    ├── market_data.py       # MarketData dataclass
    ├── fetcher.py           # yfinance fetcher + option chain IV solver
    └── cache.py             # SQLite cache via Peewee

dashboard/
└── app.py                   # Streamlit dashboard (5 pages)
```

---

## Dashboard

Run with `streamlit run dashboard/app.py`:

| Page | What it does |
|---|---|
| **Portfolio Builder** | Add European / American options, choose pricing model, view allocation pie chart |
| **Risk Analysis** | Set or auto-fetch market data, run Monte Carlo VaR, view P&L histogram with VaR lines |
| **Market Data** | Fetch live prices, view 1-year candlestick charts, inspect cache |
| **Visualizations** | Payoff diagrams, Greeks bar charts by asset |
| **Greeks Analysis** | Delta / Gamma / Vega heatmaps, real implied volatility surface from live option chains |

---

## Testing

```bash
pip install -e ".[dev]"
pytest tests/
```

103 tests covering Black-Scholes, Binomial, Merton Jump Diffusion, exotic options (barrier, Asian), Portfolio, RiskEngine, and MarketData.

---

## Dependencies

| Package | Purpose |
|---|---|
| `numpy` | Numerical arrays, Monte Carlo simulation |
| `numba` | JIT-compiled VaR Monte Carlo loop |
| `scipy` | Statistical utilities |
| `yfinance` | Live price and option chain data |
| `peewee` | SQLite market data cache |
| `streamlit` | Web dashboard |
| `plotly` | Interactive charts |

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

*Originally a JavaScript + C/C++ build by Quant Enthusiasts — fully ported to pure Python.*
