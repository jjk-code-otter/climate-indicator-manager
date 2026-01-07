#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2025 John Kennedy
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

import numpy as np
import climind.data_manager.processing as dm
from climind.config.config import DATA_DIR
from pathlib import Path
import os


def calc_stats(ts_archive, data_dir):
    all_datasets = ts_archive.read_datasets(data_dir)

    print(all_datasets)

    for ds in all_datasets:

        print(ds.metadata['name'])

        years = []
        annual_mins = []
        annual_maxs = []
        annual_means = []

        for year in range(1979, 2026):
            ds_extract = copy.deepcopy(ds)
            ds_extract = ds_extract.select_year_range(year, year)

            years.append(year)
            annual_mins.append(np.min(ds_extract.df.data))
            annual_maxs.append(np.max(ds_extract.df.data))
            annual_means.append(np.mean(ds_extract.df.data))

            if year == 2025:
                print(f"{years[-1]}, {annual_mins[-1]:.2f}, {annual_maxs[-1]:.2f}, {annual_means[-1]:.2f}")
                min_date = ds_extract.df[ds_extract.df.data == annual_mins[-1]]
                print(f"Min on {min_date.year.values[0]}-{min_date.month.values[0]:02d}-{min_date.day.values[0]:02d}")
                max_date = ds_extract.df[ds_extract.df.data == annual_maxs[-1]]
                print(f"Max on {max_date.year.values[0]}-{max_date.month.values[0]:02d}-{max_date.day.values[0]:02d}")

            if year == 2020:
                print(f"2020 {annual_means[-1]:.2f}")

        years = np.array(years)
        annual_mins = np.array(annual_mins)
        annual_maxs = np.array(annual_maxs)
        annual_means = np.array(annual_means)

        min_order = np.argsort(annual_mins)
        max_order = np.argsort(annual_maxs)

        print("Minimum ranked years")
        print(years[min_order])
        print("Maximum ranked years")
        print(years[max_order])

        min_clim8110 = np.mean(annual_mins[(years >= 1981) & (years <= 2010)])
        max_clim8110 = np.mean(annual_maxs[(years >= 1981) & (years <= 2010)])
        mean_clim8110 = np.mean(annual_means[(years >= 1981) & (years <= 2010)])

        min_clim9120 = np.mean(annual_mins[(years >= 1991) & (years <= 2020)])
        max_clim9120 = np.mean(annual_maxs[(years >= 1991) & (years <= 2020)])
        mean_clim9120 = np.mean(annual_means[(years >= 1991) & (years <= 2020)])

        print(f"1981-2010 min:{min_clim8110:.2f} max:{max_clim8110:.2f} mean:{mean_clim8110:.2f}")
        print(f"1991-2020 min:{min_clim9120:.2f} max:{max_clim9120:.2f} mean:{mean_clim9120:.2f}")


project_dir = DATA_DIR / "ManagedData"
data_dir = project_dir / "Data"

ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
METADATA_DIR = (ROOT_DIR / "..").resolve() / "climind" / "metadata_files"

archive = dm.DataArchive.from_directory(METADATA_DIR)

print("ARCTIC")
ts_archive = archive.select(
    {
        'type': 'timeseries',
        'variable': 'arctic_ice',
        'time_resolution': 'irregular',
        'name': ['NSIDC v4', 'JAXA NH', 'OSI SAF v2p3']
    }
)

calc_stats( ts_archive, data_dir)

print("ANTARCTICA")
ts_archive = archive.select(
    {
        'type': 'timeseries',
        'variable': 'antarctic_ice',
        'time_resolution': 'irregular',
        'name': ['NSIDC v4 SH', 'JAXA SH', 'OSI SAF SH v2p3']
    }
)

calc_stats( ts_archive, data_dir)