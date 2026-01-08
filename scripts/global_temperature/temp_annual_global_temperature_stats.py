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
import copy
from pathlib import Path
import os
import logging

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt
import climind.stats.utils as utils

from climind.data_types.timeseries import make_combined_series

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

if __name__ == "__main__":

    final_year = 2025

    project_dir = DATA_DIR / "ManagedData"
    ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    METADATA_DIR = (ROOT_DIR / "..").resolve() / "climind" / "metadata_files"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    fdata_dir = project_dir / "Formatted_Data"
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
                                  'name': [ #'CMST v3'
                                      #'ClimTraceGMST' # 'NOAA Interim',
                                      # 'Kadow IPCC',
                                      # 'Berkeley IPCC',
                                      # 'NOAA Interim IPCC'
                                      # 'GETQUOCS'
                                  ]})

    ts_archive = archive.select({'variable': 'tas',
                                 'type': 'timeseries',
                                 'name': ['tempNOAA', 'tempGISTEMP', 'tempERA5', 'tempJRA3Q', 'tempBerkeley', 'tempHadCRUT5', 'tempDCENT', 'CMST v3'],
                                 'time_resolution': 'monthly'})


    all_datasets = ts_archive.read_datasets(data_dir)
    ann_datasets = ann_archive.read_datasets(data_dir)
    alt_datasets = ts_archive.read_datasets(data_dir)

    all_8110_datasets = []
    all_annual_datasets = []
    for ds in all_datasets:
        #ds.change_end_month(2025, 8)
        print(ds.get_start_and_end_dates())

        ds.rebaseline(1981, 2010)
        pt.wave_plot(figure_dir, ds, f"temp_wave_{ds.metadata['name']}.png")
        pt.rising_tide_plot(figure_dir, ds, f"temp_rising_tide_{ds.metadata['name']}.png")

        annual8110 = ds.make_annual()
        all_8110_datasets.append(annual8110)
        a = annual8110.time_average(1850, 1900)
        b = annual8110.time_average(2025, 2025)
        print(f"{annual8110.metadata['display_name']} {a - b:.2f}")

        annual = ds.make_annual()
        annual.add_offset(0.69)
        annual.manually_set_baseline(1850, 1900)
        annual.select_year_range(1850, final_year)
        all_annual_datasets.append(annual)
        annual.write_csv(fdata_dir / f"{annual.metadata['name']}_{annual.metadata['variable']}.csv")


    all_datasets_b = ts_archive.read_datasets(data_dir)
    all_8110_monthly = []
    all_running_monthly = []
    for ds in all_datasets_b:
        ds.rebaseline(1981, 2010)
        all_8110_monthly.append(ds)
        ds2 = copy.deepcopy(ds)
        ds2 = ds2.running_mean(12)
        all_running_monthly.append(ds2)

    pt.rising_tide_multiple_plot(figure_dir, all_8110_monthly, "temp_rising_multiple.png", "")
    pt.rising_tide_multiple_plot(figure_dir, all_running_monthly, "temp_rising_running_multiple.png", "")
    pt.wave_multiple_plot(figure_dir, all_8110_monthly, "temp_wave_multiple.png", "")

    all_datasets_b = ts_archive.read_datasets(data_dir)
    all_9120_datasets = []
    for ds in all_datasets_b:
        ds.rebaseline(1991, 2020)
        annual9120 = ds.make_annual()
        all_9120_datasets.append(annual9120)

    all_datasets_b = ts_archive.read_datasets(data_dir)
    all_6190_datasets = []
    for ds in all_datasets_b:
        ds.rebaseline(1961, 1990)
        annual6190 = ds.make_annual()
        all_6190_datasets.append(annual6190)

    # Switch order of operations
    all_alt_datasets = []
    for ds in alt_datasets:
        annual = ds.make_annual()
        annual.rebaseline(1981, 2010)
        annual.add_offset(0.69)
        annual.manually_set_baseline(1850, 1900)
        annual.select_year_range(1850, final_year)
        all_alt_datasets.append(annual)

    # Make the combined series by taking the mean of the series
    combined = make_combined_series(all_annual_datasets)
    combined.write_csv(fdata_dir / "temp_combined_global_mean_temperature.csv")

    for ds in ann_datasets:
        ds.rebaseline(1981, 2010)
        ds.add_offset(0.69)
        ds.manually_set_baseline(1850, 1900)
        ds.select_year_range(1850, final_year)
        all_annual_datasets.append(ds)
        ds.write_csv(fdata_dir / f"{ds.metadata['name']}_{ds.metadata['variable']}.csv")


    pt.wmo_plot(figure_dir, all_annual_datasets, 'temp_annual.png', r'Global Mean Temperature Difference ($\degree$C)')

    pt.records_plot(figure_dir, all_annual_datasets, 'temp_record_margins.png', 'Record margins')

    print()
    print("Single year statistics")
    utils.run_the_numbers(all_annual_datasets, final_year, 'temp_annual_stats', report_dir)
    utils.run_the_numbers(all_8110_datasets, final_year, 'temp_annual_stats_8110', report_dir, ipcc_unc=False)
    utils.run_the_numbers(all_9120_datasets, final_year, 'temp_annual_stats_9120', report_dir, ipcc_unc=False)
    utils.run_the_numbers(all_6190_datasets, final_year, 'temp_annual_stats_6190', report_dir, ipcc_unc=False)

    utils.run_the_numbers(all_alt_datasets, final_year, 'temp_alt_stats', report_dir)
