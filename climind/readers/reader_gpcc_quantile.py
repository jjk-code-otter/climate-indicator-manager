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

import itertools
import gzip
import tempfile
import copy

from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xa

import climind.data_types.grid as gd
from climind.data_manager.metadata import CombinedMetadata
from climind.fetchers.fetcher_utils import get_n_months_back, fill_year_month
from climind.config.config import CLIMATOLOGY

def read_ts(out_dir: Path, metadata: CombinedMetadata, **kwargs):
    construction_metadata = copy.deepcopy(metadata)
    if metadata['type'] == 'timeseries':
        raise KeyError(f'That type is not known: {metadata["type"]}')

    elif metadata['type'] == 'gridded':

        filename = out_dir / metadata['filename'][0]

        if 'grid_resolution' in kwargs:
            if kwargs['grid_resolution'] == 5:
                raise KeyError(f'That space resolution is not known: {metadata["space_resolution"]}')
            if kwargs['grid_resolution'] == 1:
                return read_monthly_1x1_grid(filename, construction_metadata)
        else:
            return read_monthly_1x1_grid(filename, construction_metadata)


def read_monthly_1x1_grid(filename, metadata) -> gd.GridMonthly:

    if metadata['variable'] == "precip_quantiles_1month":
        back = 1
    elif metadata['variable'] == "precip_quantiles_3month":
        back = 3
    elif metadata['variable'] == "precip_quantiles_6month":
        back = 6
    elif metadata['variable'] == "precip_quantiles_9month":
        back = 9
    elif metadata['variable'] == "precip_quantiles_12month":
        back = 12

    new_variable_name = metadata['variable']

    dataset_list = []
    for y1, m1 in itertools.product(range(1982, 2030), range(1, 13)):
        filled_filename = str(filename).replace('YYYY', f'{y1}')
        filled_filename = filled_filename.replace('MMMM', f'{m1:02d}')
        y2, m2 = get_n_months_back(y1, m1, back=back)
        filled_filename = filled_filename.replace('*', f'{y2}{m2:02d}')
        filled_filename = Path(filled_filename)

        if filled_filename.exists():
            df = xa.open_dataset(filled_filename, decode_times=False) # the time is badly specified in some way

            variable = f'q_{y2}{m2:02d}-{y1}{m1:02d}_{CLIMATOLOGY[0]}{CLIMATOLOGY[1]}'
            if back == 1:
                variable = f'q_{y1}{m1:02d}_19512010'

            df = df[[variable]]
            df = df.rename({variable: new_variable_name})

            latitudes = np.linspace(-89.5, 89.5, 180)
            longitudes = np.linspace(-179.5, 179.5, 360)
            times = pd.date_range(start=f'{y1}-{m1:02d}-01', freq='1MS', periods=1)
            target_grid = np.zeros((1, 180, 360))
            target_grid[:, :, :] = np.flip(df[new_variable_name].data[:, :, :], 1)

            ds = gd.make_xarray(target_grid, times, latitudes, longitudes, variable=new_variable_name)

            dataset_list.append(ds)

    combo = xa.concat(dataset_list, dim='time')

    metadata['history'] = [f"Gridded dataset created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]

    return gd.GridMonthly(combo, metadata)
