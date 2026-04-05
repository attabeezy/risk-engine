# Contributing Guide

Thank you for considering contributing to the Risk Engine!

## Getting Started

### Prerequisites

1. Python 3.9+
2. Git
3. Read the [README](../README.md)
4. Complete the [Installation Guide](INSTALLATION.md)

### First-Time Contributors

Good starter tasks:
- Documentation improvements
- Test coverage additions
- Bug fixes with clear reproduction steps
- Code style improvements

## Development Workflow

### 1. Fork and Clone

```bash
# Fork on GitHub, then clone
git clone https://github.com/YOUR_USERNAME/risk-engine.git
cd risk-engine

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/risk-engine.git
```

### 2. Create a Branch

```bash
# Feature
git checkout -b feature/add-exotic-options

# Bug fix
git checkout -b fix/var-calculation

# Documentation
git checkout -b docs/api-examples
```

### 3. Make Changes

- Follow the [style guidelines](#code-style)
- Add tests for new features
- Update documentation as needed

### 4. Test Your Changes

```bash
# Run tests
pytest tests/ -v

# Check formatting
black --check .

# Run linter
ruff check .
```

### 5. Commit

Use conventional commit messages:

```bash
git commit -m "feat: Add Asian option pricing"
git commit -m "fix: Correct VaR calculation for short positions"
git commit -m "docs: Update API examples"
```

**Commit types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `perf:` Performance improvement

### 6. Push and Create PR

```bash
git push origin feature/add-exotic-options
```

Then create a pull request on GitHub.

## Code Style

### Python (PEP 8 + Black)

**Format:**
```bash
black risk_engine/ tests/ dashboard/
```

**Lint:**
```bash
ruff check .
```

### Naming Conventions

```python
class MarketDataFetcher:      # PascalCase for classes
def fetch_ticker():           # snake_case for functions
MAX_SIMULATIONS = 1000000     # UPPER_CASE for constants
```

### Type Hints

```python
def calculate_var(
    portfolio: Portfolio,
    confidence: float = 0.95
) -> float:
    """Calculate Value at Risk."""
    pass
```

### Docstrings

```python
def price_option(spot: float, strike: float) -> float:
    """
    Calculate option price.
    
    Args:
        spot: Current spot price
        strike: Strike price
        
    Returns:
        Option price
    """
    pass
```

## Testing Requirements

### All Contributions Need Tests

```python
import pytest
from risk_engine.core.black_scholes import black_scholes_price

def test_call_price_positive():
    """Call option should have positive price"""
    price = black_scholes_price(100, 100, 0.05, 0.2, 1.0, True)
    assert price > 0
```

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=risk_engine
```

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No merge conflicts with main

### PR Description

Include:
- What changes were made
- Why the changes were needed
- Any breaking changes
- Related issues (e.g., "Fixes #123")

### Review Process

1. Automated checks must pass
2. Maintainer will review
3. Address feedback
4. Maintainer merges when approved

## Contribution Types

### Code

- New features (discuss first in an issue)
- Bug fixes
- Performance improvements
- Refactoring

### Documentation

- Fix typos
- Improve explanations
- Add examples
- Write tutorials

### Testing

- Add test coverage
- Fix flaky tests
- Add edge case tests

## Questions?

- Open a GitHub issue
- Check existing issues first
- Be specific about the problem

Thank you for contributing!
