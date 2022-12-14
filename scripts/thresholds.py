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
import logging

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

    ts_archive = archive.select({'variable': 'tas',
                                 'type': 'timeseries',
                                 'time_resolution': 'monthly',
                                 'name': 'HadCRUT5'})

    all_datasets = ts_archive.read_datasets(data_dir)

    all_annual_datasets = []
    for ds in all_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        annual.add_offset(0.69)
        annual.manually_set_baseline(1850, 1900)
        annual.select_year_range(1850, final_year)
        all_annual_datasets.append(annual)

    tens = []

    for ds in all_annual_datasets:
        copy_ds = copy.deepcopy(ds)
        copy_ds.metadata['display_name'] = 'HadCRUT5 10-year'
        copy_ds.metadata['colour'] = '#a6cee3'
        tens.append(copy_ds.running_mean(10, centred=True))

        copy_ds = copy.deepcopy(ds)
        copy_ds.metadata['display_name'] = 'HadCRUT5 5-year'
        copy_ds.metadata['colour'] = '#b2df8a'
        tens.append(copy_ds.running_mean(5, centred=True))

        copy_ds = copy.deepcopy(ds)
        copy_ds.metadata['display_name'] = 'HadCRUT5 20-year'
        copy_ds.metadata['colour'] = '#1f78b4'
        tens.append(copy_ds.running_mean(20, centred=True))

    pt.neat_plot(figure_dir, tens, 'centred.png', r'Global Mean Temperature Difference ($\degree$C))')
