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
        # First line has start and end years
        line = f.readline()
        columns = line.split()
        first_year = int(columns[0])
        last_year = int(columns[1])

        # Skip over the data to get to the missing data flag
        for year in range(first_year, last_year + 1):
            f.readline()

        # Get the missing data indicator
        missing_flag_line = f.readline()
        missing_flag = float(missing_flag_line)

    # Reopen the file and read the data
    with open(filename[0], 'r') as f:
        # Skip the header
        f.readline()
        # Read all years of data
        for year in range(first_year, last_year + 1):
            line = f.readline()
            columns = line.split()
            n_columns = len(columns)
            for i in range(1, n_columns):
                value = float(columns[i])
                if value != missing_flag:
                    years.append(int(columns[0]))
                    months.append(int(i))
                    anomalies.append(value)

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    monthly = read_monthly_ts(filename, metadata)
    annual = monthly.make_annual()

    return annual
