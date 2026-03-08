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


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    years = []
    months = []
    anomalies = []
    uncertainties = []

    with open(filename[0], 'r') as f:
        f.readline()

        for line in f:
            columns = line.split(',')
            year = columns[0][0:4]

            month = columns[0][4:6]
            month = int(month)
            if month == 0:
                month =12

            years.append(int(year))
            months.append(month)

            anomalies.append(
                float(columns[1])/1e21
            )
            uncertainties.append(
                (float(columns[3])-float(columns[2]))/(2*1e21)
            )

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata, uncertainty=uncertainties)


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    monthly = read_monthly_ts(filename, metadata)
    annual = monthly.make_annual()

    return annual
