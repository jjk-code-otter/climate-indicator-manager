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

import numpy as np
import climind.plotters.plot_utils as pu

ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


def anomaly_and_rank(all_datasets, year):

    min_rank, max_rank = pu.calculate_ranks(all_datasets, year)
    mean_anomaly, min_anomaly, max_anomaly = pu.calculate_values(all_datasets, year)

    ds = all_datasets[0]
    units = ds.metadata['units']

    out_text = f'The year {year} was ranked between {ordinal(min_rank)} and {ordinal(max_rank)} highest ' \
               f'on record. The mean value for {year} was ' \
               f'{mean_anomaly:.2f}{units} ' \
               f'({min_anomaly:.2f}-{max_anomaly:.2f}{units} depending on the data set used). ' \
               f'{len(all_datasets)} data sets were used in this assessment.'

    return out_text


def max_monthly_value(all_datasets, year):
    all_ranks = []
    all_ranks_months = []
    for ds in all_datasets:
        min_rank = 9999
        min_rank_month = 99
        for month in range(1, 13):
            rank = ds.get_rank_from_year_and_month(year, month, versus_all_months=True)
            if rank is not None and rank < min_rank:
                min_rank = rank
                min_rank_month = month
        if min_rank != 9999:
            all_ranks.append(min_rank)
            all_ranks_months(min_rank_month)

    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    out_text = f'The monthly value for {month_names[min_rank_month - 1]} in {year} was the ' \
               f'{ordinal(min_rank)} highest on record.'

    return out_text


def arctic_ice_blurb(all_datasets, year):
    out_text = 'Ice was near the long-term trend line or something'

    return out_text


def glacier_blurb(all_datasets, year):
    out_text = 'This was the nth consecutive year of negative mass balance since'

    return out_text
