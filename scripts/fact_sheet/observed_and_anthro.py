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


def read_anthro():

    dir = DATA_DIR / 'data-v2023.10.11' / 'ClimateIndicator-data-ed37002' / 'data' / 'anthropogenic_warming'
    filenames = ['Gillett_GMST_timeseries.csv', 'Ribes_GMST_timeseries.csv', 'Walsh_GMST_timeseries_6048000.csv']

    anthro_data = []

    for file in filenames:
        data = pd.read_csv(dir / file, usecols=['time','anthropogenic_p50','anthropogenic_p05', 'anthropogenic_p95'])
        anthro_data.append(data)

    return anthro_data


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
                                 'name': ['HadCRUT5', 'NOAA Interim', 'GISTEMP', 'Kadow', 'Berkeley Earth', 'HadCRUT4', 'HadCRUT5 noninfilled'],
                                 'time_resolution': 'monthly'})

    all_datasets = ts_archive.read_datasets(data_dir)

    anns = []
    tens = []
    for ds in all_datasets:
        ds.rebaseline(1850, 1900)
        annual =ds.make_annual()
        annual.select_year_range(1850, final_year)
        anns.append(annual)
        tens.append(annual.running_mean(10, centred=True))

    anthro_data = read_anthro()


    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)
    plt.figure(figsize=[16, 9])

    for ds in anns:
        plt.plot(ds.df['year'], ds.df['data'],color='#f56042', linewidth=3)

    for ds in tens:
        plt.plot(ds.df['year'], ds.df['data'], color='#69c2f5', linewidth=3)

    for ds in anthro_data:
        plt.fill_between(ds.time, ds.anthropogenic_p05, ds.anthropogenic_p95, color='#ffaa17', alpha=0.2)
        plt.plot(ds.time, ds.anthropogenic_p50, color='#ffaa17', linewidth=3)

    plt.text(1945, 0.65, 'Observed\nannual', color='#f56042', fontsize=36)
    plt.text(1883, 0.45, 'Human-induced', color='#ffaa17', fontsize=36)
    plt.text(1970, 1.10, 'Observed\nlong-term', color='#69c2f5', fontsize=36)

    plt.gca().set_xlabel("Year")
    plt.gca().set_ylabel(r"$\!^\circ\!$C", rotation=90, labelpad=10)
    plt.gca().set_title('Global warming metrics', pad=5, fontdict={'fontsize': 40},
                        loc='left')

    ylim = plt.gca().get_ylim()
    yloc = ylim[1] - 0.06 * (ylim[1] - ylim[0])
    plt.text(plt.gca().get_xlim()[0], yloc, 'Difference from 1850-1900 average', fontdict={'fontsize': 30})

    plt.savefig(figure_dir / 'observed_and_anthro.png', bbox_inches='tight')
    plt.savefig(figure_dir / 'observed_and_anthro.svg', bbox_inches='tight')
    plt.close()
