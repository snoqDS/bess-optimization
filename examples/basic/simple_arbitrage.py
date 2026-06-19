"""
Simple energy arbitrage example using the battery model.
This example demonstrates how to use the battery model for energy arbitrage.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Import project modules
from src.opt_engine.models.battery.battery_model import BatteryModel
from src.opt_engine.utils.visual.visual_utils import plot_dispatch_results

# Update all imports to use absolute paths
from src.opt_engine.models.battery.battery_model import BatteryModel
from src.opt_engine.utils.visual.visual_utils import plot_dispatch_results
from config.battery_params.battery_params import get_battery_params


def main():
    print("Battery Energy Arbitrage Example")
    print("===============================")

    # Get battery parameters
    battery_params = get_battery_params("small")  # Using small battery for this example

    # Generate daily price pattern (high prices in morning and evening)
    timesteps = 24
    np.random.seed(42)
    hours = np.linspace(0, 23, timesteps)

    # Create a price pattern with morning and evening peaks
    morning_peak = np.exp(-0.5 * ((hours - 9) / 2) ** 2)  # Morning peak around 9 AM
    evening_peak = np.exp(-0.5 * ((hours - 19) / 2) ** 2)  # Evening peak around 7 PM
    base_price = 20 + 30 * (morning_peak + evening_peak)  # Combine peaks
    noise = np.random.normal(0, 1.0, timesteps)
    prices = base_price + noise

    print("\nRunning optimization...")

    # Create and solve model
    battery_model = BatteryModel(battery_params)
    battery_model.create_model(prices, timesteps)
    results = battery_model.solve()

    # Get and display results
    results_df = battery_model.get_results()
    profit = results_df.attrs["profit"]

    print(f"\nOptimization completed successfully.")
    print(f"Total profit from arbitrage: ${profit:.2f}")

    # Visualize results
    plot_dispatch_results(results_df, battery_params)


if __name__ == "__main__":
    main()
