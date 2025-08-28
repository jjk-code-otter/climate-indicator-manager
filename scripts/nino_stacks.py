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

    archive = archive.select({'variable': 'oni',
                                 'type': 'timeseries',
                                 'time_resolution': 'monthly'})

    ts  = archive.read_datasets(data_dir)[0]

    #plt.plot(ts.get_year_axis(), ts.df.data)

    taxis = ts.get_year_axis()

    from matplotlib.collections import PatchCollection
    from matplotlib.patches import Rectangle

    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)
    plt.figure(figsize=(16, 9))

    tabs = []
    for i in range(len(ts.df.data)):
        x = taxis[i] - 1/24.
        y = ts.df.data[i]
        tab = Rectangle( (x, 0), 1/12., y )
        if y > 0:
            pc = PatchCollection([tab], facecolor='#eb4034', edgecolor='#eb4034')
        else:
            pc = PatchCollection([tab], facecolor='#284dc7', edgecolor='#284dc7')

        plt.gca().add_collection(pc)

    plt.gca().set_title(r'$Oceanic\ Ni\tilde{n}o\ Index\ (\degree C)$', pad=35,
                        fontdict={'fontsize': 35},
                        loc='left')

    plt.gca().set_xlim(1949, 2024)
    plt.gca().set_ylim(-2.1,3.1)

    plt.gca().set_xlabel('Year')
    plt.gca().set_ylabel('ONI index ($\degree$C)')

    plt.savefig(project_dir / 'Figures' / 'oni_bars.png')
    plt.savefig(project_dir / 'Figures' / 'oni_bars.svg')
    plt.close()
