#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2024 John Kennedy
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
import logging

import climind.data_manager.processing as dm

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR
import climind.plotters.plot_types as pt

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

if __name__ == "__main__":

    final_year = 2022

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    fdata_dir = project_dir / "Formatted_Data"
    figure_dir = project_dir / 'Figures'

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    # some global temperature data sets are annual only, others are monthly so need to read these separately
    grid_archive = archive.select({'variable': 'tas',
                                 'type': 'gridded',
                                 'name': ["HadCRUT5_5x5", "NOAA Interim_5x5", "GISTEMP_5x5", "ERA5_5x5", "JRA-55_5x5", "Berkeley Earth_5x5"],
                                 'time_resolution': 'annual'})

    all_datasets = grid_archive.read_datasets(data_dir)

    for ds in all_datasets:
        ds.select_year_range(final_year, final_year)

    pt.dashboard_map_pastel(figure_dir, all_datasets, 'pastel_map.png', f'{final_year}')