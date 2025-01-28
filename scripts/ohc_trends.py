#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2025 John Kennedy
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
import itertools
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

final_year = 2024

project_dir = DATA_DIR / "ManagedData"
metadata_dir = METADATA_DIR

data_dir = project_dir / "Data"
fdata_dir = project_dir / "Formatted_Data"
figure_dir = project_dir / 'Figures'

archive = dm.DataArchive.from_directory(metadata_dir)

ohc_archive = archive.select(
    {'variable': 'ohc2k', 'type': 'timeseries', 'time_resolution': 'annual', "name": "Cheng TEMP"})
ohc_annual = ohc_archive.read_datasets(data_dir)
for ds in ohc_annual:
    ds.rebaseline(2005, 2020)

ds = ohc_annual[0]

x = ds.get_year_axis()
y = ds.df.data
trends = np.polyfit(x, y, 1)
trends_quad = np.polyfit(x, y, 2)

low = ds.lowess(15)

selecta = (x >= 1960) & (x < 2005)
xa = x[selecta]
ya = y[selecta]
trendsa = np.polyfit(xa, ya, 1)
selectb = (x >= 2005)
xb = x[selectb]
yb = y[selectb]
trendsb = np.polyfit(xb, yb, 1)


fig, axs = plt.subplots(2,2)

for i,j in itertools.product(range(2), range(2)):
    axs[i][j].plot(ohc_annual[0].get_year_axis(), ohc_annual[0].df.data)

axs[0][0].plot(x, trends[1] + trends[0] * x, color='orange')
axs[0][0].text(1960, 100, 'Linear')

axs[0][1].plot(xa, trendsa[1] + trendsa[0] * xa, color='orange')
axs[0][1].plot(xb, trendsb[1] + trendsb[0] * xb, color='orange')
axs[0][1].text(1960, 100, 'Split Linear')

axs[1][0].plot(low.get_year_axis(), low.df.data, color='orange')
axs[1][0].text(1960, 100, 'LOWESS')

axs[1][1].plot(x, trends_quad[2] + trends_quad[1] * x + trends_quad[0] *x *x, color='orange')
axs[1][1].text(1960, 100, 'Quadratic')

plt.savefig(figure_dir / 'ohc_trends.png', dpi=300)
plt.close()
