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
import logging
import geopandas as gp

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt

from climind.config.config import DATA_DIR, CLIMATOLOGY
from climind.definitions import METADATA_DIR

if __name__ == "__main__":
    final_year = 2022

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR

    regional_data_dir = project_dir / "RegionalData"
    regional_data_dir.mkdir(exist_ok=True)
    regional_metadata_dir = project_dir / "RegionalMetadata"
    regional_metadata_dir.mkdir(exist_ok=True)

    data_dir = project_dir / "Data"
    shape_dir = project_dir / "Shape_Files"
    fdata_dir = project_dir / "Formatted_Data"
    figure_dir = project_dir / 'Figures'
    log_dir = project_dir / 'Logs'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

    script = Path(__file__).stem
    logging.basicConfig(filename=log_dir / f'{script}.log',
                        filemode='w', level=logging.INFO)

    # Prepare the shape files
    continents = gp.read_file(shape_dir / 'WMO_RAs.shp')
    continents = continents.rename(columns={'Region': 'region'})
    print(continents)

    # Read in African subregions and select only the first of each subregion using iloc
    subregions = gp.read_file(shape_dir / 'Africa_subregion.shp')
    subregions = subregions.rename(columns={'subregion': 'region'})
    subregions = subregions.iloc[[0, 1, 2, 6, 7, 8]]
    subregions = subregions.reset_index()
    print(subregions)

    region3 = gp.read_file(shape_dir / 'South America' / 'South America.shp')
    region3 = region3.append(gp.read_file(shape_dir / 'Mexico' / 'Mexico.shp'), ignore_index=True)
    region3 = region3.append(gp.read_file(shape_dir / 'Caribbean' / 'Caribbean.shp'), ignore_index=True)
    region3 = region3.reindex()

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    datasets_to_use = ['ERA5']# ['HadCRUT5', 'GISTEMP', 'NOAAGlobalTemp', 'Berkeley Earth', 'ERA5', 'JRA-55']

    ts_archive = archive.select(
        {
            'variable': 'tas',
            'type': 'gridded',
            'time_resolution': 'monthly',
            'name': datasets_to_use[0:]
        }
    )

    all_datasets = ts_archive.read_datasets(data_dir, grid_resolution=1)

    # start processing
    for ds in all_datasets:
        ds.rebaseline(CLIMATOLOGY[0], CLIMATOLOGY[1])
        pt.nice_map(ds.df, figure_dir / f"{ds.metadata['name']}", ds.metadata['name'])

        region_names = ['Africa', 'Asia', 'South America',
                        'North America', 'South-West Pacific', 'Europe']
        for region in range(6):
            monthly_time_series = ds.calculate_regional_average(continents, region)
            annual_time_series = monthly_time_series.make_annual()
            annual_time_series.select_year_range(1900, final_year)

            wmo_ra = region + 1
            annual_time_series.metadata['name'] = f"wmo_ra_{wmo_ra}_{annual_time_series.metadata['name']}"
            dataset_name = annual_time_series.metadata['name']

            (regional_data_dir / dataset_name).mkdir(exist_ok=True)

            filename = f"{dataset_name}.csv"
            metadata_filename = f"{dataset_name}.json"

            annual_time_series.metadata['variable'] = f'wmo_ra_{wmo_ra}'
            annual_time_series.metadata[
                'long_name'] = f'Regional mean temperature for WMO RA {region + 1} {region_names[region]}'

            annual_time_series.write_csv(regional_data_dir / dataset_name / filename,
                                         metadata_filename=regional_metadata_dir / metadata_filename)

        sub_region_names = ['North Africa', 'West Africa', 'Central Africa',
                            'Eastern Africa', 'Southern Africa', 'Indian Ocean']
        for region in range(6):
            monthly_time_series = ds.calculate_regional_average(subregions, region)
            annual_time_series = monthly_time_series.make_annual()
            annual_time_series.select_year_range(1900, final_year)

            wmo_subregion = region + 1
            annual_time_series.metadata[
                'name'] = f"africa_subregion_{wmo_subregion}_{annual_time_series.metadata['name']}"
            dataset_name = annual_time_series.metadata['name']

            (regional_data_dir / dataset_name).mkdir(exist_ok=True)

            filename = f"{dataset_name}.csv"
            metadata_filename = f"{dataset_name}.json"

            annual_time_series.metadata['variable'] = f'africa_subregion_{wmo_subregion}'
            annual_time_series.metadata['long_name'] = f'Regional mean temperature for {sub_region_names[region]}'

            annual_time_series.write_csv(regional_data_dir / dataset_name / filename,
                                         metadata_filename=regional_metadata_dir / metadata_filename)

        lac_region_names = ['South America', 'Mexico', 'Caribbean']
        for region in range(3):
            monthly_time_series = ds.calculate_regional_average(region3, region)
            annual_time_series = monthly_time_series.make_annual()
            annual_time_series.select_year_range(1900, final_year)

            lac_subregion = region + 1
            dataset_name = f"lac_subregion_{lac_subregion}_{annual_time_series.metadata['name']}"
            annual_time_series.metadata['name'] = dataset_name

            (regional_data_dir / dataset_name).mkdir(exist_ok=True)

            filename = f"{dataset_name}.csv"
            metadata_filename = f"{dataset_name}.json"

            annual_time_series.metadata['variable'] = f'lac_subregion_{lac_subregion}'
            annual_time_series.metadata['long_name'] = f'Regional mean temperature for {lac_region_names[region]}'

            annual_time_series.write_csv(regional_data_dir / dataset_name / filename,
                                         metadata_filename=regional_metadata_dir / metadata_filename)
