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

import logging
from pathlib import Path

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

if __name__ == "__main__":
    final_year = 2022

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    figure_dir = project_dir / 'Figures'
    log_dir = project_dir / 'Logs'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

    script = Path(__file__).stem
    logging.basicConfig(filename=log_dir / f'{script}.log',
                        filemode='w', level=logging.INFO)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    holdall = {
        'arctic_ice': [
            {'variable': 'arctic_ice',
             'type': 'timeseries',
             'time_resolution': 'irregular'},
            'Arctic sea-ice extent'

        ],
        'antarctic_ice': [
            {'variable': 'antarctic_ice',
             'type': 'timeseries',
             'time_resolution': 'irregular'},
            'Antarctic sea-ice extent'

        ]
    }

    for key in holdall:

        print(key)

        ts_archive = archive.select(holdall[key][0])
        all_datasets = ts_archive.read_datasets(data_dir)

        for ds in all_datasets:
            print(ds.metadata['display_name'])
            # get annual max and min and dates
            this_year = ds.select_year_range(2023, 2023)
            index =ds.df.data.idxmax()
            print(ds.df.loc[[index]])
            index =ds.df.data.idxmin()
            print(ds.df.loc[[index]])


    print()