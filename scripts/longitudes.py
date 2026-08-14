#!/usr/bin/env python3

import argparse
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from climind.config.config import DATA_DIR


def find_coord(ds, candidates):
    """Find a coordinate using a list of possible names."""
    for name in candidates:
        if name in ds.coords:
            return name
    raise KeyError(f"Could not find any of these coordinates: {candidates}")


def main():
    projdir = DATA_DIR  / "ManagedData"
    filename = projdir / "Data" / "GISTEMP" / "gistemp1200_GHCNv4_ERSSTv5.nc.gz"
    lat_min = 30
    lat_max = 70

    if lat_min >= lat_max:
        raise ValueError("--lat-min must be smaller than --lat-max")

    # Read GISTEMP
    ds = xr.open_dataset(filename)

    lat_name = "lat"
    lon_name = "lon"

    # Select the anomaly variable.
    temp = ds["tempanomaly"]

    # Select June 1976 and June 2026
    june_1976 = temp.where((temp.time.dt.year == 1976) & (temp.time.dt.month == 6), drop=True).squeeze()
    june_2026 = temp.where((temp.time.dt.year == 2026) & (temp.time.dt.month == 6), drop=True).squeeze()

    lat_values = ds[lat_name].values

    if lat_values[0] < lat_values[-1]:
        lat_slice = slice(lat_min, lat_max)
    else:
        lat_slice = slice(lat_max, lat_min)

    profile_1976 = (
        june_1976
        .sel({lat_name: lat_slice})
        .mean(dim=lat_name, skipna=True)
    )

    profile_2026 = (
        june_2026
        .sel({lat_name: lat_slice})
        .mean(dim=lat_name, skipna=True)
    )

    # Convert to numpy arrays for plotting.
    longitude = profile_1976[lon_name].values
    anomaly_1976 = profile_1976.values
    anomaly_2026 = profile_2026.values

    axis_fontsize = 14
    title_fontsize = 18

    fig, ax = plt.subplots(figsize=(11, 6))

    # Remove top and right axes
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Plot lines
    ax.plot(longitude, anomaly_1976, color="tab:blue", linewidth=5)
    ax.plot(longitude, anomaly_2026, color="tab:red", linewidth=5)

    # Direct labels
    ax.annotate(
        "June 1976",
        xy=(longitude[-1], anomaly_1976[-1]),
        xytext=(8, 0),
        textcoords="offset points",
        color="tab:blue",
        va="center",
        fontweight="bold",
        fontsize=axis_fontsize,
    )

    ax.annotate(
        "June 2026",
        xy=(longitude[-1], anomaly_2026[-1]),
        xytext=(8, 0),
        textcoords="offset points",
        color="tab:red",
        va="center",
        fontweight="bold",
        fontsize=axis_fontsize,
    )

    # Zero line
    ax.axhline(0, color="black", linewidth=0.8, alpha=0.4)

    # Axis labels
    ax.set_xlabel("Longitude (°)", fontsize=axis_fontsize)
    ax.set_ylabel("Temperature anomaly (°C)", fontsize=axis_fontsize)

    # Larger tick numbers
    ax.tick_params(axis="both", labelsize=axis_fontsize)

    # Left-justified, larger title
    ax.set_title(
        f"GISTEMP June Temperature Anomalies 1976 vs 2026\n"
        f"Latitude average: {lat_min}°N to {lat_max}°N",
        loc="left",
        fontsize=title_fontsize,
        fontweight="bold",
    )

    # No grid
    ax.grid(False)

    plt.tight_layout()
    plt.savefig(projdir / "Figures" / "longitudes.png", dpi=200, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
