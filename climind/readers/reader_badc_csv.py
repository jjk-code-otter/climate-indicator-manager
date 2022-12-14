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

import climind.data_types.timeseries as ts
from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    years = []
    months = []
    anomalies = []
    prehistory = []

    with open(filename[0], 'r') as f:
        while True:
            line = f.readline()
            if line.startswith('history'):
                prehistory.append(line[10:-1])
            if "time,year,month,data" in line:
                break

        for line in f:
            if 'end data' not in line:
                columns = line.split(',')
                years.append(int(columns[1]))
                months.append(int(columns[2]))
                anomalies.append(float(columns[3]))
            else:
                break

    metadata['history'] = prehistory
    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    years = []
    anomalies = []
    prehistory = []

    with open(filename[0], 'r') as f:
        while True:
            line = f.readline()
            if line.startswith('history'):
                prehistory.append(line[10:-1])
            if "time,year,data" in line:
                break

        for line in f:
            if 'end data' not in line:
                columns = line.split(',')
                years.append(int(columns[1]))
                anomalies.append(float(columns[2]))
            else:
                break

    metadata['history'] = prehistory
    metadata.creation_message()

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata)
