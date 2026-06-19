# Battery Energy Storage System (BESS) Optimization
## User Guide

This guide explains how to use the BESS optimization project to model and optimize battery dispatch for energy arbitrage.

## Setup and Installation

1. Create and navigate to the project directory:
   mkdir -p /Projects/optimization/bess_proj
   cd /Projects/optimization/bess_proj

2. Clone the repository contents into this directory:
   git clone https://github.com/snoqDS/bess-optimization.git .
   
   Note the period at the end of the command, which clones the contents directly into the current directory.

3. Set up the Poetry environment:
   poetry install

4. The HiGHS solver should already be installed but just in case, install the HiGHS solver:
   poetry run pip install highspy

## Basic Usage

### Running the Default Optimization

To run the basic optimization with default settings:

poetry run python main.py

This will:
1. Generate synthetic price data
2. Create and solve a battery dispatch model
3. Save results to CSV and generate visualization plots

### Using Custom Battery Parameters

You can modify the battery parameters in `config/battery_params.py` or create new battery configurations.

### Working with Real Price Data

To use real price data:

1. Place your price data CSV in the `data/raw/` directory
2. Update `main.py` to load your data instead of generating synthetic data
3. Run the optimization as normal

## Advanced Usage

### Multi-day Optimization

The project includes an example of multi-day optimization with rolling horizon:

poetry run python examples/multi_day_optimization.py

This demonstrates how to optimize over longer time periods by solving a series of overlapping optimization problems.

### Extending the Model

To extend the model with additional constraints or features:

1. Modify the battery model in `src/opt_engine/models/battery.py`
2. Add new parameters to the battery configuration in `config/battery_params.py`
3. Add visualization capabilities for new variables in `src/opt_engine/utils/viz_utils.py`

## Project Structure
```
/bess_proj/
│
├── config/                         # Configuration files
│   ├── battery_params/             # Battery configurations
│   ├── pv_params/                  # PV system configurations
│   ├── load_params/                # Load/demand configurations
│   ├── grid_params/                # Grid connection parameters
│   ├── market_params/              # Market rules and structures
│   ├── resource_params/            # Other energy resources configs
│   ├── environmental_params/       # Emissions and environmental settings
│   └── regulatory_params/          # Regulatory compliance settings
│
├── data/                           # Data files
│   ├── raw/                        # Raw data
│   │   ├── price/                  # Market price data
│   │   ├── weather/                # Weather data for renewables
│   │   ├── load/                   # Load profile data
│   │   └── grid/                   # Grid condition data
│   └── processed/                  # Processed data
│
├── docs/                           # Documentation
│   ├── models/                     # Model documentation
│   ├── apis/                       # API documentation
│   └── tutorials/                  # Tutorials and guides
│
├── examples/                       # Example usage scripts
│   ├── basic/                      # Basic usage examples
│   ├── advanced/                   # Advanced optimization scenarios
│   └── real_world/                 # Real-world case studies
│
├── main.py                         # Main entry point
├── notebooks/                      # Jupyter notebooks
├── pyproject.toml                  # Poetry configuration
│
├── scripts/                        # Utility scripts
│   ├── data_processing/            # Data processing scripts
│   ├── visualization/              # Standalone visualization scripts
│   └── analysis/                   # Analysis scripts
│
├── src/                            # Source code
│   ├── opt_engine/                 # Optimization engine
│   │   ├── core/                   # Core functionality
│   │   │   ├── system.py           # Integrated system model
│   │   │   ├── optimizer.py        # Main optimizer
│   │   │   └── scheduler.py        # Optimization scheduler
│   │   │
│   │   ├── interfaces/             # External system interfaces
│   │   │   ├── market/             # Market interfaces
│   │   │   ├── grid/               # Grid interfaces
│   │   │   ├── weather/            # Weather data interfaces
│   │   │   └── regulatory/         # Regulatory reporting interfaces
│   │   │
│   │   ├── models/                 # Optimization models
│   │   │   ├── battery/            # Battery models
│   │   │   ├── pv/                 # PV generation models
│   │   │   ├── load/               # Load/demand models
│   │   │   │   ├── building.py     # Building load models
│   │   │   │   ├── ev.py           # EV charging models
│   │   │   │   └── flexible.py     # Flexible load models
│   │   │   │
│   │   │   ├── grid/               # Grid interaction models
│   │   │   ├── market/             # Market and financial models
│   │   │   │   ├── price.py        # Price forecasting
│   │   │   │   ├── arbitrage.py    # Energy arbitrage
│   │   │   │   ├── dr.py           # Demand response
│   │   │   │   └── ancillary.py    # Ancillary services
│   │   │   │
│   │   │   ├── resources/          # Other energy resources
│   │   │   │   ├── wind.py         # Wind generation
│   │   │   │   ├── chp.py          # Combined heat and power
│   │   │   │   ├── fuel_cell.py    # Fuel cell systems
│   │   │   │   ├── hydrogen.py     # Hydrogen systems
│   │   │   │   └── thermal.py      # Thermal storage
│   │   │   │
│   │   │   ├── environmental/      # Environmental models
│   │   │   │   ├── emissions.py    # Emissions tracking
│   │   │   │   └── credits.py      # Renewable credits
│   │   │   │
│   │   │   └── resilience/         # Resilience models
│   │   │       ├── microgrid.py    # Microgrid controls
│   │   │       └── backup.py       # Backup power models
│   │   │
│   │   ├── solvers/                # Solver interfaces
│   │   │   ├── deterministic/      # Deterministic solvers
│   │   │   ├── stochastic/         # Stochastic optimization
│   │   │   ├── mpc/                # Model predictive control
│   │   │   └── rl/                 # Reinforcement learning
│   │   │
│   │   └── utils/                  # Utility functions
│   │       ├── visual/             # Visualization utilities
│   │       │   ├── battery_viz.py  # Battery visualization
│   │       │   ├── pv_viz.py       # PV visualization
│   │       │   ├── load_viz.py     # Load visualization
│   │       │   └── system_viz.py   # System visualization
│   │       │
│   │       ├── analysis/           # Analysis utilities
│   │       │   ├── performance.py  # Performance analysis
│   │       │   ├── economics.py    # Economic analysis
│   │       │   └── emissions.py    # Emissions analysis
│   │       │
│   │       ├── data_utils.py       # Data utilities
│   │       └── logging_utils.py    # Logging utilities
│   │
│   └── workflows/                  # Workflow pipelines
│       ├── forecast_pipeline.py    # Forecasting pipeline
│       ├── optimization_pipeline.py # Optimization pipeline
│       ├── reporting_pipeline.py   # Reporting pipeline
│       └── integration_pipeline.py # Complete system pipeline
│
└── tests/                          # Unit tests
    ├── models/                     # Tests for models
    ├── utils/                      # Tests for utilities
    ├── workflows/                  # Tests for workflows
    └── integration/                # Integration tests
```

## Troubleshooting

- **Solver not found**: Make sure the HiGHS solver is installed in your Poetry environment
- **Optimization fails**: Check the solver status and termination condition for clues
- **Poor results**: Verify that your price data has sufficient price spread for arbitrage opportunities

## Next Steps

Future enhancements may include:
- Adding battery degradation constraints
- Incorporating forecasting uncertainty
- Implementing additional revenue streams (frequency regulation, capacity payments, etc.)
- Developing a web interface for visualization and control