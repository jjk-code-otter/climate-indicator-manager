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
import numpy as np
from scipy.signal import savgol_filter

import climind.data_types.timeseries as ts

from climind.data_manager.metadata import CombinedMetadata
from climind.readers.generic_reader import read_ts


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    df = xa.open_dataset(filename[0])

    anomalies = df.global_msl.values
    anomalies = [x * 1000 for x in anomalies]

    years = df.time.dt.year.data.tolist()
    months = df.time.dt.month.data.tolist()

    metadata.creation_message()
    outseries = ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)
    outseries.rebaseline(1993, 2015)

    return outseries


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    ts = read_monthly_ts(filename, metadata)
    ts = ts.make_annual()
    return ts
