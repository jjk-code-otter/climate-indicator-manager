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
import numpy as np

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt
import climind.stats.utils as utils

from climind.data_types.timeseries import make_combined_series

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

final_year = 2023

project_dir = DATA_DIR / "ManagedData"
metadata_dir = METADATA_DIR

data_dir = project_dir / "Data"
fdata_dir = project_dir / "Formatted_Data"
figure_dir = project_dir / 'Figures'
log_dir = project_dir / 'Logs'
report_dir = project_dir / 'Reports'
report_dir.mkdir(exist_ok=True)

# Read in the whole archive then select the various subsets needed here
archive = dm.DataArchive.from_directory(metadata_dir)

ts_archive = archive.select({'variable': 'tas',
                             'type': 'timeseries',
                             'name': [
                                 'HadCRUT5', 'NOAA Interim', 'Berkeley Earth', 'Kadow', 'Berkeley IPCC'
                             ],
                             'time_resolution': 'monthly'})

all_long_datasets = ts_archive.read_datasets(data_dir)

all_ann = []
all_offsets = []
all_names = []
for ds in all_long_datasets:
    ds.rebaseline(1850, 1900)
    ann = ds.make_annual()

    ann2 = copy.deepcopy(ann)
    all_ann.append(ann2)

    ann = ann.select_year_range(1981, 2010)
    val = np.mean(ann.df.data)
    all_offsets.append(val)
    all_names.append(ds.metadata['name'])
    print(ds.metadata['display_name'], val)

print(all_offsets)

print()

pt.neat_plot(figure_dir, all_ann, 'individual_offset_annual.png', 'Global mean temperature')

for i, offset in enumerate(all_offsets):

    ts_archive = archive.select({'variable': 'tas',
                                 'type': 'timeseries',
                                 'name': [
                                     'HadCRUT5', 'NOAA Interim', 'Berkeley Earth',
                                     'Kadow', 'GISTEMP', 'ERA5', 'JRA-55'
                                 ],
                                 'time_resolution': 'monthly'})

    all_datasets = ts_archive.read_datasets(data_dir)

    all_annual_datasets = []
    for ds in all_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        annual.add_offset(offset)
        annual.manually_set_baseline(1850, 1900)
        annual.select_year_range(1850, final_year)
        all_annual_datasets.append(annual)

    utils.run_the_numbers(all_annual_datasets, final_year, f'offset{all_names[i]}_stats', report_dir)
    pt.neat_plot(figure_dir, all_annual_datasets, f'annual_{all_names[i]}_offset.png',
                 f'{all_names[i]} baseline', yrange=[-0.5, 1.6])

# Compare the two Berkeley datasets
ts_archive = archive.select({'variable': 'tas',
                             'type': 'timeseries',
                             'name': ['Berkeley Earth', 'Berkeley IPCC'],
                             'time_resolution': 'monthly'})

all_long_datasets = ts_archive.read_datasets(data_dir)
all_ann = []
for ds in all_long_datasets:
    ds.rebaseline(1850, 1900)
    ann = ds.make_annual()
    all_ann.append(ann)

pt.neat_plot(figure_dir, all_ann, 'compare_berkeleys.png', 'Berkeley vs Berkeley IPCC')

ts_archive = archive.select({'variable': 'tas',
                             'type': 'timeseries',
                             'name': ['HadCRUT5', 'NOAA Interim', 'Berkeley Earth', 'Kadow'],
                             'time_resolution': 'monthly'})
all_datasets = ts_archive.read_datasets(data_dir)
all_annual_datasets = []
for ds in all_datasets:
    ds.rebaseline(1850, 1900)
    annual = ds.make_annual()
    annual = annual.running_mean(20, centred=True)
    all_annual_datasets.append(annual)
pt.neat_plot(figure_dir, all_annual_datasets, f'baselines_multiyear.png',
             f'Multi-year global mean temperature')
