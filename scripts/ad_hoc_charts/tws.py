import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
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

# year perc_dry perc_normal perc_wet
data = [[2002, 17, 52, 31],
        [2003, 19, 55, 26],
        [2004, 15, 56, 29],
        [2005, 15, 55, 30],
        [2006, 15, 61, 24],
        [2007, 12, 67, 21],
        [2008, 12, 72, 16],
        [2009, 12, 75, 13],
        [2010, 14, 72, 14],
        [2011, 12, 70, 18],
        [2012, 19, 68, 13],
        [2013, 15, 73, 12],
        [2014, 15, 69, 16],
        [2015, 23, 61, 16],
        [2016, 30, 55, 15],
        [2017, 30, 48, 22],
        [2018, 25, 54, 21],
        [2019, 32, 49, 19],
        [2020, 31, 47, 22],
        [2021, 37, 41, 22],
        [2022, 41, 37, 22],
        [2023, 42, 36, 22],
        [2024, 40, 36, 24],
        [2025, 42, 34, 24]]

data = np.array(data)

wmo_cols = ['#543005', '#bf812d', '#e5e5e5', '#35978f', '#003c30']

sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)
plt.figure(figsize=[16, 9])

#plt.plot(data[:, 0], data[:, 1])
#plt.plot(data[:, 0], data[:, 1] + data[:, 2])

ntime = data.shape[0]

dryboxes = []
normboxes = []
wetboxes = []
for i in range(ntime):
    # Loop over data points; create box from errors at each point
    x = data[i, 0] - 0.5
    y0 = 0.0
    y1 = data[i, 1]
    y2 = data[i, 1] + data[i, 2]
    y3 = 100

    delta = 0.05

    normboxes.append(Rectangle((x, y0), 1, y3-y0))
    dryboxes.append(Rectangle((x+delta, y0), 1-delta, y1))
    wetboxes.append(Rectangle((x+delta, y2), 1-delta, y3-y2))

    # Create patch collection with specified colour/alpha
pcnorm = PatchCollection(normboxes, facecolor=wmo_cols[2], alpha=1, edgecolor=wmo_cols[2], zorder=0, linewidth=0.5)
pcdry = PatchCollection(dryboxes, facecolor=wmo_cols[1], alpha=1, edgecolor=wmo_cols[2], zorder=1, linewidth=0.5)
pcwet = PatchCollection(wetboxes, facecolor=wmo_cols[-2], alpha=1, edgecolor=wmo_cols[2], zorder=1, linewidth=0.5)

# Add collection to Axes
plt.gca().add_collection(pcdry)
plt.gca().add_collection(pcnorm)
plt.gca().add_collection(pcwet)

plt.tick_params(
    axis='y',  # changes apply to the x-axis
    which='both',  # both major and minor ticks are affected
    left=False,  # ticks along the bottom edge are off
    right=False,  # ticks along the top edge are off
    labelright=False)

sns.despine(right=True, top=True, left=True)
plt.gca().set_ylim(0, 100)
plt.gca().set_xlim(2001.5, 2025.5)
plt.yticks([0, 25, 50, 75, 100])
plt.xticks([2002, 2005, 2010, 2015, 2020, 2025])

plt.gca().set_yticklabels(["0%", "25%", "50%", "75%", "100%"])

ylim = plt.gca().get_ylim()
yloc = ylim[1] + 0.025 * (ylim[1] - ylim[0])

plt.text(2026,85, "Above\nnormal", fontdict={'fontsize': 30}, color=wmo_cols[-2])
plt.text(2026,61, "Normal", fontdict={'fontsize': 30}, color="darkgrey")
plt.text(2026,20, "Below\nnormal", fontdict={'fontsize': 30}, color=wmo_cols[1])


plt.text(plt.gca().get_xlim()[0], yloc, "Above normal: among wettest 25% of years 2002-2020.\nBelow normal: among driest 25% of years 2002-2020.", fontdict={'fontsize': 20})
plt.text(plt.gca().get_xlim()[1], ylim[0]-10, "Source: WMO State of Global Water Resources 2025", fontdict={'fontsize': 15}, ha='right')
plt.gca().set_title("Percentage of global basin area with above or below\nnormal terrestrial water storage", pad=60,
                    fontdict={'fontsize': 40}, loc='left')

project_dir = DATA_DIR / "ManagedData"
figure_dir = project_dir / 'Figures'
image_filename = 'tws_percentages.png'

plt.savefig(figure_dir / image_filename, bbox_inches=Bbox([[0.8, 0], [16.5, 10]]))
plt.savefig(figure_dir / image_filename.replace('png', 'pdf'), bbox_inches=Bbox([[0.8, 0], [16.5, 10]]))
plt.savefig(figure_dir / image_filename.replace('png', 'svg'), bbox_inches=Bbox([[0.8, 0], [16.5, 10]]))
plt.close('all')
