# Battery Energy Storage System (BESS) Optimization

A Python optimization engine for battery dispatch to maximize revenue from energy arbitrage. Built on Pyomo and HiGHS, it supports single-day and rolling horizon multi-day optimization with ramp rate, state-of-charge, and simultaneous charge/discharge constraints.

## Features

- Battery dispatch optimization for energy arbitrage
- Rolling horizon optimization over multiple days
- Ramp rate and simultaneous charge/discharge constraints
- State of charge (SoC) min/max enforcement
- Visualization of battery dispatch, SoC, and price signals
- Modular and extensible optimization engine
- 4 pytest tests passing

## Requirements

- Python 3.11+
- Pyomo optimization framework
- HiGHS solver
- Pandas, NumPy, Matplotlib

See `pyproject.toml` for full dependency list.

## Installation

Clone the repository:

    git clone https://github.com/snoqDS/bess-optimization.git
    cd bess-optimization

Install uv if not already installed:

    curl -LsSf https://astral.sh/uv/install.sh | sh

Install dependencies:

    uv sync

Run the optimization:

    uv run python main.py

## Quick Start

Run the main optimization with default battery parameters:

    uv run python main.py

Try the examples:

    uv run python examples/basic/simple_arbitrage.py
    uv run python examples/basic/multi_day_optimization.py

Run the test suite:

    uv run pytest tests/ -v

## Project Structure

    bess-optimization/
    ├── config/                # Battery and solver configuration
    │   └── battery_params/    # Battery parameter definitions
    ├── data/                  # Data files (raw and processed)
    ├── docs/                  # Documentation and user guide
    ├── examples/              # Standalone runnable examples
    │   └── basic/             # Single and multi-day examples
    ├── notebooks/             # Jupyter notebooks for analysis
    ├── scripts/               # Utility scripts
    ├── src/
    │   └── opt_engine/        # Core optimization engine
    │       ├── core/          # Core functionality
    │       ├── interfaces/    # External system interfaces
    │       ├── models/        # Battery and market models
    │       ├── solvers/       # Solver interfaces
    │       └── utils/         # Utilities, logging, visualization
    ├── tests/                 # Test suite
    ├── main.py                # Main entry point
    └── pyproject.toml         # Project configuration

## Roadmap

- [ ] Real market price data integration (ERCOT, CAISO via GridStatus)
- [ ] Weather integration for forecasting high-stress and high-price periods
- [ ] Multi-asset portfolio optimization (solar + BESS + flexible load)
- [ ] Degradation modeling for battery lifecycle costing
- [ ] REST API wrapper for dispatch recommendations
- [ ] Streamlit dashboard for visualization

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.

Copyright 2026 Philip Regulski

## Contact

- GitHub: [snoqDS](https://github.com/snoqDS)
- LinkedIn: [philregulski](https://www.linkedin.com/in/philregulski/)
