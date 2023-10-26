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
import climind.data_types.grid as gd
import climind.data_types.timeseries as ts
import copy
from climind.readers.generic_reader import get_last_modified_time
from climind.data_manager.metadata import CombinedMetadata


def read_ts(out_dir: Path, metadata: CombinedMetadata, **kwargs):
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
    dataset_list = []
    for year, month in itertools.product(range(1993, 2030), range(1, 13)):
        filled_filename = filename / f"dt_global_twosat_phy_l4_{year}{month:02d}_vDT2021-M01.nc"
        if filled_filename.exists():
            dataset_list.append(xa.open_dataset(filled_filename))
    combo = xa.concat(dataset_list, dim='time')
    combo['sla'] = combo['sla'] * 1000.0

    times = combo.time.data
    latitudes = combo.latitude.data
    longitudes = combo.longitude.data
    target_grid = combo.sla.data

    combo = gd.make_xarray(target_grid, times, latitudes, longitudes, variable='sealevel')

    return combo
