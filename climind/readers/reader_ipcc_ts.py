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
from climind.data_manager.metadata import CombinedMetadata
import copy


def read_ts(out_dir: Path, metadata: CombinedMetadata):
    filename = metadata['filename'][0]
    filename = out_dir / filename

    construction_metadata = copy.deepcopy(metadata)

    if metadata['time_resolution'] == 'monthly':
        raise NotImplementedError('No official monthly version')
    elif metadata['time_resolution'] == 'annual':
        return read_annual_ts(filename, construction_metadata)
    else:
        raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')


def read_annual_ts(filename: str, metadata: CombinedMetadata):
    years = []
    anomalies = []
    """
    HadCRUT, NOAA, Berkeley, Kadow,, 
    HadCRUT confidence limit lower, HadCRUT confidence limit upper
    """
    name = metadata['name']
    if name == 'Kadow IPCC':
        col = 4
    elif name == 'Berkeley IPCC':
        col = 3
    elif name == 'NOAA Interim IPCC':
        col = 2
    else:
        raise KeyError(f"Oh honey, what you doin'  here? {name}")

    with open(filename, 'r') as f:
        f.readline()
        for line in f:
            columns = line.split(',')
            if columns[0] == '':
                break
            year = columns[0]
            years.append(int(year))
            anomalies.append(float(columns[col]))

    metadata['history'] = [f"Time series created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata)
