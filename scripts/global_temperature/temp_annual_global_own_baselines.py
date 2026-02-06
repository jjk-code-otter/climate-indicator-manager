#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2023 John Kennedy
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

    ts_archive = archive.select({'variable': 'tas',
                                 'type': 'timeseries',
                                 'name': [
                                     'tempNOAA', 'tempBerkeley',
                                     'tempHadCRUT5', 'tempDCENT',
                                     'tempCMST', 'CMA_GMST',
                                     'Calvert 2024',
                                     'GloSAT',
                                     'tempGISTEMP',
                                     'COBE-STEMP3',
                                     'Kadow'
                                 ],
                                 'time_resolution': 'monthly'})

    all_datasets = ts_archive.read_datasets(data_dir)

    all_8110_datasets = []
    all_annual_datasets = []
    tens = []
    twentys = []
    for ds in all_datasets:
        ds.rebaseline(1850, 1900)
        pt.wave_plot(figure_dir, ds, f"temp_own_wave_{ds.metadata['name']}.png")
        pt.rising_tide_plot(figure_dir, ds, f"temp_own_rising_tide_{ds.metadata['name']}.png")

        annual8110 = ds.make_annual()
        annual8110.select_year_range(1850, final_year)
        all_8110_datasets.append(annual8110)
        tens.append(annual8110.running_mean(10))
        twentys.append(annual8110.running_mean(20))

        annual = ds.make_annual()
        annual.select_year_range(1850, final_year)
        all_annual_datasets.append(annual)

    all_datasets_b = ts_archive.read_datasets(data_dir)
    all_8110_monthly = []
    for ds in all_datasets_b:
        ds.rebaseline(1850, 1900)
        all_8110_monthly.append(ds)

    threes = []
    for ds in all_8110_datasets:
        threes.append(ds.running_mean(3))

    pt.rising_tide_multiple_plot(figure_dir, all_8110_monthly, "temp_own_rising_multiple.png", '')
    pt.wave_multiple_plot(figure_dir, all_8110_monthly, "temp_own_wave_multiple.png", '')

    pt.wmo_plot(figure_dir, all_8110_datasets, 'temp_own_annual.png', 'Global mean temperature')
    pt.wmo_plot(figure_dir, threes, 'temp_own_threes.png', '3-year Global mean temperature')

    print()
    print("Single year statistics")
    utils.run_the_numbers(all_annual_datasets, final_year, 'temp_own_annual_stats', report_dir)
    utils.run_the_numbers(all_8110_datasets, final_year, 'temp_own_annual_stats_8110', report_dir, ipcc_unc=False)
    utils.run_the_numbers(threes, final_year, 'temp_own_threeyear_stats', report_dir)
    utils.run_the_numbers(tens, final_year, 'temp_own_tenyear_stats', report_dir)
    utils.run_the_numbers(twentys, final_year, 'temp_own_twentyyear_stats', report_dir)
