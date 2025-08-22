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


def read_monthly_1x1_grid(filename: List[Path], metadata: CombinedMetadata) -> gd.GridMonthly:
    return read_monthly_grid(filename, metadata)


def read_monthly_grid(filename: List[Path], metadata: CombinedMetadata) -> gd.GridMonthly:
    df = xa.open_dataset(filename[0])
    return gd.GridMonthly(df, metadata)


def read_monthly_5x5_grid(filename: List[Path], metadata: CombinedMetadata) -> gd.GridMonthly:
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

    return gd.GridMonthly(ds, metadata)


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    years = []
    months = []
    anomalies = []

    with open(filename[0], 'r') as f:
        if metadata['name'] == 'Berkeley Earth Hires LSAT':
            for _ in range(51):
                f.readline()
        else:
            for _ in range(35):
                f.readline()

        for line in f:
            columns = line.split()
            year = columns[0]
            month = columns[1]

            years.append(int(year))
            months.append(int(month))
            if columns[2] != '' and int(year) >= 1850:
                anomalies.append(float(columns[2]))
            else:
                anomalies.append(np.nan)

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    monthly = read_monthly_ts(filename, metadata)
    annual = monthly.make_annual()

    return annual
