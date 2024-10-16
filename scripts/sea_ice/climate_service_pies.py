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

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path
from climind.config.config import DATA_DIR
import seaborn as sns
from matplotlib.patches import Polygon


def draw_segment(fig, ax, x0, y0, r1, r2, pc1, pc2, color, text_color):

    if pc2-pc1 <= 0:
        return

    theta = np.arange(pc1, pc2 + 0.1, 0.5)

    xs_outer = r1 * np.sin(2 * np.pi * theta / 100.) + x0
    ys_outer = r1 * np.cos(2 * np.pi * theta / 100.) + y0

    xs_inner = np.flip(r2 * np.sin(2 * np.pi * theta / 100.) + x0)
    ys_inner = np.flip(r2 * np.cos(2 * np.pi * theta / 100.) + y0)

    xs = np.concatenate((xs_outer, xs_inner))
    ys = np.concatenate((ys_outer, ys_inner))

    coords = np.transpose(np.stack([xs, ys]))

    p = Polygon(coords, facecolor=color, transform=fig.dpi_scale_trans, alpha=0.9, zorder=99)
    ax.add_patch(p)

    r3 = 0.5 * (r1 + r2)

    if pc2-pc1 < 5:
        r3 = r1 + 0.25 * (r1-r2)

    x = r3 * np.sin(2 * np.pi * (pc2 + pc1)/200) + x0
    y = r3 * np.cos(2 * np.pi * (pc2 + pc1)/200) + y0

    ax.text(x, y, f'{pc2 - pc1}%', transform=fig.dpi_scale_trans, zorder=100, ha='center', va='center', color=text_color)


def draw_pie(fig, ax, x0, y0, r1, r2, slices):
#    colours = ['#E2EEDC', '#CEDCBB', '#B4CE97', '#637D44', '#43542F', '#7F7F7F']
    colours = ['#d4e4fc', '#9ab6e3', '#6b8fc9', '#416cb0', '#204e96', '#7F7F7F']
    text_colours = ['black', 'black', 'black', 'white', 'white', 'white']
    cum_sum = 0
    for i in range(len(slices)):
        draw_segment(fig, ax, x0, y0, r1, r2, cum_sum, cum_sum + slices[i], colours[i], text_colours[i])
        cum_sum += slices[i]


title = "Level of capacity 2023 - 2024"
regions = ['I', 'II', 'III', 'IV', 'V', 'VI']

Advanced = [8, 15, 0, 18, 27, 16]
Full = [23, 24, 33, 9, 18, 18]
Essential = [34, 29, 50, 14, 37, 38]
Basic = [19, 24, 17, 27, 18, 18]
Lessthanbasic = [15, 0, 0, 5, 0, 2]
NoData = [1, 8, 0, 27, 0, 8]

#colours = ['#E2EEDC', '#CEDCBB', '#B4CE97', '#637D44', '#43542F', '#7F7F7F']
colours = ['#d4e4fc', '#9ab6e3', '#6b8fc9', '#416cb0', '#204e96', '#7F7F7F']

names = ['Less than basic', 'Basic', 'Essential','Full','Advanced','No data']

region_x = [9, 11, 6.2, 5.0, 12.25, 8.25]
region_y = [4, 6.2, 3.8, 6.05, 3.74, 6.3]

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

sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

fig = plt.figure(figsize=(16, 9))
ax = plt.axes(projection=ccrs.EqualEarth())
ax.add_feature(cfeature.LAND, facecolor='#cFcFcF')
ax.coastlines(linewidth=1, color='#676767')
ax.set_global()

for i in range(6):
    draw_pie(
        fig, ax, region_x[i], region_y[i], 1, 0.5,
        [Lessthanbasic[i], Basic[i], Essential[i], Full[i], Advanced[i], NoData[i]]
    )

ypos = 1
delta = 0.3
xpos = 5 + delta
p = Polygon([[0+xpos,0+ypos],[0.25+xpos,0+ypos],[0.25+xpos,0.25+ypos],[0+xpos,0.25+ypos]], facecolor=colours[0], transform=fig.dpi_scale_trans, clip_on=False)
ax.add_patch(p)
ax.text(xpos - 0.05, 0.125+ypos, 'Climate Service implementation level:', transform=fig.dpi_scale_trans, va='center', ha='right')
ax.text(0.3+xpos, 0.125+ypos, 'Less than basic', transform=fig.dpi_scale_trans, va='center')

xpos = 6.5+ delta
p = Polygon([[0+xpos,0+ypos],[0.25+xpos,0+ypos],[0.25+xpos,0.25+ypos],[0+xpos,0.25+ypos]], facecolor=colours[1], transform=fig.dpi_scale_trans, clip_on=False)
ax.add_patch(p)
ax.text(0.3+xpos, 0.125+ypos, 'Basic', transform=fig.dpi_scale_trans, va='center')

xpos= 7.3+ delta
p = Polygon([[0+xpos,0+ypos],[0.25+xpos,0+ypos],[0.25+xpos,0.25+ypos],[0+xpos,0.25+ypos]], facecolor=colours[2], transform=fig.dpi_scale_trans, clip_on=False)
ax.add_patch(p)
ax.text(0.3+xpos, 0.125+ypos, 'Essential', transform=fig.dpi_scale_trans, va='center')

xpos =8.3+ delta
p = Polygon([[0+xpos,0+ypos],[0.25+xpos,0+ypos],[0.25+xpos,0.25+ypos],[0+xpos,0.25+ypos]], facecolor=colours[3], transform=fig.dpi_scale_trans, clip_on=False)
ax.add_patch(p)
ax.text(0.3+xpos, 0.125+ypos, 'Full', transform=fig.dpi_scale_trans, va='center')

xpos = 8.94+ delta
p = Polygon([[0+xpos,0+ypos],[0.25+xpos,0+ypos],[0.25+xpos,0.25+ypos],[0+xpos,0.25+ypos]], facecolor=colours[4], transform=fig.dpi_scale_trans, clip_on=False)
ax.add_patch(p)
ax.text(0.3+xpos, 0.125+ypos, 'Advanced', transform=fig.dpi_scale_trans, va='center')

xpos=10.0+ delta
p = Polygon([[0+xpos,0+ypos],[0.25+xpos,0+ypos],[0.25+xpos,0.25+ypos],[0+xpos,0.25+ypos]], facecolor=colours[5], transform=fig.dpi_scale_trans, clip_on=False)
ax.add_patch(p)
ax.text(0.3+xpos, 0.125+ypos, 'No data', transform=fig.dpi_scale_trans, va='center')

plt.savefig(DATA_DIR / 'ManagedData' / 'Figures' / 'climate_service_pies.svg',transparent=True)
plt.show()
plt.close()
