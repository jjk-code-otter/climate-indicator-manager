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

from typing import Tuple
import numpy as np
from numpy import ndarray


def calculate_trends(all_datasets: list, y1: int, y2: int) -> Tuple[float, float, float]:
    """
    given a set of data sets, return the mean, min and max trends from the data sets calculated
    using OLS between the chosen years.

    Parameters
    ----------
    all_datasets : list
        list of data sets
    y1 : int
        first year for trend
    y2 : int
        last year for trend

    Returns
    -------
    Tuple[float, float, float]
        returns the mean trend, minimum trend and maximum trend from the input datasets in units/decade
    """
    all_trends = []

    for ds in all_datasets:
        subset = ds.df.loc[(ds.df['year'] >= y1) & (ds.df['year'] <= y2) & (~ds.df['data'].isnull())]

        if len(subset) > 25:
            trends = np.polyfit(subset['year'], subset['data'], 1)
            all_trends.append(trends[0] * 10.)

    # calculate the mean trend and max and min trends
    mean_trend = float(np.mean(all_trends))
    max_trend = float(np.max(all_trends))
    min_trend = float(np.min(all_trends))

    return mean_trend, min_trend, max_trend


def calculate_ranks(all_datasets: list, y1: int, ascending: bool = False) -> Tuple[float, float]:
    """
    given a set of data sets, return the min and max ranks from the data sets.

    Parameters
    ----------
    all_datasets : list
        list of data sets
    y1 : int
        year to calculate trends for
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
        subrank = ranked[ds.df['year'] == y1]['data']
        if len(subrank) == 0:
            rank = None
        else:
            rank = int(subrank.iloc[0])
            all_ranks.append(rank)

    if len(all_ranks) == 0:
        raise ValueError("Year not found in any data set")

    # calculate the mean trend and max and min trends
    max_rank = np.max(all_ranks)
    min_rank = np.min(all_ranks)

    return min_rank, max_rank


def calculate_values(all_datasets: list, y1: int) -> Tuple[float, float, float]:
    """
    given a set of data sets, return the mean min and max values from the data sets for specified year.

    Parameters
    ----------
    all_datasets : list
        list of data sets
    y1 : int
        year to calculate values for

    Returns
    -------
    Tuple[float, float, float]
        Return the mean, min and max values for the chosen year from all_datasets
    """
    all_ranks = []

    for ds in all_datasets:
        value = ds.df[ds.df['year'] == y1]['data']
        all_ranks.append(value.values[0])

    # calculate the mean trend and max and min trends
    mean_rank = float(np.mean(all_ranks))
    max_rank = float(np.max(all_ranks))
    min_rank = float(np.min(all_ranks))

    return mean_rank, min_rank, max_rank


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


def get_first_and_last_years(all_datasets):
    """
    Extract the first and last years from a list of data sets
    Parameters
    ----------
    all_datasets

    Returns
    -------
    int, int
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


def caption_builder(all_datasets):
    first_year, last_year = get_first_and_last_years(all_datasets)

    ds = all_datasets[-1]

    number_to_word = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
                      'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen']

    caption = f"{ds.metadata['time_resolution']} {ds.metadata['long_name']} ({ds.metadata['units']}"
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
        dataset_names_for_caption.append(f"{ds.metadata['name']}")

    caption += ', '.join(dataset_names_for_caption)
    caption += '.'

    return caption
