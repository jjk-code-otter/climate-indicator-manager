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
import pandas as pd
from typing import List

import climind.data_types.timeseries as ts

from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata, **kwargs):
    lines_to_skip = 31

    if 'first_difference' in kwargs:
        first_diff = kwargs['first_difference']
    else:
        first_diff = False

    dates = []
    years = []
    months = []
    uncertainties = []
    data = []

    with open(filename[0], 'r') as in_file:
        for _ in range(lines_to_skip):
            in_file.readline()

        for line in in_file:
            columns = line.split()
            decimal_year = float(columns[0])
            year_int = int(decimal_year)
            diny = 1 + int(365. * (decimal_year - year_int))
            month = int(np.rint(12. * (decimal_year - year_int) + 1.0))

            dates.append(f'{year_int} {diny:03d}')

            years.append(year_int)
            months.append(month)
            data.append(float(columns[1]))
            uncertainties.append(float(columns[2]))

    dates = pd.to_datetime(dates, format='%Y %j')
    years2 = dates.year.tolist()
    months2 = dates.month.tolist()

    dico = {'year': years, 'month': months, 'data': data}
    df = pd.DataFrame(dico)

    if first_diff:
        df['data'] = df.diff()['data']
        data = df['data'].values.tolist()

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years2, months2, data, metadata=metadata, uncertainty=uncertainties)


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata, **kwargs):
    monthly = read_monthly_ts(filename, metadata, **kwargs)
    annual = monthly.make_annual_by_selecting_month(8)
    return annual
