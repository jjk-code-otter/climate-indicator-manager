"""
This script calculates various statistics of global mean temperatures using monthly averages.
Each month (jan, feb .. .dec) is treated separately to show how trend vs variability changes
through the year. It also makes plots of these data in a variety of styles.
"""
from pathlib import Path
import numpy as np
import logging
import calendar

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt
import climind.stats.utils as utils

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

    logging.basicConfig(filename=log_dir / 'example.log',
                        filemode='w', level=logging.INFO)

    for month in range(1, 13):
        month_word = calendar.month_name[month]

        # Read in the whole archive then select the various subsets needed here
        archive = dm.DataArchive.from_directory(metadata_dir)

        ts_archive = archive.select({'variable': 'tas',
                                     'type': 'timeseries',
                                     'time_resolution': 'monthly'})

        sst_archive = archive.select({'variable': 'sst',
                                      'type': 'timeseries',
                                      'time_resolution': 'monthly'})

        lsat_archive = archive.select({'variable': 'lsat',
                                       'type': 'timeseries',
                                       'time_resolution': 'monthly'})

        all_datasets = ts_archive.read_datasets(data_dir)
        lsat_datasets = lsat_archive.read_datasets(data_dir)
        sst_datasets = sst_archive.read_datasets(data_dir)

        anns = []
        for ds in all_datasets:
            ds.rebaseline(1981, 2010)
            annual = ds.make_annual_by_selecting_month(month)
            annual.select_year_range(1850, final_year)
            anns.append(annual)

        lsat_anns = []
        for ds in lsat_datasets:
            ds.rebaseline(1981, 2010)
            annual = ds.make_annual_by_selecting_month(month)
            annual.select_year_range(1850, final_year)
            lsat_anns.append(annual)

        sst_anns = []
        for ds in sst_datasets:
            ds.rebaseline(1981, 2010)
            annual = ds.make_annual_by_selecting_month(month)
            annual.select_year_range(1850, final_year)
            sst_anns.append(annual)

        pt.neat_plot(figure_dir, lsat_anns, f'lsat_{month:02d}_only.png', f'Global mean LSAT for {month_word}')

        pt.neat_plot(figure_dir, sst_anns, f'sst_{month:02d}_only.png', f'Global mean SST for {month_word}')

        pt.neat_plot(figure_dir, anns, f'{month:02d}_only.png', f'Global Mean Temperature for {month_word} ($\degree$C)')
        pt.dark_plot(figure_dir, anns, f'dark_{month:02d}_only.png', f'Global Mean Temperature for {month_word} ($\degree$C)')

        print()
        print(f"Single month ({month_word}) statistics")
        utils.run_the_numbers(anns, final_year, f'{month:02d}_only_stats', report_dir)

