"""
Smoke tests to verify core dependencies are installed and working correctly.
"""

import pytest


def test_pyomo_import():
    """Pyomo imports successfully."""
    import pyomo.environ as pyo
    assert pyo is not None


def test_highs_import():
    """HiGHS imports successfully."""
    import highspy
    assert highspy is not None


def test_pandas_import():
    """Pandas imports successfully."""
    import pandas as pd
    assert pd is not None


def test_basic_optimization():
    """Pyomo + HiGHS solve a simple LP correctly."""
    import pyomo.environ as pyo

    model = pyo.ConcreteModel()
    model.x = pyo.Var(domain=pyo.NonNegativeReals)
    model.y = pyo.Var(domain=pyo.NonNegativeReals)
    model.profit = pyo.Objective(expr=3 * model.x + 4 * model.y, sense=pyo.maximize)
    model.constraint1 = pyo.Constraint(expr=model.x + 2 * model.y <= 10)
    model.constraint2 = pyo.Constraint(expr=3 * model.x + model.y <= 15)

    solver = pyo.SolverFactory("appsi_highs")
    results = solver.solve(model)

    # Optimal: x=4, y=3 gives profit=3*4+4*3=24
    assert pyo.value(model.profit) == pytest.approx(24.0, rel=1e-3)
    assert pyo.value(model.x) == pytest.approx(4.0, rel=1e-3)
    assert pyo.value(model.y) == pytest.approx(3.0, rel=1e-3)
