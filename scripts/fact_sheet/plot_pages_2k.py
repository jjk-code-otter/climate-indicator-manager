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

import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def binomcoeffs(n):
    return (np.poly1d([0.5, 0.5]) ** n).coeffs


STANDARD_PARAMETER_SET = {
    'axes.axisbelow': False,
    'axes.labelsize': 23,
    'xtick.labelsize': 23,
    'ytick.labelsize': 23,
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

data_dir_env = os.getenv('DATADIR')
DATA_DIR = Path(data_dir_env) / 'Proxies'

filenames = ['BHM.txt', 'CPS.txt', 'DA.txt', 'M08.txt', 'OIE.txt', 'PAI.txt', 'PCR.txt']

data_list = []
lows = []
highs = []

for file in filenames:
    this_data_set = np.loadtxt(DATA_DIR / file, dtype=None, skiprows=1, delimiter='\t')
    time = this_data_set[:, 0]
    this_data_set = this_data_set[:, 1:]

    # Smooth the data by convolving with a binomial filter
    this_data_set = np.apply_along_axis(np.convolve, axis=0, arr=this_data_set, v=binomcoeffs(21), mode='valid')

    # Get summary stats from the 1000 ensemble members for this model
    this_mean = np.mean(this_data_set, axis=1)
    this_low = np.quantile(this_data_set, 0.05, axis=1)
    this_high = np.quantile(this_data_set, 0.95, axis=1)

    # Subtract 1850-1900 climatology
    time = time[10:-11]
    index = (time >= 1850) & (time <= 1900)
    selection = this_mean[index]
    climatology = np.median(selection, axis=0)

    this_mean = this_mean - climatology
    this_low = this_low - climatology
    this_high = this_high - climatology

    # Add to data list
    data_list.append(this_mean)
    lows.append(this_low)
    highs.append(this_high)

# Plot each model as a separate line and shaded area
sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)
plt.figure(figsize=[24, 9])
for i, array in enumerate(data_list):
    plt.fill_between(time, lows[i], highs[i], alpha=0.1, color='#f56042')
    plt.plot(time, array, color='#f56042', linewidth=1)

plt.gca().set_xlabel("Year")
plt.gca().set_ylabel(r"$\!^\circ\!$C", rotation=90, labelpad=10)
plt.gca().set_title('Global temperature change of the past 2000 years', pad=5, fontdict={'fontsize': 40}, loc='left')

plt.savefig(Path(data_dir_env) / 'ManagedData' / 'Figures' / 'pages2k.png', bbox_inches='tight')
plt.savefig(Path(data_dir_env) / 'ManagedData' / 'Figures' / 'pages2k.svg', bbox_inches='tight')
plt.close()
