import pyomo.environ as pyo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta


def create_battery_dispatch_model(prices, timesteps, battery_params):
    """
    Create a battery dispatch optimization model for energy arbitrage

    Parameters:
    -----------
    prices : array-like
        Electricity prices for each timestep
    timesteps : int
        Number of timesteps in the optimization horizon
    battery_params : dict
        Dictionary containing battery parameters:
        - capacity: Maximum energy storage capacity (MWh or kWh)
        - power_max: Maximum charge/discharge rate (MW or kW)
        - efficiency_charge: Charging efficiency (0-1)
        - efficiency_discharge: Discharging efficiency (0-1)
        - initial_soc: Initial state of charge (MWh or kWh)
        - delta_t: Time step duration (hours)

    Returns:
    --------
    model : pyomo.ConcreteModel
        Pyomo model ready to be solved
    """

    # Extract battery parameters
    capacity = battery_params["capacity"]
    power_max = battery_params["power_max"]
    efficiency_charge = battery_params["efficiency_charge"]
    efficiency_discharge = battery_params["efficiency_discharge"]
    initial_soc = battery_params["initial_soc"]
    delta_t = battery_params["delta_t"]

    # Create model
    model = pyo.ConcreteModel()

    # Define sets
    model.T = pyo.RangeSet(1, timesteps)

    # Define parameters
    model.price = pyo.Param(
        model.T, initialize={t: prices[t - 1] for t in range(1, timesteps + 1)}
    )
    model.delta_t = pyo.Param(initialize=delta_t)

    # Define variables
    model.P_out = pyo.Var(model.T, domain=pyo.NonNegativeReals, bounds=(0, power_max))
    model.P_in = pyo.Var(model.T, domain=pyo.NonNegativeReals, bounds=(0, power_max))
    model.SoC = pyo.Var(model.T, domain=pyo.NonNegativeReals, bounds=(0, capacity))

    # Define objective function
    def objective_rule(model):
        return sum(
            model.price[t] * model.P_out[t] * model.delta_t
            - model.price[t] * model.P_in[t] * model.delta_t
            for t in model.T
        )

    model.Objective = pyo.Objective(rule=objective_rule, sense=pyo.maximize)

    # Define constraints

    # State of Charge evolution constraint
    def soc_evolution_rule(model, t):
        if t == 1:
            return model.SoC[t] == initial_soc - (
                model.P_out[t] * model.delta_t / efficiency_discharge
            ) + (model.P_in[t] * efficiency_charge * model.delta_t)
        else:
            return model.SoC[t] == model.SoC[t - 1] - (
                model.P_out[t] * model.delta_t / efficiency_discharge
            ) + (model.P_in[t] * efficiency_charge * model.delta_t)

    model.SoCEvolution = pyo.Constraint(model.T, rule=soc_evolution_rule)

    return model


def visualize_results(results_df, battery_params):
    """
    Create visualizations of battery dispatch results

    Parameters:
    -----------
    results_df : pandas.DataFrame
        DataFrame containing results with columns:
        - Time: Timestep index
        - Price: Electricity price
        - Power_Out: Battery discharge power
        - Power_In: Battery charge power
        - State_of_Charge: Battery state of charge
    battery_params : dict
        Dictionary of battery parameters
    """
    # Create a datetime index for better x-axis formatting
    start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    time_index = [start_time + timedelta(hours=t - 1) for t in results_df["Time"]]
    results_df["Datetime"] = time_index

    # Create net power (positive for discharge, negative for charge)
    results_df["Net_Power"] = results_df["Power_Out"] - results_df["Power_In"]

    # Create figure with two subplots sharing x-axis
    fig, (ax1, ax2, ax3) = plt.subplots(
        3, 1, figsize=(12, 10), sharex=True, gridspec_kw={"height_ratios": [2, 2, 1]}
    )

    # Set up colors
    price_color = "tab:red"
    soc_color = "tab:blue"
    charge_color = "tab:green"
    discharge_color = "tab:orange"

    # Plot 1: State of Charge
    ax1.plot(
        results_df["Datetime"],
        results_df["State_of_Charge"],
        color=soc_color,
        linewidth=2,
    )
    ax1.set_ylabel("State of Charge (kWh)", color=soc_color, fontsize=12)
    ax1.tick_params(axis="y", labelcolor=soc_color)
    ax1.set_ylim(0, battery_params["capacity"] * 1.05)
    ax1.set_title("Battery Dispatch Optimization Results", fontsize=14)
    ax1.grid(True, alpha=0.3)

    # Plot 2: Battery Power (Charge/Discharge)
    ax2.bar(
        results_df["Datetime"],
        results_df["Power_In"],
        color=charge_color,
        label="Charge",
        alpha=0.7,
        width=0.02,
    )
    ax2.bar(
        results_df["Datetime"],
        results_df["Power_Out"],
        color=discharge_color,
        label="Discharge",
        alpha=0.7,
        width=0.02,
    )
    ax2.set_ylabel("Power (kW)", fontsize=12)
    ax2.set_ylim(0, battery_params["power_max"] * 1.1)
    ax2.legend(loc="upper right")
    ax2.grid(True, alpha=0.3)

    # Plot 3: Electricity Prices
    ax3.plot(
        results_df["Datetime"], results_df["Price"], color=price_color, linewidth=2
    )
    ax3.set_ylabel("Price ($/kWh)", color=price_color, fontsize=12)
    ax3.tick_params(axis="y", labelcolor=price_color)
    ax3.set_xlabel("Time", fontsize=12)
    ax3.grid(True, alpha=0.3)

    # Format x-axis
    for ax in [ax1, ax2, ax3]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))

    plt.tight_layout()
    return fig


# Example usage
if __name__ == "__main__":
    # Example input data
    timesteps = 24  # 24 hours

    # Random prices for example (with morning and evening peaks)
    hours = np.linspace(0, 23, timesteps)
    base_price = (
        20 + 15 * np.sin(np.pi * (hours - 10) / 12) ** 2
    )  # Morning and evening peaks
    np.random.seed(42)
    noise = np.random.normal(0, 1.5, timesteps)
    prices = base_price + noise

    # Battery parameters
    battery_params = {
        "capacity": 100,  # 100 kWh
        "power_max": 25,  # 25 kW
        "efficiency_charge": 0.95,
        "efficiency_discharge": 0.95,
        "initial_soc": 50,  # 50 kWh (half full)
        "delta_t": 1.0,  # 1-hour timesteps
    }

    # Create and solve the model
    model = create_battery_dispatch_model(prices, timesteps, battery_params)

    # Set solver to HiGHS
    solver = pyo.SolverFactory("appsi_highs")
    results = solver.solve(model, tee=True)

    # Check solution status
    if results.solver.status == pyo.SolverStatus.ok:
        print("Solution is optimal")

        # Extract and print results
        power_out = [model.P_out[t].value for t in model.T]
        power_in = [model.P_in[t].value for t in model.T]
        soc = [model.SoC[t].value for t in model.T]

        # Calculate profit
        profit = sum(
            prices[t - 1] * power_out[t - 1] * battery_params["delta_t"]
            - prices[t - 1] * power_in[t - 1] * battery_params["delta_t"]
            for t in range(1, timesteps + 1)
        )

        print(f"Total profit: ${profit:.2f}")

        # Create results dataframe
        results_df = pd.DataFrame(
            {
                "Time": range(1, timesteps + 1),
                "Price": prices,
                "Power_Out": power_out,
                "Power_In": power_in,
                "State_of_Charge": soc,
            }
        )

        print(results_df.head())

        # Visualize results
        fig = visualize_results(results_df, battery_params)
        plt.savefig("battery_dispatch_results.png", dpi=300, bbox_inches="tight")
        plt.show()
    else:
        print("Solver did not find an optimal solution")
