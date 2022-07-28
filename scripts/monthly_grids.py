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
    print(continents)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    ts_archive = archive.select({'variable': 'tas',
                                 'type': 'gridded',
                                 'time_resolution': 'monthly',
                                 'name': ['HadCRUT5',
                                          'GISTEMP',
                                          'ERA5',
                                          'NOAAGlobalTemp',
                                          'Berkeley Earth',
                                          'JRA-55']})

    all_datasets = ts_archive.read_datasets(data_dir, grid_resolution=5)

    all_ts = []
    for ds in all_datasets:
        ds.rebaseline(1981, 2010)
        ts = ds.calculate_regional_average(continents, 5)
        ts = ts.make_annual()
        all_ts.append(ts)
        pt.nice_map(ds.df, figure_dir / f"{ds.metadata['name']}", ds.metadata['name'])

pt.neat_plot(figure_dir, all_ts, 'regional.png', '')
pass