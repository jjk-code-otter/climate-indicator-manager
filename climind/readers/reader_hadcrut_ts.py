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
import xarray as xa
import climind.data_types.timeseries as ts
import climind.data_types.grid as gd
import numpy as np
import copy
from climind.readers.generic_reader import read_ts
from climind.data_manager.metadata import CombinedMetadata


# def read_ts(out_dir: Path, metadata: CombinedMetadata, **kwargs):
#     filename = out_dir / metadata['filename'][0]
#
#     construction_metadata = copy.deepcopy(metadata)
#
#     if metadata['type'] == 'timeseries':
#         if metadata['time_resolution'] == 'monthly':
#             return read_monthly_ts(filename, construction_metadata)
#         elif metadata['time_resolution'] == 'annual':
#             return read_annual_ts(filename, construction_metadata)
#         else:
#             raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')
#
#     elif metadata['type'] == 'gridded':
#         print(kwargs)
#         if 'grid_resolution' in kwargs:
#             if kwargs['grid_resolution'] == 5:
#                 return read_monthly_grid(filename, construction_metadata)
#             if kwargs['grid_resolution'] == 1:
#                 return read_monthly_1x1_grid(filename, construction_metadata)
#         else:
#             return read_monthly_grid(filename, construction_metadata)


def read_monthly_grid(filename: str, metadata: CombinedMetadata):
    df = xa.open_dataset(filename)
    metadata['history'] = [f"Gridded dataset created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]
    return gd.GridMonthly(df, metadata)


def read_monthly_5x5_grid(filename: str, metadata: CombinedMetadata):
    return read_monthly_grid(filename, CombinedMetadata)


def read_monthly_1x1_grid(filename: str, metadata: CombinedMetadata):
    df = xa.open_dataset(filename)
    # regrid to 1x1
    lats = np.arange(-89.5, 90.5, 1.0)
    lons = np.arange(-179.5, 180.5, 1.0)

    # Copy 5-degree grid cell value into all one degree cells
    grid = np.repeat(df.tas_mean, 5, 1)
    grid = np.repeat(grid, 5, 2)

    df = gd.make_xarray(grid, df.time.data, lats, lons)

    metadata['history'] = [f"Gridded dataset created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]
    metadata['history'].append("Regridded to 1 degree latitude-longitude resolution")

    return gd.GridMonthly(df, metadata)


def read_monthly_ts(filename: str, metadata: CombinedMetadata):
    years = []
    months = []
    anomalies = []

    with open(filename, 'r') as f:
        f.readline()
        for line in f:
            columns = line.split(',')
            year = columns[0][0:4]
            month = columns[0][5:7]

            years.append(int(year))
            months.append(int(month))
            if columns[1] != '':
                anomalies.append(float(columns[1]))
            else:
                anomalies.append(np.nan)

    metadata['history'] = [f"Time series created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: str, metadata: CombinedMetadata):
    monthly = read_monthly_ts(filename, metadata)
    annual = monthly.make_annual()

    return annual
