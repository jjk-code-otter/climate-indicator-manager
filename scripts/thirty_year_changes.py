#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2024 John Kennedy
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

    final_year = 2023
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

    all_details = []

    all_details.append({'variable': 'tas', 'type': 'timeseries', 'time_resolution': 'monthly', 'name': ['HadCRUT5', 'GISTEMP', 'NOAA Interim', 'ERA5', 'JRA-55', 'Berkeley Earth']})
    all_details.append({'variable': 'sst', 'type': 'timeseries', 'time_resolution': 'monthly'})
    all_details.append({'variable': 'lsat', 'type': 'timeseries', 'time_resolution': 'monthly'})
    all_details.append({'variable': 'co2', 'type': 'timeseries', 'time_resolution': 'monthly'})
    all_details.append({'variable': 'ch4', 'type': 'timeseries', 'time_resolution': 'monthly'})
    all_details.append({'variable': 'n2o', 'type': 'timeseries', 'time_resolution': 'monthly'})
    all_details.append({'variable': 'sealevel', 'type': 'timeseries', 'time_resolution': 'monthly'})
    all_details.append({'variable': 'arctic_ice', 'type': 'timeseries', 'time_resolution': 'monthly'})
    all_details.append({'variable': 'antarctic_ice', 'type': 'timeseries', 'time_resolution': 'monthly'})
    all_details.append({'variable': 'glacier', 'type': 'timeseries', 'time_resolution': 'annual'})

    for details in all_details:

        ts_archive = archive.select(details)

        all_datasets = ts_archive.read_datasets(data_dir)

        all_annual_datasets = []
        tens = []
        for ds in all_datasets:
            if ds.metadata['variable'] in ['tas', 'sst', 'lsat']:
                ds.rebaseline(1981, 2010)
                annual = ds.make_annual()
                annual.select_year_range(1850, final_year)
                all_annual_datasets.append(annual)
                tens.append(annual.running_mean(10))
            if ds.metadata['variable'] in ['co2', 'ch4', 'n2o']:
                annual = ds.make_annual()
                annual.select_year_range(1850, final_year)
                all_annual_datasets.append(annual)
                tens.append(annual.running_mean(10))
            if ds.metadata['variable'] in ['sealevel']:
                monthly = ds.make_monthly()
                annual = monthly.make_annual()
                annual.select_year_range(1850, final_year)
                all_annual_datasets.append(annual)
                tens.append(annual.running_mean(10))
            if ds.metadata['variable'] in ['arctic_ice']:
                annual = ds.make_annual_by_selecting_month(9)
                annual.select_year_range(1850, final_year)
                all_annual_datasets.append(annual)
                tens.append(annual.running_mean(10))
            if ds.metadata['variable'] in ['antarctic_ice']:
                annual = ds.make_annual_by_selecting_month(2)
                annual.select_year_range(1850, final_year)
                all_annual_datasets.append(annual)
                tens.append(annual.running_mean(10))
            if ds.metadata['variable'] in ['glacier']:
                ds.select_year_range(1850, final_year)
                all_annual_datasets.append(ds)
                tens.append(ds.running_mean(10))

        for ds in tens:
            print(ds.metadata['variable'])
            print(ds.metadata['name'])
            if 'WDCGG' in ds.metadata['display_name']:
                print(f'2013-2022 {ds.get_value_from_year(2022):.2f} 1993-2002 {ds.get_value_from_year(2002):.2f}')
                print(f'{ds.get_value_from_year(2022)-ds.get_value_from_year(2002):.2f}')
            else:
                print(f'2014-2023 {ds.get_value_from_year(2023):.2f} 1993-2002 {ds.get_value_from_year(2002):.2f}')
                print(f'{ds.get_value_from_year(2023) - ds.get_value_from_year(2002):.2f}')


