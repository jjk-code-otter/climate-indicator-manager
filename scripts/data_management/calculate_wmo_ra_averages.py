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


def process_africa_shape_files(in_shape_dir):
    subregions = gp.read_file(in_shape_dir / 'Africa_subregion.shp')
    subregions = subregions.rename(columns={'subregion': 'region'})
    # Select only the first of each subregion using iloc
    subregions = subregions.iloc[[0, 1, 2, 6, 7, 8]]
    subregions = subregions.reset_index()
    return subregions


def process_lac_shape_files(in_shape_dir):
    additional_regions = ['Mexico and Central America', 'Caribbean', 'Mexico',
                          'Central America', 'Latin America and Caribbean']

    subregions = gp.read_file(in_shape_dir / 'South America' / 'South America.shp')
    for reg in additional_regions:
        addition = gp.read_file(in_shape_dir / reg / f'{reg}.shp')
        subregions = subregions._append(addition, ignore_index=True)

    subregions = subregions.reindex()
    return subregions


def process_arab_shape_files(in_shape_dir):
    additional_regions = ['North African Arab Countries', 'East African Arab Countries',
                          'Arabian Peninsula Arab Countries', 'Near East Arab Countries']

    subregions = gp.read_file(in_shape_dir / 'League of Arab States' / 'League of Arab States.shp')
    for reg in additional_regions:
        addition = gp.read_file(in_shape_dir / reg / f'{reg}.shp')
        subregions = subregions._append(addition, ignore_index=True)

    subregions = subregions.reindex()
    return subregions


def process_regions(region_names, region_shapes, regional_data_dir, ds, stub, start_year, final_year, long_names,
                    land_only=True) -> None:
    n_regions = len(region_names)

    for region in range(n_regions):
        monthly_time_series = ds.calculate_regional_average_missing(region_shapes, region, land_only=land_only)
        annual_time_series = monthly_time_series.make_annual()
        annual_time_series.select_year_range(start_year, final_year)

        wmo_ra = region + 1
        annual_time_series.metadata['name'] = f"{stub}_{wmo_ra}_{annual_time_series.metadata['name']}"
        dataset_name = annual_time_series.metadata['name']

        (regional_data_dir / dataset_name).mkdir(exist_ok=True)

        filename = f"{dataset_name}.csv"
        metadata_filename = f"{dataset_name}.json"

        annual_time_series.metadata['variable'] = f'{stub}_{wmo_ra}'
        annual_time_series.metadata['long_name'] = long_names[region]

        annual_time_series.write_csv(regional_data_dir / dataset_name / filename,
                                     metadata_filename=regional_metadata_dir / metadata_filename)


if __name__ == "__main__":

    test = False

    if test:
        start_year = 1850
        output_data_dir = "RegionalTestData"
        output_metadata_dir = "RegionalTestMetadata"
        datasets_to_use = [
            'DCENT_MLE'
            # 'Calvert 2024', 'DCENT', 'GloSAT',
            # 'GETQUOCS', 'CMST', 'Vaccaro', 'Kadow CMIP', 'NOAA Interim', 'Kadow', 'HadCRUT5',
            # 'GISTEMP', 'NOAAGlobalTemp', 'Berkeley Earth', 'ERA5', 'JRA-55', 'JRA-3Q', 'NOAA v6'
        ]
    else:
        start_year = 1900
        output_data_dir = "RegionalData"
        output_metadata_dir = "RegionalMetadata"
        datasets_to_use = [
            'HadCRUT5',
            #'GISTEMP',
            #'NOAA v6',
            #'Berkeley Earth',
            #'ERA5',
            #'JRA-3Q'
        ]

    final_year = 2024

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

    script = Path(__file__).stem
    logging.basicConfig(filename=log_dir / f'{script}.log',
                        filemode='w', level=logging.INFO)

    # Read in the WMO RA shape file
    continents = gp.read_file(shape_dir / 'WMO_RAs.shp')
    continents = continents.rename(columns={'Region': 'region'})
    print(continents)

    # Read in African subregions
    africa_subregions = process_africa_shape_files(shape_dir)
    print(africa_subregions)

    # Read in LAC subregions
    lac_subregions = process_lac_shape_files(shape_dir)
    print(lac_subregions)

    # Read in Arab subregions
    arab_subregions = process_arab_shape_files(shape_dir)
    print(arab_subregions)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    ts_archive = archive.select(
        {
            'variable': 'tas',
            'type': 'gridded',
            'time_resolution': 'monthly',
            'name': datasets_to_use
        }
    )

    all_datasets = ts_archive.read_datasets(data_dir, grid_resolution=1)

    # start processing
    for ds in all_datasets:
        ds.rebaseline(CLIMATOLOGY[0], CLIMATOLOGY[1])
        pt.nice_map(ds.df, figure_dir / f"{ds.metadata['name']}", ds.metadata['name'])

        region_names = ['Africa', 'Asia', 'South America',
                        'North America', 'South-West Pacific', 'Europe']
        long_names = [f'Regional mean temperature for WMO RA {i + 1} {region_names[i]}' for i in range(6)]
        process_regions(region_names, continents, regional_data_dir, ds, 'wmo_ra', start_year, final_year, long_names)

        # Do land and ocean processing for the RA areas.
        long_names = [f'Regional mean land and ocean temperature for WMO RA {i + 1} {region_names[i]}' for i in
                      range(6)]
        process_regions(region_names, continents, regional_data_dir, ds, 'wmo_ra_land_ocean', start_year, final_year,
                        long_names, land_only=False)

        sub_region_names = ['North Africa', 'West Africa', 'Central Africa',
                            'Eastern Africa', 'Southern Africa', 'Indian Ocean']
        long_names = [f'Regional mean temperature for WMO RA 1 {sub_region_names[i]}' for i in range(6)]
        process_regions(sub_region_names, africa_subregions, regional_data_dir, ds, 'africa_subregion', start_year,
                        final_year, long_names)

        lac_region_names = ['South America', 'Mexico and Central America', 'Caribbean',
                            'Mexico', 'Central America', 'Latin America and Caribbean']
        long_names = [f'Regional mean temperature for {lac_region_names[i]}' for i in range(6)]
        process_regions(lac_region_names, lac_subregions, regional_data_dir, ds, 'lac_subregion', start_year,
                        final_year, long_names)

        arab_region_names = ['League of Arab States', 'North African Arab Countries', 'East African Arab Countries',
                             'Arabian Peninsula Arab Countries', 'Near East Arab Countries']
        long_names = [f'Regional mean temperature for {arab_region_names[i]}' for i in range(5)]
        process_regions(arab_region_names, arab_subregions, regional_data_dir, ds, 'arab_subregion', start_year,
                        final_year, long_names)
