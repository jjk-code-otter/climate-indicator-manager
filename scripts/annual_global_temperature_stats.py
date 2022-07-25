"""
This script calculates various statistics of global mean temperatures using annual, five-year and ten-year
averages. It also makes plots of these data in a variety of styles.
"""
from pathlib import Path
import numpy as np
import logging

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
    fdata_dir = project_dir / "Formatted_Data"
    figure_dir = project_dir / 'Figures'
    log_dir = project_dir / 'Logs'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

    logging.basicConfig(filename=log_dir / 'example.log',
                        filemode='w', level=logging.INFO)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    # some global temperature data sets are annual only, others are monthly so need to read these separately
    ann_archive = archive.select({'variable': 'tas',
                                  'type': 'timeseries',
                                  'time_resolution': 'annual',
                                  'name': [  # 'NOAA Interim',
                                      'Kadow IPCC',
                                      # 'Berkeley IPCC',
                                      'NOAA Interim IPCC']})

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
    ann_datasets = ann_archive.read_datasets(data_dir)

    lsat_datasets = lsat_archive.read_datasets(data_dir)
    sst_datasets = sst_archive.read_datasets(data_dir)

    anns = []
    for ds in all_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        annual.add_offset(0.69)
        annual.manually_set_baseline(1850, 1900)
        annual.select_year_range(1850, final_year)
        anns.append(annual)
        annual.write_csv(fdata_dir / f"{annual.metadata['name']}_{annual.metadata['variable']}.csv")

    for ds in ann_datasets:
        ds.rebaseline(1981, 2010)
        ds.add_offset(0.69)
        ds.manually_set_baseline(1850, 1900)
        ds.select_year_range(1850, final_year)
        anns.append(ds)
        ds.write_csv(fdata_dir / f"{ds.metadata['name']}_{ds.metadata['variable']}.csv")

    lsat_anns = []
    for ds in lsat_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        annual.select_year_range(1850, final_year)
        lsat_anns.append(annual)

    sst_anns = []
    for ds in sst_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        annual.select_year_range(1850, final_year)
        sst_anns.append(annual)

    pt.neat_plot(figure_dir, lsat_anns, 'annual_lsat.png', 'Global mean LSAT')

    pt.neat_plot(figure_dir, sst_anns, 'annual_sst.png', 'Global mean SST')

    pt.neat_plot(figure_dir, anns, 'annual.png', 'Global Mean Temperature Difference ($\degree$C)')
    pt.dark_plot(figure_dir, anns, 'annualdark.png', 'Global Mean Temperature Difference ($\degree$C)')

    print()
    print("Single year statistics")
    utils.run_the_numbers(anns, final_year, 'annual_stats', report_dir)

