"""
Script to download or generate price data for the BESS optimization.
"""

import argparse
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import project modules
from src.opt_engine.utils.data_utils import (
    generate_synthetic_price_data,
    save_price_data,
)


def main():
    parser = argparse.ArgumentParser(
        description="Download or generate price data for BESS optimization"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="synthetic",
        choices=["synthetic", "download"],
        help="Mode of data acquisition: synthetic or download",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to generate data for (synthetic mode only)",
    )
    parser.add_argument(
        "--points_per_day",
        type=int,
        default=24,
        help="Number of data points per day (synthetic mode only)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/price_data.csv",
        help="Output filepath for the price data",
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for synthetic data generation"
    )
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    if args.mode == "synthetic":
        print(
            f"Generating synthetic price data for {args.days} days with {args.points_per_day} points per day..."
        )
        prices, df = generate_synthetic_price_data(
            days=args.days, points_per_day=args.points_per_day, seed=args.seed
        )
        filepath = save_price_data(df, args.output)
        print(f"Synthetic price data saved to: {filepath}")
    else:
        # Note: You would implement real data download here, e.g., from an API
        print("Real data download not implemented yet. Using synthetic data instead.")
        prices, df = generate_synthetic_price_data(
            days=args.days, points_per_day=args.points_per_day, seed=args.seed
        )
        filepath = save_price_data(df, args.output)
        print(f"Synthetic price data saved to: {filepath}")

    # Print summary statistics
    print("\nPrice data summary:")
    print(f"  Number of data points: {len(df)}")
    print(f"  Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"  Price range: ${df['price'].min():.2f} to ${df['price'].max():.2f}")
    print(f"  Average price: ${df['price'].mean():.2f}")


if __name__ == "__main__":
    main()
