# Workflow

This document describes the key workflows in finmarketpy: data fetching, backtesting, analytics, and visualization. Each workflow is illustrated with mermaid diagrams and references to actual source files.

## Strategy Backtesting Workflow

The primary workflow is constructing and backtesting a trading strategy. This is orchestrated by the `TradingModel.construct_strategy()` method in `src/finmarketpy/backtest/backtestengine.py`.

### End-to-End Flow

```mermaid
sequenceDiagram
    participant User as User Strategy
    participant TM as TradingModel
    participant BR as BacktestRequest
    participant Market as findatapy Market
    participant TI as TechIndicator
    participant BT as Backtest
    participant RE as RiskEngine
    participant Chart as chartpy

    User->>TM: construct_strategy()
    TM->>BR: load_parameters()
    BR-->>TM: BacktestRequest with dates, TC, vol params

    TM->>Market: load_assets(br)
    Market-->>TM: asset_df, spot_df, spot_df2, basket_dict

    loop For each basket key
        TM->>TI: construct_signal(spot_df, tech_params)
        TI-->>TM: signal_df (+1, -1, 0)

        TM->>BT: calculate_trading_PnL(br, asset_df, signal_df)
        BT->>RE: calculate_leverage_factor()
        RE-->>BT: leverage adjustments
        BT-->>TM: cumulative P&L, ret_stats
    end

    TM->>TM: compare_strategy_vs_benchmark()
    TM->>TM: _assign_final_strategy_results()

    User->>TM: plot_strategy_pnl()
    TM->>Chart: Chart.plot(pnl_df, style)
```

### Step-by-Step Breakdown

1. **Parameter Loading** -- `load_parameters()` creates a `BacktestRequest` object with all backtest settings: date range, transaction costs (in basis points), volatility targeting parameters, position limits, stop loss/take profit levels, and technical indicator parameters via `TechParams`.

2. **Asset Loading** -- `load_assets()` uses findatapy's `Market` class to fetch market data. Returns a tuple of `(asset_df, spot_df, spot_df2, basket_dict)` where `basket_dict` maps strategy names to lists of tickers.

3. **Signal Construction** -- `construct_signal()` generates trading signals (typically +1 for long, -1 for short). Uses `TechIndicator` or custom logic. The signal DataFrame must have matching columns to the asset DataFrame.

4. **P&L Calculation** -- `Backtest.calculate_trading_PnL()` handles:
   - Signal delay application
   - Date alignment between assets and signals
   - Stop loss / take profit signal modification
   - Signal-level volatility adjustment
   - Portfolio-level volatility adjustment
   - Position limit enforcement
   - Transaction cost application
   - Cumulative index construction

5. **Analysis** -- `TradeAnalysis` provides post-backtest tools: TC sensitivity, parameter sweeps, seasonality of strategy returns, and HTML report generation.

## Data Fetching Workflow

Market data retrieval is handled by findatapy, but finmarketpy provides convenience wrappers, particularly `QuickChart` in `src/finmarketpy/economics/quickchart.py`.

```mermaid
flowchart TD
    A[User calls QuickChart.plot_chart<br/>or TradingModel.load_assets] --> B[Create MarketDataRequest]
    B --> C{Data Source}
    C -->|Bloomberg| D[Bloomberg API]
    C -->|Quandl| E[Quandl API]
    C -->|FRED/ALFRED| F[FRED API]
    C -->|Alpha Vantage| G[Alpha Vantage API]
    C -->|CSV/Parquet| H[Local Files]
    D --> I[findatapy Market.fetch_market]
    E --> I
    F --> I
    G --> I
    H --> I
    I --> J{Cache Available?}
    J -->|Yes| K[Return Cached DataFrame]
    J -->|No| L[Download & Cache]
    L --> K
    K --> M[pandas DataFrame<br/>columns: ticker.field]
```

### QuickChart One-Line Usage

`QuickChart` wraps the entire data fetch + plot workflow into a single method call:

```python
from finmarketpy.economics import QuickChart

qc = QuickChart(engine='plotly', data_source='fred')
qc.plot_chart(
    tickers={'US 10Y': 'DGS10'},
    start_date='2020-01-01',
    title='US 10 Year Treasury Yield'
)
```

**Source**: `src/finmarketpy/economics/quickchart.py`

## FX Total Return Index Workflow

Constructing FX total return indices involves fetching spot rates, deposit rates, and forward points, then computing carry-adjusted returns. This is handled by the curve module.

### FX Spot Total Return Index

```mermaid
flowchart TD
    A[FXSpotCurve.fetch_continuous_time_series] --> B[Fetch FX Spot Prices<br/>via findatapy]
    B --> C[Fetch Base & Terms<br/>Deposit Rates]
    C --> D[Calculate Day Count<br/>Fractions]
    D --> E{Numba Available?}
    E -->|Yes| F[_spot_index_numba<br/>guvectorize accelerated]
    E -->|No| G[_spot_index<br/>pure Python loop]
    F --> H[Total Return Index]
    G --> H
    H --> I[DataFrame with<br/>carry-adjusted returns]
```

The total return index formula for each day `i` is:

```
TRI[i] = TRI[i-1] * (1 + (1 + base_depo * dt / base_daycount) * (spot[i] / spot[i-1])
                         - (1 + terms_depo * dt / terms_daycount))
```

**Source**: `src/finmarketpy/curve/fxspotcurve.py` (lines 31-60)

### FX Forwards Roll Workflow

```mermaid
flowchart TD
    A[FXForwardsCurve.construct_total_returns_index] --> B[Fetch Forward Points<br/>for multiple tenors]
    B --> C[Interpolate to<br/>trading tenor]
    C --> D[Determine Roll Dates<br/>based on roll_event]

    D --> E{Roll Event Type}
    E -->|month-end| F[N days before month end]
    E -->|quarter-end| G[N days before quarter end]
    E -->|expiry-date| H[N days before delivery]

    F --> I[Build continuous<br/>forward series]
    G --> I
    H --> I

    I --> J[Calculate daily<br/>forward returns]
    J --> K{Cum Index Type}
    K -->|mult| L[Multiplicative index<br/>starting at 100]
    K -->|add| M[Additive index<br/>starting at 0]
    L --> N[Total Return Index]
    M --> N
```

Roll parameters are configured in `MarketConstants`:
- `fx_forwards_roll_event`: When to roll (`'month-end'`, `'quarter-end'`, `'year-end'`, `'delivery-date'`)
- `fx_forwards_roll_days_before`: How many days before the event to roll (default: 5)
- `fx_forwards_roll_months`: Roll frequency in months (default: 1)
- `fx_forwards_trading_tenor`: Primary trading tenor (default: `'1M'`)

**Source**: `src/finmarketpy/curve/fxforwardscurve.py`

## Analytics Workflows

### Technical Indicator Signal Generation

```mermaid
flowchart TD
    A[TechIndicator.create_tech_ind<br/>data_frame, name, tech_params] --> B{Indicator Type}
    B -->|SMA| C[Rolling Mean<br/>window = sma_period]
    B -->|EMA| D[Exponential Moving Average<br/>span = ema_period]
    B -->|RSI| E[Relative Strength Index<br/>period = rsi_period]
    B -->|BB| F[Bollinger Bands<br/>period, std_dev]
    B -->|ROC| G[Rate of Change<br/>period = roc_period]
    B -->|ATR| H[Average True Range]
    B -->|SMA2| I[Double SMA Crossover<br/>fast_period, slow_period]
    B -->|polarity| J[Sign of Input]
    B -->|long_only| K[Always +1]

    C --> L[Compare: price vs indicator]
    D --> L
    E --> M[Compare: RSI vs thresholds]
    F --> N[Compare: price vs bands]
    G --> O[Compare: ROC vs 0]
    I --> P[Compare: fast vs slow SMA]
    J --> Q[Sign of value]
    K --> R[Constant +1]

    L --> S[Signal DataFrame<br/>+1 long, -1 short]
    M --> S
    N --> S
    O --> S
    P --> S
    Q --> S
    R --> S

    S --> T{Filter?}
    T -->|long_only| U[max signal, 0]
    T -->|short_only| V[min signal, 0]
    T -->|flip| W[signal * -1]
    T -->|none| X[Raw signal]
```

**Source**: `src/finmarketpy/economics/techindicator.py`

### Seasonality Analysis

The `Seasonality` class in `src/finmarketpy/economics/seasonality.py` provides multiple temporal aggregation methods:

- `time_of_day_seasonality()` -- Average returns by hour/minute of day (for intraday data)
- `bus_day_of_month_seasonality()` -- Average returns by business day of month
- `monthly_seasonality()` -- Average returns by calendar month

These can be computed across all years or broken down year-by-year for comparison.

### Event Study Workflow

```mermaid
flowchart TD
    A[EventStudy] --> B[Load Event Dates<br/>e.g. FOMC meetings]
    B --> C[Align with Price Data]
    C --> D{Frequency}
    D -->|Intraday| E[get_intraday_moves_over_custom_event<br/>minute-level windows]
    D -->|Daily| F[get_daily_moves_over_custom_event<br/>day-level windows]
    D -->|Weekly| G[get_weekly_moves_over_custom_event<br/>week-level windows]
    E --> H[Extract return windows<br/>around each event]
    F --> H
    G --> H
    H --> I[Average across events]
    I --> J[Cumulative event response]
    J --> K[Plot via chartpy]
```

The `EventStudy` class handles timezone conversions (UTC to New York), NY 10am cutoff logic for FX markets, and alignment of event dates with business day calendars.

**Source**: `src/finmarketpy/economics/eventstudy.py`

## Sensitivity Analysis Workflow

`TradeAnalysis` in `src/finmarketpy/backtest/tradeanalysis.py` supports parameter sweep analysis:

```mermaid
flowchart TD
    A[TradeAnalysis.run_arbitrary_sensitivity] --> B[Define parameter_list<br/>e.g. TC = 0, 0.5, 1.0, 1.5, 2.0 bp]
    B --> C{Parallel?}
    C -->|Yes| D[SwimPool.create_pool]
    D --> E[pool.apply_async for each param set]
    E --> F[Collect results from pool]
    C -->|No| G[Sequential loop]
    G --> H[Run strategy for each param set]
    F --> I[Combine P&L series]
    H --> I
    I --> J[Calculate IR and Returns<br/>for each parameter]
    J --> K[Plot cumulative P&L lines]
    J --> L[Plot IR bar chart]
    J --> M[Plot Returns bar chart]
```

Built-in sensitivity tests include:
- `run_tc_shock()` -- Transaction cost sensitivity (0bp to 2bp in 0.25bp steps)
- `run_arbitrary_sensitivity()` -- Any parameter combination from `BacktestRequest`

**Source**: `src/finmarketpy/backtest/tradeanalysis.py` (lines 229-381)

## Visualization Workflow

finmarketpy uses chartpy for all visualization. The `TradingModel` base class provides built-in plotting methods that produce standardized output.

### Strategy Report Generation

`TradeAnalysis.run_strategy_returns_stats()` generates a multi-panel HTML report:

```python
# Generates 6-panel Canvas:
# [strategy_pnl,        individual_trade_pnl]
# [component_pnl,       component_IR]
# [portfolio_leverage,   individual_leverage]
canvas = Canvas([[pnl, individual],
                 [pnl_comp, ir_comp],
                 [leverage, ind_lev]])
canvas.generate_canvas(page_title='Strategy Return Statistics')
```

Available plot methods on `TradingModel`:
- `plot_strategy_pnl()` -- Final strategy cumulative P&L
- `plot_strategy_group_pnl_trades()` -- Individual asset P&L contributions
- `plot_strategy_group_benchmark_pnl()` -- Strategy vs benchmark
- `plot_strategy_group_benchmark_pnl_ir()` -- Information ratios
- `plot_strategy_leverage()` -- Portfolio leverage over time
- `plot_strategy_group_leverage()` -- Per-asset leverage

**Source**: `src/finmarketpy/backtest/tradeanalysis.py` (lines 55-147)

## Network Analysis Workflow

The `src/finmarketpy/network_analysis/` module uses scikit-learn's graphical LASSO to learn the conditional independence structure of asset returns.

```mermaid
flowchart TD
    A[Asset Return Time Series] --> B[learn_network_structure]
    B --> C[GraphicalLassoCV<br/>Cross-validated sparse precision matrix]
    C --> D[Correlation Matrix<br/>from covariance]
    D --> E[Locally Linear Embedding<br/>for 2D positioning]
    E --> F[Node positions + edges]
    F --> G[plot_network_structure<br/>matplotlib visualization]
```

**Source**: `src/finmarketpy/network_analysis/learn_network_structure.py`

## FX Volatility Surface Workflow

The `FXVolSurface` class constructs and interpolates FX vol surfaces using FinancePy as a backend.

```mermaid
flowchart TD
    A[Market Data<br/>spot, forwards, depos, vols] --> B[FXVolSurface.__init__]
    B --> C[Parse ATM vols<br/>25D and 10D strangles/RRs]
    C --> D[Select interpolation scheme]
    D --> E{Vol Function Type}
    E -->|CLARK5| F[Clark 5-parameter model]
    E -->|CLARK| G[Clark model]
    E -->|BBG| H[Bloomberg convention]
    E -->|SABR| I[SABR model]
    F --> J[Calibrate FinancePy<br/>FXVolSurfacePlus]
    G --> J
    H --> J
    I --> J
    J --> K[Interpolate vol for<br/>any strike/tenor]
    K --> L[Price options<br/>via FXOptionsPricer]
```

**Source**: `src/finmarketpy/curve/volatility/fxvolsurface.py`

---
## See Also
- [README](README.md) — Project overview and quick start
- [Architecture](architecture.md) — System design and components
- [State Management](state-management.md) — State lifecycle and data models
- [Development](development.md) — Development guide and best practices
