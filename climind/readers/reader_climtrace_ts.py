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

import climind.data_types.timeseries as ts
from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts

def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    years = []
    anomalies = []
    uncertainties = []

    with open(filename[0], 'r') as f:
        f.readline()
        for line in f:
            columns = line.split(',')
            year = columns[0]
            anom = columns[4]
            error = columns[6]

            years.append(int(year))
            anomalies.append(float(anom))
            uncertainties.append(float(error)*1.96)

    metadata.creation_message()

    return ts.TimeSeriesAnnual(years, anomalies, uncertainty=uncertainties, metadata=metadata)
