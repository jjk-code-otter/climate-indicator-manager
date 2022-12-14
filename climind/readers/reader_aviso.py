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
import pandas as pd
from typing import List

import climind.data_types.timeseries as ts

from climind.data_manager.metadata import CombinedMetadata
from climind.readers.generic_reader import read_ts


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesIrregular:
    years = []
    anomalies = []

    with open(filename[0], 'r') as f:
        f.readline()

        for line in f:
            columns = line.split()

            # This is "decimal year" which we convert in a rough and ready way
            decimal_year = float(columns[0])
            year_int = int(decimal_year)
            diny = 1 + int(365. * (decimal_year - year_int))

            years.append(f'{year_int} {diny:03d}')
            anomalies.append(float(columns[1]))

    dates = pd.to_datetime(years, format='%Y %j')
    years = dates.year.tolist()
    months = dates.month.tolist()
    days = dates.day.tolist()

    metadata.creation_message()
    outseries = ts.TimeSeriesIrregular(years, months, days, anomalies,
                                       metadata=metadata)

    return outseries
