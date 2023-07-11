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
import logging
from pathlib import Path

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt

import matplotlib.pyplot as plt
import seaborn as sns

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

if __name__ == "__main__":

    final_year = 2022

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    figure_dir = project_dir / 'Figures'
    log_dir = project_dir / 'Logs'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

    script = Path(__file__).stem
    logging.basicConfig(filename=log_dir / f'{script}.log',
                        filemode='w', level=logging.INFO)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    ts_archive = archive.select(
        {'variable': 'arctic_ice', 'type': 'timeseries', 'time_resolution': 'monthly', 'display_name': 'NSIDC'})
    anom_datasets = ts_archive.read_datasets(data_dir)

    for ds in anom_datasets:
        ds.rebaseline(1991, 2020)

    actual_datasets = ts_archive.read_datasets(data_dir)

    STANDARD_PARAMETER_SET = {
        'axes.axisbelow': False,
        'axes.labelsize': 20,
        'xtick.labelsize': 15,
        'ytick.labelsize': 15,
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
    plt.plot(anom_datasets[0].get_year_axis(), anom_datasets[0].df.data)
    plt.plot(actual_datasets[0].get_year_axis(), actual_datasets[0].df.data)
    plt.gca().set_ylabel('million km$^2$')
    sns.despine(right=True, top=True, left=True)

    plt.text(1979, 6.0, 'Actual', fontsize=20, color='C1')
    plt.text(1979, 2.6, 'Anomaly, difference from 1991-2020 average', fontsize=20, color='C0')

    plt.gca().set_title('Arctic sea ice extent (million km$^2$)', pad=5, fontdict={'fontsize': 30}, loc='left')

    plt.savefig(figure_dir / 'compare_actual_anomaly_ice.png')
    plt.savefig(figure_dir / 'compare_actual_anomaly_ice.pdf')
    plt.savefig(figure_dir / 'compare_actual_anomaly_ice.svg')

    plt.close()
