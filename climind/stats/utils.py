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


def run_the_numbers(datasets: list, match_year: int, title: str, output_dir: Path):
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

    """

    with open(output_dir / f'{title}_{match_year}.txt', 'w') as output_file:

        all_match_values = []
        all_match_ranks = []

        # Table summary of all data sets
        out_line = 'Year '
        for ds in datasets:
            out_line += f"{ds.metadata['name']:10.10} "
        output_file.write(f'{out_line}\n')

        for year in range(match_year - 12, match_year + 1):

            out_line = f'{year} '
            for ds in datasets:
                rank = ds.get_rank_from_year(year)
                value = ds.get_value_from_year(year)
                if rank is not None:
                    out_line += f'{value:.2f} ({rank:2d})  '
                else:
                    out_line += f'_.__ (__)  '
            output_file.write(f'{out_line}\n')

        # data set by dataset summary
        for ds in datasets:
            for year in range(match_year - 12, match_year + 1):
                rank = ds.get_rank_from_year(year)
                value = ds.get_value_from_year(year)

                if rank is not None:
                    #                print(f'{year} Rank:{rank} Value:{value:.3f}')
                    if year == match_year:
                        all_match_values.append(value)
                        all_match_ranks.append(rank)

        if len(all_match_values) > 0:
            sd = np.std(all_match_values) * 1.645
            sd = np.sqrt(sd ** 2 + (0.24 / 2) ** 2)

            output_file.write('\n')
            output_file.write(f'Mean for {match_year}: {np.mean(all_match_values):.2f} +- {sd:.2f} degC '
                        f'[{np.min(all_match_values):.2f}-{np.max(all_match_values):.2f}]\n')
            output_file.write(f'Rank between {np.min(all_match_ranks)} and {np.max(all_match_ranks)}\n')
            output_file.write(f'Based on {len(all_match_values)} data sets.\n')
        else:
            output_file.write('NO DATA\n')
