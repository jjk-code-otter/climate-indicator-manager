#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2026 John Kennedy
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

import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

import climind.data_manager.processing as dm
from climind.config.config import DATA_DIR
from pathlib import Path
import os

STANDARD_PARAMETER_SET = {
    'axes.axisbelow': False,
    'axes.labelsize': 23,
    'xtick.labelsize': 23,
    'ytick.labelsize': 23,
    'axes.edgecolor': 'dimgrey',
    'axes.facecolor': 'None',

    'axes.grid.axis': 'y',
    'grid.color': 'lightgrey',
    'grid.alpha': 0.5,

    'axes.labelcolor': 'dimgrey',
    'axes.labelpad': 4,

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

wmo_standard_colors = [
                "#204e96",  # Main blue
                "#f5a729", "#7ab64a", "#23abd1",  # Secondary colours
                "#008F90", "#00AE4D", "#869519", "#98411E", "#A18972",  # Additional colours (natural shades)
                "#000000", "#000000", "#000000", "#000000", "#000000", "#000000"
            ]

project_dir = DATA_DIR / "ManagedData"
data_dir = project_dir / "Data"

ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
METADATA_DIR = (ROOT_DIR / "..").resolve() / "climind" / "metadata_files"

figure_dir = project_dir / 'Figures'

archive = dm.DataArchive.from_directory(METADATA_DIR)

print("ARCTIC")
ts_archive_nh = archive.select(
    {
        'type': 'timeseries',
        'variable': 'arctic_ice',
        'time_resolution': 'irregular',
        'name': ['NSIDC v4', 'JAXA NH', 'OSI SAF v2p3']
    }
)

ts_archive_sh = archive.select(
    {
        'type': 'timeseries',
        'variable': 'antarctic_ice',
        'time_resolution': 'irregular',
        'name': ['NSIDC v4 SH', 'JAXA SH', 'OSI SAF SH v2p3']
    }
)


all_datasets_nh = ts_archive_nh.read_datasets(data_dir)
all_datasets_sh = ts_archive_sh.read_datasets(data_dir)

sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

plt.figure(figsize=[16, 9])

for i, ds in enumerate(all_datasets_nh):
    ds = ds.select_year_range(1979,2025)
    df = ds.df
    annual_mean = df.groupby(['year'])['data'].mean()
    annual_min = df.groupby(['year'])['data'].min()
    annual_max = df.groupby(['year'])['data'].max()

    print(annual_mean)

    plt.plot(annual_mean, color=wmo_standard_colors[i])
    plt.plot(annual_min, linestyle='--', color=wmo_standard_colors[i])
    plt.plot(annual_max, linestyle='--', color=wmo_standard_colors[i])

sns.despine(right=True, top=True, left=True)
ylim = plt.gca().get_ylim()
yloc = ylim[1] + 0.005 * (ylim[1] - ylim[0])
full_title = "Arctic sea-ice extent (million km$^2$)"
subtitle='Annual mean, minimum and maximum'
plt.text(plt.gca().get_xlim()[0], yloc, subtitle, fontdict={'fontsize': 30})
plt.gca().set_title(full_title, pad=35, fontdict={'fontsize': 40}, loc='left')
plt.savefig(figure_dir / 'arctic_mean_min_max.png')
plt.savefig(figure_dir / 'arctic_mean_min_max.svg')
plt.close('all')

plt.figure(figsize=[16, 9])

for i, ds in enumerate(all_datasets_sh):
    ds = ds.select_year_range(1979,2025)
    df = ds.df
    annual_mean = df.groupby(['year'])['data'].mean()
    annual_min = df.groupby(['year'])['data'].min()
    annual_max = df.groupby(['year'])['data'].max()

    print(annual_mean)

    plt.plot(annual_mean, color=wmo_standard_colors[i])
    plt.plot(annual_min, linestyle='--', color=wmo_standard_colors[i])
    plt.plot(annual_max, linestyle='--', color=wmo_standard_colors[i])

sns.despine(right=True, top=True, left=True)
ylim = plt.gca().get_ylim()
yloc = ylim[1] + 0.005 * (ylim[1] - ylim[0])
full_title = "Antarctic sea-ice extent (million km$^2$)"
subtitle='Annual mean, minimum and maximum'
plt.text(plt.gca().get_xlim()[0], yloc, subtitle, fontdict={'fontsize': 30})
plt.gca().set_title(full_title, pad=35, fontdict={'fontsize': 40}, loc='left')
plt.savefig(figure_dir / 'antarctic_mean_min_max.png')
plt.savefig(figure_dir / 'antarctic_mean_min_max.svg')
plt.close('all')