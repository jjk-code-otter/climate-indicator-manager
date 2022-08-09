"""
This script calculates various statistics of global mean temperatures using monthly averages.
Each month (jan, feb .. .dec) is treated separately to show how trend vs variability changes
through the year. It also makes plots of these data in a variety of styles.
"""
import logging
from pathlib import Path

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

if __name__ == "__main__":

    final_year = 2022

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    figure_dir = project_dir / 'Figures'
    log_dir = project_dir / 'Logs'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

    script = Path(__file__).stem
    logging.basicConfig(filename=log_dir / f'{script}.log',
                        filemode='w', level=logging.INFO)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)


    mhw_archive = archive.select({'variable': 'mhw'})
    mcs_archive = archive.select({'variable': 'mcs'})

    mhw = mhw_archive.read_datasets(data_dir)
    mcs = mcs_archive.read_datasets(data_dir)

    pt.marine_heatwave_plot(figure_dir, mhw, mcs, 'marine_heatwave.png')
