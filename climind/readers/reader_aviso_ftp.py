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
import xarray as xa
import climind.data_types.timeseries as ts
import copy

from climind.data_manager.metadata import CombinedMetadata
from climind.readers.generic_reader import read_ts


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata):
    df = xa.open_dataset(filename[0])

    correction = xa.open_dataset(filename[0].parent / 'Topex-A_correction.nc')
    msl_correction = correction.tpa_correction.values.tolist()

    anomalies = df.msl.values.tolist()

    for i in range(len(msl_correction)):
        anomalies[i] = (anomalies[i] - msl_correction[i])

    for i in range(len(anomalies)):
        anomalies[i] = anomalies[i] * 1000.

    years = df.time.dt.year.data.tolist()
    months = df.time.dt.month.data.tolist()
    days = df.time.dt.day.data.tolist()

    metadata.creation_message()
    outseries = ts.TimeSeriesIrregular(years, months, days, anomalies,
                                       metadata=metadata)

    return outseries
