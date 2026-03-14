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
import xarray as xa
from scipy.signal import savgol_filter
import climind.data_types.timeseries as ts

from climind.data_manager.metadata import CombinedMetadata
from climind.readers.generic_reader import read_ts

from datetime import timedelta, datetime


def convert_partial_year(number):
    year = int(number)
    d = timedelta(days=(number - year) * 365)
    day_one = datetime(year, 1, 1)
    date = d + day_one
    return date


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesIrregular:
    anomalies = []
    years = []
    months = []
    days = []
    time = []

    header_length = 42
    data_column = 2
    if metadata["name"] == "NASA Sealevel new2":
        header_length = 47
        data_column = 1

    with open(filename[0], 'r') as f:
        for i in range(header_length):
            f.readline()

        for line in f:
            columns = line.split()

            time.append(float(columns[0]))

            converted_date = convert_partial_year(float(columns[0]))
            anomalies.append(float(columns[data_column]) * 10) # convert to mm from cm
            years.append(converted_date.year)
            months.append(converted_date.month)
            days.append(converted_date.day)

    time = np.array(time)
    time = time - time[0]

    anomalies = np.array(anomalies)
    anomalies = anomalies - anomalies[0]
    anomalies = savgol_filter(anomalies, 9, 1)

    #deseasonalise
    X = np.column_stack([
        np.ones_like(time),  # constant term
        np.sin(2 * np.pi * time),  # annual sine
        np.cos(2 * np.pi * time),  # annual cosine
        np.sin(4 * np.pi * time),  # semi-annual sine
        np.cos(4 * np.pi * time)  # semi-annual cosine
    ])
    # Least-squares fit
    coeffs, _, _, _ = np.linalg.lstsq(X, anomalies, rcond=None)
    # Seasonal component (exclude constant so mean is preserved)
    seasonal = X[:, 1:] @ coeffs[1:]
    # Deseasonalised series
    anomalies = anomalies - seasonal

    anomalies = anomalies.tolist()

    # Glacial isostatic adjustment of 0.3 mm per year
    anomalies = anomalies + 0.3 * time

    metadata.creation_message()
    outseries = ts.TimeSeriesIrregular(years, months, days, anomalies, metadata=metadata)

    return outseries