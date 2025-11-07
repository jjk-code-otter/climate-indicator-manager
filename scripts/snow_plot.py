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

import copy
from pathlib import Path
import os
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt
import climind.stats.utils as utils

from climind.data_types.timeseries import make_combined_series

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

    final_year = 2023

    project_dir = DATA_DIR / "ManagedData"
    ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    METADATA_DIR = (ROOT_DIR / "..").resolve() / "climind" / "metadata_files"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    fdata_dir = project_dir / "Formatted_Data"
    figure_dir = project_dir / 'Figures'
    log_dir = project_dir / 'Logs'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

    script = Path(__file__).stem
    logging.basicConfig(filename=log_dir / f'{script}.log',
                        filemode='w', level=logging.INFO)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    nh_archive = archive.select({'variable': 'snow',
                                 'type': 'timeseries',
                                 'time_resolution': 'monthly'})

    nam_archive = archive.select({'variable': 'snow_nam',
                                 'type': 'timeseries',
                                 'time_resolution': 'monthly'})

    nh  = nh_archive.read_datasets(data_dir)[0]
    nam = nam_archive.read_datasets(data_dir)[0]

    nh = nh.make_annual_by_selecting_month(5)
    nam = nam.make_annual_by_selecting_month(5)

    nh_clim = nh.running_mean(30)
    nam_clim = nam.running_mean(30)

    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

    plt.figure(figsize=(16, 9))

    col_nh = '#007478'
    col_nam = '#00b9bf'

    plt.plot(nh.df.year, nh.df.data, linewidth=3, color=col_nh)
    plt.plot([1967,2023], [nh_clim.df.data[2020-1967],nh_clim.df.data[2020-1967]],
             linewidth=1, color=col_nh, linestyle=':')

    plt.plot(nam.df.year, nam.df.data, linewidth=3, color=col_nam)
    plt.plot([1967, 2023], [nam_clim.df.data[2020 - 1967], nam_clim.df.data[2020 - 1967]],
             linewidth=1, color=col_nam, linestyle=':')

    plt.gca().set_title('May Snow Cover Extent 1967-2023 (million km$^2$)', pad=35,
                        fontdict={'fontsize': 35},
                        loc='left')
    plt.gca().set_xlabel('Date')
    plt.gca().set_ylabel('million km$^2$')
    plt.gca().set_ylim(0,25)

    ylim = plt.gca().get_ylim()
    xlim = plt.gca().get_xlim()

    yloc = ylim[0] + 0.95 * (ylim[1] - ylim[0])
    xloc = xlim[0] + 0.03 * (xlim[1] - xlim[0])
    plt.text(xloc, yloc, 'Northern Hemisphere', color=col_nh, fontdict={'fontsize': 24})

    yloc = ylim[0] + 0.69 * (ylim[1] - ylim[0])
    xloc = xlim[0] + 0.09 * (xlim[1] - xlim[0])
    plt.text(xloc, yloc, '1991-2020 average', color=col_nh, fontdict={'fontsize': 18})

    yloc = ylim[0] + 0.48 * (ylim[1] - ylim[0])
    xloc = xlim[0] + 0.03 * (xlim[1] - xlim[0])
    plt.text(xloc, yloc, 'North America', color=col_nam, fontdict={'fontsize': 24})

    yloc = ylim[0] + 0.32 * (ylim[1] - ylim[0])
    xloc = xlim[0] + 0.09 * (xlim[1] - xlim[0])
    plt.text(xloc, yloc, '1991-2020 average', color=col_nam, fontdict={'fontsize': 18})

    plt.savefig(project_dir / 'Figures' / 'may_snow_cover.png')
    plt.savefig(project_dir / 'Figures' / 'may_snow_cover.svg')
    plt.close()