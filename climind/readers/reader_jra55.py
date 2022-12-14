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
from typing import List
import xarray as xa
import pandas as pd
import numpy as np

import climind.data_types.timeseries as ts
import climind.data_types.grid as gd
from climind.readers.generic_reader import get_last_modified_time
from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts


def read_grid(filename: List[Path]):
    dataset_list = []
    returned_filename = None
    for year in range(1958, 2020):

        filled_filename = str(filename[0]).replace('YYYY', f'{year}')
        filled_filename = Path(filled_filename)

        if filled_filename.exists():
            field = xa.open_dataset(filled_filename, engine='cfgrib')
            field = field.rename({'t2m': 'tas_mean'})
            dataset_list.append(field)
            returned_filename = filled_filename

    for year, month in itertools.product(range(2020, 2050), range(1, 13)):

        filled_filename = str(filename[1]).replace('YYYY', f'{year}')
        filled_filename = Path(filled_filename.replace('MMMM', f'{month:02d}'))

        if filled_filename.exists():
            field = xa.open_dataset(filled_filename, engine='cfgrib')
            field = field.expand_dims('time')
            field = field.rename({'t2m': 'tas_mean'})
            dataset_list.append(field)
            returned_filename = filled_filename

    combo = xa.concat(dataset_list, dim='time')
    return combo, returned_filename


def read_monthly_grid(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> gd.GridMonthly:
    ds, filled_filename = read_grid(filename)
    metadata.dataset['last_modified'] = [get_last_modified_time(filled_filename)]
    metadata.creation_message()
    return gd.GridMonthly(ds, metadata)


def read_monthly_5x5_grid(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> gd.GridMonthly:
    ds, filled_filename = read_grid(filename)
    metadata.dataset['last_modified'] = [get_last_modified_time(filled_filename)]

    jra55_125 = ds.tas_mean
    number_of_months = jra55_125.shape[0]

    target_grid = np.zeros((number_of_months, 36, 72))

    transfer = np.zeros((5, 5)) + 1.0
    transfer[0, :] = transfer[0, :] * 0.5
    transfer[4, :] = transfer[4, :] * 0.5
    transfer[:, 0] = transfer[:, 0] * 0.5
    transfer[:, 4] = transfer[:, 4] * 0.5

    transfer_sum = np.sum(transfer)

    for month in range(number_of_months):

        enlarged_array = np.zeros((145, 289))
        enlarged_array[:, 0:288] = jra55_125[month, :, :]
        enlarged_array[:, 288] = jra55_125[month, :, 0]

        for xx, yy in itertools.product(range(72), range(36)):
            lox = xx * 4
            hix = (xx + 1) * 4
            loy = yy * 4
            hiy = (yy + 1) * 4

            weighted = transfer * enlarged_array[loy:hiy + 1, lox:hix + 1]
            grid_mean = np.sum(weighted) / transfer_sum
            target_grid[month, yy, xx] = grid_mean

    # flip and shift target_grid to match HadCRUT-like coords lat -90 to 90 and lon -180 to 180
    target_grid = np.flip(target_grid, 1)
    target_grid = np.roll(target_grid, 36, 2)

    latitudes = np.linspace(-87.5, 87.5, 36)
    longitudes = np.linspace(-177.5, 177.5, 72)
    times = pd.date_range(start=f'{1958}-{1:02d}-01', freq='1MS', periods=number_of_months)

    ds = gd.make_xarray(target_grid, times, latitudes, longitudes)

    # update encoding
    for key in ds.data_vars:
        ds[key].encoding.update({'zlib': True, '_FillValue': -1e30})

    metadata.creation_message()
    metadata['history'].append("Regridded to 5 degree latitude-longitude resolution")

    return gd.GridMonthly(ds, metadata)


def read_monthly_1x1_grid(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> gd.GridMonthly:
    ds, filled_filename = read_grid(filename)
    metadata.dataset['last_modified'] = [get_last_modified_time(filled_filename)]

    jra55_125 = ds.tas_mean
    number_of_months = jra55_125.shape[0]

    target_grid = np.zeros((number_of_months, 180, 360))

    for month in range(number_of_months):
        enlarged_array = np.zeros((145, 289))
        enlarged_array[:, 0:288] = jra55_125[month, :, :]
        enlarged_array[:, 288] = jra55_125[month, :, 0]

        regridded = gd.simple_regrid(enlarged_array, -180. - 1.25 / 2., -90. - 1.25 / 2., 1.25, 1.0)

        target_grid[month, :, :] = regridded[:, :]

    # flip and shift target_grid to match HadCRUT-like coords lat -90 to 90 and lon -180 to 180
    target_grid = np.flip(target_grid, 1)
    target_grid = np.roll(target_grid, 180, 2)

    latitudes = np.linspace(-89.5, 89.5, 180)
    longitudes = np.linspace(-179.5, 179.5, 360)
    times = pd.date_range(start=f'{1958}-{1:02d}-01', freq='1MS', periods=number_of_months)

    ds = gd.make_xarray(target_grid, times, latitudes, longitudes)

    # update encoding
    for key in ds.data_vars:
        ds[key].encoding.update({'zlib': True, '_FillValue': -1e30})

    metadata.creation_message()
    metadata['history'].append("Regridded to 1 degree latitude-longitude resolution")

    return gd.GridMonthly(ds, metadata)


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    years = []
    months = []
    anomalies = []

    with open(filename[0], 'r') as f:
        for line in f:
            columns = line.split()
            year = columns[0][0:4]
            month = columns[0][5:7]

            years.append(int(year))
            months.append(int(month))
            anomalies.append(float(columns[1]))

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    monthly = read_monthly_ts(filename, metadata)
    annual = monthly.make_annual()

    return annual
