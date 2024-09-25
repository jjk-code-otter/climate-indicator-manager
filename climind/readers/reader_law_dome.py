#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2024 John Kennedy
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
import numpy as np

import climind.data_types.timeseries as ts
from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts

def read_chunk(f, search_string):

    years = []
    values = []

    for line in f:
        if line == '			\n' or line == '\n':
            break
        columns = line.split()
        if len(columns) < 3:
            break
        years.append(int(np.floor(float(columns[1]))))

        value_column = 2
        if search_string == 'CH4':
            value_column = 3
        values.append(float(columns[value_column]))

    return years, values


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    years = []
    anomalies = []

    if metadata['variable'] == 'ch4':
        search_string = 'CH4'
    elif metadata['variable'] == 'n2o':
        search_string = 'N2O'
    elif metadata['variable'] == 'co2':
        search_string = 'CO2'
    else:
        raise ValueError

    with open(filename[0], 'r') as f:
        for line in f:
            if search_string in line:
                break

        years, values = read_chunk(f, search_string)

    metadata.creation_message()

    return ts.TimeSeriesAnnual(years, values, metadata=metadata)
