# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

finmarketpy is a Python library for backtesting trading strategies and analyzing market data. It provides prebuilt templates for strategy backtesting, seasonality analysis, event studies, and risk management with volatility targeting.

**Key Dependencies**:
- findatapy - market data retrieval (https://github.com/cuemacro/findatapy)
- chartpy - visualization with matplotlib/plotly/bokeh (https://github.com/cuemacro/chartpy)
- Optional: financepy (for FX options pricing)

## Build and Development Commands

### Environment Setup
```bash
# Create virtual environment and install dependencies
make install

# This runs:
# - uv venv --python '3.9'
# - uv sync -vv --frozen
```

### Testing
```bash
# Run all tests
make test                    # or: uv run pytest tests

# Run specific test file
uv run pytest tests/test_backtestengine.py

# Run specific test
uv run pytest tests/test_backtestengine.py::test_function_name

# Run with coverage
uv run pytest --cov=finmarketpy tests
```

### Code Quality
```bash
# Run autoformatting and linting
make fmt

# This runs pre-commit hooks:
# - ruff (linting and formatting)
# - Other configured checks

# Check dependencies
make deptry                  # or: uv run deptry 'finmarketpy'
```

### Notebooks
```bash
# Launch Marimo notebooks
make marimo                  # or: uv run marimo edit notebooks
```

### Cleanup
```bash
# Remove caches and build artifacts
make clean
```

## Architecture Overview

### Core Modules

**finmarketpy/backtest/** - Backtesting engine and trade analysis
- `BacktestRequest` - Configuration object for backtests (inherits from findatapy's MarketDataRequest)
  - Defines start/finish dates, transaction costs, volatility targeting
  - Signal parameters, portfolio construction, position limits
  - Take profit/stop loss parameters
- `BacktestEngine` (in `backtestengine.py`) - Executes backtests
  - Applies transaction costs, volatility scaling, max leverage constraints
  - Supports parallel execution for parameter sweeps (via multiprocessing/threading)
  - Returns portfolio time series and statistics
- `TradeAnalysis` - Post-backtest analysis and sensitivity testing
- `BacktestComparison` - Compare multiple strategies

**finmarketpy/economics/** - Market analysis tools
- `TechIndicator` - Technical indicators (SMA, EMA, Bollinger, RSI, etc.)
- `Seasonality` - Analyze seasonal patterns in returns
- `EventStudy` - Market behavior around economic events
- `QuickChart` - One-line market data download and plotting

**finmarketpy/curve/** - Pricing and total return indices
- `FXSpotCurve` - FX spot total return indices (including carry)
- `FXForwardsCurve` - FX forwards total return indices
- `FXOptionsCurve` - FX vanilla options total return indices
- `FXVolSurface` - FX volatility surface interpolation (via FinancePy)
- Subdirectories:
  - `rates/` - FX forwards pricing
  - `volatility/` - Options pricing, vol stats, implied PDF

**finmarketpy/util/** - Configuration and utilities
- `MarketConstants` - Global configuration (parallel processing settings, roll conventions, pricing parameters)
  - Can be overridden by creating `marketcred.py` in the same directory
  - Override persists across upgrades (unlike editing `marketconstants.py` directly)

### Key Design Patterns

**Configuration Override Pattern**:
- Constants defined in `marketconstants.py`, `chartconstants.py` (chartpy), `dataconstants.py` (findatapy)
- Create `*cred.py` files to override settings without modifying source
- Prevents settings from being overwritten on library upgrades

**Backtest Flow**:
1. Define `BacktestRequest` with strategy parameters
2. `BacktestEngine` processes signals against market data
3. Apply transaction costs, volatility targeting, position limits
4. `TradeAnalysis` for sensitivity analysis and statistics
5. chartpy for visualization (matplotlib/plotly/bokeh)

**Parallel Processing**:
- Controlled by `MarketConstants.backtest_thread_technique` ("thread" or "multiprocessing")
- `MarketConstants.backtest_thread_no` sets thread count (platform-specific defaults)
- Used for parameter sweeps and sensitivity analysis
- SwimPool wrapper handles threading/multiprocessing abstraction

**Total Return Indices**:
- Spot, forwards, and options curves construct total return indices
- Roll logic defined in `MarketConstants` (roll event, days before, tenor)
- Support for different index types ('mult' vs 'add')

## Python Version and Dependencies

- **Python**: 3.9+ (specified in pyproject.toml)
- **Package Management**: uv (modern, fast alternative to pip/poetry)
- **Key Dependencies**: pandas>=1.5.3, numpy<2, numba, scikit-learn, blosc
- **Optional**: financepy==0.370 (install with `--no-deps` to avoid version conflicts)

## Testing Strategy

Tests are in `tests/` directory:
- `test_backtestengine.py` - Backtest execution tests
- `test_techindicator.py` - Technical indicator tests
- `conftest.py` - Shared pytest fixtures

Run tests frequently during development. The backtest engine has complex state management around signals, positions, and P&L calculation.

## Common Development Workflows

### Adding a New Technical Indicator
1. Add method to `finmarketpy/economics/techindicator.py`
2. Follow existing patterns (e.g., `create_sma`, `create_bollinger_bands`)
3. Add test to `tests/test_techindicator.py`

### Creating a Trading Strategy
1. Subclass or use `TradingModel` pattern (see examples)
2. Define signals using `TechIndicator`
3. Configure `BacktestRequest` with:
   - Market data parameters (tickers, data source)
   - Signal parameters
   - Transaction costs, volatility targeting
4. Run backtest with `BacktestEngine`
5. Analyze with `TradeAnalysis`

See `finmarketpy_examples/tradingmodelfxtrend_example.py` for complete example.

### Working with FX Pricing
- FX spot: Use `FXSpotCurve` to build total return indices with carry
- FX forwards: Use `FXForwardsPricer` for interpolation, `FXForwardsCurve` for total returns
- FX options: Use `FXOptionsPricer` (via FinancePy), `FXOptionsCurve` for total returns
- FX vol surface: Use `FXVolSurface` for SABR/Clark interpolation

## Configuration Files

**finmarketpy/util/marketconstants.py** - Key settings to review:
- `backtest_thread_technique` and `backtest_thread_no` - Parallel processing
- `fx_forwards_*` - FX forwards roll conventions
- `fx_options_*` - FX options pricing parameters
- Database settings (MongoDB, Redis)

**Create marketcred.py** (not in version control) to override:
```python
class MarketCred(object):
    backtest_thread_no = {'linux': 4, 'windows': 1, 'mac': 4}
    db_username = 'your_username'
    db_password = 'your_password'
    # ... other overrides
```

## Examples Directory

`finmarketpy_examples/` contains working examples:
- `backtest_example.py` - Basic backtesting
- `tradingmodelfxtrend_example.py` - FX trend following strategy
- `seasonality_examples.py` - Seasonal pattern analysis
- `events_examples.py` - Event study analysis
- `fx_options_pricing_examples.py` - Options pricing
- `vol_stats_examples.py` - Realized vol and vol risk premium

Examples in `finmarketpy_examples/finmarketpy_notebooks/` are Jupyter notebooks (some available on Binder).

## Known Issues

**Numba Cache Issues with financepy**:
- If you see `Failed in nopython mode pipeline` errors
- Delete `__pycache__` folders in financepy installation directory
- Example path: `C:\Anaconda3\envs\py310class\Lib\site-packages\financepy`

**FinancePy Version**:
- Recommended: financepy==0.370
- Install with `--no-deps` to avoid library version conflicts
- API changes frequently, so specific version is important

**Parallel Processing**:
- Works better on Linux than Windows
- On Windows, set `backtest_thread_no = 1` to avoid multiprocessing issues
- Some data providers rate-limit parallel requests

## Key Files Reference

- `pyproject.toml` - Project metadata, dependencies, tool configuration
- `Makefile` - Common development commands
- `uv.lock` - Locked dependency versions (don't edit manually)
- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `INSTALL.md` - Detailed installation instructions for all platforms
- `PLANNED_FEATURES.md` - Roadmap and feature requests
