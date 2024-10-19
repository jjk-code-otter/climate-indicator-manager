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
import climind.data_types.timeseries as ts

from climind.data_manager.metadata import CombinedMetadata
from climind.readers.generic_reader import read_ts

from datetime import timedelta, datetime
from scipy.signal import savgol_filter


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesIrregular:
    ds = xa.open_dataset(filename[0])

    anomalies = (10 * ds.MSL_filtered_GIA_TPA_corrected_adjusted.values).tolist()
    years = ds.time.dt.year.values.tolist()
    months = ds.time.dt.month.values.tolist()
    days = ds.time.dt.day.values.tolist()

    metadata.creation_message()
    outseries = ts.TimeSeriesIrregular(years, months, days, anomalies, metadata=metadata)

    return outseries
