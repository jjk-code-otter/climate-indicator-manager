#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2026 John Kennedy
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
import pandas as pd
import numpy as np

import climind.data_types.timeseries as ts
import climind.data_types.grid as gd

from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts

def read_monthly_grid(filename: List[Path], metadata: CombinedMetadata) -> gd.GridMonthly:
    df = xa.open_dataset(filename[0])
    if metadata['variable'] == 'tas':
        df = df[['ts_mean']]
        df = df.rename_vars({'ts_mean': 'tas_mean'})
    elif metadata['variable'] == 'sst':
        df = df[['sst']]
    elif metadata['variable'] == 'lsat':
        df = df[['lsat']]

    vals = df.tas_mean.values
    vals = np.roll(vals, 36, axis=2)

    latitudes = np.linspace(-87.5, 87.5, 36)
    longitudes = np.linspace(-177.5, 177.5, 72)
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=vals.shape[0])

    ds = gd.make_xarray(vals, times, latitudes, longitudes)

    metadata['history'] = [f"Gridded dataset created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]
    return gd.GridMonthly(ds, metadata)


def read_monthly_5x5_grid(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> gd.GridMonthly:
    return read_monthly_grid(filename, metadata)


def read_monthly_1x1_grid(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> gd.GridMonthly:
    df = xa.open_dataset(filename[0])
    # regrid to 1x1
    lats = np.arange(-89.5, 90.5, 1.0)
    lons = np.arange(-179.5, 180.5, 1.0)

    # Roll grid to get meridian in right place. Copy 5-degree grid cell value into all one degree cells
    grid = np.roll(df.ts_mean.values, 36, axis=2)
    grid = np.repeat(grid, 5, 1)
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
        for i in range(8):
            f.readline()
        for line in f:
            columns = line.split(',')
            year = columns[0]
            for month in range(1,13):
                anom = float(columns[month])

                years.append(int(year))
                months.append(int(month))
                anomalies.append(anom)

            if year == '2025':
                break

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)

def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    years = []
    anomalies = []
    uncs = []

    with open(filename[0], 'r') as f:
        for i in range(8):
            f.readline()
        for line in f:
            columns = line.split(',')
            year = columns[0]
            anom = float(columns[1])
            unc = float(columns[2]) * 1.96

            years.append(int(year))
            anomalies.append(anom)
            uncs.append(unc)

            if year == '2025':
                break

    metadata.creation_message()

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata, uncertainty=uncs)
