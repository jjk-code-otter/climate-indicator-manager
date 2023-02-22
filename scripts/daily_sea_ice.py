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

project_dir = DATA_DIR / "ManagedData"
data_dir = project_dir / "Data"

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

df['climatology'] = climatology
df['anomalies'] = df.Extent - climatology

plt.plot(df.anomalies)
plt.show()

plt.plot(df[df['Year'] >= 2012].Extent)
plt.plot(df[df['Year'] >= 2012].climatology)

plt.show()


print()