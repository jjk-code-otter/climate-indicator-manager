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

from pathlib import Path
import os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
#from scipy.signal import detrend
from statsmodels.tsa.tsatools import detrend

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

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

if __name__ == "__main__":
    final_year = 2025

    project_dir = DATA_DIR / "ManagedData"
    ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    METADATA_DIR = (ROOT_DIR / "..").resolve() / "climind" / "metadata_files"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    figure_dir = project_dir / 'Figures'
    log_dir = project_dir / 'Logs'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    gmst_archive = archive.select({'variable': 'tas', 'time_resolution': 'monthly',
                                   'type': 'timeseries', 'name': 'ERA5'})
    gmst = gmst_archive.read_datasets(data_dir)
    gmst = gmst[0]
    gmst.rebaseline(1981, 2010)
    gmst.add_offset(0.69)
    gmst = gmst.select_year_range(1980, 2025)

    oni_archive = archive.select({'variable': 'oni', 'time_resolution': 'monthly', 'type': 'timeseries'})
    oni = oni_archive.read_datasets(data_dir)[0]
    oni = oni.select_year_range(1980, 2025)

    aod_archive = archive.select({'variable': 'aod', 'time_resolution': 'monthly', 'type': 'timeseries'})
    aod = aod_archive.read_datasets(data_dir)[0]


    gmst_taxis = gmst.get_year_axis()
    oni_taxis = oni.get_year_axis()
    aod_taxis = aod.get_year_axis()

    detrended = detrend(gmst.df.data, order=2)
    trend = gmst.df.data - detrended

    flum = np.zeros(len(gmst.df.data))
    for i in range(1, len(gmst.df.data)-1):
        flum[i] = np.mean(gmst.df.data[i-1:i+2])

    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

    fig, axs = plt.subplots(2, 1, sharex=False, gridspec_kw={'height_ratios': [2.5, 1]})
    fig.set_size_inches(16, 9)

    axs[0].plot(gmst_taxis, gmst.df.data, color='orange', linewidth=3)
    axs[0].plot(gmst_taxis, trend, color='red', linewidth=3)
    #axs[0][0].plot(gmst_taxis, trend+0.1*oni.df.data, linewidth=3, color='dodgerblue')


    axs[1].plot(gmst_taxis, detrended, color='orange', linewidth=3)
    axs[1].plot(oni_taxis, oni.df.data * 0.1, linewidth=3, color='dodgerblue')
    #axs[1][0].plot(oni_taxis+0.5, oni.df.data * 0.1, linestyle='--', linewidth=3, color='dodgerblue')
    #axs[1][0].plot(aod_taxis, -2 * aod.df.data, linewidth=3, color='purple')

    for y in range(1980,2026):
        axs[1].plot([y,y],[-0.5,0.5],linewidth=0.5,color='lightgrey')

    plt.subplots_adjust(left=0.1,
                        bottom=0.1,
                        right=0.9,
                        top=0.90,
                        wspace=0.1,
                        hspace=0.3)

    axs[0].set_xlim(1980, 2026)
    axs[0].set_ylim(0.1, 1.8)
    axs[0].set_title(f'Global mean temperature ({gmst.metadata["display_name"]})', loc='left', fontsize=24)
    axs[0].set_ylabel('Anomaly')

    axs[1].set_xlim(1980, 2026)
    axs[1].set_ylim(-0.5, 0.5)
    axs[1].set_title('Detrended', loc='left', fontsize=24)
    axs[1].set_ylabel('Anomaly')

    plt.savefig(figure_dir / "gmst_enso.png", dpi=300)
    plt.savefig(figure_dir / "gmst_enso.svg", dpi=300)
    plt.savefig(figure_dir / "gmst_enso.pdf", dpi=300)

    plt.close('all')
