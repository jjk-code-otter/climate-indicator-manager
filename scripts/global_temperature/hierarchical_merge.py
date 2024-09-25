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
import matplotlib.pyplot as plt
import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt
import climind.stats.utils as utils
from climind.data_types.timeseries import make_combined_series

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR
import seaborn as sns
import pandas as pd

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
    final_year = 2024

    project_dir = DATA_DIR / "ManagedData"
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

    # some global temperature data sets are annual only, others are monthly so need to read these separately
    ann_archive = archive.select(
        {
            'variable': 'tas',
            'type': 'timeseries',
            'time_resolution': 'annual',
            'name': ['GETQUOCS', 'HadCRUT5', 'Berkeley Earth', 'GISTEMP', 'Berkeley IPCC']
        }
    )

    ts_archive = archive.select(
        {'variable': 'tas',
         'type': 'timeseries',
         'name': ['DCENT',
                  'CMST',
                  'NOAA v6', 'ERA5', 'JRA-55',
                  'NOAA Interim', 'JRA-3Q', 'Kadow', 'Calvert 2024', 'Vaccaro', 'Cowtan and Way'],
         'time_resolution': 'monthly'
         }
    )

    all_datasets = ts_archive.read_datasets(data_dir)
    ann_datasets = ann_archive.read_datasets(data_dir)

    all_ann_datasets = []
    for ds in all_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        all_ann_datasets.append(annual)

    for ds in ann_datasets:
        ds.rebaseline(1981, 2010)
        all_ann_datasets.append(ds)

    group_had5 = []
    group_had4 = []
    group_noaa = []
    group_cmst = []
    group_rean = []
    group_berk = []
    group_dcent = []

    group_ipcc = []

    def wee_plotter(ax, ds, color, linewidth, alpha):
        ax.plot(ds.df.year, ds.df.data, color=color, linewidth=linewidth, alpha=alpha)
        if 'uncertainty' in ds.df:
            ax.fill_between(
                ds.df.year,
                ds.df['data'] + ds.df['uncertainty'],
                ds.df['data'] - ds.df['uncertainty'],
                color=color, alpha=alpha * 0.3
            )


    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)
    fig, axs = plt.subplots(3, sharex=True)
    fig.set_size_inches(16, 16)

    y = 0.72
    x = 1850
    dy = -0.1
    dx = 20
    for ds in all_ann_datasets:
        if ds.metadata['name'] in ['HadCRUT5', 'NOAA Interim', 'Berkeley IPCC','Kadow']:
            group_ipcc.append(ds)

        if ds.metadata['name'] in ['HadCRUT5', 'Kadow', 'Calvert 2024']:
            group_had5.append(ds)
            color = 'red'
        elif ds.metadata['name'] in ['Cowtan and Way', 'Vaccaro', 'GETQUOCS']:
            group_had4.append(ds)
            color = 'orange'
        elif ds.metadata['name'] in ['NOAA Interim', 'NOAA v6', 'GISTEMP']:
            group_noaa.append(ds)
            color = 'blue'
        elif ds.metadata['name'] in ['Berkeley Earth']:
            group_berk.append(ds)
            color = 'grey'
        elif ds.metadata['name'] in ['DCENT']:
            group_dcent.append(ds)
            color = 'black'
        elif ds.metadata['name'] in ['CMST']:
            group_cmst.append(ds)
            color = '#598ade'
        elif ds.metadata['name'] in ['ERA5', 'JRA-3Q', 'JRA-55']:
            group_rean.append(ds)
            color = 'purple'

        axs[0].text(x, y, ds.metadata['name'], color=color)
        y += dy
        if y < -0.25:
            x += dx
            y = 0.72

        wee_plotter(axs[0], ds, color, 1, 1)

    had5 = make_combined_series(group_had5, augmented_uncertainty=False)
    had4 = make_combined_series(group_had4, augmented_uncertainty=False)
    noaa = make_combined_series(group_noaa, augmented_uncertainty=False)
    rean = make_combined_series(group_rean, augmented_uncertainty=False)
    berk = make_combined_series(group_berk, augmented_uncertainty=False)
    cmst = make_combined_series(group_cmst, augmented_uncertainty=False)
    dcent = make_combined_series(group_dcent, augmented_uncertainty=False)

    ipcc = make_combined_series(group_ipcc, augmented_uncertainty=False)

    had_berk = make_combined_series([had5, berk])
    noaa_cmst = make_combined_series([noaa, cmst])

    #combo_combo = make_combined_series([had_berk, noaa_cmst, rean], augmented_uncertainty=False)
    combo_combo = make_combined_series([had_berk, noaa_cmst, rean, dcent], augmented_uncertainty=False)

    wee_plotter(axs[1], had5, 'red', 2, 1)
    wee_plotter(axs[1], had4, 'orange', 2, 1)
    wee_plotter(axs[1], noaa, 'blue', 2, 1)
    wee_plotter(axs[1], rean, 'purple', 2, 1)
    wee_plotter(axs[1], berk, 'grey', 2, 1)
    wee_plotter(axs[1], cmst, '#598ade', 2, 1)
    wee_plotter(axs[1], dcent, 'black', 2, 1)

    axs[1].text(1850, 0.72, 'HadCRUT5 group', color='red')
    axs[1].text(1850, 0.72 + dy, 'HadCRUT4 group', color='orange')
    axs[1].text(1850, 0.72 + 2 * dy, 'NOAA group', color='blue')
    axs[1].text(1850, 0.72 + 3 * dy, 'Reanalysis group', color='purple')
    axs[1].text(1850, 0.72 + 4 * dy, 'Berkeley Earth', color='grey')
    axs[1].text(1850, 0.72 + 5 * dy, 'CMST', color='#598ade')
    axs[1].text(1850, 0.72 + 6 * dy, 'DCENT', color='black')

    wee_plotter(axs[2], combo_combo, 'darkgreen', 2, 1.0)
#    axs[1].plot(combo_combo.df.year, combo_combo.df.data, color='darkgreen', linewidth=2)

    axs[2].plot(ipcc.df.year, ipcc.df.data, color='black')

    plt.subplots_adjust(wspace=0, hspace=0)

    axs[2].text(1850, 0.71, 'Combined', color='darkgreen', fontsize=24)
    axs[2].text(1850, 0.71 + 2*dy, 'IPCC', color='black', fontsize=24)


    for ax in axs:
        ax.set_ylim(-1.26, 0.93)
        ax.set_yticks([-1,-0.5,0,0.5])

    plt.savefig(figure_dir / 'combo_combo.png', bbox_inches='tight')
    plt.savefig(figure_dir / 'combo_combo.svg', bbox_inches='tight')
    plt.savefig(figure_dir / 'combo_combo.pdf', bbox_inches='tight')
    plt.close()
