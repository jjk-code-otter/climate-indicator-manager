import numpy as np
import xarray as xa
import matplotlib.pyplot as plt

from climind.config.config import DATA_DIR


def main():
    projdir = DATA_DIR / "ManagedData"
    filename = projdir / "Data" / "GISTEMP" / "gistemp1200_GHCNv4_ERSSTv5.nc.gz"
    lat_min = 30
    lat_max = 70
    month = 7

    month_names = [
        "January", "February", "March",
        "April", "May", "June",
        "July", "August", "September",
        "October", "November", "December"
    ]

    if lat_min >= lat_max:
        raise ValueError("--lat-min must be smaller than --lat-max")

    # Open file and select the anomaly variable.
    ds = xa.open_dataset(filename)
    temp = ds["tempanomaly"]

    lat_name = "lat"
    lon_name = "lon"

    # Select June 1976 and June 2026
    june_1976 = temp.where((temp.time.dt.year == 1976) & (temp.time.dt.month == month), drop=True).squeeze()
    june_2026 = temp.where((temp.time.dt.year == 2026) & (temp.time.dt.month == month), drop=True).squeeze()

    lat_values = ds[lat_name].values

    # rearrange the latitudes if needed
    if lat_values[0] < lat_values[-1]:
        lat_slice = slice(lat_min, lat_max)
    else:
        lat_slice = slice(lat_max, lat_min)

    temp_by_long_1976 = june_1976.sel({lat_name: lat_slice}).mean(dim=lat_name, skipna=True)
    temp_by_long_2026 = june_2026.sel({lat_name: lat_slice}).mean(dim=lat_name, skipna=True)

    # Convert to numpy arrays for plotting.
    longitude = temp_by_long_1976[lon_name].values
    anomaly_1976 = temp_by_long_1976.values
    anomaly_2026 = temp_by_long_2026.values

    axis_fontsize = 14
    title_fontsize = 22

    fig, ax = plt.subplots(figsize=(16, 9))

    # Remove top and right axes
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Plot lines
    ax.plot(longitude, anomaly_1976, color="tab:blue", linewidth=5)
    ax.plot(longitude, anomaly_2026, color="tab:red", linewidth=5)

    # Direct labels
    ax.annotate(
        f"{month_names[month-1]} 1976",
        xy=(longitude[-1], anomaly_1976[-1]),
        xytext=(8, 0),
        textcoords="offset points",
        color="tab:blue",
        va="center",
        fontweight="bold",
        fontsize=axis_fontsize,
    )

    ax.annotate(
        f"{month_names[month-1]} 2026",
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
    ax.set_xlabel("Longitude (°E)", fontsize=axis_fontsize)
    ax.set_ylabel("Temperature anomaly (°C)", fontsize=axis_fontsize)

    # Larger tick numbers
    ax.tick_params(axis="both", labelsize=axis_fontsize)

    # Left-justified, larger title
    ax.set_title(
        f"GISTEMP {month_names[month-1]} Temperature Anomalies 1976 vs 2026\n"
        f"Latitude average: {lat_min}°N to {lat_max}°N",
        loc="left",
        fontsize=title_fontsize,
        fontweight="bold",
    )

    # No grid
    ax.grid(False)

    plt.tight_layout()
    plt.savefig(projdir / "Figures" / f"longitudes_{month_names[month-1]}.png", dpi=200, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
