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


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> ts.TimeSeriesAnnual:

    years = []
    anomalies = []
    uncertainties = []

    with open(filename[0], 'r') as f:
        f.readline()
        for line in f:
            columns = line.split(',')

            year = columns[1]
            data = float(columns[6])
            unc=  float(columns[7])

            years.append(int(float(year)))
            anomalies.append(data)
            uncertainties.append(unc)

    metadata.creation_message()

    anomalies = np.array(anomalies)
    anomalies = np.cumsum(anomalies)
    anomalies = anomalies.tolist()

    uncertainties = np.array(uncertainties)
    uncertainties = uncertainties * uncertainties
    uncertainties = np.cumsum(uncertainties)
    uncertainties = np.sqrt(uncertainties)
    uncertainties = uncertainties.tolist()

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata, uncertainty=uncertainties)
