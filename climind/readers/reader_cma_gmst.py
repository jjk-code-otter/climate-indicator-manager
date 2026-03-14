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
import itertools
import xarray as xa
import pandas as pd
import numpy as np

import climind.data_types.timeseries as ts
import climind.data_types.grid as gd


from climind.data_manager.metadata import CombinedMetadata
from climind.readers.generic_reader import get_last_modified_time
from climind.readers.generic_reader import read_ts

def read_monthly_grid(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> gd.GridMonthly:

    filenames = []
    for year, month in itertools.product(range(1850, 2050), range(1, 13)):
        fname = str(filename[0])
        fname = fname.replace("YYYY", f"{year}")
        fname = fname.replace("MMMM", f"{month:02d}")
        fname = Path(fname)
        if fname.exists():
            filenames.append(fname)

    n_time = len(filenames)
    n_lat = 89
    n_lon = 180

    data_array = np.zeros((n_time, n_lat, n_lon))

    for i, fname in enumerate(filenames):
        ds = xa.open_dataset(fname, engine='netcdf4')
        data_array[i, :, :] = ds.anomaly.values[:, :]

    data_array = np.flip(data_array, axis=1)

    latitudes = np.linspace(-88, 88, 89)
    longitudes = np.linspace(-179, 179, 180)
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=n_time)

    ds = gd.make_xarray(data_array, times, latitudes, longitudes)

    metadata.dataset['last_modified'] = [get_last_modified_time(filenames[-1])]
    metadata.creation_message()
    return gd.GridMonthly(ds, metadata)

def read_monthly_5x5_grid(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> gd.GridMonthly:
    ds = read_monthly_grid(filename, metadata, **kwargs)
    g2 = ds.df.tas_mean.values
    nt = g2.shape[0]

    target_grid = np.zeros((nt, 36, 72))

    for t in range(nt):

        enlarged_array = np.zeros((91, 180)) + np.nan
        enlarged_array[1:90, :] = g2[t, :, :]

        for xx, yy in itertools.product(range(72), range(36)):
            transfer = np.zeros((3,3,))+1.0

            if np.mod(xx, 2) == 0:
                transfer[:, 2] = transfer[:, 2] * 0.5
            else:
                transfer[:, 0] = transfer[:, 0] * 0.5

            if np.mod(yy, 2) == 0:
                transfer[0, :] = transfer[0, :] * 0.5
            else:
                transfer[2, :] = transfer[2, :] * 0.5

            lox = int(np.floor(xx * 2.5))
            hix = int(np.floor((xx + 1) * 2.5) - np.mod(xx, 2))

            loy = int(np.floor(yy * 2.5) + np.mod(yy, 2))
            hiy = int(np.floor((yy + 1) * 2.5))

            selection = enlarged_array[loy:hiy + 1, lox:hix + 1]

            nonmissing = ~np.isnan(selection)

            weighted = np.sum(transfer[nonmissing] * selection[nonmissing]) / np.sum(transfer[nonmissing])

            target_grid[t, yy, xx] = weighted

    latitudes = np.linspace(-87.5, 87.5, 36)
    longitudes = np.linspace(-177.5, 177.5, 72)
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=nt)

    ds = gd.make_xarray(target_grid, times, latitudes, longitudes)

    return gd.GridMonthly(ds, metadata)

def read_monthly_1x1_grid(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> gd.GridMonthly:

    ds = read_monthly_grid(filename, metadata, **kwargs)
    g2 = ds.df.tas_mean.values
    nt = g2.shape[0]

    target_grid = np.zeros((nt, 180, 360)) + np.nan
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=nt)

    lats = np.arange(-89.5, 90.5, 1.0)
    lons = np.arange(-179.5, 180.5, 1.0)

    # Copy 5-degree grid cell value into all one degree cells
    grid = np.repeat(g2, 2, 1)
    grid = np.repeat(grid, 2, 2)

    target_grid[:, 1:179, :] = grid[:, :, :]

    df = gd.make_xarray(target_grid, times, lats, lons)

    return gd.GridMonthly(df, metadata)


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    years = []
    months = []
    anomalies = []

    with open(filename[0], 'r') as f:
        f.readline()
        for line in f:
            columns = line.rstrip().split(',')
            year = int(columns[0])
            for month in range(1,13):
                years.append(year)
                months.append(int(month))
                anomalies.append(float(columns[month]))

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)

def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    ts = read_monthly_ts(filename, metadata)
    ts = ts.make_annual()
    return ts