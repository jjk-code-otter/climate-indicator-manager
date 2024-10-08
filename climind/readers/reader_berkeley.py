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
import itertools
from pathlib import Path
import xarray as xa
import pandas as pd
import numpy as np
from typing import List

import climind.data_types.timeseries as ts
import climind.data_types.grid as gd

from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts


def read_monthly_1x1_grid(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> gd.GridMonthly:
    return read_monthly_grid(filename, metadata)


def read_monthly_grid(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> gd.GridMonthly:
    """
    Although Berkeley Earth is 1x1 already, the time dimension is extremely non-standard.
    In order to get consistency with the other data sets regridded to 1x1, the data is copied
    into a consistent xarray Dataset.

    Parameters
    ----------
    filename: str
        Filename of the netcdf grid
    metadata: CombinedMetadata
        CombinedMetadata object holding the dataset metadata.

    Returns
    -------
    GridMonthly
    """
    df = xa.open_dataset(filename[0])
    number_of_months = len(df.time.data)

    latitudes = np.linspace(-89.5, 89.5, 180)
    longitudes = np.linspace(-179.5, 179.5, 360)
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=number_of_months)

    target_grid = np.zeros((number_of_months, 180, 360))
    target_grid[:, :, :] = df.temperature.data[:, :, :]

    ds = gd.make_xarray(target_grid, times, latitudes, longitudes)

    # update encoding
    for key in ds.data_vars:
        ds[key].encoding.update({'zlib': True, '_FillValue': -1e30})

    metadata.creation_message()

    return gd.GridMonthly(ds, metadata)


def read_monthly_5x5_grid(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> gd.GridMonthly:
    berkeley = xa.open_dataset(filename[0])
    number_of_months = len(berkeley.time.data)
    target_grid = np.zeros((number_of_months, 36, 72))

    for m, xx, yy in itertools.product(range(number_of_months), range(72), range(36)):
        transfer = np.zeros((5, 5)) + 1.0

        lox = xx * 5
        hix = lox + 4
        loy = yy * 5
        hiy = loy + 4

        selection = berkeley.temperature.data[m, loy:hiy + 1, lox:hix + 1]
        index = (~np.isnan(selection))
        if np.count_nonzero(index) > 0:
            weighted = transfer[index] * selection[index]
            grid_mean = np.sum(weighted) / np.sum(transfer[index])
        else:
            grid_mean = np.nan
        target_grid[m, yy, xx] = grid_mean

    latitudes = np.linspace(-87.5, 87.5, 36)
    longitudes = np.linspace(-177.5, 177.5, 72)
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=number_of_months)

    ds = gd.make_xarray(target_grid, times, latitudes, longitudes)

    # update encoding
    for key in ds.data_vars:
        ds[key].encoding.update({'zlib': True, '_FillValue': -1e30})

    metadata.creation_message()
    metadata['history'].append("Regridded to 5 degree latitude-longitude resolution")

    return gd.GridMonthly(ds, metadata)


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    years = []
    months = []
    anomalies = []
    uncertainties = []

    with open(filename[0], 'r') as f:
        for _ in range(86):
            f.readline()

        for line in f:
            columns = line.split()
            if len(columns) < 2:
                break
            years.append(int(columns[0]))
            months.append(int(columns[1]))
            anomalies.append(float(columns[2]))
            uncertainties.append(float(columns[3]))

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata, uncertainty=uncertainties)


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    years = []
    anomalies = []
    uncertainties = []

    with open(filename[0], 'r') as f:
        for _ in range(58):
            f.readline()

        for line in f:
            columns = line.split()
            if len(columns) < 2:
                break
            years.append(int(columns[0]))
            anomalies.append(float(columns[1]))
            uncertainties.append(float(columns[2]))

    metadata.creation_message()

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata, uncertainty=uncertainties)
