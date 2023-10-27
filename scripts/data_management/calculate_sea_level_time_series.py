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


def process_africa_sea_level_shape_files(in_shape_dir):
    subregions = gp.read_file(in_shape_dir / 'Sealevel_Regions_Africa' / 'Africa.shp')
    subregions = subregions.rename(columns={'subregions': 'region'})
    return subregions


def process_regions(region_names, region_shapes, regional_data_dir, ds, stub, start_year, final_year,
                    long_names) -> None:
    n_regions = len(region_names)

    for region in range(n_regions):
        monthly_time_series = ds.calculate_regional_average_missing(region_shapes, region, land_only=False,
                                                                    ocean_only=False)
        wmo_ra = region + 1
        monthly_time_series.metadata['name'] = f"{stub}_{wmo_ra}_{monthly_time_series.metadata['name']}"
        dataset_name = monthly_time_series.metadata['name']

        (regional_data_dir / dataset_name).mkdir(exist_ok=True)

        filename = f"{dataset_name}.csv"
        metadata_filename = f"{dataset_name}.json"

        monthly_time_series.metadata['variable'] = f'{stub}_{wmo_ra}'
        monthly_time_series.metadata['long_name'] = long_names[region]

        monthly_time_series.write_csv(regional_data_dir / dataset_name / filename,
                                      metadata_filename=regional_metadata_dir / metadata_filename)


if __name__ == "__main__":

    datasets_to_use = ['CDS sea level']
    start_year = 1993
    final_year = 2022

    output_data_dir = "RegionalData"
    output_metadata_dir = "RegionalMetadata"

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

    sea_level_subregions = process_africa_sea_level_shape_files(shape_dir)
    print(sea_level_subregions)

    for ds in all_datasets:
        sub_region_names = sea_level_subregions.Name
        long_names = [f'Regional mean sea level for WMO RA 1 {sub_region_names[i]}' for i in range(8)]

        process_regions(sub_region_names, sea_level_subregions, regional_data_dir, ds, 'sl_africa_subregion',
                        start_year, final_year, long_names)

    print(long_names)

    print("Got here")
