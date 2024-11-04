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

from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
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

archive = dm.DataArchive.from_directory(metadata_dir)
archive = archive.select({'type': 'timeseries'})

co2_archive = archive.select({'variable': 'co2', 'time_resolution':'monthly', 'display_name': 'WDCGG'})
ch4_archive = archive.select({'variable': 'ch4', 'time_resolution':'monthly', 'display_name': 'WDCGG'})
n2o_archive = archive.select({'variable': 'n2o', 'time_resolution':'monthly', 'display_name': 'WDCGG'})

co2 = co2_archive.read_datasets(data_dir)
ch4 = ch4_archive.read_datasets(data_dir)
n2o = n2o_archive.read_datasets(data_dir)

co2_rate_archive = archive.select({'variable': 'co2rate', 'time_resolution':'annual', 'display_name': 'WDCGG'})
ch4_rate_archive = archive.select({'variable': 'ch4rate', 'time_resolution':'annual', 'display_name': 'WDCGG'})
n2o_rate_archive = archive.select({'variable': 'n2orate', 'time_resolution':'annual', 'display_name': 'WDCGG'})

co2_rate = co2_rate_archive.read_datasets(data_dir)
ch4_rate = ch4_rate_archive.read_datasets(data_dir)
n2o_rate = n2o_rate_archive.read_datasets(data_dir)

# PLOT
STANDARD_PARAMETER_SET = {
    'axes.axisbelow': False,
    'axes.labelsize': 10,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'axes.edgecolor': 'lightgrey',
    'axes.facecolor': 'None',

    'axes.grid.axis': 'both',
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

fig, axs = plt.subplots(2, 3, sharex=True)
fig.set_size_inches(16, 8)

for ds in co2:
    axs[0][0].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[0][0].set_yticks(np.arange(340, 430, 20))
axs[0][0].tick_params(labelbottom=True, length=0)
axs[0][0].set_title('(a) Carbon Dioxide concentration (ppm)', loc='left')
axs[0][0].set_ylabel('ppm')

for ds in co2_rate:
    axs[1][0].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[1][0].set_yticks(np.arange(0.0, 4.1, 1.0))
axs[1][0].tick_params(labelbottom=True, length=0)
axs[1][0].set_title('(d) Carbon Dioxide growth rate (ppm/year)', loc='left')
axs[1][0].set_ylabel('ppm/year')

for ds in ch4:
    axs[0][1].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[0][1].set_yticks(np.arange(1650.0, 1960.0, 50.))
axs[0][1].tick_params(labelbottom=True, length=0)
axs[0][1].set_title('(b) Methane concentration (ppb)', loc='left')
axs[0][1].set_ylabel('ppb')

for ds in ch4_rate:
    axs[1][1].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[1][1].set_yticks(np.arange(-5.0, 21.0, 5.0))
axs[1][1].tick_params(labelbottom=True, length=0)
axs[1][1].set_title('(e) Methane growth rate (ppb/year)', loc='left')
axs[1][1].set_ylabel('ppb/year')

for ds in n2o:
    axs[0][2].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[0][2].set_yticks(np.arange(300.0, 350.0, 10.))
axs[0][2].tick_params(labelbottom=True, length=0)
axs[0][2].set_title('(c) Nitrous Oxide concentration (ppb)', loc='left')
axs[0][2].set_ylabel('ppb')

for ds in n2o_rate:
    axs[1][2].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[1][2].set_yticks(np.arange(0.0, 1.6, 0.5))
axs[1][2].tick_params(labelbottom=True, length=0)
axs[1][2].set_title('(f) Nitrous Oxide growth rate (ppb/year)', loc='left')
axs[1][2].set_ylabel('ppb/year')

axs[0][0].set_xticks(np.arange(1990, 2030, 10))
axs[1][0].set_xticks(np.arange(1990, 2030, 10))

axs[0][1].set_xticks(np.arange(1990, 2030, 10))
axs[1][1].set_xticks(np.arange(1990, 2030, 10))

axs[0][2].set_xticks(np.arange(1990, 2030, 10))
axs[1][2].set_xticks(np.arange(1990, 2030, 10))

plt.subplots_adjust(hspace=0.3)

sns.despine(right=True, top=True, left=True, bottom=True)

plt.savefig(figure_dir / "greenhouse_gases.png", dpi=300)
plt.savefig(figure_dir / "greenhouse_gases.svg", dpi=300)
plt.savefig(figure_dir / "greenhouse_gases.pdf", dpi=300)
plt.close()

