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

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
import seaborn as sns
import numpy as np

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


efos = 10.1
efos_unc = 0.5

eluc = 1.0
eluc_unc = 0.7

gatm = 5.9
gatm_unc = 0.2

socean = 2.9
socean_unc = 0.4

sland = 2.3
sland_unc = 1.0


plt.figure(figsize=[16, 9])

sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)
plt.plot([0,5], [-1, 12])
ax = plt.gca()

coords = np.array([[0, 0], [1, 0], [1, efos], [0, efos], [0, 0]])
p = Polygon(coords, color='red')
ax.add_patch(p)

coords = np.array([[0, efos], [1, efos], [1, efos+eluc], [0, efos+eluc], [0, efos]])
p = Polygon(coords, color='green')
ax.add_patch(p)

coords = np.array([[0, efos-efos_unc], [1, efos-efos_unc], [1, efos+efos_unc], [0, efos+efos_unc], [0, efos-efos_unc]])
p = Polygon(coords, color='black', alpha=0.3)
ax.add_patch(p)

coords = np.array([[0, efos+eluc-eluc_unc], [1, efos+eluc-eluc_unc], [1, efos+eluc+eluc_unc], [0, efos+eluc+eluc_unc], [0, efos+eluc-eluc_unc]])
p = Polygon(coords, color='black', alpha=0.3)
ax.add_patch(p)



plt.show()
plt.close()