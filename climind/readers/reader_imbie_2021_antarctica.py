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
import numpy as np
from typing import List

import climind.data_types.timeseries as ts

from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> ts.TimeSeriesMonthly:
    if 'first_difference' in kwargs:
        first_diff = kwargs['first_difference']
    else:
        first_diff = False

    with open(filename[0], 'r') as in_file:

        in_file.readline()

        years = []
        months = []
        mass_balance = []
        uncertainty = []

        for line in in_file:
            columns = line.split(',')

            decimal_year = float(columns[0])
            year_int = int(decimal_year)
            month = int(np.rint(12. * (decimal_year - year_int) + 1.0))

            if not first_diff:
                data = float(columns[3])
                unc = float(columns[4])
            else:
                data = float(columns[1])
                unc = float(columns[2])

            years.append(year_int)
            months.append(month)
            mass_balance.append(data)
            uncertainty.append(unc)

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, mass_balance, metadata=metadata, uncertainty=uncertainty)


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> ts.TimeSeriesAnnual:
    monthly = read_monthly_ts(filename, metadata, **kwargs)
    annual = monthly.make_annual(cumulative=True)
    return annual
