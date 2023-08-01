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
import xarray as xa

import climind.data_types.timeseries as ts
from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    years = []
    months = []
    anomalies = []

    with open(filename[0], 'r') as f:
        for _ in range(7):
            f.readline()
        for line in f:
            columns = line.split()
            year = columns[1]
            month = columns[2]
            data = float(columns[4])

            years.append(int(year))
            months.append(int(month))
            if data == -999:
                anomalies.append(np.nan)
            else:
                anomalies.append(data / 1e6)

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_irregular_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesIrregular:

    df = xa.open_dataset(filename[0])

    years = df.time.dt.year.data.tolist()
    months = df.time.dt.month.data.tolist()
    days = df.time.dt.day.data.tolist()
    anomalies = df.sie.data.tolist()

    metadata.creation_message()

    return ts.TimeSeriesIrregular(years, months, days, anomalies, metadata=metadata)