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
import copy

import climind.data_types.timeseries as ts
import climind.data_types.grid as gd
from climind.readers.generic_reader_utils import find_latest, get_latest_filename_and_url
from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import get_last_modified_time

def read_ts(out_dir: Path, metadata: CombinedMetadata, **kwargs):
    filename_with_wildcards = metadata['filename'][0]
    filename = [find_latest(out_dir, filename_with_wildcards)]

    last_modified = get_last_modified_time(filename[0])

    construction_metadata = copy.deepcopy(metadata)
    construction_metadata.dataset['last_modified'] = [last_modified]

    if metadata['type'] == 'timeseries':
        if metadata['time_resolution'] == 'monthly':
            return read_monthly_ts(filename, construction_metadata)
        elif metadata['time_resolution'] == 'annual':
            return read_annual_ts(filename, construction_metadata)
        else:
            raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')
    elif metadata['type'] == 'gridded':
        if 'grid_resolution' in kwargs:
            if kwargs['grid_resolution'] == 1:
                return read_monthly_1x1_grid(filename, construction_metadata)
            if kwargs['grid_resolution'] == 5:
                return read_monthly_grid(filename, construction_metadata)
        else:
            return read_monthly_grid(filename, construction_metadata)



def read_monthly_grid(filename: List[Path], metadata: CombinedMetadata) -> gd.GridMonthly:
    df = xa.open_dataset(filename[0])
    df = df.rename({'tas': 'tas_mean'})
    #df.tas_mean.data = np.roll(df.tas_mean.data, 36, 2)
    metadata['history'] = [f"Gridded dataset created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]
    return gd.GridMonthly(df, metadata)


def read_monthly_5x5_grid(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> gd.GridMonthly:
    return read_monthly_grid(filename, metadata)


def read_monthly_1x1_grid(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> gd.GridMonthly:
    df = xa.open_dataset(filename[0])
    df = df.rename({'tas': 'tas_mean'})
    df.tas_mean.data = np.roll(df.tas_mean.data, 36, 2)
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
    df = xa.open_dataset(filename[0])

    ntimes = df.tas.data.shape[0]

    years = df.time.dt.year.data.tolist()
    months = df.time.dt.month.data.tolist()
    anomalies = np.reshape(df.tas.data, (ntimes)).tolist()

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    return read_monthly_ts(filename, metadata).make_annual()
