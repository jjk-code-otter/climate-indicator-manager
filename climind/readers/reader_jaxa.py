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
    ts = read_irregular_ts(filenames, metadata)
    ts = ts.make_monthly()
    ts.df.drop(ts.df.tail(1).index, inplace=True) # Clip the last month because it is always incomplete except for one day
    _, end_date = ts.get_start_and_end_dates()
    ts.metadata.dataset['last_month'] = str(end_date)
    return ts


def read_irregular_ts(filenames: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesIrregular:
    years = []
    months = []
    days = []
    extents = []

    with open(filenames[0], 'r') as f:
        for line in f:
            columns = line.split()

            year = int(columns[2])
            month = int(columns[0])
            day = int(columns[1])
            data = float(columns[3])

            if data != -9999:
                years.append(year)
                months.append(month)
                days.append(day)
                extents.append(data/1e6)

    metadata.creation_message()

    return ts.TimeSeriesIrregular(years, months, days, extents, metadata=metadata)