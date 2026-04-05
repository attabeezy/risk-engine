# Installation Guide

Complete installation instructions for the Risk Engine.

## Prerequisites

- **Python**: 3.9 or higher
- **pip**: Latest version recommended

## Quick Install

```bash
# Clone repository
git clone https://github.com/yourusername/risk-engine.git
cd risk-engine

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Run the Dashboard

```bash
streamlit run dashboard/app.py
```

Navigate to `http://localhost:8501` in your browser.

## Development Setup

For development with testing and linting tools:

```bash
pip install -r requirements-dev.txt
```

This adds:
- `pytest` - Testing framework
- `pytest-cov` - Code coverage
- `black` - Code formatter
- `ruff` - Fast linter
- `mypy` - Type checker

## Verify Installation

```python
# Test imports
from risk_engine.core.black_scholes import black_scholes_price
from risk_engine.portfolio.risk_engine import RiskEngine

# Price a call option
price = black_scholes_price(
    spot=100, strike=100, rate=0.05, 
    vol=0.2, expiry=1.0, is_call=True
)
print(f"Option price: ${price:.2f}")
```

## Troubleshooting

### ModuleNotFoundError

Ensure you've activated the virtual environment and installed dependencies:

```bash
pip install -r requirements.txt
```

### Streamlit not found

```bash
pip install streamlit
```

### yfinance errors

Market data fetching requires internet connection. Check your network and try:

```bash
pip install --upgrade yfinance
```

## Next Steps

- [Quickstart Guide](quickstart_guide.md) - Get started quickly
- [API Reference](api_reference.md) - Python API documentation
- [Market Data Guide](market_data_guide.md) - YFinance integration
