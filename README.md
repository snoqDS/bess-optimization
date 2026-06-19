# Battery Energy Storage System (BESS) Optimization

A Python project for optimizing battery dispatch to maximize revenue from energy arbitrage.

## Features

- Battery dispatch optimization for energy arbitrage
- Visualization of battery state of charge, power, and prices
- Support for rolling horizon optimization over multiple days
- Modular and extensible codebase

## Requirements

- See pyproject.toml for more details of all libs.

- Python 3.13+
- Pyomo optimization framework
- HiGHS solver
- Pandas, NumPy, Matplotlib

## Installation

1. Create and navigate to your project directory:
   mkdir -p /Projects/optimization/bess_proj
   cd /Projects/optimization/bess_proj

2. Clone the repository contents into this directory:
   git clone https://github.com/snoqDS/bess-optimization.git .

3. Set up the Poetry environment:
   poetry install

4. The HiGHS solver should already be installed but just in case, install the HiGHS solver:
   poetry run pip install highspy

## Quick Start

Run the main optimization:
poetry run python main.py

Try the examples:
poetry run python examples/simple_arbitrage.py
poetry run python examples/multi_day_optimization.py

## Documentation

For detailed usage instructions, see the [User Guide](docs/user_guide.md).

## Project Structure
```
/bess_proj/
│
├── config/                # Configuration files
├── data/                  # Data files
├── docs/                  # Documentation
├── examples/              # Example usage scripts
├── main.py                # Main entry point
├── notebooks/             # Jupyter notebooks
├── pyproject.toml         # Poetry configuration
├── scripts/               # Utility scripts
├── src/                   # Source code
│   └── opt_engine/        # Optimization engine
│       ├── core/          # Core functionality
│       ├── interfaces/    # External system interfaces
│       ├── models/        # Optimization models
│       ├── solvers/       # Solver interfaces
│       └── utils/         # Utility functions
└── tests/                 # Unit tests
```

## License

See LICENSE.md file for details.

Copyright (c) 2025 Philip Regulski

## Contact

https://github.com/snoqDS