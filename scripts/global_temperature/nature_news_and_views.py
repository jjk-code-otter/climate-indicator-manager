#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2022 John Kennedy
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
import copy
import os
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

if __name__ == "__main__":

    final_year = 2024

    project_dir = DATA_DIR / "ManagedData"
    ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    METADATA_DIR = (ROOT_DIR / "..").resolve() / "climind" / "metadata_files"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    fdata_dir = project_dir / "Formatted_Data"
    figure_dir = project_dir / 'Figures'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    # some global temperature data sets are annual only, others are monthly so need to read these separately
    ts_archive = archive.select({'variable': 'tas',
                                 'type': 'timeseries',
                                 'name': ['HadCRUT5', 'NOAA v6', 'Berkeley Earth', 'Kadow', 'DCENT'],
                                 'time_resolution': 'monthly'})

    sst_archive = archive.select({'variable': 'sst',
                                  'type': 'timeseries',
                                  'name': ['HadSST4', 'ERSST v6', 'DCENT SST'],
                                  'time_resolution': 'monthly'})

    lsat_archive = archive.select({'variable': 'lsat',
                                   'type': 'timeseries',
                                   'name': ['CRUTEM5', 'NOAA LSAT v6', 'Berkeley Earth LSAT', 'DCENT LSAT'],
                                   'time_resolution': 'monthly'})

    all_datasets = ts_archive.read_datasets(data_dir)
    alt_datasets = ts_archive.read_datasets(data_dir)

    lsat_datasets = lsat_archive.read_datasets(data_dir)
    sst_datasets = sst_archive.read_datasets(data_dir)

    all_8110_datasets = []
    all_annual_datasets = []
    for ds in all_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        annual.select_year_range(1850, final_year)
        all_annual_datasets.append(annual)

    lsat_anns = []
    lsat_mons = []
    for ds in lsat_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        annual.select_year_range(1850, final_year)
        lsat_anns.append(annual)

    sst_anns = []
    sst_mons = []
    for ds in sst_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        annual.select_year_range(1850, final_year)
        sst_anns.append(annual)

    # pt.neat_plot(figure_dir, lsat_anns, 'NNV_annual_lsat.png', 'Global mean LSAT')
    # pt.neat_plot(figure_dir, sst_anns, 'NNV_annual_sst.png', 'Global mean SST')
    # pt.neat_plot(figure_dir, all_annual_datasets, 'NNV_annual.png', r'Global Mean Temperature Difference ($\degree$C)')

    all_1900 = []
    all_ww2 = []
    for ds in all_annual_datasets:
        all_1900.append(ds.time_average(1900,1915))
        all_ww2.append(ds.time_average(1939,1945))

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
    plt.figure(figsize=[16, 9])

    colors = ['#bae4bc', '#bb0000', '#7bccc4', '#43a2ca', '#0868ac']
    colors = ['#84e3d6', '#ff6021', '#7bccc4', '#43a2ca', '#0868ac']
    lw = [3, 5, 3, 3, 3]
    zod = [1, 2, 1, 1, 1]
    plt.fill_between([1900, 1930], [-1.20, -1.20], [0.0, 0.0], color='lightgrey', alpha=0.5)
    plt.text(1915, 0.05, 'Sippel et al.', ha='center', fontsize=20)
    plt.text(1947, 0.05, 'World War 2\nWarm Anomaly', ha='center', fontsize=20)

    plt.fill_between([1939, 1945], [-1.20, -1.20], [0.0, 0.0], color='lightgrey', alpha=0.2)

    sns.despine(right=True, top=True, left=True)
    for i, ds in enumerate(all_annual_datasets):
        plt.plot(ds.df.year, ds.df.data, color=colors[i], linewidth=2, label=ds.metadata['display_name'],
                 zorder=zod[i])
        plt.plot([1900,1916],[all_1900[i],all_1900[i]], color=colors[i], linewidth=4, label=None)
        #plt.plot([1916,1939],[all_1900[i],all_ww2[i]], color=colors[i], linewidth=4, label=None, linestyle=':')
        plt.plot([1939,1946],[all_ww2[i],all_ww2[i]], color=colors[i], linewidth=4, label=None)


    plt.legend()
    # get handles and labels
    handles, labels = plt.gca().get_legend_handles_labels()
    # add legend to plot
    order = [1, 0, 2, 3, 4]
    leg = plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order],
                     frameon=False, prop={'size': 20}, labelcolor='linecolor',
                     handlelength=0, handletextpad=0.3, loc="upper left", bbox_to_anchor=(0.75, 0.35))
    for line in leg.get_lines():
        line.set_linewidth(3.0)
    for item in leg.legendHandles:
        item.set_visible(False)

    plt.title('New analyses suggest less early 20th century warming', fontsize=35, loc='left')
    plt.text(plt.gca().get_xlim()[0], 0.8, r'Global temperature difference from 1981-2010 average ($\!^\circ\!$C)', fontdict={'fontsize': 24})

    plt.gca().set_ylim(-1.1, 0.9)
    plt.yticks([-1, -0.5, 0, 0.5])
    plt.xticks([1850, 1900, 1950, 2000])

    plt.savefig(figure_dir / 'NNV_annual.png', bbox_inches='tight')
    plt.savefig(figure_dir / 'NNV_annual.svg', bbox_inches='tight')
    plt.close()


    # Trend version
    plt.figure(figsize=[16, 9])

    colors = ['#bae4bc', '#bb0000', '#7bccc4', '#43a2ca', '#0868ac']
    colors = ['#84e3d6', '#ff6021', '#7bccc4', '#43a2ca', '#0868ac']
    lw = [3, 5, 3, 3, 3]
    zod = [1, 2, 1, 1, 1]
    plt.fill_between([1900, 1930], [-1.20, -1.20], [0.0, 0.0], color='lightgrey', alpha=0.5)
    plt.text(1915, 0.05, 'Sippel et al.', ha='center', fontsize=20)
    plt.text(1947, 0.05, 'World War 2\nWarm Anomaly', ha='center', fontsize=20)

    plt.fill_between([1939, 1945], [-1.20, -1.20], [0.0, 0.0], color='lightgrey', alpha=0.2)

    sns.despine(right=True, top=True, left=True)
    for i, ds in enumerate(all_annual_datasets):
        plt.plot(ds.df.year, ds.df.data, color=colors[i], linewidth=2, label=ds.metadata['display_name'],
                 zorder=zod[i])

        selector = (ds.df.year >= 1910) & (ds.df.year <= 1945)
        results = np.polyfit(ds.df.year[selector], ds.df.data[selector], 1)

        plt.plot([1910,1945],[results[1] + 1910 * results[0], results[1] + 1945 * results[0]], color=colors[i], linewidth=4, label=None, zorder=zod[i]+5)


    plt.legend()
    # get handles and labels
    handles, labels = plt.gca().get_legend_handles_labels()
    # add legend to plot
    order = [1, 0, 2, 3, 4]
    leg = plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order],
                     frameon=False, prop={'size': 20}, labelcolor='linecolor',
                     handlelength=0, handletextpad=0.3, loc="upper left", bbox_to_anchor=(0.75, 0.35))
    for line in leg.get_lines():
        line.set_linewidth(3.0)
    for item in leg.legendHandles:
        item.set_visible(False)

    plt.title('New analysis suggest less early 20th century warming', fontsize=35, loc='left')
    plt.text(plt.gca().get_xlim()[0], 0.8, r'Global temperature difference from 1981-2010 average ($\!^\circ\!$C)', fontdict={'fontsize': 24})

    plt.gca().set_ylim(-1.1, 0.9)
    plt.yticks([-1, -0.5, 0, 0.5])
    plt.xticks([1850, 1900, 1950, 2000])

    plt.savefig(figure_dir / 'NNV_annual_trend.png', bbox_inches='tight')
    plt.savefig(figure_dir / 'NNV_annual_trend.svg', bbox_inches='tight')
    plt.close()
