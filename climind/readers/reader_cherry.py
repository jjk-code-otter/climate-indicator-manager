#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2023 John Kennedy
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
from datetime import date
import numpy as np

import climind.data_types.timeseries as ts
from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    years = []
    anomalies = []

    with open(filename[0], 'r', encoding="utf8") as f:
        for line in f:
            if "STNNo. A.D.     FiFD FuFD WORK TYPE Name of reference" in line:
                break

        for line in f:
            if line == '\n':
                break

            year = int(line[6:10])

            day = line[23:25]
            month = line[21:23]

            if day != "  " and month != "  ":
                flower_date = date(year, int(month), int(day))
                day_in_year = flower_date.timetuple().tm_yday

                years.append(year)
                anomalies.append(day_in_year)

    years.append(2022)
    anomalies.append(date(2022, 4, 1).timetuple().tm_yday)

    metadata.creation_message()

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata)
