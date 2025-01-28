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
import copy
from pathlib import Path
import numpy as np

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

if __name__ == "__main__":
    final_year = 2024

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    figure_dir = project_dir / 'Figures'
    log_dir = project_dir / 'Logs'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

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

            oot = ds.df.rolling(5, center=True, min_periods=1).mean()
            ds.df.data = oot.data

            all_years_max = []
            all_years_min = []
            for y in range(1991, 2021):
                copy_ds = copy.deepcopy(ds)
                this_year = copy_ds.select_year_range(y, y)
                all_years_max.append(np.max(copy_ds.df.data))
                all_years_min.append(np.min(copy_ds.df.data))

            print(f"Climatological max extent {np.mean(all_years_max)}")
            print(f"Climatological min extent {np.mean(all_years_min)}")

            copy_ds = copy.deepcopy(ds)
            this_year = copy_ds.select_year_range(final_year, final_year)
            print(f"{final_year} Max = {np.max(copy_ds.df.data)}, which is {np.max(copy_ds.df.data)-np.mean(all_years_max)}")
            print(f"{final_year} Min = {np.min(copy_ds.df.data)}, which is {np.min(copy_ds.df.data)-np.mean(all_years_min)}")


        print("\n\n")