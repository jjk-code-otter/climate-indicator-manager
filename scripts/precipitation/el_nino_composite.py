#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2025 John Kennedy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from climind.config.config import DATA_DIR, CLIMATOLOGY
from pathlib import Path
import xarray as xa
import pandas as pd
import numpy as np
import itertools
from climind.data_types.grid import make_xarray
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


def read_monthly_25_grid(data_dir):
    # read appropriate climatology given climatology spec in config file
    file = data_dir / "normals_1951_2000_v2022_25.nc.gz"
    climatology = xa.open_dataset(file, decode_times=False)
    climatology = climatology[['precip']]
    target_climatology = np.zeros((12, 72, 144))
    target_climatology[:, :, :] = np.flip(climatology.precip.data[:, :, :], 1)

    dataset_list = []
    for year in range(1891, 2030):
        filled_filename = data_dir / f"full_data_monthly_v2022_{year}_{year + 9}_25.nc.gz"

        if filled_filename.exists():
            df = xa.open_dataset(filled_filename)
            df = df[['precip']]

            latitudes = np.linspace(-88.75, 88.75, 72)
            longitudes = np.linspace(-178.75, 178.75, 144)
            times = pd.date_range(start=f'{year}-01-01', freq='1MS', periods=120)

            target_grid = np.zeros((120, 72, 144))
            target_grid[:, :, :] = np.flip(df.precip.data[:, :, :], 1)

            for i, t in enumerate(times):
                target_grid[i, :, :] = target_grid[i, :, :] - target_climatology[t.month - 1, :, :]

            ds = make_xarray(target_grid, times, latitudes, longitudes, variable='pre')
            dataset_list.append(ds)

    combo = xa.concat(dataset_list, dim='time')

    return combo


def calculate_average_precipitation(data_dir):
    """
    Calculate average precipitation patterns for the first six months of El Niño years.

    Parameters:
        el_nino_file (str): Path to the CSV file with El Niño years.
        precipitation_file (str): Path to the NetCDF file with gridded precipitation data.

    Returns:
        xarray.DataArray: A DataArray with the average precipitation for El Niño years.
    """
    # Load El Niño years from CSV
    el_nino_years = [
        1983, 1998, 1973, 1931, 1992, 1966, 1919, 1926, 1958,
        1897, 2010, 1987, 1942, 1988, 1941, 1995, 1915, 2003,
        1903, 1900, 1906, 2007, 1978, 1980, 2024
    ]

    # Load the precipitation data
    ds = read_monthly_25_grid(data_dir)

    # Ensure time dimension is datetime
    ds['time'] = pd.to_datetime(ds['time'].values)

    # Filter data for El Niño years and first six months
    el_nino_times = ds['time'].where(ds['time.year'].isin(el_nino_years), drop=True)
    first_n_months = el_nino_times.where( (el_nino_times.dt.month >= 1)&(el_nino_times.dt.month <= 6), drop=True)

    # Select data for first six months of El Niño years
    el_nino_precip = ds.sel(time=first_n_months)

    # Calculate the average precipitation
    avg_precip = el_nino_precip.mean(dim='time')

    return avg_precip


def plot_composite_map(avg_precip):
    fig, ax = plt.subplots(figsize=(16, 9), subplot_kw={'projection': ccrs.EqualEarth()})

    ax.coastlines()

    avg_precip['pre'].plot(
        ax=ax,
        transform=ccrs.PlateCarree(),
        cmap='BrBG',
        cbar_kwargs={'label': 'Precipitation (mm)'}, vmin=-25, vmax=25
    )

    ax.set_title('Average Precipitation for El Niño Years (JFM)', fontsize=16)
    plt.show()


# Example usage
if __name__ == "__main__":
    data_dir = DATA_DIR / 'ManagedData' / 'Data' / 'GPCC_full_data'
    avg_precip = calculate_average_precipitation(data_dir)
    plot_composite_map(avg_precip)
