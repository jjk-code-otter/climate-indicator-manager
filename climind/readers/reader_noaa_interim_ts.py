#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2022 John Kennedy
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
from itertools import product

import numpy as np
import pandas as pd

import climind.data_types.grid as gd
import climind.data_types.timeseries as ts
from climind.data_manager.metadata import CombinedMetadata
import copy

from climind.readers.generic_reader import read_ts


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    years = []
    anomalies = []

    with open(filename[0], 'r') as f:
        f.readline()
        f.readline()
        for line in f:
            columns = line.split()
            if len(columns) != 4:
                break
            year = columns[0]
            years.append(int(year))
            anomalies.append(float(columns[1]))

    metadata.creation_message()

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata)


def read_one_month(filehandle):
    year_month = filehandle.readline()
    columns = year_month.split()
    year = int(columns[1])
    month = int(columns[0])

    outarray = np.zeros((1, 36, 72))

    for i in range(36):
        line = filehandle.readline().rstrip()
        columns = line.split()
        columns = np.array([float(x) for x in columns])
        outarray[0, i, :] = columns[:]

    return year, month, outarray


def read_monthly_grid(filename: List[Path], metadata: CombinedMetadata) -> gd.GridMonthly:
    years = []
    months = []
    number_of_months = (2020 - 1850 + 1) * 12
    data_array = np.zeros((number_of_months, 36, 72))
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=number_of_months)

    count = 0
    with open(filename[0], 'r') as f:
        for y, m in product(range(1850, 2021), range(1, 13)):
            year, month, month_array = read_one_month(f)
            data_array[count, :, :] = month_array[0, :, :]
            count += 1
            if y != year or m != month:
                print(f"mismatch {y} {year} or {m} {month}")

    latitudes = np.linspace(-87.5, 87.5, 36)
    longitudes = np.linspace(-177.5, 177.5, 72)

    data_array = np.roll(data_array, 36, 2)

    ds = gd.make_xarray(data_array, times, latitudes, longitudes)

    # update encoding
    for key in ds.data_vars:
        ds[key].encoding.update({'zlib': True, '_FillValue': -1e30})

    metadata.creation_message()

    return gd.GridMonthly(ds, metadata)


def read_monthly_5x5_grid(filename: List[Path], metadata: CombinedMetadata, **kwargs):
    return read_monthly_grid(filename, metadata)


def read_monthly_1x1_grid(filename: Path, metadata: CombinedMetadata, **kwargs) -> gd.GridMonthly:
    df = read_monthly_grid(filename, metadata)
    df = df.df
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
