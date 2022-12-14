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


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> ts.TimeSeriesMonthly:
    if 'first_difference' in kwargs:
        first_diff = kwargs['first_difference']
    else:
        first_diff = False

    df = pd.read_excel(filename[0])
    df = df.rename(columns={'Cumulative ice mass change (Gt)': 'data',
                            'Cumulative ice mass change uncertainty (Gt)': 'uncertainty'})

    # Clip out missing data, which constitute quite a lof the of series
    df = df[~np.isnan(df['data'])]

    df['data'] = df.diff()['data']

    decimal_year = df['Year'].values
    year_int = decimal_year.astype(int)
    months = np.rint(12. * (decimal_year - year_int) + 1.0).astype(int)

    years = year_int.tolist()
    months = months.tolist()

    if not first_diff:
        df['data'] = df.cumsum()['data']

    mass_balance = df['data'].tolist()
    uncertainty = df['uncertainty'].tolist()

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, mass_balance, metadata=metadata, uncertainty=uncertainty)


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> ts.TimeSeriesAnnual:
    monthly = read_monthly_ts(filename, metadata, **kwargs)
    annual = monthly.make_annual(cumulative=True)
    return annual
