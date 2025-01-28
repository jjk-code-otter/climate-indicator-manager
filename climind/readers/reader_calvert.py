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
import xarray as xa
import numpy as np

import climind.data_types.timeseries as ts
import climind.data_types.grid as gd

from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    years = []
    months = []
    anomalies = []
    uncertainties = []

    with open(filename[0], 'r') as f:
        # burn header lines
        for i in range(9):
            f.readline()

        for line in f:
            columns = line.split()
            year = columns[0]
            month = columns[1]
            anomaly = columns[2]
            uncertainty = (float(columns[4])-float(columns[3]))/2.0

            years.append(int(year))
            months.append(int(month))
            anomalies.append(float(anomaly))
            uncertainties.append(uncertainty)

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, uncertainty=uncertainties, metadata=metadata)


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    years = []
    anomalies = []
    uncertainties = []

    with open(filename[0], 'r') as f:
        # burn header lines
        for i in range(9):
            f.readline()

        for line in f:
            columns = line.split()
            year = columns[0]
            anomaly = columns[1]
            uncertainty = (float(columns[3])-float(columns[2]))/2.0

            years.append(int(year))
            anomalies.append(float(anomaly))
            uncertainties.append(uncertainty)

    metadata.creation_message()

    return ts.TimeSeriesAnnual(years, anomalies, uncertainty=uncertainties, metadata=metadata)
