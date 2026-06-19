"""Battery dispatch optimization model."""

import pyomo.environ as pyo
import pandas as pd

from src.opt_engine.utils.logging_utils import get_logger


class BatteryModel:
    """
    Battery energy storage system optimization model.

    Model for optimizing battery operations to maximize revenue by charging
    when electricity prices are low and discharging when prices are high,
    subject to physical and operational constraints.
    """

    def __init__(self, battery_params):
        """
        Initialize a battery model.

        battery_params : dict
            Dictionary of battery parameters including:
            - capacity: Battery energy capacity (kWh)
            - power_max: Maximum charge/discharge power (kW)
            - efficiency_charge: Charging efficiency (decimal, 0-1)
            - efficiency_discharge: Discharging efficiency (decimal, 0-1)
            - initial_soc: Initial state of charge (kWh)
            - delta_t: Timestep duration (hours)
            - soc_min: Minimum state of charge allowed (decimal, 0-1, optional)
            - soc_max: Maximum state of charge allowed (decimal, 0-1, optional)
            - ramp_limit: Maximum power change per timestep (kW/timestep, optional)

        """
        self.battery_params = battery_params
        self.model = None
        self.logger = get_logger(__name__)
        self.logger.debug(
            f"Initialized battery model with parameters: {battery_params}"
        )

    def create_model(self, prices, timesteps):
        """
        Create a Pyomo optimization model for battery dispatch.

        This model creates decision variables for charging and discharging,
        implements constraints for battery operation, and sets up the objective
        function to maximize profit.

        Parameters
        ----------
        prices : array-like
            Electricity prices for each timestep.
        timesteps : int
            Number of timesteps in the optimization horizon.

        Returns
        -------
        model : pyomo.ConcreteModel
            Pyomo model ready to be solved.
        """
        # Extract battery parameters
        capacity = self.battery_params["capacity"]
        power_max = self.battery_params["power_max"]
        efficiency_charge = self.battery_params["efficiency_charge"]
        efficiency_discharge = self.battery_params["efficiency_discharge"]
        initial_soc = self.battery_params["initial_soc"]
        delta_t = self.battery_params["delta_t"]
        ramp_limit = self.battery_params.get(
            "ramp_limit", float("inf")
        )  # Default to no limit if not provided

        # Get SoC constraints
        soc_min_pct = self.battery_params.get(
            "soc_min", 0.0
        )  # Default to 0 if not provided
        soc_max_pct = self.battery_params.get(
            "soc_max", 1.0
        )  # Default to 1 if not provided

        # Calculate absolute SoC limits
        soc_min = soc_min_pct * capacity
        soc_max = soc_max_pct * capacity

        self.logger.debug(
            f"SoC constraints: min={soc_min} kWh ({soc_min_pct*100}%), max={soc_max} kWh ({soc_max_pct*100}%)"
        )

        # Create model
        self.model = pyo.ConcreteModel()
        model = self.model

        # Define sets
        model.T = pyo.RangeSet(1, timesteps)

        # Define parameters
        model.price = pyo.Param(
            model.T, initialize={t: prices[t - 1] for t in range(1, timesteps + 1)}
        )
        model.delta_t = pyo.Param(initialize=delta_t)

        # Define variables
        # Power output (discharge) at each timestep [kW]
        model.P_out = pyo.Var(
            model.T, domain=pyo.NonNegativeReals, bounds=(0, power_max)
        )
        # Power input (charge) at each timestep [kW]
        model.P_in = pyo.Var(
            model.T, domain=pyo.NonNegativeReals, bounds=(0, power_max)
        )
        # State of Charge at each timestep [kWh]
        model.SoC = pyo.Var(
            model.T, domain=pyo.NonNegativeReals, bounds=(soc_min, soc_max)
        )
        # Binary variable indicating charging (1) or discharging (0) mode
        model.is_charging = pyo.Var(model.T, domain=pyo.Binary)
        # Net power variable (P_out - P_in) for cleaner ramp rate formulation
        model.P_net = pyo.Var(model.T, domain=pyo.Reals, bounds=(-power_max, power_max))

        # Validate initial SoC is within bounds
        if initial_soc < soc_min:
            self.logger.warning(
                f"Initial SoC {initial_soc} kWh is below minimum {soc_min} kWh. Setting to minimum."
            )
            initial_soc = soc_min
        elif initial_soc > soc_max:
            self.logger.warning(
                f"Initial SoC {initial_soc} kWh is above maximum {soc_max} kWh. Setting to maximum."
            )
            initial_soc = soc_max

        # Define objective function: Maximize profit.
        # Revenue from discharging minus cost of charging
        def objective_rule(model):
            return sum(
                model.price[t] * model.P_out[t] * model.delta_t  # Revenue
                - model.price[t] * model.P_in[t] * model.delta_t  # Cost
                for t in model.T
            )

        model.Objective = pyo.Objective(rule=objective_rule, sense=pyo.maximize)

        # Define constraints

        # State of Charge evolution constraint (energy conservation)
        # Tracks how the battery's SoC changes over time based on:
        # - Energy lost when discharging (divided by discharge efficiency)
        # - Energy gained when charging (multiplied by charge efficiency)
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

        # No simultaneous charge and discharge constraint
        # When is_charging = 1, P_out must be 0
        # When is_charging = 0, P_in must be 0
        def no_simultaneous_charge_discharge_in_rule(model, t):
            return model.P_in[t] <= power_max * model.is_charging[t]

        def no_simultaneous_charge_discharge_out_rule(model, t):
            return model.P_out[t] <= power_max * (1 - model.is_charging[t])

        model.NoSimChargeIn = pyo.Constraint(
            model.T, rule=no_simultaneous_charge_discharge_in_rule
        )
        model.NoSimChargeOut = pyo.Constraint(
            model.T, rule=no_simultaneous_charge_discharge_out_rule
        )

        # Net power definition constraint
        # This links the net power variable to the charge and discharge power variables
        def net_power_rule(model, t):
            return model.P_net[t] == model.P_out[t] - model.P_in[t]

        model.NetPowerDef = pyo.Constraint(model.T, rule=net_power_rule)

        # Ramp rate constraints
        # These constraints limit how quickly the battery can change its power output
        # between consecutive timesteps
        def ramp_up_limit_rule(model, t):
            if t == 1:
                return pyo.Constraint.Skip
            return model.P_net[t] - model.P_net[t - 1] <= ramp_limit

        def ramp_down_limit_rule(model, t):
            if t == 1:
                return pyo.Constraint.Skip
            return model.P_net[t - 1] - model.P_net[t] <= ramp_limit

        model.RampUpLimit = pyo.Constraint(model.T, rule=ramp_up_limit_rule)
        model.RampDownLimit = pyo.Constraint(model.T, rule=ramp_down_limit_rule)

        self.logger.debug(
            f"Added ramp rate constraints with limit: {ramp_limit} kW/timestep"
        )

        return model

    def solve(self, solver_name="appsi_highs", tee=False):
        """
        Solve the optimization model.

        Parameters
        ----------
        solver_name : str, optional
            Name of the solver to use, by default 'appsi_highs'.
        tee : bool, optional
            Whether to show solver output, by default False.

        Returns
        -------
        results : pyomo.opt.results.SolverResults
            Solver results.
        """
        if self.model is None:
            raise ValueError(
                "Model has not been created yet. Call create_model() first."
            )

        solver = pyo.SolverFactory(solver_name)
        results = solver.solve(self.model, tee=tee)
        return results

    def get_results(self):
        """
        Extract results from the solved model.

        Returns
        -------
        results_df : pandas.DataFrame
            DataFrame containing optimization results including:
            - Time: Timestep index
            - Price: Electricity price at each timestep
            - Power_Out: Discharge power at each timestep
            - Power_In: Charge power at each timestep
            - State_of_Charge: Battery SoC at each timestep
            - Net_Power: Net power (Power_Out - Power_In)
            - Ramp_Rate: Power ramp rate between timesteps
            - is_charging: Binary indicator of charging mode

        DataFrame attrs also includes:
            - profit: Total profit from battery operation
        """
        if self.model is None:
            raise ValueError(
                "Model has not been created yet. Call create_model() first."
            )

        model = self.model

        # Extract results
        power_out = [model.P_out[t].value for t in model.T]
        power_in = [model.P_in[t].value for t in model.T]
        net_power = [model.P_net[t].value for t in model.T]
        soc = [model.SoC[t].value for t in model.T]
        prices = [model.price[t] for t in model.T]
        is_charging = [model.is_charging[t].value for t in model.T]

        # Calculate ramp rates between consecutive timesteps
        ramp_rates = [0]  # First timestep has no ramp rate
        for i in range(1, len(net_power)):
            ramp_rates.append(net_power[i] - net_power[i - 1])

        # Calculate profit
        profit = sum(
            prices[t - 1] * power_out[t - 1] * model.delta_t.value
            - prices[t - 1] * power_in[t - 1] * model.delta_t.value
            for t in range(1, len(power_out) + 1)
        )

        # Create results dataframe
        results_df = pd.DataFrame(
            {
                "Time": range(1, len(power_out) + 1),
                "Price": prices,
                "Power_Out": power_out,
                "Power_In": power_in,
                "Net_Power": net_power,
                "State_of_Charge": soc,
                "Ramp_Rate": ramp_rates,
                "is_charging": is_charging,
            }
        )

        # Add metadata
        results_df.attrs["profit"] = profit

        return results_df
