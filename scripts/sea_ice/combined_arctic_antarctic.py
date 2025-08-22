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


from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

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


if __name__ == "__main__":

    final_year = 2025

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    figure_dir = project_dir / 'Figures'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    arctic_selection = {'variable': 'arctic_ice', 'type': 'timeseries', 'time_resolution': 'monthly'}
    antarctic_selection = {'variable': 'antarctic_ice', 'type': 'timeseries', 'time_resolution': 'monthly'}

    ts_arctic_archive = archive.select(arctic_selection)
    all_arctic = ts_arctic_archive.read_datasets(data_dir)

    ts_antarctic_archive = archive.select(antarctic_selection)
    all_antarctic = ts_antarctic_archive.read_datasets(data_dir)

    for ds in all_arctic:
        ds.rebaseline(1991, 2020)

    for ds in all_antarctic:
        ds.rebaseline(1991, 2020)

    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

    fig, axs = plt.subplots(2, sharex=True)
    fig.set_size_inches(16, 9)

    sns.despine(right=True, top=True, left=True)
    sns.despine(right=True, top=True, left=True, bottom=True, ax=axs[0])

    wmo_standard_colors = [
        "#204e96",  # Main blue
        "#f5a729", "#7ab64a", "#23abd1",  # Secondary colours
        "#008F90", "#00AE4D", "#869519", "#98411E", "#A18972"  # Additional colours (natural shades)
    ]

    for i, ds in enumerate(all_arctic):
        x_values = ds.get_year_axis()
        axs[0].plot(x_values, ds.df['data'], color=wmo_standard_colors[i], label=ds.metadata['display_name'], zorder=100-i)

    axs[0].set_yticks([-3,-2,-1,0,1,2])
    axs[0].set_xticks([1980, 1990, 2000, 2010, 2020])
    axs[0].set_title('Arctic sea-ice extent 1979-2025 (million km$^2$)', pad=25, loc='left', fontsize=30)
    axs[0].set_ylim(-3.05,2.3)
    ylim = axs[0].get_ylim()
    yloc = ylim[1] + 0.005 * (ylim[1] - ylim[0])
    axs[0].text(axs[0].get_xlim()[0], yloc, 'Difference from 1991-2020 average', fontdict={'fontsize': 90/4})

    for i, ds in enumerate(all_antarctic):
        x_values = ds.get_year_axis()
        axs[1].plot(x_values, ds.df['data'], color=wmo_standard_colors[i], label=ds.metadata['display_name'], zorder=100-i)

    axs[1].set_yticks([-3,-2,-1,0,1,2])
    axs[1].set_xticks([1980, 1990, 2000, 2010, 2020])
    axs[1].set_title('Antarctic sea-ice extent 1979-2025 (million km$^2$)', pad=5, loc='left', fontsize=30)
    axs[1].set_ylim(-3.05, 2.3)
    ylim = axs[1].get_ylim()
    yloc = ylim[1] - 0.081 * (ylim[1] - ylim[0])
    axs[1].text(axs[1].get_xlim()[0], yloc, 'Difference from 1991-2020 average', fontdict={'fontsize': 90/4})

    axs[0].legend()
    handles, labels = axs[0].get_legend_handles_labels()

    order=[0,1]
    loc = "upper right"
    bbox_to_anchor = (0.96, 0.96)

    leg = axs[0].legend([handles[idx] for idx in order], [labels[idx] for idx in order],
                     frameon=False, prop={'size': 20}, labelcolor='linecolor',
                     handlelength=0, handletextpad=0.3, loc=loc, bbox_to_anchor=bbox_to_anchor)
    for line in leg.get_lines():
        line.set_linewidth(3.0)
    for item in leg.legendHandles:
        item.set_visible(False)


    plt.subplots_adjust(hspace=0.2)

    plt.savefig(figure_dir / 'arctic_and_antarctic_ice_extent.png')
    plt.savefig(figure_dir / 'arctic_and_antarctic_ice_extent.svg')
    plt.savefig(figure_dir / 'arctic_and_antarctic_ice_extent.pdf')

    plt.close()