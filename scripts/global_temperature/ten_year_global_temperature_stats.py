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

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt
import climind.stats.utils as utils

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

if __name__ == "__main__":

    final_year = 2025
    last_digit = final_year - 2020

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

    # some global temperature data sets are annual only, others are monthly so need to read these separately
    ann_archive = archive.select({'variable': 'tas',
                                  'type': 'timeseries',
                                  'time_resolution': 'annual',
                                  'name': [  # 'NOAA Interim',
                                      #'Kadow IPCC',
                                      # 'Berkeley IPCC',
                                       #  'NOAA Interim IPCC'
                                  ]})

    ts_archive = archive.select({'variable': 'tas',
                                 'type': 'timeseries',
                                 'time_resolution': 'monthly',
                                 'name': ['HadCRUT5', 'GISTEMP', 'NOAA v6', 'ERA5', 'JRA-3Q', 'Berkeley Earth']})

    ipcc_archive = archive.select({'variable': 'tas',
                                 'type': 'timeseries',
                                 'time_resolution': 'monthly',
                                 'name': ['HadCRUT5', 'NOAA v6', 'Kadow', 'Berkeley IPCC']})

    sst_archive = archive.select({'variable': 'sst',
                                  'type': 'timeseries',
                                  'time_resolution': 'monthly'})

    lsat_archive = archive.select({'variable': 'lsat',
                                   'type': 'timeseries',
                                   'time_resolution': 'monthly'})

    lsat_ann_archive = archive.select({'variable': 'lsat',
                                       'type': 'timeseries',
                                       'time_resolution': 'annual',
                                       'name': []})

    all_datasets = ts_archive.read_datasets(data_dir)
    ipcc_datasets = ipcc_archive.read_datasets(data_dir)
    ann_datasets = ann_archive.read_datasets(data_dir)

    lsat_datasets = lsat_archive.read_datasets(data_dir)
    lsat_ann_datasets = lsat_ann_archive.read_datasets(data_dir)
    sst_datasets = sst_archive.read_datasets(data_dir)

    all_annual_datasets = []
    for ds in all_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        annual.add_offset(0.69)
        annual.manually_set_baseline(1850, 1900)
        annual.select_year_range(1850, final_year)
        all_annual_datasets.append(annual)

    for ds in ann_datasets:
        ds.rebaseline(1981, 2010)
        ds.add_offset(0.69)
        ds.manually_set_baseline(1850, 1900)
        ds.select_year_range(1850, final_year)
        all_annual_datasets.append(ds)

    all_ipcc_datasets = []
    for ds in ipcc_datasets:
        ds.rebaseline(1850, 1900)
        annual = ds.make_annual()
        annual.select_year_range(1850, final_year)
        all_ipcc_datasets.append(annual)

    lsat_anns = []
    for ds in lsat_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        annual.select_year_range(1850, final_year)
        lsat_anns.append(annual)

    for ds in lsat_ann_datasets:
        ds.rebaseline(1981, 2010)
        ds.select_year_range(1850, final_year)
        lsat_anns.append(ds)

    sst_anns = []
    for ds in sst_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        annual.select_year_range(1850, final_year)
        sst_anns.append(annual)

    fives = []
    tens = []
    twenties = []
    thirties = []
    dtens = []

    ipcc_fives = []
    ipcc_tens = []
    ipcc_twenties = []
    ipcc_thirties = []
    ipcc_dtens = []

    sst_tens = []
    sst_dtens = []

    lsat_tens = []
    lsat_dtens = []

    for ds in all_annual_datasets:
        fives.append(ds.running_mean(5))
        tens.append(ds.running_mean(10))
        twenties.append(ds.running_mean(20))
        thirties.append(ds.running_mean(30))
        dtens.append(ds.running_mean(10).select_decade(last_digit))

    for ds in all_ipcc_datasets:
        ipcc_fives.append(ds.running_mean(5))
        ipcc_tens.append(ds.running_mean(10))
        ipcc_twenties.append(ds.running_mean(20))
        ipcc_thirties.append(ds.running_mean(30))
        ipcc_dtens.append(ds.running_mean(10).select_decade(last_digit))

    fdata_dir = project_dir / "Formatted_Data"
    for ds in dtens:
        ds.write_csv(fdata_dir / f"decadal_{ds.metadata['name']}_{ds.metadata['variable']}.csv")

    for ds in sst_anns:
        sst_tens.append(ds.running_mean(10))
        sst_dtens.append(ds.running_mean(10).select_decade(last_digit))
    for ds in lsat_anns:
        lsat_tens.append(ds.running_mean(10))
        lsat_dtens.append(ds.running_mean(10).select_decade(last_digit))

    pt.neat_plot(figure_dir, sst_tens, 'ten_sst.png', r'10-year Global Mean SST Difference ($\degree$C))')
    pt.neat_plot(figure_dir, lsat_tens, 'ten_lsat.png', r'10-year Global Mean LSAT Difference ($\degree$C))')
    pt.neat_plot(figure_dir, fives, 'five.png', r'5-year Global Mean Temperature Difference ($\degree$C))')
    pt.neat_plot(figure_dir, tens, 'ten.png', r'10-year Global Mean Temperature Difference ($\degree$C))')
    pt.neat_plot(figure_dir, twenties, 'twenty.png', r'20-year Global Mean Temperature Difference ($\degree$C))')
    pt.neat_plot(figure_dir, thirties, 'thirty.png', r'30-year Global Mean Temperature Difference ($\degree$C))')

    pt.neat_plot(figure_dir, ipcc_tens, 'ipcc_ten.png', r'10-year Global Mean Temperature Difference ($\degree$C))')
    pt.neat_plot(figure_dir, ipcc_twenties, 'ipcc_twenty.png', r'20-year Global Mean Temperature Difference ($\degree$C))')

    pt.decade_plot(figure_dir, sst_dtens, 'dten_sst.png',
                   r'10-year Global Mean SST Difference ($\degree$C))')
    pt.decade_plot(figure_dir, lsat_dtens, 'dten_lsat.png',
                   r'10-year Global Mean LSAT Difference ($\degree$C))')
    pt.decade_plot(figure_dir, dtens, 'dten.png',
                   r'10-year Global Mean Temperature Difference ($\degree$C))')

    utils.run_the_numbers(fives, final_year, 'fiveyear_stats', report_dir)
    utils.run_the_numbers(tens, final_year, 'tenyear_stats', report_dir)
    utils.run_the_numbers(lsat_tens, final_year, 'lsat_tenyear_stats', report_dir)
    utils.run_the_numbers(sst_tens, final_year, 'sst_tenyear_stats', report_dir)
    utils.run_the_numbers(twenties, final_year, 'twentyyear_stats', report_dir)
    utils.run_the_numbers(thirties, final_year, 'thirtyyear_stats', report_dir)

    utils.run_the_numbers(ipcc_tens, final_year, 'ipcc_tenyear_stats', report_dir)
    utils.run_the_numbers(ipcc_twenties, final_year, 'ipcc_twentyyear_stats', report_dir)
