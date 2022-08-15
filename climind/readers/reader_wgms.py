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
import climind.data_types.timeseries as ts
import numpy as np
import copy
from climind.data_manager.metadata import CombinedMetadata


def read_ts(out_dir: Path, metadata: CombinedMetadata, **kwargs):
    filename = out_dir / metadata['filename'][0]

    construction_metadata = copy.deepcopy(metadata)

    if metadata['time_resolution'] == 'monthly':
        raise NotImplementedError
    elif metadata['time_resolution'] == 'annual':
        return read_annual_ts(filename, construction_metadata, **kwargs)
    else:
        raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')


def read_annual_ts(filename: str, metadata: CombinedMetadata, **kwargs):

    if 'first_difference' in kwargs:
        first_diff = kwargs['first_difference']
    else:
        first_diff = False

    years = []
    anomalies = []

    with open(filename, 'r') as f:
        for i in range(1):
            f.readline()
        for line in f:
            columns = line.split(',')
            year = columns[0]

            if first_diff:
                data = float(columns[2])/1000.
            else:
                data = float(columns[3])/1000.

            years.append(int(year))
            anomalies.append(data)

    metadata['history'] = [f"Time series created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata)
