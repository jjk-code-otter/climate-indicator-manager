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
import logging
import geopandas as gp

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt

from climind.config.config import DATA_DIR, CLIMATOLOGY
from climind.definitions import METADATA_DIR

if __name__ == "__main__":

    datasets_to_use = ['CDS sea level']
    start_year = 1900
    output_data_dir = "RegionalData"
    output_metadata_dir = "RegionalMetadata"

    final_year = 2022

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR

    regional_data_dir = project_dir / output_data_dir
    regional_data_dir.mkdir(exist_ok=True)
    regional_metadata_dir = project_dir / output_metadata_dir
    regional_metadata_dir.mkdir(exist_ok=True)

    data_dir = project_dir / "Data"
    shape_dir = project_dir / "Shape_Files"
    fdata_dir = project_dir / "Formatted_Data"
    figure_dir = project_dir / 'Figures'
    log_dir = project_dir / 'Logs'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    ts_archive = archive.select(
        {
            'variable': 'sealevel',
            'type': 'gridded',
            'time_resolution': 'monthly',
            'name': datasets_to_use
        }
    )

    all_datasets = ts_archive.read_datasets(data_dir)



    for ds in all_datasets:
        ts = ds.calculate_regional_average(regions, region_number, land_only=False)

    print("Got here")