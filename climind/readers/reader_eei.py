#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2026 John Kennedy
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
import itertools
import xarray as xa
import numpy as np
from typing import List

import climind.data_types.grid as gd
import climind.data_types.timeseries as ts

from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts

def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    years = []
    uncertainties = []
    anomalies = []

    with open(filename[0], 'r') as f:
        f.readline()

        for line in f:
            columns = line.split(',')

            year = int(columns[2])

            if metadata['name'] == "Miniere EEI":
                anom_column = 3
                unc_column = 4
            elif metadata['name'] == "IAP EEI":
                anom_column = 5
                unc_column = 6
            elif metadata['name'] == "Copernicus EEI":
                anom_column = 7
                unc_column = 8
            elif metadata['name'] == "CERES EEI":
                anom_column = 9
                unc_column = 10

            if columns[anom_column] != "":
                anomaly = float(columns[anom_column])
                unc = float(columns[unc_column])

                years.append(year)
                uncertainties.append(unc)
                anomalies.append(anomaly)

    metadata.creation_message()

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata, uncertainty=uncertainties)
