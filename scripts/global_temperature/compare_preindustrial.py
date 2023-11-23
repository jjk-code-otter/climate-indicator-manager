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
import matplotlib.pyplot as plt

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

# Just the four long datasets
ts_archive = archive.select({'variable': 'tas',
                             'type': 'timeseries',
                             'name': ['HadCRUT5', 'NOAA Interim', 'Berkeley Earth', 'Kadow'],
                             'time_resolution': 'monthly'})
all_datasets = ts_archive.read_datasets(data_dir)

all_annual_datasets = []
all_climatologies = []
all_names = []
for ds in all_datasets:
    all_names.append(ds.metadata['display_name'])
    ds.rebaseline(1991, 2020)
    all_climatologies.append(ds.calculate_climatology(1850, 1900))
    ds.rebaseline(1850, 1900)
    annual = ds.make_annual()
    annual = annual.running_mean(20, centred=True)
    all_annual_datasets.append(annual)

pt.neat_plot(figure_dir, all_annual_datasets, f'baselines_multiyear.png',
             f'Multi-year global mean temperature')

daily_offsets = []
with open(data_dir / 'ERA5' / 'era5_daily_sfc_temp_global_anomalies_with_preindustrial_1940-2023.csv', 'r') as f:
    for _ in range(18):
        f.readline()
    for _ in range(365):
        line = f.readline()
        columns = line.split(',')
        split_date = columns[0].split('-')
        daily_offsets.append(float(columns[3]) - float(columns[4]))

import seaborn as sns

STANDARD_PARAMETER_SET = {
    'axes.axisbelow': False,
    'axes.labelsize': 20,
    'xtick.labelsize': 15,
    'ytick.labelsize': 15,
    'axes.edgecolor': 'lightgrey',
    'axes.facecolor': 'None',

    'axes.grid.axis': 'y',
    'grid.color': 'lightgrey',
    'grid.alpha': 0.5,

    'axes.labelcolor': 'dimgrey',

    'axes.spines.left': False,
    'axes.spines.right': False,
    'axes.spines.top': False,

    'figure.facecolor': 'white',
    'lines.solid_capstyle': 'round',
    'patch.edgecolor': 'w',
    'patch.force_edgecolor': True,
    'text.color': 'dimgrey',

    'xtick.bottom': True,
    'xtick.color': 'dimgrey',
    'xtick.direction': 'out',
    'xtick.top': False,
    'xtick.labelbottom': True,

    'ytick.major.width': 0.4,
    'ytick.color': 'dimgrey',
    'ytick.direction': 'out',
    'ytick.left': False,
    'ytick.right': False
}
sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)
plt.figure(figsize=(16, 9))
colors = [all_datasets[i].metadata['colour'] for i in range(4)]
for i, c in enumerate(all_climatologies):
    plt.plot(range(1, 13), c.climatology, label=all_names[i], linewidth=3, color=colors[i])

b = np.array([-0.99, -1.02, -1.03, -0.97, -0.88, -0.84, -0.78, -0.86, -0.92, -0.91, -0.94, -0.97])
h = np.array([-0.97, -1.00, -1.03, -0.97, -0.88, -0.82, -0.77, -0.79, -0.79, -0.87, -0.97, -0.94])
n = np.array([-0.83, -0.84, -0.87, -0.84, -0.76, -0.76, -0.72, -0.73, -0.77, -0.81, -0.83, -0.80])

plt.plot(range(1, 13), b, label='C3S Berkeley', linestyle='--', linewidth=3, color='#009e73')
plt.plot(range(1, 13), h, label='C3S HadCRUT5', linestyle='--', linewidth=3, color='dimgrey')
plt.plot(range(1, 13), n, label='C3S NOAA', linestyle='--', linewidth=3, color='#e69f00')

plt.plot(range(1,13), (b+h+n)/3., label='C3S average', linestyle='--', linewidth=3, color='#AA0000')
plt.plot(np.arange(0.5, 12.4999, 12. / 365.), daily_offsets, linestyle=':', linewidth=3, color="#AA0000", label='C3S daily')

plt.gca().set_xlim(-0.5, 12.5)
plt.gca().set_ylim(-1.12, -0.69)

plt.gca().set_xlabel('Month')
plt.gca().set_ylabel('Offset')

plt.gca().set_title('Monthly offsets 1850-1900 vs 1991-2020', loc='left', fontsize=24)

plt.legend()

plt.savefig(figure_dir / 'seasonal_cycle_offset.png')
plt.savefig(figure_dir / 'seasonal_cycle_offset.svg')
plt.close('all')
