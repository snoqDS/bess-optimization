"""Visualization utilities for battery dispatch results."""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta


def plot_dispatch_results(results_df, battery_params, show=True, save_path=None):
    """
    Create visualizations of battery dispatch results.

    Parameters
    ----------
    results_df : pandas.DataFrame
        DataFrame containing results with columns:
        - Time: Timestep index
        - Price: Electricity price
        - Power_Out: Battery discharge power
        - Power_In: Battery charge power
        - Net_Power: Net power (Power_Out - Power_In)
        - State_of_Charge: Battery state of charge
        - Ramp_Rate: Power ramp rate between timesteps
    battery_params : dict
        Dictionary of battery parameters.
    show : bool, optional
        Whether to display the plot, by default True.
    save_path : str, optional
        Path to save the figure, by default None.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The created figure.
    """
    # Create a datetime index for better x-axis formatting
    start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    time_index = [start_time + timedelta(hours=t - 1) for t in results_df["Time"]]
    results_df = results_df.copy()
    results_df["Datetime"] = time_index

    # Create figure with four subplots sharing x-axis
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(
        4, 1, figsize=(12, 14), sharex=True, gridspec_kw={"height_ratios": [2, 2, 1, 1]}
    )

    # Set up colors
    price_color = "tab:red"
    soc_color = "tab:blue"
    soc_pct_color = "tab:purple"
    charge_color = "tab:green"
    discharge_color = "tab:orange"
    net_power_color = "tab:cyan"
    ramp_color = "tab:brown"

    # Plot 1: State of Charge (kWh)
    ax1.plot(
        results_df["Datetime"],
        results_df["State_of_Charge"],
        color=soc_color,
        linewidth=2,
        label="SoC (kWh)",
    )
    ax1.set_ylabel("State of Charge (kWh)", color=soc_color, fontsize=12)
    ax1.tick_params(axis="y", labelcolor=soc_color)
    ax1.set_ylim(0, battery_params["capacity"] * 1.05)
    ax1.set_title("Battery Dispatch Optimization Results", fontsize=14)
    ax1.grid(True, alpha=0.3)

    # Create a twin axis for SoC percentage
    ax1_twin = ax1.twinx()

    # Calculate SoC percentage
    soc_percentage = results_df["State_of_Charge"] / battery_params["capacity"] * 100

    # Plot SoC percentage
    ax1_twin.plot(
        results_df["Datetime"],
        soc_percentage,
        color=soc_pct_color,
        linewidth=2,
        linestyle="--",
        label="SoC (%)",
    )
    ax1_twin.set_ylabel("State of Charge (%)", color=soc_pct_color, fontsize=12)
    ax1_twin.tick_params(axis="y", labelcolor=soc_pct_color)
    ax1_twin.set_ylim(0, 105)

    # Add SoC constraints if available
    if "soc_min" in battery_params and "soc_max" in battery_params:
        min_soc_pct = battery_params["soc_min"] * 100
        max_soc_pct = battery_params["soc_max"] * 100
        ax1_twin.axhspan(0, min_soc_pct, alpha=0.2, color="red")
        ax1_twin.axhspan(max_soc_pct, 100, alpha=0.2, color="red")
        ax1_twin.axhline(
            y=min_soc_pct, color="red", linestyle="--", alpha=0.7, linewidth=1
        )
        ax1_twin.axhline(
            y=max_soc_pct, color="red", linestyle="--", alpha=0.7, linewidth=1
        )

    # Combine legends from both y-axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

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

    # Plot Net Power as a line on the same axis
    ax2_twin = ax2.twinx()
    ax2_twin.plot(
        results_df["Datetime"],
        results_df["Net_Power"],
        color=net_power_color,
        linewidth=2,
        label="Net Power",
    )
    ax2_twin.set_ylabel("Net Power (kW)", color=net_power_color, fontsize=12)
    ax2_twin.tick_params(axis="y", labelcolor=net_power_color)

    # Set y-axis limits for net power
    power_max = battery_params["power_max"]
    ax2_twin.set_ylim(-power_max * 1.1, power_max * 1.1)

    # Add zero line for net power
    ax2_twin.axhline(y=0, color="black", linestyle="-", alpha=0.3)

    ax2.set_ylabel("Power (kW)", fontsize=12)
    ax2.set_ylim(0, power_max * 1.1)

    # Combine legends
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    ax2.grid(True, alpha=0.3)

    # Plot 3: Electricity Prices
    ax3.plot(
        results_df["Datetime"], results_df["Price"], color=price_color, linewidth=2
    )
    ax3.set_ylabel("Price ($/kWh)", color=price_color, fontsize=12)
    ax3.tick_params(axis="y", labelcolor=price_color)
    ax3.grid(True, alpha=0.3)

    # Plot 4: Ramp Rates
    ax4.bar(
        results_df["Datetime"],
        results_df["Ramp_Rate"],
        color=ramp_color,
        alpha=0.7,
        width=0.02,
    )
    ax4.set_ylabel("Ramp Rate (kW/timestep)", color=ramp_color, fontsize=12)
    ax4.tick_params(axis="y", labelcolor=ramp_color)
    ax4.set_xlabel("Time", fontsize=12)
    ax4.grid(True, alpha=0.3)

    # Add ramp limit lines if available
    if "ramp_limit" in battery_params:
        ramp_limit = battery_params["ramp_limit"]
        ax4.axhline(
            y=ramp_limit, color="red", linestyle="--", alpha=0.7, label="Ramp Limit"
        )
        ax4.axhline(y=-ramp_limit, color="red", linestyle="--", alpha=0.7)
        ax4.legend(loc="upper right")

    # Calculate max ramp rate for y-axis limit
    max_ramp = max(
        abs(results_df["Ramp_Rate"].max()), abs(results_df["Ramp_Rate"].min())
    )
    if "ramp_limit" in battery_params:
        max_ramp = max(max_ramp, battery_params["ramp_limit"])

    # Set symmetric y-axis limits for ramp rates
    ax4.set_ylim(-max_ramp * 1.1, max_ramp * 1.1)

    # Add zero line for ramp rates
    ax4.axhline(y=0, color="black", linestyle="-", alpha=0.3)

    # Format x-axis
    for ax in [ax1, ax2, ax3, ax4]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))

    # Add profit information
    if "profit" in results_df.attrs:
        profit = results_df.attrs["profit"]
        plt.figtext(0.01, 0.01, f"Total profit: ${profit:.2f}", fontsize=12, ha="left")

    plt.tight_layout()

    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    # Show if requested
    if show:
        plt.show()

    return fig


def plot_ramp_rate_analysis(results_df, battery_params, show=True, save_path=None):
    """
    Create visualizations focusing on ramp rate analysis.

    Parameters
    ----------
    results_df : pandas.DataFrame
        DataFrame containing results with columns including Ramp_Rate
    battery_params : dict
        Dictionary of battery parameters.
    show : bool, optional
        Whether to display the plot, by default True.
    save_path : str, optional
        Path to save the figure, by default None.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The created figure.
    """
    ramp_limit = battery_params.get("ramp_limit", float("inf"))

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: Ramp rate distribution histogram
    ax1.hist(results_df["Ramp_Rate"], bins=20, color="tab:blue", alpha=0.7)
    ax1.set_xlabel("Ramp Rate (kW/timestep)", fontsize=12)
    ax1.set_ylabel("Frequency", fontsize=12)
    ax1.set_title("Distribution of Ramp Rates", fontsize=14)

    # Add ramp limit lines if available
    if ramp_limit < float("inf"):
        ax1.axvline(
            x=ramp_limit, color="red", linestyle="--", alpha=0.7, label="Ramp Limit"
        )
        ax1.axvline(x=-ramp_limit, color="red", linestyle="--", alpha=0.7)
        ax1.legend()

    ax1.grid(True, alpha=0.3)

    # Plot 2: Ramp rate vs. Price Differential scatter plot
    # Calculate price differential between adjacent timesteps
    price_diff = [0]  # First timestep has no differential
    for i in range(1, len(results_df)):
        price_diff.append(results_df["Price"].iloc[i] - results_df["Price"].iloc[i - 1])

    # Create a new column for price differential
    results_df_copy = results_df.copy()
    results_df_copy["Price_Diff"] = price_diff

    # Skip the first point (which has ramp rate of 0)
    scatter = ax2.scatter(
        results_df_copy["Price_Diff"][1:],
        results_df_copy["Ramp_Rate"][1:],
        c=results_df_copy["Price"][1:],
        cmap="viridis",
        alpha=0.7,
        s=50,
    )

    # Add colorbar for price
    cbar = plt.colorbar(scatter, ax=ax2)
    cbar.set_label("Price ($/kWh)", fontsize=12)

    # Add ramp limit lines if available
    if ramp_limit < float("inf"):
        ax2.axhline(
            y=ramp_limit, color="red", linestyle="--", alpha=0.7, label="Ramp Limit"
        )
        ax2.axhline(y=-ramp_limit, color="red", linestyle="--", alpha=0.7)
        ax2.legend()

    ax2.set_xlabel("Price Differential ($/kWh)", fontsize=12)
    ax2.set_ylabel("Ramp Rate (kW/timestep)", fontsize=12)
    ax2.set_title("Ramp Rate vs. Price Differential", fontsize=14)
    ax2.grid(True, alpha=0.3)

    # Add zero lines
    ax2.axhline(y=0, color="black", linestyle="-", alpha=0.3)
    ax2.axvline(x=0, color="black", linestyle="-", alpha=0.3)

    plt.tight_layout()

    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    # Show if requested
    if show:
        plt.show()

    return fig
