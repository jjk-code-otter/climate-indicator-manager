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

import matplotlib.pyplot as plt
import geopandas as gp
from cartopy import crs as ccrs

from climind.config.config import DATA_DIR

project_dir = DATA_DIR / "ManagedData"
shape_dir = project_dir / "Shape_Files"
figure_dir = project_dir / 'Figures'

continents = gp.read_file(shape_dir / 'WMO_RAs.shp')
continents = continents.rename(columns={'Region': 'region'})
print(continents)

fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})

ax.coastlines()

continents.plot(ax=ax, column='region', alpha=0.7,cmap='tab10',
                edgecolor="white", linewidth=2)
ax.set_xlim(-180,180)
ax.set_ylim(-90,90)
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_xticks([])
ax.set_yticks([])

fs = 25

plt.text(5,-10,'RA 1', fontsize=fs, color='white')
plt.text(75,45,'RA 2', fontsize=fs, color='white')
plt.text(-90,-25,'RA 3', fontsize=fs, color='white')
plt.text(-120,45,'RA 4', fontsize=fs, color='white')
plt.text(120,-30,'RA 5', fontsize=fs, color='white')
plt.text(-15,55,'RA 6', fontsize=fs, color='white')

my_dpi=200
fig.set_size_inches(1920/my_dpi, 1080/my_dpi)
plt.savefig(figure_dir / 'WMO_RA_map.png', dpi=my_dpi, bbox_inches='tight')
