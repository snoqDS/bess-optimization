"""Utilities for data processing and handling."""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def load_price_data(filepath, column_name="price"):
    """
    Load price data from a CSV file.

    Parameters
    ----------
    filepath : str
        Path to the CSV file.
    column_name : str, optional
        Name of the column containing price data, by default 'price'.

    Returns
    -------
    numpy.ndarray
        Array of price values.
    """
    try:
        df = pd.read_csv(filepath)
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in {filepath}.")
        return df[column_name].values
    except Exception as e:
        raise IOError(f"Error loading price data from {filepath}: {e}")


def generate_synthetic_price_data(days=1, points_per_day=24, seed=None):
    """
    Generate synthetic price data for testing.

    Parameters
    ----------
    days : int, optional
        Number of days to generate data for, by default 1.
    points_per_day : int, optional
        Number of data points per day, by default 24.
    seed : int, optional
        Random seed for reproducibility, by default None.

    Returns
    -------
    numpy.ndarray
        Array of synthetic price values.
    pandas.DataFrame
        DataFrame with timestamps and prices.
    """
    if seed is not None:
        np.random.seed(seed)

    # Total number of points
    total_points = days * points_per_day

    # Time points in hours
    hours = np.linspace(0, 24 * days - 24 / points_per_day, total_points)

    # Base daily pattern with morning and evening peaks
    day_pattern = np.zeros(total_points)
    for d in range(days):
        day_offset = d * points_per_day
        day_hours = hours[day_offset : day_offset + points_per_day] % 24

        # Morning peak around 9 AM
        morning_peak = 15 * np.exp(-0.5 * ((day_hours - 9) / 2) ** 2)

        # Evening peak around 7 PM
        evening_peak = 20 * np.exp(-0.5 * ((day_hours - 19) / 2) ** 2)

        # Combine peaks
        day_pattern[day_offset : day_offset + points_per_day] = (
            morning_peak + evening_peak
        )

    # Add weekly pattern (weekends lower than weekdays)
    weekly_factor = np.ones(total_points)
    for d in range(days):
        day_offset = d * points_per_day
        # Assume starting on Monday (day 0)
        day_of_week = d % 7

        # Weekend factor (lower prices on weekends)
        if day_of_week >= 5:  # Saturday and Sunday
            weekly_factor[day_offset : day_offset + points_per_day] = 0.8

    # Base price with noise
    base_price = 20 + day_pattern * weekly_factor
    noise = np.random.normal(0, 1.0, total_points)
    prices = base_price + noise

    # Create datetime index
    start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    timestamps = [start_time + timedelta(hours=h) for h in hours]

    # Create DataFrame
    df = pd.DataFrame({"timestamp": timestamps, "price": prices})

    return prices, df


def save_price_data(prices, filepath, timestamp_column=True):
    """
    Save price data to CSV.

    Parameters
    ----------
    prices : pandas.DataFrame or numpy.ndarray
        Price data to save. If DataFrame, must have 'timestamp' and 'price' columns.
        If array, will create timestamps.
    filepath : str
        Path to save the CSV file.
    timestamp_column : bool, optional
        Whether to include a timestamp column if prices is an array, by default True.

    Returns
    -------
    str
        Path to the saved file.
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    if isinstance(prices, np.ndarray):
        if timestamp_column:
            # Create timestamps
            start_time = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            timestamps = [start_time + timedelta(hours=i) for i in range(len(prices))]
            df = pd.DataFrame({"timestamp": timestamps, "price": prices})
        else:
            df = pd.DataFrame({"price": prices})
    else:
        df = prices

    df.to_csv(filepath, index=False)
    return filepath
