"""
Command-line interface utilities for the BESS optimization engine.
"""

import argparse


def parse_bess_arguments():
    """
    Parse command line arguments for the BESS optimization engine.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="BESS Optimization Engine - A tool for solving battery energy storage system optimization problems"
    )

    parser.add_argument("--config", type=str, help="Path to configuration file")

    parser.add_argument(
        "--battery-type",
        choices=["default", "small", "large"],
        default="default",
        help="Battery configuration type to use",
    )

    parser.add_argument(
        "--timesteps", type=int, default=24, help="Number of timesteps to optimize"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )

    parser.add_argument("--log-file", type=str, help="Save logs to specified file")

    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Directory to save output files",
    )

    parser.add_argument(
        "--no-plot", action="store_true", help="Disable visualization plot"
    )

    parser.add_argument(
        "--solver",
        type=str,
        default="appsi_highs",  # Or whatever solver name works on your system
        help="Name of the solver to use",
    )

    # Add more command-line arguments as needed

    return parser.parse_args()
