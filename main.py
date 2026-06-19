"""
BESS Optimization Engine - Main entry point
====================================

This script serves as the main entry point for the BESS optimization engine.
It sets up logging and provides a command-line interface for the application.
"""

import logging
import os
import sys
import time
from datetime import datetime

# Import project modules
from src.opt_engine.models.battery.battery_model import BatteryModel
from src.opt_engine.utils.logging_utils import setup_logging, get_logger
from src.opt_engine.utils.visual.visual_utils import plot_dispatch_results
from src.opt_engine.utils.cli_utils import parse_bess_arguments
from src.opt_engine.utils.data_utils import generate_synthetic_price_data
from config.battery_params.battery_params import get_battery_params


def main():
    """Main entry point for the application."""
    # Parse command-line arguments
    args = parse_bess_arguments()

    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Set up logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = args.log_file or os.path.join(
        output_dir, f"optimization_run_{timestamp}.log"
    )
    log_level = getattr(logging, args.log_level)
    setup_logging(log_level=log_level, log_file=log_file)

    # Get logger for this module
    logger = get_logger(__name__)

    logger.info("==============================================")
    logger.info("Battery Energy Storage System (BESS) Optimization")
    logger.info("==============================================")

    try:
        # Record start time for performance tracking
        start_time = time.time()

        # Load battery configuration
        battery_type = args.battery_type
        battery_params = get_battery_params(battery_type)
        logger.info(f"Using {battery_type} battery configuration:")
        for key, value in battery_params.items():
            logger.info(f"  {key}: {value}")

        # Generate or load price data
        timesteps = args.timesteps
        logger.info(f"Generating synthetic price data for {timesteps} timesteps...")
        prices, _ = generate_synthetic_price_data(
            days=1, points_per_day=timesteps, seed=42
        )
        logger.info(f"Price range: ${min(prices):.2f} to ${max(prices):.2f}")

        # Create and solve the battery model
        logger.info("Creating optimization model...")
        battery_model = BatteryModel(battery_params)
        battery_model.create_model(prices, timesteps)

        logger.info(f"Solving optimization model using solver: {args.solver}...")
        results = battery_model.solve(solver_name=args.solver, tee=True)

        # Check if the solution is optimal
        if (
            results.solver.status.value == "ok"
            and results.solver.termination_condition.value == "optimal"
        ):
            logger.info("Found optimal solution!")

            # Get and print results
            results_df = battery_model.get_results()
            profit = results_df.attrs["profit"]
            logger.info(f"Total profit: ${profit:.2f}")

            # Save results to CSV
            csv_path = os.path.join(output_dir, f"battery_results_{timestamp}.csv")
            results_df.to_csv(csv_path, index=False)
            logger.info(f"Results saved to: {csv_path}")

            # Plot and save visualization unless disabled
            if not args.no_plot:
                logger.info("Generating visualization...")
                fig_path = os.path.join(output_dir, f"battery_plot_{timestamp}.png")
                plot_dispatch_results(
                    results_df, battery_params, show=True, save_path=fig_path
                )
                logger.info(f"Plot saved to: {fig_path}")
        else:
            logger.error("Solver did not find an optimal solution.")
            logger.error(f"Solver status: {results.solver.status}")
            logger.error(
                f"Termination condition: {results.solver.termination_condition}"
            )

        # Calculate and log execution time
        execution_time = time.time() - start_time
        logger.info(f"Optimization completed in {execution_time:.2f} seconds")

        return 0

    except Exception as e:
        logger.exception(f"Error in optimization process: {str(e)}")
        return 1

    finally:
        logger.info("==============================================")
        logger.info("End of optimization run")
        logger.info("==============================================")


if __name__ == "__main__":
    sys.exit(main())
