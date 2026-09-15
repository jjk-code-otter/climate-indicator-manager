import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import seaborn as sns
import numpy as np

from climind.config.config import DATA_DIR

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

sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)
plt.figure(figsize=[16, 9])

data = [56, 62, 75, 83, 93, 104, 109, 116, 122, 130, 136]

years = [x for x in range(2015, 2026)]

plt.plot(years, data, marker="o")

plt.tick_params(
    axis='y',  # changes apply to the x-axis
    which='both',  # both major and minor ticks are affected
    left=False,  # ticks along the bottom edge are off
    right=False,  # ticks along the top edge are off
    labelright=False)

sns.despine(right=True, top=True, left=True)
plt.gca().set_ylim(0, 150)
plt.yticks([0, 20 , 40, 60, 80, 100, 120, 140])
plt.xticks(years)

ylim = plt.gca().get_ylim()
yloc = ylim[1] + 0.005 * (ylim[1] - ylim[0])

plt.text(plt.gca().get_xlim()[0], yloc, "Source: Sendai Framework Monitor", fontdict={'fontsize': 30})
plt.gca().set_title("Number of countries reporting existence of MHEWS", pad=35, fontdict={'fontsize': 40}, loc='left')

project_dir = DATA_DIR / "ManagedData"
figure_dir = project_dir / 'Figures'
image_filename = 'mhews_existence.png'

plt.savefig(figure_dir / image_filename, bbox_inches=Bbox([[0.8, 0], [14.5, 9]]))
plt.savefig(figure_dir / image_filename.replace('png', 'pdf'))
plt.savefig(figure_dir / image_filename.replace('png', 'svg'))
plt.close('all')
