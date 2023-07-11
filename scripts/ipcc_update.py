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
import pandas as pd
import seaborn as sns

import matplotlib.pyplot as plt

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

ipcc_dir = DATA_DIR / "ManagedData" / "Data" / "IPCC"
figure_dir = DATA_DIR / "ManagedData" / "Figures"

df = pd.read_excel(
    ipcc_dir / 'GMST time series - February 2023.xlsx',
    usecols='L, M, N, O, Q',
    header=1,
    nrows=2022 - 1850 + 1
)

df = df.rename(columns={df.columns[0]: 'Year'})
df10 = df.rolling(10).mean()
df10_steps = df10.iloc[12::10, :]
df10_steps = df10_steps.reset_index()

STANDARD_PARAMETER_SET = {
    'axes.axisbelow': False,
    'axes.labelsize': 15,
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

fig, axs = plt.subplots(2, 1, sharex=True)
fig.set_size_inches(16, 9)

colours = ['', '#000000', '#33a8df', '#ec2089', '#f47e20']

for ds in range(1, 5):
    axs[0].plot(
        df.Year,
        df[df.columns[ds]],
        color=colours[ds],
        label=df.columns[ds],
        linewidth=3
    )

axs[0].set_ylabel('$\!^\circ\!$C')
axs[0].set_ylim(-0.3, 1.4)

legend = axs[0].legend(ncol=2, fontsize=15)
frame = legend.get_frame()
frame.set_facecolor('white')
frame.set_edgecolor('white')

for i in range(17):
    for ds in range(1, 5):
        print([df10.Year[i] - 4.5, df10.Year[i] + 4.5])
        axs[1].plot(
            [df10.Year[i] - 4.5 + 0.5, df10.Year[i] + 4.5 + 0.5],
            [df10[df.columns[ds]][i], df10[df.columns[ds]][i]],
            color=colours[ds],
            linewidth=3
        )

axs[1].set_ylabel('$\!^\circ\!$C')
axs[1].set_ylim(-0.3, 1.4)
axs[1].set_xlim(1849,2023)

# sns.despine(right=True, top=True, left=True, bottom=True)

plt.savefig(figure_dir / 'IPCC_update_global_mean_temperature.png' , bbox_inches='tight')
plt.savefig(figure_dir / 'IPCC_update_global_mean_temperature.svg' , bbox_inches='tight')
plt.savefig(figure_dir / 'IPCC_update_global_mean_temperature.pdf' , bbox_inches='tight')

plt.close()