"""
Multi-day optimization example with rolling horizon.
This example demonstrates how to optimize battery dispatch over multiple days
using a rolling horizon approach.
"""

import sys
import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import project modules
from src.opt_engine.models.battery.battery_model import BatteryModel
from src.opt_engine.utils.visual.visual_utils import plot_dispatch_results
from src.opt_engine.utils.data_utils import generate_synthetic_price_data
from config.battery_params.battery_params import get_battery_params
from src.opt_engine.utils.logging_utils import get_logger, setup_logging


class RollingHorizonOptimizer:
    """Rolling horizon optimization for battery dispatch."""

    def __init__(self, battery_params, horizon_hours=24, step_hours=6):
        """
        Initialize the rolling horizon optimizer.

        Parameters
        ----------
        battery_params : dict
            Dictionary of battery parameters.
        horizon_hours : int, optional
            Optimization horizon length in hours, by default 24.
        step_hours : int, optional
            Step size for rolling horizon in hours, by default 6.
        """
        self.battery_params = battery_params
        self.horizon_hours = horizon_hours
        self.step_hours = step_hours
        self.battery_model = BatteryModel(battery_params)
        self.logger = get_logger(__name__)

    def optimize(self, prices, total_hours):
        """
        Perform rolling horizon optimization.

        Parameters
        ----------
        prices : array-like
            Array of electricity prices for the entire period.
        total_hours : int
            Total number of hours to optimize for.

        Returns
        -------
        pandas.DataFrame
            DataFrame with optimization results.
        """
        # Number of optimization steps
        num_steps = (total_hours - self.horizon_hours) // self.step_hours + 1

        # Initialize results storage
        all_results = []
        current_soc = self.battery_params["initial_soc"]

        self.logger.info(f"Performing rolling horizon optimization with:")
        self.logger.info(f"  Total period: {total_hours} hours")
        self.logger.info(f"  Horizon length: {self.horizon_hours} hours")
        self.logger.info(f"  Step size: {self.step_hours} hours")
        self.logger.info(f"  Number of optimization steps: {num_steps}")

        for step in range(num_steps):
            start_hour = step * self.step_hours
            end_hour = min(
                start_hour + self.horizon_hours, total_hours
            )  # Make sure we don't go past the end

            self.logger.info(
                f"Optimization step {step+1}/{num_steps}: Hours {start_hour} to {end_hour}"
            )

            # Get price slice for this horizon
            price_slice = prices[start_hour:end_hour]

            # Update initial SOC for this horizon
            step_battery_params = self.battery_params.copy()
            step_battery_params["initial_soc"] = current_soc

            # Create and solve model for this horizon
            self.battery_model = BatteryModel(step_battery_params)
            self.battery_model.create_model(price_slice, len(price_slice))
            results = self.battery_model.solve(tee=False)

            if (
                results.solver.status.value == "ok"
                and results.solver.termination_condition.value == "optimal"
            ):
                # Get results
                results_df = self.battery_model.get_results()

                # Only keep the first step_hours of results (or less for the last step)
                keep_hours = min(
                    self.step_hours, len(results_df), total_hours - start_hour
                )

                # Check if we have enough results
                if keep_hours <= 0 or keep_hours > len(results_df):
                    self.logger.warning(
                        f"Cannot keep {keep_hours} hours from results with length {len(results_df)}"
                    )
                    if len(all_results) > 0:
                        break  # We already have some results, so just stop here
                    else:
                        continue  # Skip this step and try the next one

                step_results = results_df.iloc[:keep_hours].copy()

                # Adjust time index
                step_results["Time"] = step_results["Time"] + start_hour

                # Store results
                all_results.append(step_results)

                # Update SOC for next iteration
                if keep_hours > 0 and keep_hours <= len(results_df):
                    current_soc = results_df.iloc[keep_hours - 1]["State_of_Charge"]
                    self.logger.info(f"Step profit: ${results_df.attrs['profit']:.2f}")
                    self.logger.info(f"New SOC: {current_soc:.2f} kWh")
                else:
                    # Use the last available SOC
                    current_soc = results_df.iloc[-1]["State_of_Charge"]
                    self.logger.info(f"Step profit: ${results_df.attrs['profit']:.2f}")
                    self.logger.info(
                        f"New SOC (using last available): {current_soc:.2f} kWh"
                    )
            else:
                self.logger.error(f"Solver failed with status: {results.solver.status}")
                self.logger.error(
                    f"Termination condition: {results.solver.termination_condition}"
                )
                break

        # Combine all results
        if all_results:
            combined_results = pd.concat(all_results, ignore_index=True)

            # Calculate total profit
            total_profit = sum(
                combined_results["Price"]
                * combined_results["Power_Out"]
                * self.battery_params["delta_t"]
                - combined_results["Price"]
                * combined_results["Power_In"]
                * self.battery_params["delta_t"]
            )

            combined_results.attrs["profit"] = total_profit
            return combined_results
        else:
            return None


def main():
    # Set up logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, f"multi_day_optimization_{timestamp}.log")
    setup_logging(log_level=logging.INFO, log_file=log_file)
    logger = get_logger(__name__)

    logger.info("Multi-Day Battery Optimization with Rolling Horizon")
    logger.info("=================================================")

    # Get battery parameters
    battery_params = get_battery_params("default")

    # Generate multi-day price data
    days = 3
    points_per_day = 24
    logger.info(f"Generating synthetic price data for {days} days...")
    prices, price_df = generate_synthetic_price_data(
        days=days, points_per_day=points_per_day, seed=42
    )

    # Initialize rolling horizon optimizer
    horizon_hours = 24
    step_hours = 6
    optimizer = RollingHorizonOptimizer(
        battery_params, horizon_hours=horizon_hours, step_hours=step_hours
    )

    # Perform optimization
    logger.info("Starting rolling horizon optimization...")
    results_df = optimizer.optimize(prices, total_hours=days * points_per_day)

    if results_df is not None:
        logger.info("Optimization completed successfully!")
        logger.info(f"Total profit over {days} days: ${results_df.attrs['profit']:.2f}")

        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
        os.makedirs(output_dir, exist_ok=True)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = os.path.join(output_dir, f"multi_day_results_{timestamp}.csv")
        results_df.to_csv(csv_path, index=False)
        logger.info(f"Results saved to: {csv_path}")

        # Plot results for each day
        for day in range(days):
            day_start = day * points_per_day
            day_end = (day + 1) * points_per_day

            day_results = results_df[
                (results_df["Time"] >= day_start) & (results_df["Time"] < day_end)
            ].copy()
            day_results["Time"] = day_results["Time"] - day_start + 1

            # Add day profit to attributes
            day_profit = sum(
                day_results["Price"]
                * day_results["Power_Out"]
                * battery_params["delta_t"]
                - day_results["Price"]
                * day_results["Power_In"]
                * battery_params["delta_t"]
            )
            day_results.attrs["profit"] = day_profit

            # Plot and save
            fig_path = os.path.join(output_dir, f"day_{day+1}_results_{timestamp}.png")
            plot_dispatch_results(
                day_results, battery_params, show=True, save_path=fig_path
            )
            logger.info(f"Day {day+1} plot saved to: {fig_path}")
    else:
        logger.error("Optimization failed.")


if __name__ == "__main__":
    main()
