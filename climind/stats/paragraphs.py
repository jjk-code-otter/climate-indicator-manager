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

import climind.plotters.plot_utils as pu
from typing import Union, List
from climind.data_types.timeseries import TimeSeriesMonthly, TimeSeriesAnnual

ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


def rank_ranges(low, high):
    if low == high:
        return f"the {ordinal(low)}"
    elif low < high:
        return f"between the {ordinal(low)} and {ordinal(high)}"
    else:
        return f"between the {ordinal(high)} and {ordinal(low)}"


def dataset_name_list(all_datasets):
    names = []
    for ds in all_datasets:
        names.append(ds.metadata['display_name'])

    if len(names) == 1:
        name_list = f"{names[0]}"
    elif len(names) == 2:
        name_list = f"{names[0]} and {names[1]}"
    else:
        name_list = f"{', '.join(names[0:-1])}, and {names[-1]}"

    return name_list


def fancy_html_units(units):
    equivalence = {
        "degC": "&deg;C",
        "millionkm2": "million km<sup>2</sup>",
        "ph": "pH",
        "mwe": "m w.e."
    }

    if units in equivalence:
        fancy = equivalence[units]
    else:
        fancy = units

    return fancy


def anomaly_and_rank(all_datasets, year):
    min_rank, max_rank = pu.calculate_ranks(all_datasets, year)
    mean_anomaly, min_anomaly, max_anomaly = pu.calculate_values(all_datasets, year)

    ds = all_datasets[0]
    units = fancy_html_units(ds.metadata['units'])

    out_text = f'The year {year} was ranked {rank_ranges(min_rank, max_rank)} highest ' \
               f'on record. The mean value for {year} was ' \
               f'{mean_anomaly:.2f}{units} ' \
               f'({min_anomaly:.2f}-{max_anomaly:.2f}{units} depending on the data set used). ' \
               f'{len(all_datasets)} data sets were used in this assessment: {dataset_name_list(all_datasets)}.'

    return out_text


def max_monthly_value(all_datasets, year):
    all_ranks = []
    all_ranks_months = []
    all_values = []
    for ds in all_datasets:
        min_rank = 9999
        min_rank_month = 99
        min_value = -99
        for month in range(1, 13):
            rank = ds.get_rank_from_year_and_month(year, month, versus_all_months=True)
            if rank is not None and rank < min_rank:
                min_rank = rank
                min_rank_month = month
                min_value = ds.get_value(year, month)
        if min_rank != 9999:
            all_ranks.append(min_rank)
            all_ranks_months.append(min_rank_month)
            all_values.append(min_value)

    units = fancy_html_units(ds.metadata['units'])

    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    out_text = f'The monthly value for {month_names[all_ranks_months[0] - 1]} {year} was the ' \
               f'{ordinal(all_ranks[0])} highest on record at {all_values[0]:.1f}{units}.'

    return out_text


def arctic_ice_paragraph(all_datasets, year):
    march = []
    september = []
    for ds in all_datasets:
        march.append(ds.make_annual_by_selecting_month(3))
        september.append(ds.make_annual_by_selecting_month(9))

    units = fancy_html_units(ds.metadata['units'])

    min_march_rank, max_march_rank = pu.calculate_ranks(march, year, ascending=True)
    mean_march_value, min_march_value, max_march_value = pu.calculate_values(march, year)

    min_september_rank, max_september_rank = pu.calculate_ranks(september, year, ascending=True)
    mean_september_value, min_september_value, max_september_value = pu.calculate_values(september, year)

    out_text = f'Arctic sea ice extent in March {year} was between {min_march_value:.2f} and ' \
               f'{max_march_value:.2f}{units}. ' \
               f'This was {rank_ranges(min_march_rank, max_march_rank)} lowest extent on record. ' \
               f'In September the extent was between {min_september_value:.2f} and ' \
               f'{max_september_value:.2f}{units}. ' \
               f'This was {rank_ranges(min_september_rank, max_september_rank)} lowest extent on record. ' \
               f'Data sets used were: {dataset_name_list(all_datasets)}'

    return out_text


def glacier_paragraph(all_datasets: List[Union[TimeSeriesMonthly, TimeSeriesAnnual]], year: int) -> str:
    """
    Write the glacier paragraph
    Parameters
    ----------
    all_datasets: list[Union[TimeSeriesMonthly, TimeSeriesAnnual]]
        list of data sets to be processed
    year: int
        Year for which to do the evaluation

    Returns
    -------

    """
    counter = 0
    last_positive = 1900
    for ds in all_datasets:
        first_year = ds.df['year'][0]
        for check_year in range(first_year + 1, year + 1):
            value1 = ds.get_value_from_year(check_year - 1)
            value2 = ds.get_value_from_year(check_year)
            diff = value2 - value1
            if diff >= 0.0:
                counter = 0
                last_positive = check_year
            else:
                counter += 1

    units = fancy_html_units(ds.metadata['units'])

    out_text = f'This was the {ordinal(counter)} consecutive year of negative mass balance since {last_positive + 1}.' \
               f' Cumulative glacier loss since 1976 is {ds.get_value_from_year(year):.1f}{units}.'

    return out_text
