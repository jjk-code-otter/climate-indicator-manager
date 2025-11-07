#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2023 John Kennedy
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
import os
import argparse

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-y", help="year for plot", type=int)
    parser.add_argument("-m", help="month for plot", type=int)
    parser.add_argument("-q", help="how many months in the quantile period", type=int)
    args = parser.parse_args()

    plot_year = args.y
    plot_month = args.m
    how_many_months = args.q

    how_many_months = 3


    project_dir = DATA_DIR / "ManagedData"
    ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    METADATA_DIR = (ROOT_DIR / "..").resolve() / "climind" / "metadata_files"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    figure_dir = project_dir / 'Figures'

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    names = [
        f'GPCC quantiles {how_many_months}month'
    ]

    for name in names:
        print(name)
        ts_archive = archive.select({'variable': f'precip_quantiles_{how_many_months}month',
                                     'type': 'gridded',
                                     'time_resolution': 'monthly',
                                     'name': name})

        all_datasets = ts_archive.read_datasets(data_dir, grid_resolution=1)

        ds = all_datasets[0]

        filename = figure_dir / f"{how_many_months}month_quantile_map_{plot_year}_{plot_month:02d}_{ds.metadata['name']}"
        title = f"{ds.metadata['name']} {plot_year}_{plot_month:02d}"

        # try:
        pt.plot_map_by_year_and_month(ds, plot_year, plot_month, filename, title,
                                      var=f'precip_quantiles_{how_many_months}month')
        # except:
        #    print(f"Not for this month {plot_year}-{plot_month:02d} and data sets {name}")
