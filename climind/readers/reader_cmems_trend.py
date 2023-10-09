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
from typing import Tuple
import itertools
import xarray as xa
import numpy as np
import pandas as pd
import climind.data_types.grid as gd
import climind.data_types.timeseries as ts
import copy
from climind.readers.generic_reader import read_ts
from climind.data_manager.metadata import CombinedMetadata


def gread_ts(out_dir: Path, metadata: CombinedMetadata, **kwargs):
    construction_metadata = copy.deepcopy(metadata)

    if metadata['type'] == 'gridded':

        filename = out_dir

        if 'grid_resolution' in kwargs:
            if kwargs['grid_resolution'] == 5:
                return
            if kwargs['grid_resolution'] == 1:
                return
        else:
            return read_monthly_grid(filename, construction_metadata)


def read_monthly_grid(filename, metadata):
    combo = read_grid(filename)
    metadata['history'] = [f"Gridded dataset created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]
    return gd.GridMonthly(combo, metadata)


def read_grid(filename: Path):
    df = xa.open_dataset(filename[0])
    df = df.rename({'msl_trend': 'sealeveltrend'})

    latitudes = df.latitude.data
    longitudes = df.longitude.data
    times = pd.date_range(start='1993-01-01', freq='1MS', periods=1)

    grid = df.sealeveltrend.data
    grid = np.reshape(grid, (1, 720, 1440))
    ds = gd.make_xarray(grid, times, latitudes, longitudes, variable='sealeveltrend')

    return ds
