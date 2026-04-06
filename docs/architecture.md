# Architecture

This document describes the design and architecture of finmarketpy, including its layered structure, class hierarchies, component interactions, and key design decisions.

## Trading Paradigm & Key Features

| Feature | Support | Details |
|---------|---------|---------|
| Backtesting Approach | Vector-based | Pandas DataFrame operations; signals and returns computed as full arrays |
| Live Trading | No | Library produces signals and analytics but does not connect to brokers |
| Paper Trading | No | No simulated execution engine |
| Multi-Asset | Yes | FX (spot, forwards, options), equities via findatapy data sources |
| Data Feeds | findatapy abstraction | Bloomberg, Quandl, FRED, Yahoo Finance, and others via findatapy |
| ML Integration | No | No built-in ML; scikit-learn used only for network analysis module |
| Risk Management | Built-in | Two-level volatility targeting (signal and portfolio), position limits (max net/abs exposure), stop-loss/take-profit |
| Optimization | No | No hyperparameter or portfolio optimization; sensitivity sweeps via TradeAnalysis |
| Execution | Simulated | Backtest-only P&L calculation with configurable transaction costs |

## System Layers

finmarketpy follows a layered architecture where each layer depends only on layers below it. External libraries (findatapy, chartpy, financepy) provide foundational capabilities.

```mermaid
graph TB
    subgraph "User Layer"
        US[User Strategy<br/>TradingModel subclass]
        UE[User Examples<br/>finmarketpy_examples/]
    end

    subgraph "Orchestration Layer"
        TM[TradingModel<br/>Abstract base]
        TA[TradeAnalysis<br/>Sensitivity & Reporting]
        BC[BacktestComparison<br/>Multi-strategy comparison]
    end

    subgraph "Engine Layer"
        BT[Backtest<br/>P&L calculation engine]
        PWC[PortfolioWeightConstruction<br/>Weight optimization]
        RE[RiskEngine<br/>Vol targeting & limits]
    end

    subgraph "Analytics Layer"
        TI[TechIndicator]
        SEA[Seasonality]
        EVS[EventStudy]
        QC[QuickChart]
        ML[MarketLiquidity]
        REP[Report]
    end

    subgraph "Curve Layer"
        FXS[FXSpotCurve]
        FXF[FXForwardsCurve]
        FXO[FXOptionsCurve]
        FXV[FXVolSurface]
    end

    subgraph "Configuration Layer"
        MC[MarketConstants]
        BR[BacktestRequest]
        TP[TechParams]
    end

    subgraph "External Libraries"
        FDP[findatapy<br/>Data & Calculations]
        CP[chartpy<br/>Visualization]
        FP[financepy<br/>Options Pricing]
    end

    US --> TM
    TM --> BT
    TM --> TI
    TA --> TM
    BC --> TM
    BT --> PWC
    BT --> RE
    BT --> BR
    PWC --> RE
    FXV --> FP
    FXS --> FDP
    FXF --> FDP
    TI --> FDP
    SEA --> FDP
    TM --> CP
    QC --> CP
    QC --> FDP
    MC --> BT
    MC --> FXF
    MC --> FXV
```

## Class Hierarchy

### Backtest Module Inheritance

`BacktestRequest` extends findatapy's `MarketDataRequest`, inheriting all market data parameters while adding backtest-specific fields (transaction costs, vol targeting, position limits).

```mermaid
classDiagram
    class MarketDataRequest {
        +start_date
        +finish_date
        +tickers
        +fields
        +data_source
        +freq
    }

    class BacktestRequest {
        +spot_tc_bp
        +portfolio_vol_adjust
        +portfolio_vol_target
        +portfolio_vol_max_leverage
        +signal_vol_adjust
        +signal_vol_target
        +max_net_exposure
        +max_abs_exposure
        +take_profit
        +stop_loss
        +signal_delay
        +cum_index
        +tech_params: TechParams
    }

    class TradingModel {
        <<abstract>>
        +load_parameters()* BacktestRequest
        +load_assets()* tuple
        +construct_signal()* DataFrame
        +construct_strategy()
        +construct_individual_strategy()
        +compare_strategy_vs_benchmark()
        +plot_strategy_pnl()
        +plot_strategy_leverage()
    }

    class Backtest {
        -_pnl: DataFrame
        -_portfolio: DataFrame
        -_portfolio_signal: DataFrame
        -_portfolio_leverage: DataFrame
        +calculate_trading_PnL()
        +calculate_diagnostic_trading_PnL()
        +calculate_exposures()
        +portfolio_cum() DataFrame
        +portfolio_pnl_ret_stats() RetStats
        +pnl() DataFrame
        +signal() DataFrame
    }

    class PortfolioWeightConstruction {
        -_br: BacktestRequest
        -_risk_engine: RiskEngine
        +optimize_portfolio_weights()
        +calculate_signal_weights_for_portfolio()
    }

    class RiskEngine {
        +calculate_leverage_factor()
        +calculate_vol_adjusted_returns()
        +calculate_vol_adjusted_index_from_prices()
        +calculate_position_clip_adjustment()
    }

    MarketDataRequest <|-- BacktestRequest
    TradingModel --> Backtest : creates & uses
    TradingModel --> BacktestRequest : configures
    Backtest --> PortfolioWeightConstruction : delegates weighting
    Backtest --> RiskEngine : delegates risk
    PortfolioWeightConstruction --> RiskEngine : uses
```

### Curve Module Hierarchy

The curve module uses an abstract base class pattern. Each concrete curve class handles a different asset class while sharing a common interface.

```mermaid
classDiagram
    class AbstractCurve {
        <<abstract>>
        +generate_key()*
        +fetch_continuous_time_series()*
        +construct_total_returns_index()*
    }

    class FXSpotCurve {
        -_market_data_generator
        -_depo_tenor: str
        -_construct_via_currency: str
        +generate_key()
        +fetch_continuous_time_series()
        +construct_total_returns_index()
    }

    class FXForwardsCurve {
        -_fx_forwards_trading_tenor: str
        -_roll_days_before: int
        -_roll_event: str
        -_roll_months: int
        -_cum_index: str
        +generate_key()
        +fetch_continuous_time_series()
        +construct_total_returns_index()
    }

    class FXOptionsCurve {
        -_fx_options_trading_tenor: str
        -_roll_event: str
        -_strike: str
        -_contract_type: str
        +generate_key()
        +fetch_continuous_time_series()
        +construct_total_returns_index()
    }

    class AbstractVolSurface {
        <<abstract>>
    }

    class FXVolSurface {
        -_market_df: DataFrame
        -_asset: str
        -_tenors: list
        -_vol_function_type
        -_atm_method
        -_delta_method
        +build_vol_surface()
        +extract_vol_surface()
        +calculate_implied_vol()
    }

    AbstractCurve <|-- FXSpotCurve
    AbstractCurve <|-- FXForwardsCurve
    AbstractCurve <|-- FXOptionsCurve
    AbstractVolSurface <|-- FXVolSurface
```

## Component Interactions

### Backtest Engine Internals

The `Backtest.calculate_trading_PnL()` method is the core computation pipeline. It coordinates signal processing, risk adjustments, and P&L calculation in a specific order.

```mermaid
flowchart TD
    A[Signal DataFrame + Asset DataFrame] --> B[Apply Signal Delay]
    B --> C[Align Asset & Signal dates]
    C --> D{Stop Loss / Take Profit?}
    D -->|Yes| E[Calculate cumulative trade returns]
    E --> F[Apply risk stop signals]
    F --> G[Mask non-trading days]
    D -->|No| H[Continue]
    G --> H

    H --> I[PortfolioWeightConstruction.optimize_portfolio_weights]

    subgraph Weight Optimization
        I --> J{Signal Vol Adjust?}
        J -->|Yes| K[RiskEngine.calculate_leverage_factor<br/>per-signal level]
        K --> L[Scale signals by leverage]
        J -->|No| L
        L --> M[Calculate signal P&L with TC]
        M --> N{Portfolio Combination?}
        N -->|sum| O[Sum signals]
        N -->|mean| P[Average signals]
        N -->|weighted| Q[Apply custom weights]
        O --> R[Portfolio returns]
        P --> R
        Q --> R
        R --> S{Portfolio Vol Adjust?}
        S -->|Yes| T[RiskEngine.calculate_leverage_factor<br/>portfolio level]
        S -->|No| U[Leverage = 1.0]
        T --> V[Return weights & leverage]
        U --> V
    end

    V --> W[Calculate exposures]
    W --> X{Position Limits?}
    X -->|Yes| Y[RiskEngine.calculate_position_clip_adjustment]
    Y --> Z[Apply clip to signals & leverage]
    X -->|No| AA[Continue]
    Z --> AA
    AA --> AB[Calculate final portfolio returns with TC]
    AB --> AC[Create cumulative index<br/>multiplicative or additive]
    AC --> AD[Store results:<br/>_pnl, _portfolio, _portfolio_signal, etc.]
```

### Two-Level Volatility Targeting

finmarketpy supports volatility targeting at two independent levels, each controlled by separate `BacktestRequest` parameters.

```mermaid
graph TB
    subgraph "Signal Level"
        R1[Raw Signal per Asset<br/>e.g. +1, -1, 0]
        SV[Signal Vol Parameters<br/>signal_vol_target = 0.10<br/>signal_vol_periods = 20]
        SL[Signal Leverage<br/>target_vol / realized_vol]
        AS[Adjusted Signal<br/>signal * leverage]
    end

    subgraph "Portfolio Level"
        PP[Portfolio Returns<br/>weighted sum of signal P&Ls]
        PV[Portfolio Vol Parameters<br/>portfolio_vol_target = 0.10<br/>portfolio_vol_periods = 20]
        PL[Portfolio Leverage<br/>target_vol / realized_vol]
        AP[Final Portfolio<br/>portfolio * leverage]
    end

    subgraph "Position Limits"
        MN[max_net_exposure]
        MA[max_abs_exposure]
        CL[Position Clip Adjustment]
    end

    R1 --> SV
    SV --> SL
    SL --> AS
    AS --> PP
    PP --> PV
    PV --> PL
    PL --> AP
    AP --> MN
    AP --> MA
    MN --> CL
    MA --> CL
```

## Key Design Decisions

### 1. Configuration Override Pattern

`MarketConstants` defines all global settings as class-level attributes. Users override settings by creating a `marketcred.py` file with a `MarketCred` class in the same directory. The `MarketConstants.__init__()` method dynamically reads `MarketCred` attributes and overwrites its own. This pattern prevents user settings from being lost during library upgrades.

**Source**: `src/finmarketpy/util/marketconstants.py` (lines 140-159)

```python
# In marketconstants.py __init__:
try:
    from finmarketpy.util.marketcred import MarketCred
    for k in MarketConstants.__dict__.keys():
        if k in cred_keys and '__' not in k:
            setattr(MarketConstants, k, getattr(MarketCred, k))
except:
    pass
```

### 2. Inheritance from findatapy

`BacktestRequest` inherits from findatapy's `MarketDataRequest`, gaining all data retrieval parameters (tickers, data source, dates, frequency) while adding backtest-specific fields. This means a single object configures both data fetching and backtesting.

**Source**: `src/finmarketpy/backtest/backtestrequest.py` (line 26)

### 3. Abstract TradingModel Pattern

Users implement trading strategies by subclassing `TradingModel` and overriding three abstract methods: `load_parameters()`, `load_assets()`, and `construct_signal()`. The base class handles all backtest execution, benchmark comparison, plotting, and statistics. This clean separation means strategy logic is isolated from infrastructure.

**Source**: `src/finmarketpy/backtest/backtestengine.py` (lines 954-1020)

### 4. Numba Acceleration for Curve Construction

FX spot total return index calculation uses numba's `@guvectorize` decorator for performance-critical loops. A pure Python fallback (`_spot_index`) exists for environments where numba is unavailable.

**Source**: `src/finmarketpy/curve/fxspotcurve.py` (lines 31-60)

### 5. Parallel Processing Abstraction

Parallel execution uses findatapy's `SwimPool`, which abstracts over multiple multiprocessing backends (`multiprocess`, `multiprocessing`, `pathos`). The technique (threading vs multiprocessing) and thread count are configured in `MarketConstants` with platform-specific defaults (8 threads on Linux/Mac, 1 on Windows).

**Source**: `src/finmarketpy/util/marketconstants.py` (lines 32-41)

### 6. Blosc Compression for Parallel Backtests

When running portfolio sub-strategies in parallel, the final strategy's `Backtest` object (which is large) is compressed using blosc before being returned across process boundaries. This reduces memory pressure during multi-process execution.

**Source**: `src/finmarketpy/backtest/backtestengine.py` (lines 1376-1381)

## Module Dependency Graph

```mermaid
graph LR
    subgraph finmarketpy
        backtest --> economics
        backtest --> util
        economics --> util
        curve --> util
        curve_vol[curve/volatility] --> util
        curve_rates[curve/rates] --> util
        network[network_analysis]
    end

    subgraph External
        findatapy
        chartpy
        financepy
    end

    backtest --> findatapy
    backtest --> chartpy
    economics --> findatapy
    economics --> chartpy
    curve --> findatapy
    curve_vol --> financepy
    network --> sklearn[scikit-learn]
```

## Data Flow Summary

All data in finmarketpy flows as pandas DataFrames. Signals are typically represented as DataFrames with values of +1 (long), -1 (short), or 0 (flat). Asset prices are DataFrames with columns named `{ticker}.{field}` (e.g., `EURUSD.close`). Returns are computed from prices by `Calculations.calculate_returns()` from findatapy.

The library does not maintain persistent state between runs. Each `construct_strategy()` call is self-contained: it fetches data, generates signals, runs the backtest, and stores results as instance attributes on the `TradingModel` subclass. Results can then be plotted or exported via the various accessor methods (`strategy_pnl()`, `strategy_signal()`, etc.).

---
## See Also
- [README](README.md) — Project overview and quick start
- [Workflow](workflow.md) — Event flows and processing pipelines
- [State Management](state-management.md) — State lifecycle and data models
- [Development](development.md) — Development guide and best practices
