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
import numpy as np

import climind.data_types.timeseries as ts
from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    years = []
    months = []
    anomalies = []

    with open(filename[0], 'r') as f:
        for line in f:
            columns = line.split()

            time_split = columns[0].split('.')
            year = int(time_split[0])
            month_bit = time_split[1]

            correspondence = {
                '00': 1,
                '02': 1,
                '04': 1,
                '06': 1,

                '12': 2,
                '13': 2,

                '20': 3,
                '21': 3,
                '25': 3,

                '26': 4,
                '28': 4,
                '29': 4,
                '30': 4,
                '31': 4,

                '32': 5,
                '36': 5,
                '37': 5,
                '38': 5,
                '44': 5,

                '45': 6,
                '46': 6,

                '52': 7,
                '53': 7,
                '54': 7,
                '55': 7,

                '62': 8,
                '63': 8,
                '64': 8,

                '70': 9,
                '71': 9,

                '79': 10,
                '83': 10,

                '84': 11,
                '88': 11,
                '91': 11,

                '95': 12,
                '96': 12,
                '98': 12,
            }

            if month_bit == '00':
                year -= 1
                month = 12
            else:
                month = correspondence[month_bit]

            years.append(year)
            months.append(month)

            anom = float(columns[1])
            if anom == 0.0:
                anomalies.append(None)
            else:
                anomalies.append(anom)

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)
