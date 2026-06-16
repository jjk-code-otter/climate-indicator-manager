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
import climind.data_types.timeseries as ts
from climind.data_manager.metadata import CombinedMetadata
from climind.readers.generic_reader import read_ts


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    """
    The PSL monthly format has three main sections. The first line has the start and end years, then there is a
    data section with each row being a year and 13 columns year and 12 months of data. Finally, there's a metadata
    section at the end. The first line of the metadata gives the missing data indicator.

    Parameters
    ----------
    filename: List[Path]
        List of paths for the filenames
    metadata: CombinedMetadata
        Metadata object

    Returns
    -------
    ts.TimeSeriesMonthly
        Monthly time series read from the file
    """
    years = []
    months = []
    anomalies = []

    with open(filename[0], 'r') as f:
        f.readline()

        for line in f:
            for i in range(12):
                columns = line.split()
                anom = float(columns[i+1])
                if anom != 99.9:
                    years.append(int(columns[0]))
                    months.append(int(i+1))
                    anomalies.append(anom)

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    monthly = read_monthly_ts(filename, metadata)
    annual = monthly.make_annual()

    return annual
