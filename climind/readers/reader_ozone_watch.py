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
import xarray as xa
import numpy as np

import climind.data_types.timeseries as ts
import climind.data_types.grid as gd

from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts

def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    years = []
    anomalies = []

    with open(filename[0], 'r') as f:
        # burn first ten lines
        header_length = 10
        if metadata['variable'] in ['ozone_hole', 'ozone_minimum']:
            header_length = 9

        for i in range(header_length):
            f.readline()

        for line in f:
            columns = line.split()
            year = columns[0]

            if metadata['variable'] == 'max_ozone_hole':
                anomaly = columns[2]
            elif metadata['variable'] == 'min_ozone_minimum':
                anomaly = columns[4]
            elif metadata['variable'] == 'ozone_minimum':
                anomaly = columns[2]
            elif metadata['variable'] == 'ozone_hole':
                anomaly = columns[1]

            years.append(int(year))
            anomalies.append(float(anomaly))

    metadata.creation_message()

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata)
