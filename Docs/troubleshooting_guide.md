# Troubleshooting Guide

Solutions to common issues when using the Risk Engine.

## Installation Issues

### ModuleNotFoundError

**Symptom:**
```
ModuleNotFoundError: No module named 'risk_engine'
```

**Solution:**
Ensure you're in the project root and have activated your virtual environment:

```bash
cd risk-engine
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Numba Compilation Errors

**Symptom:**
```
NumbaError: Failed to compile...
```

**Solution:**
Update numba and numpy:

```bash
pip install --upgrade numba numpy
```

### Streamlit Version Issues

**Symptom:**
```
AttributeError: module 'streamlit' has no attribute '...'
```

**Solution:**
```bash
pip install --upgrade streamlit>=1.32.0
```

## Market Data Issues

### Failed to Fetch Data

**Symptom:**
```
Failed to fetch data for AAPL: No price data available
```

**Solutions:**

1. Check internet connectivity
2. Verify ticker symbol exists on Yahoo Finance
3. Try force refresh:
```python
from risk_engine.market_data.fetcher import MarketDataFetcher
fetcher = MarketDataFetcher()
data = fetcher.fetch_single("AAPL", force_refresh=True)
```

### Cache Issues

**Symptom:**
Old data returned or cache errors.

**Solution:**
Delete the cache file and let it regenerate:

```bash
rm market_data_cache.db
```

### Rate Limiting

**Symptom:**
Multiple consecutive fetch failures.

**Solution:**
Yahoo Finance may rate limit requests. Wait a few minutes and try again, or reduce fetch frequency.

## Runtime Issues

### Slow VaR Calculations

**Symptom:**
VaR calculations take too long.

**Solutions:**

1. Reduce simulation count:
```python
engine = RiskEngine(simulations=10000)  # Instead of 100000
```

2. Ensure Numba JIT compilation completed (first run is slower)

### Memory Issues

**Symptom:**
```
MemoryError or process killed
```

**Solution:**
Reduce portfolio size or simulation count:

```python
# Process in batches
engine = RiskEngine(simulations=50000)
```

### NaN in Results

**Symptom:**
Results contain NaN values.

**Solutions:**

1. Check input data is valid (no negative prices, zero volatility, etc.)
2. Verify market data:
```python
print(market_data)  # Inspect values
assert market_data.spot > 0
assert market_data.volatility > 0
```

## Dashboard Issues

### Port Already in Use

**Symptom:**
```
Port 8501 is already in use
```

**Solution:**
Use a different port:

```bash
streamlit run dashboard/app.py --server.port 8502
```

### Plotly Charts Not Rendering

**Symptom:**
Charts appear blank or fail to load.

**Solution:**
```bash
pip install --upgrade plotly>=5.18.0
```

### Slow Dashboard Loading

**Symptom:**
Dashboard takes a long time to load.

**Solutions:**

1. Check if market data is being fetched on every reload
2. Use cached data when possible
3. Reduce initial portfolio size

## Common Error Messages

### "Invalid option parameters"

Check that:
- Strike price > 0
- Expiry > 0
- Volatility > 0 and < 5 (500%)
- Spot price > 0

### "Portfolio is empty"

Ensure you've added instruments to the portfolio:

```python
from risk_engine.portfolio.portfolio import Portfolio
from risk_engine.instruments.european import EuropeanOption, OptionType

portfolio = Portfolio()
option = EuropeanOption(OptionType.CALL, strike=100, expiry=1.0, asset_id="AAPL")
portfolio.add_instrument(option, quantity=100)
```

### "Market data not found"

Provide market data or ensure fetcher can reach Yahoo Finance:

```python
from risk_engine.market_data.market_data import MarketData
market_data = MarketData(spot=100, rate=0.05, volatility=0.2)
```

## Getting Help

1. Check the [FAQ](faq_guide.md)
2. Review [API Reference](api_reference.md)
3. Open an issue on GitHub with:
   - Python version (`python --version`)
   - Operating system
   - Full error message and stack trace
   - Minimal code to reproduce
