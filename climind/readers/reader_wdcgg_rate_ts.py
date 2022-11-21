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
import numpy as np
import copy

from typing import List

import climind.data_types.timeseries as ts
from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata):
    years = []
    months = []
    anomalies = []

    with open(filename[0], 'r') as f:
        f.readline()
        for line in f:
            columns = line.split(',')
            year = columns[0]
            month = columns[1]
            years.append(int(year))
            months.append(int(month))
            if columns[4] != '' and columns[4] != 'NaN':
                anomalies.append(float(columns[4]))
            else:
                anomalies.append(np.nan)

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata):
    years = []
    anomalies = []
    uncertainty = []

    with open(filename[0], 'r') as f:
        f.readline()
        for line in f:
            columns = line.split(',')
            year = columns[0]
            years.append(int(year))
            if columns[1] != '':
                anomalies.append(float(columns[1]))
                uncertainty.append(float(columns[2]))
            else:
                anomalies.append(np.nan)
                uncertainty.append(np.nan)

    increments = [np.nan]
    for i in range(1, len(anomalies)):
        increments.append(anomalies[i]-anomalies[i-1])

    metadata.creation_message()

    return ts.TimeSeriesAnnual(years, increments, metadata=metadata)