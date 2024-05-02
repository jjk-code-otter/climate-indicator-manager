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

import copy
from pathlib import Path
import logging

import climind.data_manager.processing as dm

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

import matplotlib.pyplot as plt
import seaborn as sns

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

    final_year = 2023

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    fdata_dir = project_dir / "Formatted_Data"
    figure_dir = project_dir / 'Figures'

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    # some global temperature data sets are annual only, others are monthly so need to read these separately
    ts_archive = archive.select({'variable': 'tas',
                                 'type': 'timeseries',
                                 'name': ['HadCRUT5', 'NOAA Interim', 'GISTEMP', 'Kadow', 'Berkeley Earth'],
                                 'time_resolution': 'monthly'})

    sst_archive = archive.select({'variable': 'sst',
                                  'type': 'timeseries',
                                  'time_resolution': 'monthly'})

    lsat_archive = archive.select({'variable': 'lsat',
                                   'type': 'timeseries',
                                   'time_resolution': 'monthly'})

    lsat_ann_archive = archive.select({'variable': 'lsat',
                                       'type': 'timeseries',
                                       'time_resolution': 'annual',
                                       'name': 'CLSAT'})

    all_datasets = ts_archive.read_datasets(data_dir)
    lsat_datasets = lsat_archive.read_datasets(data_dir)
    lsat_ann_datasets = lsat_ann_archive.read_datasets(data_dir)
    sst_datasets = sst_archive.read_datasets(data_dir)

    anns = []
    for ds in all_datasets:
        ds.rebaseline(1850, 1900)
        annual = ds.make_annual()
        annual.select_year_range(1850, final_year)
        anns.append(annual)

    lsat_anns = []
    for ds in lsat_datasets:
        ds.rebaseline(1850, 1900)
        annual = ds.make_annual()
        annual.select_year_range(1850, final_year)
        lsat_anns.append(annual)

    for ds in lsat_ann_datasets:
        ds.rebaseline(1850, 1900)
        ds.select_year_range(1850, final_year)
        lsat_anns.append(ds)

    sst_anns = []
    for ds in sst_datasets:
        ds.rebaseline(1850, 1900)
        annual = ds.make_annual()
        annual.select_year_range(1850, final_year)
        sst_anns.append(annual)

    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)
    plt.figure(figsize=[16, 9])

    # for ds in anns:
    #     plt.plot(ds.df['year'], ds.df['data'],color='#999999')

    for ds in sst_anns:
        plt.plot(ds.df['year'], ds.df['data'], color='#55cfc8', linewidth=2)

    for ds in lsat_anns:
        plt.plot(ds.df['year'], ds.df['data'], color='#a14a1b', linewidth=2)

    plt.text(1960, 1.04, 'Land', color='#a14a1b', fontsize=36)
    plt.text(1990, 0.04, 'Ocean', color='#55cfc8', fontsize=36)

    plt.gca().set_xlabel("Year")
    plt.gca().set_ylabel(r"$\!^\circ\!$C", rotation=90, labelpad=10)
    plt.gca().set_title('Land and ocean warming', pad=5, fontdict={'fontsize': 40},
                        loc='left')

    ylim = plt.gca().get_ylim()
    yloc = ylim[1] - 0.06 * (ylim[1] - ylim[0])
    plt.text(plt.gca().get_xlim()[0], yloc, 'Difference from 1850-1900 average', fontdict={'fontsize': 30})

    plt.savefig(figure_dir / 'land_ocean.png', bbox_inches='tight')
    plt.savefig(figure_dir / 'land_ocean.svg', bbox_inches='tight')
    plt.close()
