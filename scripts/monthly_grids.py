from pathlib import Path
import logging
import geopandas as gp
import regionmask

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

if __name__ == "__main__":
    final_year = 2022

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR

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

    continents = gp.read_file(shape_dir / 'WMO_RAs.shp')
    continents = continents.rename(columns={'Region':'region'})
    print(continents)

    subregions = gp.read_file(shape_dir / 'Africa_subregion.shp')
    subregions = subregions.rename(columns={'subregion': 'region'})
    print(subregions)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    names = ['HadCRUT5',
             'GISTEMP',
             'ERA5',
             'NOAAGlobalTemp',
             'Berkeley Earth',
             'JRA-55']

    ts_archive = archive.select({'variable': 'tas',
                                 'type': 'gridded',
                                 'time_resolution': 'monthly',
                                 'name': names[:]})

    all_datasets = ts_archive.read_datasets(data_dir, grid_resolution=5)

    all_ts = []
    all_ts_sub = []

    for region in range(6):
        all_ts.append([])
    for region in range(6):
        all_ts_sub.append([])

    for ds in all_datasets:
        ds.rebaseline(1981, 2010)

        for region in range(6):
            ts = ds.calculate_regional_average(continents, region)
            ts = ts.make_annual()
            ts.select_year_range(1900, 2022)
            all_ts[region].append(ts)

        for i, region in enumerate([0, 1, 2, 6, 7, 8]):
            ts = ds.calculate_regional_average(subregions, region)
            ts = ts.make_annual()
            ts.select_year_range(1900, 2022)
            all_ts_sub[i].append(ts)
        pt.nice_map(ds.df, figure_dir / f"{ds.metadata['name']}", ds.metadata['name'])

    region_names = ['Africa', 'Asia', 'South America', 'North America', 'South-West Pacific', 'Europe']
    for region in range(6):
        print(region_names[region], continents.region[region])
        pt.neat_plot(figure_dir,
                     all_ts[region],
                     f'regional_RA{region + 1}.png',
                     f'WMO RA{region + 1} - {region_names[region]}')

    sub_region_names = ['North Africa', 'West Africa', 'Central Africa', 'Eastern Africa', 'Southern Africa',
                        'Indian Ocean']
    for i, region in enumerate([0, 1, 2, 6, 7, 8]):
        print(sub_region_names[i], subregions.region[region])
        pt.neat_plot(figure_dir,
                     all_ts_sub[i],
                     f'subregional_{i+1}.png',
                     f'WMO RA{i + 1} - {sub_region_names[i]}')
