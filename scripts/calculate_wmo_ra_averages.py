from pathlib import Path
import logging
import geopandas as gp

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt

from climind.config.config import DATA_DIR
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

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    datasets_to_use = ['HadCRUT5', 'GISTEMP', 'ERA5', 'NOAAGlobalTemp', 'Berkeley Earth', 'JRA-55']

    ts_archive = archive.select(
        {
            'variable': 'tas',
            'type': 'gridded',
            'time_resolution': 'monthly',
            'name': datasets_to_use[0:5]
        }
    )

    all_datasets = ts_archive.read_datasets(data_dir, grid_resolution=1)

    # start processing
    for ds in all_datasets:
        ds.rebaseline(1981, 2010)
        pt.nice_map(ds.df, figure_dir / f"{ds.metadata['name']}", ds.metadata['name'])

        region_names = ['Africa', 'Asia', 'South America',
                        'North America', 'South-West Pacific', 'Europe']
        for region in range(6):
            monthly_time_series = ds.calculate_regional_average(continents, region)
            annual_time_series = monthly_time_series.make_annual()
            annual_time_series.select_year_range(1900, 2021)

            wmo_ra = region + 1
            annual_time_series.metadata['name'] = f"wmo_ra_{wmo_ra}_{annual_time_series.metadata['name']}"
            dataset_name = annual_time_series.metadata['name']

            (regional_data_dir / dataset_name).mkdir(exist_ok=True)

            filename = f"{dataset_name}.csv"
            metadata_filename = f"{dataset_name}.json"

            annual_time_series.metadata['variable'] = f'wmo_ra_{wmo_ra}'
            annual_time_series.metadata['long_name'] = f'Regional mean temperature for WMO RA {region+1} {region_names[region]}'

            annual_time_series.write_csv(regional_data_dir / dataset_name / filename,
                                         metadata_filename=regional_metadata_dir / metadata_filename)

        sub_region_names = ['North Africa', 'West Africa', 'Central Africa',
                            'Eastern Africa', 'Southern Africa', 'Indian Ocean']
        for region in range(6):
            monthly_time_series = ds.calculate_regional_average(subregions, region)
            annual_time_series = monthly_time_series.make_annual()
            annual_time_series.select_year_range(1900, 2021)

            wmo_subregion = region + 1
            annual_time_series.metadata['name'] = f"africa_subregion_{wmo_subregion}_{annual_time_series.metadata['name']}"
            dataset_name = annual_time_series.metadata['name']

            (regional_data_dir / dataset_name).mkdir(exist_ok=True)

            filename = f"{dataset_name}.csv"
            metadata_filename = f"{dataset_name}.json"

            annual_time_series.metadata['variable'] = f'africa_subregion_{wmo_subregion}'
            annual_time_series.metadata['long_name'] = f'Regional mean temperature for {sub_region_names[region]}'

            annual_time_series.write_csv(regional_data_dir/ dataset_name / filename,
                                         metadata_filename=regional_metadata_dir / metadata_filename)
