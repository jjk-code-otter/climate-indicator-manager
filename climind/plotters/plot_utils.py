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

from typing import Tuple, Union, List
import numpy as np
from numpy import ndarray

import climind.stats.paragraphs as pg
from climind.data_types.timeseries import TimeSeriesMonthly, TimeSeriesAnnual
from climind.data_types.grid import GridAnnual


def calculate_trends(all_datasets: List[TimeSeriesAnnual], trend_start_year: int, trend_end_year: int) -> Tuple[
    float, float, float]:
    """
    given a set of data sets, return the mean, min and max trends from the data sets calculated
    using OLS between the chosen years.

    Parameters
    ----------
    all_datasets : List[TimeSeriesAnnual]
        list of :class:`.TimeSeriesAnnual` data sets
    trend_start_year : int
        first year for trend
    trend_end_year : int
        last year for trend

    Returns
    -------
    Tuple[float, float, float]
        returns the mean trend, minimum trend and maximum trend from the input datasets in units/decade
    """
    all_trends = []

    for ds in all_datasets:
        subset = ds.df.loc[
            (ds.df['year'] >= trend_start_year) & (ds.df['year'] <= trend_end_year) & (~ds.df['data'].isnull())]

        if len(subset) > 25:
            trends = np.polyfit(subset['year'], subset['data'], 1)
            all_trends.append(trends[0] * 10.)

    # calculate the mean trend and max and min trends
    mean_trend = float(np.mean(all_trends))
    max_trend = float(np.max(all_trends))
    min_trend = float(np.min(all_trends))

    return mean_trend, min_trend, max_trend


def calculate_ranks(all_datasets: List[TimeSeriesAnnual], year: int, ascending: bool = False) -> Tuple[int, int]:
    """
    given a set of data sets, return the min and max ranks from the data sets for a given year.

    Parameters
    ----------
    all_datasets : list
        list of data sets
    year : int
        year to calculate ranks for
    ascending: bool
        Set to true to rank low (1st) to high (nth) rather than high (1st) to low (nth)

    Returns
    -------
    Tuple[float, float]
        Return the minimum and maximum rank for the specified year in all data sets
    """
    all_ranks = []

    for ds in all_datasets:
        ranked = ds.df.rank(method='min', ascending=ascending)
        subrank = ranked[ds.df['year'] == year]['data']
        if len(subrank) != 0:
            rank = int(subrank.iloc[0])
            all_ranks.append(rank)

    if len(all_ranks) == 0:
        raise ValueError(f"Year {year} not found in any data sets of {ds.metadata['variable']}")

    # calculate the mean trend and max and min trends
    max_rank = np.max(all_ranks)
    min_rank = np.min(all_ranks)

    return int(min_rank), int(max_rank)


def calculate_values(all_datasets: List[TimeSeriesAnnual], year: int) -> Tuple[float, float, float]:
    """
    given a set of data sets, return the mean min and max values from the data sets for specified year.

    Parameters
    ----------
    all_datasets : list
        list of :class:`.TimeSeriesAnnual` data sets
    year : int
        year to calculate values for

    Returns
    -------
    Tuple[float, float, float]
        Return the mean, min and max values for the chosen year from all_datasets
    """
    all_values = []

    for ds in all_datasets:
        value = ds.df[ds.df['year'] == year]['data']
        if len(value) > 0:
            all_values.append(value.values[0])

    # calculate the mean trend and max and min trends
    mean_value = float(np.mean(all_values))
    max_value = float(np.max(all_values))
    min_value = float(np.min(all_values))

    return mean_value, min_value, max_value


def calculate_values_ipcc_style(all_datasets: List[TimeSeriesAnnual], year: int) -> Tuple[float, float, float]:
    """
    given a set of data sets, return the mean min and max values from the data sets for specified year.

    Parameters
    ----------
    all_datasets : list
        list of :class:`.TimeSeriesAnnual` data sets
    year : int
        year to calculate values for

    Returns
    -------
    Tuple[float, float, float]
        Return the mean, min and max values for the chosen year from all_datasets
    """
    all_values = []

    for ds in all_datasets:
        value = ds.df[ds.df['year'] == year]['data']
        if len(value) > 0:
            all_values.append(value.values[0])

    # calculate the mean trend and max and min trends
    mean_value = float(np.mean(all_values))
    stdev_value = float(np.std(all_values)) * 1.645
    stdev_value = np.sqrt(stdev_value ** 2 + (0.24 / 2) ** 2)

    max_value = mean_value + stdev_value
    min_value = mean_value - stdev_value

    return mean_value, min_value, max_value


def calculate_highest_year_and_values(all_datasets: List[TimeSeriesAnnual]) -> Tuple[List[int], List[List[float]]]:
    """
    From the list of :class:`.TimeSeriesAnnual` get the year that ranks first in each data set. Then, for
    each of those years get the highest and lowest data value from all of the data sets.

    Parameters
    ----------
    all_datasets: List[TimeSeriesAnnual]
        List of :class:`.TimeSeriesAnnual` data sets

    Returns
    -------
    Tuple[List[int], List[List[float]]]
        The first returned element is a list of years that rank first in the data sets. The second element is
        a list with the same length as the first. Each element in the list is two-element list holding the
        lowest and highest values found in any of the datasets for the corresponding year in the first list.
    """
    all_highest_years = []
    all_highest_values = []
    for ds in all_datasets:
        highest_year = ds.get_year_from_rank(1)
        for year in highest_year:
            all_highest_years.append(year)

    # Get the unique highest years
    unique_highest_years = list(set(all_highest_years))

    for high_year in unique_highest_years:
        mean_anomaly, min_anomaly, max_anomaly = calculate_values(all_datasets, high_year)
        all_highest_values.append([min_anomaly, max_anomaly])

    return unique_highest_years, all_highest_values


def set_lo_hi_ticks(limits: list, spacing: float) -> Tuple[float, float, ndarray]:
    """
    Given axis limits and a preferred spacing, calculate new high and low values and a set of ticks

    Parameters
    ----------
    limits: list
        the lower and upper limits of the current axis
    spacing: float
        The preferred tick spacing

    Returns
    -------

    """
    lo = spacing * (1 + (limits[0] // spacing))
    hi = spacing * (1 + (limits[1] // spacing))
    ticks = np.arange(lo, hi, spacing)

    return lo, hi, ticks


def get_first_and_last_years(all_datasets: List[Union[TimeSeriesMonthly, TimeSeriesAnnual]]) -> Tuple[int, int]:
    """
    Extract the first and last years from a list of data sets

    Parameters
    ----------
    all_datasets: List[Union[TimeSeriesMonthly, TimeSeriesAnnual]])
        List containing the data sets for which we want the first and last years
    Returns
    -------
    Tuple[int, int]
        First and last years
    """
    first_years = []
    last_years = []
    for ds in all_datasets:
        first_years.append(ds.df['year'].tolist()[0])
        last_years.append(ds.df['year'].tolist()[-1])
    first_year = np.min(first_years)
    last_year = np.max(last_years)

    return first_year, last_year


def caption_builder(all_datasets: List[Union[TimeSeriesMonthly, TimeSeriesAnnual]]) -> str:
    """
    Write a caption for the standard time series plots.

    Parameters
    ----------
    all_datasets: List[Union[TimeSeriesMonthly, TimeSeriesAnnual]]
        List of datasets used in the plot
    Returns
    -------
    str
        Caption for the collection of data sets
    """
    first_year, last_year = get_first_and_last_years(all_datasets)

    ds = all_datasets[-1]

    number_to_word = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
                      'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen']

    fancy_units = pg.fancy_html_units(ds.metadata['units'])

    caption = f"{ds.metadata['time_resolution']}".capitalize()
    caption += f" {ds.metadata['long_name']} ({fancy_units}"
    if not ds.metadata['actual']:
        caption += f", difference from the {ds.metadata['climatology_start']}-{ds.metadata['climatology_end']} average"
    caption += ") "
    caption += f" from {first_year}-{last_year}. "
    if 1 < len(all_datasets) < 17:
        caption += f"Data are from the following {number_to_word[len(all_datasets)]} data sets: "
    else:
        caption += f"Data are from "

    dataset_names_for_caption = []
    for ds in all_datasets:
        dataset_names_for_caption.append(f"{ds.metadata['display_name']}")

    caption += ', '.join(dataset_names_for_caption)
    caption += '.'

    return caption


def map_caption_builder(all_datasets: List[Union[GridAnnual]], grid_type: str) -> str:
    """
    Write a caption for the standard map plots.

    Parameters
    ----------
    all_datasets: List[Union[GridAnnual]]
        List of datasets used in the plot
    grid_type: str
        Type is one of 'mean', 'rank' or 'unc'.
    Returns
    -------
    str
        Caption for the collection of data sets
    """

    ds = all_datasets[-1]

    number_to_word = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
                      'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen']

    fancy_units = pg.fancy_html_units(ds.metadata['units'])

    caption = f"{ds.metadata['time_resolution']}".capitalize()
    caption += f" {ds.metadata['long_name']}"

    if grid_type == 'unc':
        caption += " uncertainty"
        calculation = 'half-range'
    elif grid_type == 'rank':
        caption += " rank"
        calculation = 'median rank'
    else:
        caption += " anomaly"
        calculation = 'median'

    caption += f" ({fancy_units}"
    if not ds.metadata['actual'] and grid_type not in ['unc', 'rank']:
        caption += f", difference from the {ds.metadata['climatology_start']}-{ds.metadata['climatology_end']} average"
    caption += ") "

    caption += f" for 2024. "
    caption += f"Data shown are the {calculation} of the following {number_to_word[len(all_datasets)]} data sets: "

    dataset_names_for_caption = []
    for ds in all_datasets:
        dataset_names_for_caption.append(f"{ds.metadata['display_name']}")

    caption += ', '.join(dataset_names_for_caption)
    caption += '.'

    if 'precip' in ds.metadata['variable']:
        caption += ' White areas indicate where there were too few data to reliably estimate the percentiles.'

    return caption
