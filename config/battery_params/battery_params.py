"""Battery parameters configuration."""

# Default battery parameters
DEFAULT_BATTERY_PARAMS = {
    "capacity": 100,  # 100 kWh
    "power_max": 25,  # 25 kW
    "efficiency_charge": 0.95,
    "efficiency_discharge": 0.95,
    "initial_soc": 50,  # 50 kWh (half full)
    "delta_t": 1.0,  # 1-hour timesteps
    "soc_min": 0.2,  # Minimum SoC (20% of capacity)
    "soc_max": 0.8,  # Maximum SoC (80% of capacity)
    "ramp_limit": 10,  # Maximum power change per timestep (kW/timestep)
}

# Different battery configurations
SMALL_BATTERY = {
    "capacity": 50,  # 50 kWh
    "power_max": 10,  # 10 kW
    "efficiency_charge": 0.95,
    "efficiency_discharge": 0.95,
    "initial_soc": 25,  # 25 kWh
    "delta_t": 1.0,  # 1-hour timesteps
    "soc_min": 0.2,  # Minimum SoC (20% of capacity)
    "soc_max": 0.8,  # Maximum SoC (80% of capacity)
    "ramp_limit": 5,  # Maximum power change per timestep (kW/timestep)
}

LARGE_BATTERY = {
    "capacity": 500,  # 500 kWh
    "power_max": 100,  # 100 kW
    "efficiency_charge": 0.95,
    "efficiency_discharge": 0.95,
    "initial_soc": 250,  # 250 kWh
    "delta_t": 1.0,  # 1-hour timesteps
    "soc_min": 0.2,  # Minimum SoC (20% of capacity)
    "soc_max": 0.8,  # Maximum SoC (80% of capacity)
    "ramp_limit": 40,  # Maximum power change per timestep (kW/timestep)
}


# Function to get battery parameters
def get_battery_params(battery_type="default"):
    """
    Get battery parameters based on the specified battery type.

    Parameters
    ----------
    battery_type : str, optional
        Type of battery configuration to use, by default 'default'.
        Options: 'default', 'small', 'large'.

    Returns
    -------
    dict
        Dictionary of battery parameters.
    """
    if battery_type.lower() == "default":
        return DEFAULT_BATTERY_PARAMS.copy()
    elif battery_type.lower() == "small":
        return SMALL_BATTERY.copy()
    elif battery_type.lower() == "large":
        return LARGE_BATTERY.copy()
    else:
        raise ValueError(f"Unknown battery type: {battery_type}")
