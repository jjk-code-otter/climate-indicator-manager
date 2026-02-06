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
from typing import List, Union
from climind.data_types.timeseries import TimeSeriesMonthly, TimeSeriesAnnual


def table_by_year(datasets, match_year: int, years_to_show: int = 20) -> str:
    out_text = ''
    for year in range(match_year - years_to_show, match_year + 1):

        out_line = f'{year} '
        for ds in datasets:
            rank = ds.get_rank_from_year(year)
            value = ds.get_value_from_year(year)
            if rank is not None:
                out_line += f'{value:.2f} ({rank:2d})  '
            else:
                out_line += f'_.__ (__)  '

        out_text += f'{out_line}\n'

    return out_text


def record_margin_table_by_year(datasets, match_year: int, years_to_show: int = 50) -> str:
    out_text = ''
    for year in range(match_year - years_to_show, match_year + 1):

        out_line = f'{year} '
        for ds in datasets:

            first_year, last_year = ds.get_first_and_last_year()
            index = year - first_year

            if year > last_year:
                margin = "XXXXXXXXX"
            else:
                subset = ds.df['data'][0: index + 1]
                latest = ds.df['data'][index]
                if np.max(subset) == latest:
                    margin = latest - max(ds.df['data'][0:index])
                    margin = f"{margin:.2f}     "
                else:
                    margin = "---------"

            out_line += f'{margin}  '

        out_text += f'{out_line}\n'

    return out_text


def get_values(datasets, match_year):
    all_match_values = []
    for ds in datasets:
        value = ds.get_value_from_year(match_year)
        if value is not None:
            all_match_values.append(value)
    return all_match_values


def get_ranks(datasets, match_year):
    all_match_ranks = []
    for ds in datasets:
        rank = ds.get_rank_from_year(match_year)
        if rank is not None:
            all_match_ranks.append(rank)
    return all_match_ranks


def run_the_numbers(datasets: List[Union[TimeSeriesMonthly, TimeSeriesAnnual]],
                    match_year: int, title: str, output_dir: Path, ipcc_unc: bool = True):
    """
    Given a list of datasets calculate various statistics relating to ranking and values

    Parameters
    ----------
    datasets: list
        List of data sets
    match_year: int
        Year of interest. Stats will be calculated up to the year of interest, but note that rankings will
        include years after the year of interest if it is not the most recent year in the data sets
    title: str
        name for the file
    output_dir: Path

    Returns
    -------
    None
    """

    with open(output_dir / f'{title}_{match_year}.txt', 'w') as output_file:

        # Table summary of all data sets
        out_line = 'Year '
        for ds in datasets:
            out_line += f"{ds.metadata['name']:10.10} "
        output_file.write(f'{out_line}\n')

        output_file.write(table_by_year(datasets, match_year))

        all_match_values = get_values(datasets, match_year)
        all_match_ranks = get_ranks(datasets, match_year)

        if len(all_match_values) > 0:
            sd = np.std(all_match_values) * 1.645
            if ipcc_unc:
                sd = np.sqrt((sd ** 2) + ((0.25 / 2) ** 2))

            mean_value = np.mean(all_match_values)
            min_value = np.min(all_match_values)
            max_value = np.max(all_match_values)
            min_rank = np.min(all_match_ranks)
            max_rank = np.max(all_match_ranks)

            output_file.write('\n')
            output_file.write(f'Mean for {match_year}: {mean_value :.2f} +- {sd:.2f} degC '
                              f'[{min_value :.2f}-{max_value :.2f}]\n')
            output_file.write(f'(alt rep) Mean for {match_year}: {mean_value :.2f} '
                              f'[{mean_value - sd:.2f} - {mean_value + sd:.2f}] degC\n')
            output_file.write(f'Rank between {min_rank} and {max_rank}\n')
            output_file.write(f'Based on {len(all_match_values)} data sets.\n')

            output_file.write('\n')
            output_file.write(f'Mean for {match_year}: {mean_value :.4f} +- {sd:.4f} degC '
                              f'[{min_value :.4f}-{max_value :.4f}]\n')
            output_file.write(f'(alt rep) Mean for {match_year}: {mean_value :.4f} '
                              f'[{mean_value - sd:.4f} - {mean_value + sd:.4f}] degC\n')
            output_file.write(f'Rank between {min_rank} and {max_rank}\n')
            output_file.write(f'Based on {len(all_match_values)} data sets.\n')
        else:
            output_file.write('NO DATA\n')


def record_margins(datasets: List[Union[TimeSeriesMonthly, TimeSeriesAnnual]],
                   match_year: int, title: str, output_dir: Path):
    with open(output_dir / f'{title}_{match_year}.txt', 'w') as output_file:
        # Table summary of all data sets
        out_line = 'Year '
        for ds in datasets:
            out_line += f"{ds.metadata['name']:10.10} "
        output_file.write(f'{out_line}\n')

        output_file.write(record_margin_table_by_year(datasets, match_year, years_to_show=50))


def get_latitudes(resolution):
    """
    Generate a "latitude" array running from -90 + half the resolution to 90 - half the resolution.

    Parameters
    ----------
    resolution: float
        Resolution of the grid

    Returns
    -------
    ndarray
    """
    return np.arange(-90.0 + resolution / 2., 90.0 + resolution / 2., resolution)


def get_n_years_from_n_months(n_months):
    """
    For a given number of months, count the number of full years

    Parameters
    ----------
    n_months: int
        Number of months to convert to whole years

    Returns
    -------
    int
        Number of whole years
    """
    n_years = int(np.floor(n_months / 12.))
    return n_years


def monthly_to_annual_array(monthly_means):
    """
    Calculate 12-month averages from a monthly array of shape (n_months, 3). For use in the IPCC
    averaging method

    Parameters
    ----------
    monthly_means: ndarray(n_months, 3)

    Returns
    -------
    ndarray(n_years, 3)
        Returns the annual averages
    """
    annual_means = np.mean(monthly_means.reshape((-1, 12, 3)), axis=1)
    return annual_means


def rolling_average(input_array, window_length):
    """
    Calculate a rolling average of specified window_length

    Parameters
    ----------
    input_array: ndarray
        input array for which rolling averages are to be calculated
    window_length: int
        length of rolling average window

    Returns
    -------
    ndarray

    """
    out = np.zeros((len(input_array)))
    out[:] = np.nan
    for i in range(window_length, len(input_array) + 1):
        out[i - int(window_length / 2) - 1] = np.mean(input_array[i - window_length:i])
    return out
