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
from typing import List
import numpy as np

import climind.data_types.timeseries as ts
from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts


def read_monthly_ts(filenames: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    years = []
    months = []
    anomalies = []
    time = []

    for filename in filenames:
        with open(filename, 'r') as f:
            f.readline()
            for line in f:
                columns = line.split(',')
                year = columns[0]
                month = columns[1]
                data = float(columns[4])

                years.append(int(year))
                months.append(int(month))
                time.append(float(year) + (float(month) - 1) / 12.)

                if data == -9999:
                    anomalies.append(np.nan)
                else:
                    anomalies.append(data)

    # Sort based on time axis
    anomalies = [x for _, x in sorted(zip(time, anomalies))]
    years = [x for _, x in sorted(zip(time, years))]
    months = [x for _, x in sorted(zip(time, months))]

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_irregular_ts(filenames: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    years = []
    months = []
    days = []
    extents = []

    with open(filenames[0], 'r') as f:
        f.readline()
        f.readline()

        for line in f:
            columns = line.split(',')
            years.append(int(columns[0]))
            months.append(int(columns[1]))
            days.append(int(columns[2]))
            extents.append(float(columns[3]))

    metadata.creation_message()

    return ts.TimeSeriesIrregular(years, months, days, extents, metadata=metadata)