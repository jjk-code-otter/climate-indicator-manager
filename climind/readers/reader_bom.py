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
import xarray as xa
import numpy as np

from datetime import datetime, timedelta

import climind.data_types.timeseries as ts

from climind.data_manager.metadata import CombinedMetadata
from climind.readers.generic_reader import read_ts


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesIrregular:

    years = []
    months = []
    days = []
    anomalies = []

    with (open(filename[0], 'r') as f):
        for line in f:
            columns = line.split(',')

            year1 = int(columns[0][0:4])
            month1 = int(columns[0][4:6])
            day1 = int(columns[0][6:])

            year2 = int(columns[1][0:4])
            month2 = int(columns[1][4:6])
            day2 = int(columns[1][6:])

            dt = datetime(year2, month2, day2) - datetime(year1, month1, day1)
            midpoint = datetime(year1, month1, day1) + dt/2.

            anom = float(columns[2])

            if metadata['variable'] == 'soi':
                anom = anom / 10.

            years.append(midpoint.year)
            months.append(midpoint.month)
            days.append(midpoint.day)
            anomalies.append(anom)

    metadata.creation_message()
    outseries = ts.TimeSeriesIrregular(years, months, days, anomalies, metadata=metadata).make_monthly()

    return outseries


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    ts = read_monthly_ts(filename, metadata)
    ts = ts.make_monthly()
    ts = ts.make_annual()
    return ts
