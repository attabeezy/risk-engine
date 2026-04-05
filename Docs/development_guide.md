# Development Guide

Guide for contributing to the Risk Engine.

## Development Setup

### Prerequisites

```bash
# Clone and setup
git clone https://github.com/yourusername/risk-engine.git
cd risk-engine

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dev dependencies
pip install -r requirements-dev.txt
```

### Development Dependencies

- `pytest` - Testing framework
- `pytest-cov` - Code coverage
- `black` - Code formatter
- `ruff` - Fast linter
- `mypy` - Type checker

## Project Structure

```
risk-engine/
├── dashboard/
│   └── app.py                  # Streamlit dashboard
├── risk_engine/
│   ├── core/                   # Pricing models
│   │   ├── black_scholes.py    # Black-Scholes model
│   │   ├── binomial.py         # Binomial tree
│   │   ├── jump_diffusion.py   # Merton model
│   │   └── exotic.py           # Exotic options (Asian, Barrier)
│   ├── instruments/            # Option classes
│   │   ├── base.py             # Base instrument
│   │   ├── european.py         # European options
│   │   ├── american.py         # American options
│   │   ├── asian.py            # Asian options
│   │   └── barrier.py          # Barrier options
│   ├── portfolio/              # Portfolio management
│   │   ├── portfolio.py        # Portfolio class
│   │   └── risk_engine.py      # VaR calculations
│   ├── market_data/            # Market data
│   │   ├── market_data.py      # MarketData class
│   │   ├── fetcher.py          # YFinance integration
│   │   └── cache.py            # SQLite caching
│   └── utils/                  # Utilities
├── tests/                      # Test files
├── Docs/                       # Documentation
├── requirements.txt            # Production dependencies
└── requirements-dev.txt        # Development dependencies
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=risk_engine --cov-report=html
```

### Run Specific Test

```bash
pytest tests/test_black_scholes.py -v
```

### Writing Tests

```python
import pytest
from risk_engine.core.black_scholes import black_scholes_price

def test_call_price_at_the_money():
    """ATM call should have positive price"""
    price = black_scholes_price(
        spot=100, strike=100, rate=0.05,
        vol=0.2, expiry=1.0, is_call=True
    )
    assert price > 0
    assert price < 100  # Less than spot

def test_put_call_parity():
    """Verify put-call parity holds"""
    call = black_scholes_price(100, 100, 0.05, 0.2, 1.0, True)
    put = black_scholes_price(100, 100, 0.05, 0.2, 1.0, False)
    
    # C - P = S - K*e^(-rT)
    import math
    expected_diff = 100 - 100 * math.exp(-0.05)
    assert abs(call - put - expected_diff) < 0.01
```

## Code Style

### Python Style (PEP 8 + Black)

**Format code:**
```bash
black risk_engine/ tests/ dashboard/
```

**Lint code:**
```bash
ruff check risk_engine/ tests/
```

**Type check:**
```bash
mypy risk_engine/
```

### Naming Conventions

```python
class MarketDataFetcher:      # PascalCase for classes
def fetch_ticker(ticker):      # snake_case for functions
MAX_SIMULATIONS = 1000000      # UPPER_CASE for constants
spot_price = 100.0             # snake_case for variables
```

### Type Hints

```python
def calculate_var(
    portfolio: Portfolio,
    market_data: dict[str, MarketData],
    confidence: float = 0.95
) -> float:
    """
    Calculate Value at Risk.
    
    Args:
        portfolio: Portfolio of instruments
        market_data: Market data by asset ID
        confidence: Confidence level (0-1)
        
    Returns:
        VaR value (negative number representing potential loss)
    """
    pass
```

## Contributing

### Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/add-greeks-heatmap
   ```
3. **Make changes with tests**
4. **Run tests and linting**
   ```bash
   pytest tests/ -v
   black .
   ruff check .
   ```
5. **Commit with clear messages**
   ```bash
   git commit -m "feat: Add Greeks heatmap visualization"
   ```
6. **Push and create PR**

### Commit Message Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions
- `refactor:` Code refactoring
- `perf:` Performance improvements

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No merge conflicts

## Adding New Features

### Adding a New Pricing Model

1. Create file in `risk_engine/core/`:
```python
# risk_engine/core/my_model.py
from typing import Tuple

def my_model_price(
    spot: float,
    strike: float,
    rate: float,
    vol: float,
    expiry: float,
    is_call: bool
) -> float:
    """Price option using my model."""
    # Implementation
    pass
```

2. Add tests in `tests/`:
```python
# tests/test_my_model.py
def test_my_model_basic():
    price = my_model_price(100, 100, 0.05, 0.2, 1.0, True)
    assert price > 0
```

3. Update `risk_engine/__init__.py` exports
4. Update documentation

### Adding a New Instrument Type

1. Create class in `risk_engine/instruments/`:
```python
# risk_engine/instruments/lookback.py
from .base import Instrument

class LookbackOption(Instrument):
    def __init__(self, ...):
        pass
    
    def price(self, market_data: MarketData) -> float:
        pass
```

2. Add tests
3. Integrate with dashboard if applicable

## Performance Profiling

### Using cProfile

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here
result = engine.calculate_portfolio_risk(portfolio, market_data)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Numba Tips

- First call compiles the function (slow)
- Subsequent calls are fast
- Use `@njit` for pure numerical code
- Avoid Python objects inside `@njit` functions

## Questions?

- Open a GitHub issue
- Check existing documentation
