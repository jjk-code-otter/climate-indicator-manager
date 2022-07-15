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

    final_year = 2020

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
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
        annual.select_year_range(1850, final_year)
        anns.append(annual)

    for ds in ann_datasets:
        ds.rebaseline(1981, 2010)
        ds.add_offset(0.69)
        ds.select_year_range(1850, final_year)
        anns.append(ds)

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

    tens = []
    dtens = []

    sst_tens = []
    sst_dtens = []

    lsat_tens = []
    lsat_dtens = []

    for ds in anns:
        tens.append(ds.running_mean(10))
        dtens.append(ds.running_mean(10).select_decade())

    for ds in sst_anns:
        sst_tens.append(ds.running_mean(10))
        sst_dtens.append(ds.running_mean(10).select_decade())
    for ds in lsat_anns:
        lsat_tens.append(ds.running_mean(10))
        lsat_dtens.append(ds.running_mean(10).select_decade())

    pt.neat_plot(figure_dir, sst_tens, 'ten_sst.png', '10-year Global Mean SST Difference ($\degree$C))')
    pt.neat_plot(figure_dir, lsat_tens, 'ten_lsat.png', '10-year Global Mean LSAT Difference ($\degree$C))')
    pt.neat_plot(figure_dir, tens, 'ten.png', '10-year Global Mean Temperature Difference ($\degree$C))')

    pt.decade_plot(figure_dir, sst_dtens, 'dten_sst.png',
                   '10-year Global Mean SST Difference ($\degree$C))',
                   'Compared to 1981-2010 average')
    pt.decade_plot(figure_dir, lsat_dtens, 'dten_lsat.png',
                   '10-year Global Mean LSAT Difference ($\degree$C))',
                   'Compared to 1981-2010 average')
    pt.decade_plot(figure_dir, dtens, 'dten.png',
                   '10-year Global Mean Temperature Difference ($\degree$C))',
                   'Compared to 1850-1900 average')

    utils.run_the_numbers(tens, final_year, 'tenyear_stats', report_dir)
