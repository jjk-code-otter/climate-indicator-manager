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

from climind.config.config import DATA_DIR, CLIMATOLOGY
from climind.definitions import METADATA_DIR
import matplotlib.pyplot as plt
import pandas as pd
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

project_dir = DATA_DIR / "ManagedData"
data_dir = project_dir / "Data"

#sea_ice_file = data_dir / "NSIDC" / "N_seaice_extent_daily_v3.0.csv"
sea_ice_file = data_dir / "NSIDC SH" / "S_seaice_extent_daily_v3.0.csv"

df = pd.read_csv(sea_ice_file, skiprows=[1])
df.columns = df.columns.str.replace(' ', '')
df['date'] = pd.to_datetime(dict(year=df['Year'], month=df['Month'], day=df['Day']))
df = df.set_index('date')

df2 = df[df['Year'] >= 1991]
df2 = df2[df2['Year'] <= 2020]

climatology = df2.groupby([df2.index.month, df2.index.day]).mean()
climatology = climatology.Extent[zip(df.index.month, df.index.day)]
climatology.index = df.index

df3 = df[df['Year'] < 2022]

climatology_max = df3.groupby([df3.index.month, df3.index.day]).max()
climatology_max = climatology_max.Extent[zip(df.index.month, df.index.day)]
climatology_max.index = df.index

climatology_min = df3.groupby([df3.index.month, df3.index.day]).min()
climatology_min = climatology_min.Extent[zip(df.index.month, df.index.day)]
climatology_min.index = df.index

df['climatology'] = climatology
df['cmax'] = climatology_max
df['cmin'] = climatology_min
df['anomalies'] = df.Extent - climatology

# plt.plot(df.anomalies)
# plt.show()

fig = plt.figure(figsize=(16, 9))
sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

plt.plot(df[df['Year'] == 2022].cmin, color='lightgrey')
plt.plot(df[df['Year'] == 2022].cmax, color='lightgrey')
plt.plot(df[df['Year'] == 2022].Extent, color='red')
plt.plot(df[df['Year'] == 2022].climatology, color='black')

plt.plot(df[df['Year'] == 2022].cmax - df[df['Year'] == 2022].climatology, color='lightgrey')
plt.plot(df[df['Year'] == 2022].cmin - df[df['Year'] == 2022].climatology, color='lightgrey')
plt.plot(df[df['Year'] == 2022].climatology - df[df['Year'] == 2022].climatology, color='black')
plt.plot(df[df['Year'] == 2022].Extent - df[df['Year'] == 2022].climatology, color='red')
sns.despine(right=True, top=True, left=True)
plt.gca().set_ylim(-5, 22)
plt.show()
