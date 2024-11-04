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
import pandas as pd

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
    h4_infilled_archive = archive.select({'variable': 'tas',
                                 'type': 'timeseries',
                                 'name': ['Cowtan and Way', 'Vaccaro'],
                                 'time_resolution': 'monthly'})
    h4_infilled_archive_2 = archive.select({'variable': 'tas',
                                 'type': 'timeseries',
                                 'name': ['GETQUOCS'],
                                 'time_resolution': 'annual'})

    h4_archive = archive.select({'variable': 'tas',
                                 'type': 'timeseries',
                                 'name': ['HadCRUT4'],
                                 'time_resolution': 'monthly'})

    h5_infilled_archive = archive.select({'variable': 'tas',
                                          'type': 'timeseries',
                                          'name': ['HadCRUT5', 'Kadow', 'Calvert 2024'],
                                          'time_resolution': 'monthly'})

    h5_archive = archive.select({'variable': 'tas',
                                 'type': 'timeseries',
                                 'name': ['HadCRUT5 noninfilled'],
                                 'time_resolution': 'monthly'})

    h4_datasets = h4_archive.read_datasets(data_dir)
    h4_infilled_datasets = h4_infilled_archive.read_datasets(data_dir)
    h4_infilled_datasets_2 = h4_infilled_archive_2.read_datasets(data_dir)

    h5_infilled_datasets = h5_infilled_archive.read_datasets(data_dir)
    h5_datasets = h5_archive.read_datasets(data_dir)

    h4_anns = []
    for ds in h4_datasets:
        ds.rebaseline(1961,1990)
        annual = ds.make_annual()
        annual.select_year_range(1850, 2021)
        h4_anns.append(annual)

    h4_infilled_anns = []
    for ds in h4_infilled_datasets:
        ds.rebaseline(1961,1990)
        annual = ds.make_annual()
        annual.select_year_range(1850, 2023)
        h4_infilled_anns.append(annual)
    for ds in h4_infilled_datasets_2:
        ds.rebaseline(1961,1990)
        ds.select_year_range(1850, 2023)
        h4_infilled_anns.append(ds)

    h5_anns = []
    for ds in h5_datasets:
        ds.rebaseline(1961,1990)
        annual = ds.make_annual()
        annual.select_year_range(1850, 2023)
        h5_anns.append(annual)

    h5_infilled_anns = []
    for ds in h5_infilled_datasets:
        ds.rebaseline(1961,1990)
        annual = ds.make_annual()
        annual.select_year_range(1850, 2023)
        h5_infilled_anns.append(annual)

    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)
    plt.figure(figsize=[16, 9])

    for ds in h5_infilled_anns:
        label = ds.metadata['display_name']+'-HadCRUT5 non-infilled'
        plt.plot(ds.df['year'], ds.df['data'] - h5_anns[0].df['data'], linewidth=3, label=label)

    for ds in h4_infilled_anns:
        label = ds.metadata['display_name']+'-HadCRUT4'
        plt.plot(ds.df['year'], ds.df['data'] - h4_anns[0].df['data'][0:len(ds.df['data'])], linewidth=3, label=label)

    plt.legend(loc='upper right', fontsize=24)

    plt.gca().set_xlabel("Year")
    plt.gca().set_ylabel(r"$\!^\circ\!$C", rotation=90, labelpad=10)

    plt.gca().set_ylim(-0.22, 0.33)

    plt.gca().set_title('Global mean temperature',
                        pad=35, fontdict={'fontsize': 40}, loc='left')
    ylim = plt.gca().get_ylim()
    yloc = ylim[1] + 0.006 * (ylim[1] - ylim[0])
    plt.text(plt.gca().get_xlim()[0], yloc, 'Difference from non-infilled dataset', fontdict={'fontsize': 30})

    plt.savefig(figure_dir / 'infilling.png', bbox_inches='tight')
    plt.savefig(figure_dir / 'infilling.svg', bbox_inches='tight')
    plt.close()
