#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2023 John Kennedy
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

from pathlib import Path
from typing import List
import xarray as xa
import numpy as np
import pandas as pd

import climind.data_types.timeseries as ts
import climind.data_types.grid as gd

from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts

def read_monthly_grid(filename: List[Path], metadata: CombinedMetadata) -> gd.GridMonthly:
    df = xa.open_dataset(filename[0])

    number_of_months = df.temperature_anomaly.data.shape[0]
    latitudes = np.linspace(-87.5, 87.5, 36)
    longitudes = np.linspace(-177.5, 177.5, 72)
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=number_of_months)

    target_grid = np.zeros((number_of_months, 36, 72))
    target_grid[:, :, :] = df.temperature_anomaly.data[:, :, :]

    df = gd.make_xarray(target_grid, times, latitudes, longitudes)

    metadata['history'] = [f"Gridded dataset created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]
    return gd.GridMonthly(df, metadata)


def read_monthly_5x5_grid(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> gd.GridMonthly:
    return read_monthly_grid(filename, metadata)

def read_monthly_1x1_grid(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> gd.GridMonthly:
    df = xa.open_dataset(filename[0])

    number_of_months = df.temperature_anomaly.data.shape[0]
    latitudes = np.linspace(-87.5, 87.5, 36)
    longitudes = np.linspace(-177.5, 177.5, 72)
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=number_of_months)

    target_grid = np.zeros((number_of_months, 36, 72))
    target_grid[:, :, :] = df.temperature_anomaly.data[:, :, :]

    df = gd.make_xarray(target_grid, times, latitudes, longitudes)

    # regrid to 1x1
    lats = np.arange(-89.5, 90.5, 1.0)
    lons = np.arange(-179.5, 180.5, 1.0)

    # Copy 5-degree grid cell value into all one degree cells
    grid = np.repeat(df.tas_mean, 5, 1)
    grid = np.repeat(grid, 5, 2)

    df = gd.make_xarray(grid, df.time.data, lats, lons)

    metadata.creation_message()
    metadata['history'].append("Regridded to 1 degree latitude-longitude resolution")

    return gd.GridMonthly(df, metadata)

def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    years = []
    months = []
    anomalies = []

    with open(filename[0], 'r') as f:
        f.readline()
        for line in f:
            columns = line.split()
            year = columns[0]
            month = columns[1:13]

            for i, m in enumerate(month):
                years.append(int(year))
                months.append(int(i+1))
                anomalies.append(float(m))

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    monthly = read_monthly_ts(filename, metadata)
    annual = monthly.make_annual()

    return annual