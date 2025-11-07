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

    final_year = 2076

    project_dir = DATA_DIR / "ManagedData"
    ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    METADATA_DIR = (ROOT_DIR / "..").resolve() / "climind" / "metadata_files"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    fdata_dir = project_dir / "Formatted_Data"
    figure_dir = project_dir / 'Figures'
    log_dir = project_dir / 'Logs'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    # some global temperature data sets are annual only, others are monthly so need to read these separately
    ts_archive = archive.select({
        'variable': 'tas',
        'type': 'timeseries',
        'time_resolution': 'monthly',
        'origin': 'model',
        'name': 'AWI-CM-1-1-MR',
        'scenario': 'ssp126'
    })

    ts_archive = archive.select({
        'variable': 'tas',
        'type': 'timeseries',
        'time_resolution': 'monthly',
        'origin': 'obs',
        'name': 'HadCRUT5'
    })

    all_datasets = ts_archive.read_datasets(data_dir)

    all_annual_datasets = []
    all_30s = []
    all_20s = []
    all_10s = []
    for ds in all_datasets:
        ds.rebaseline(1850, 1900)
        annual = ds.make_annual()
        annual.select_year_range(1850, final_year)
        all_annual_datasets.append(annual)
        all_30s.append(annual.running_trend(30))

        all_20s.append(annual)

        all_20s.append(annual.running_trend(30))
        all_20s[-1].metadata['display_name'] = '30-year trend endpoint'
        all_20s[-1].metadata['colour'] = 'orange'

        all_20s.append(annual.running_mean(30, centred=True))
        all_20s[-1].metadata['display_name'] = '30-year moving average'
        all_20s[-1].metadata['colour'] = 'lightblue'

        all_20s.append(annual.running_mean(20, centred=True))
        all_20s[-1].metadata['display_name'] = '20-year moving average'
        all_20s[-1].metadata['colour'] = 'black'
        all_20s[-1].metadata['zpos'] = 100

        all_20s.append(annual.running_mean(10, centred=True))
        all_20s[-1].metadata['display_name'] = '10-year moving average'
        all_20s[-1].metadata['colour'] = 'pink'

        npoints = 20
        all_20s.append(annual.running_lowess(number_of_points=npoints))
        all_20s[-1].metadata['display_name'] = f'Running lowess {npoints}-point'
        all_20s[-1].metadata['colour'] = 'lightgreen'

        npoints = 20
        all_20s.append(annual.lowess(number_of_points=npoints))
        all_20s[-1].metadata['display_name'] = f'Lowess {npoints}-point'
        all_20s[-1].metadata['colour'] = 'purple'

        all_10s.append(annual.running_mean(10, centred=True))

    common_title = r'Global Mean Temperature Difference ($\degree$C)'
    pt.neat_plot(figure_dir, all_annual_datasets, 'model_annual.png', common_title)
    pt.neat_plot(figure_dir, all_30s, 'model_30s.png', common_title)
    pt.neat_plot(figure_dir, all_20s, 'model_20s.png', common_title)
    pt.neat_plot(figure_dir, all_10s, 'model_10s.png', common_title)


