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
import pandas as pd

import climind.data_types.timeseries as ts
from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> ts.TimeSeriesMonthly:
    if 'first_difference' in kwargs:
        first_diff = kwargs['first_difference']
    else:
        first_diff = False

    dates = []
    mass_balance = []

    with open(filename[0], 'r') as in_file:
        in_file.readline()
        for line in in_file:
            if int(line[0:4]) > 1985:
                columns = line.split(',')
                dates.append(columns[0])
                mass_balance.append(float(columns[1]))

    parsed_dates = pd.to_datetime(dates, format='%Y-%m-%d')
    years = parsed_dates.year.tolist()
    months = parsed_dates.month.tolist()

    dico = {'year': years, 'month': months, 'data': mass_balance}

    df = pd.DataFrame(dico)
    mdf_year = df.groupby(['year', 'month'])['year'].mean()
    mdf_month = df.groupby(['year', 'month'])['month'].mean()
    mdf_data = df.groupby(['year', 'month'])['data'].sum()

    mdf_year = mdf_year.astype(int)
    mdf_month = mdf_month.astype(int)

    if not first_diff:
        mdf_data = mdf_data.cumsum()

    years = mdf_year.values.tolist()
    months = mdf_month.values.tolist()
    mass_balance = mdf_data.values.tolist()

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, mass_balance, metadata=metadata)


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> ts.TimeSeriesAnnual:
    if 'first_difference' in kwargs:
        first_diff = kwargs['first_difference']
    else:
        first_diff = False

    years = []
    mass_balance = []

    with open(filename[0], 'r') as in_file:
        in_file.readline()
        for line in in_file:
            columns = line.split(',')
            years.append(int(columns[0]))
            mass_balance.append(float(columns[1]))

    if not first_diff:
        dico = {'year': years, 'data': mass_balance}
        df = pd.DataFrame(dico)
        mdf_year = df['year'].astype(int)
        mdf_data = df['data'].cumsum()
        years = mdf_year.values.tolist()
        mass_balance = mdf_data.values.tolist()

    metadata.creation_message()

    return ts.TimeSeriesAnnual(years, mass_balance, metadata=metadata)
