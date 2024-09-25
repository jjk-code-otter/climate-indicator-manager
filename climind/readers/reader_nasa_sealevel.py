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
import climind.data_types.timeseries as ts

from climind.data_manager.metadata import CombinedMetadata
from climind.readers.generic_reader import read_ts

from datetime import timedelta, datetime


def convert_partial_year(number):
    year = int(number)
    d = timedelta(days=(number - year) * 365)
    day_one = datetime(year, 1, 1)
    date = d + day_one
    return date


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesIrregular:
    anomalies = []
    years = []
    months = []
    days = []

    with open(filename[0], 'r') as f:
        for i in range(52):
            f.readline()

        for line in f:
            columns = line.split()

            converted_date = convert_partial_year(float(columns[2]))
            anomalies.append(float(columns[11]) + 37.64)
            years.append(converted_date.year)
            months.append(converted_date.month)
            days.append(converted_date.day)

    metadata.creation_message()
    outseries = ts.TimeSeriesIrregular(years, months, days, anomalies, metadata=metadata)

    return outseries
