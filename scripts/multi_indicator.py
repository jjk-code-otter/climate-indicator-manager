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
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt
import climind.stats.utils as utils

from climind.data_types.timeseries import make_combined_series

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR


def stripe(ax, time, data, time_start, time_end):

    ax.plot(time, data)



final_year = 2024

project_dir = DATA_DIR / "ManagedData"
metadata_dir = METADATA_DIR

data_dir = project_dir / "Data"
fdata_dir = project_dir / "Formatted_Data"
figure_dir = project_dir / 'Figures'

archive = dm.DataArchive.from_directory(metadata_dir)

tas_archive = archive.select(
    {
        'variable': 'tas', 'type': 'timeseries', 'time_resolution': 'monthly', 'origin': 'obs',
        'name': ['HadCRUT5', 'NOAA v6', 'GISTEMP', 'Berkeley Earth', 'JRA-3Q', 'ERA5']
    }
)
all_tas_datasets = tas_archive.read_datasets(data_dir)
tas_annual = []
for ds in all_tas_datasets:
    ds.rebaseline(1981, 2010)
    annual = ds.make_annual()
    annual.add_offset(0.69)
    annual.manually_set_baseline(1850, 1900)
    annual.select_year_range(1960, final_year)
    tas_annual.append(annual)

ohc_archive = archive.select(
    {
        'variable': 'ohc2k', 'type': 'timeseries', 'time_resolution': 'annual'
    }
)
ohc_annual = ohc_archive.read_datasets(data_dir)
for ds in ohc_annual:
    ds.rebaseline(2005, 2020)
    #ds.add_year(2022, 96.74878325523227, 8.430242333320507)

ph_archive = archive.select(
    {
        'variable': 'ph', 'type': 'timeseries', 'time_resolution': 'annual',
        'name': ['CMEMS']
    }
)
ph_annual = ph_archive.read_datasets(data_dir)

sealevel_archive = archive.select(
    {
        'variable': 'sealevel', 'type': 'timeseries', 'name': ['AVISO ftp','NASA Sealevel']
    }
)
sealevel_annual = sealevel_archive.read_datasets(data_dir)
for ds in sealevel_annual:
    ds.select_year_range(1993,2023)

ghg_archive = archive.select(
    {
        'variable': 'co2', 'type': 'timeseries', 'time_resolution': 'monthly',
        'name': 'WDCGG'
    }
)
ghg_annual = ghg_archive.read_datasets(data_dir)

ch4_archive = archive.select(
    {
        'variable': 'ch4', 'type': 'timeseries', 'time_resolution': 'monthly',
        'name': 'WDCGG CH4'
    }
)
ch4_annual = ch4_archive.read_datasets(data_dir)

n2o_archive = archive.select(
    {
        'variable': 'n2o', 'type': 'timeseries', 'time_resolution': 'monthly',
        'name': 'WDCGG N2O'
    }
)
n2o_annual = n2o_archive.read_datasets(data_dir)

seaice_archive = archive.select(
    {
        'variable': 'arctic_ice', 'type': 'timeseries', 'time_resolution': 'monthly'
    }
)
seaice_data = seaice_archive.read_datasets(data_dir)
seaice_annual = []
for ds in seaice_data:
    ds.rebaseline(1981, 2010)
    annual = ds.make_annual_by_selecting_month(9)
    seaice_annual.append(annual)

seaicesh_archive = archive.select(
    {
        'variable': 'antarctic_ice', 'type': 'timeseries', 'time_resolution': 'monthly'
    }
)
seaicesh_data = seaicesh_archive.read_datasets(data_dir)
seaicesh_annual = []
for ds in seaicesh_data:
    ds.rebaseline(1981, 2010)
    annual = ds.make_annual_by_selecting_month(9)
    seaicesh_annual.append(annual)

glacier_archive = archive.select(
    {
        'variable': 'glacier', 'type': 'timeseries', 'time_resolution': 'annual'
    }
)
glacier_annual = glacier_archive.read_datasets(data_dir)

greenland_archive = archive.select(
    {
        'variable': 'greenland', 'type': 'timeseries', 'time_resolution': 'monthly'
    }
)
greenland_annual = greenland_archive.read_datasets(data_dir)
for ds in greenland_annual:
    ds.zero_on_month(2005, 7)

antarctic_archive = archive.select(
    {
        'variable': 'antarctica', 'type': 'timeseries', 'time_resolution': 'monthly'
    }
)
antarctic_annual = antarctic_archive.read_datasets(data_dir)
for ds in antarctic_annual:
    ds.zero_on_month(2005, 6)


# PLOT
STANDARD_PARAMETER_SET = {
    'axes.axisbelow': False,
    'axes.labelsize': 10,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
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

fig, axs = plt.subplots(4, sharex=True)
fig.set_size_inches(6, 8)

for ds in ghg_annual:
    axs[0].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[0].set_yticks(np.arange(340, 430, 20))
axs[0].tick_params(labelbottom=False, length=0)
axs[0].set_title('Carbon Dioxide (ppm)', loc='left')

for ds in ohc_annual:
    axs[1].plot(ds.df['year'], ds.df['data'], color='C0', zorder=99)
axs[1].set_yticks(np.arange(-300.0, 150.0, 100.))
axs[1].tick_params(labelbottom=False, length=0)
axs[1].set_title('Ocean Heat Content, change from 2005-2020 (ZJ)', loc='left')

for ds in sealevel_annual:
    axs[2].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[2].set_yticks(np.arange(0.0, 120.0, 20.))
axs[2].tick_params(labelbottom=False, length=0)
axs[2].set_title('Sea Level (mm)', loc='left')

for ds in tas_annual:
    axs[3].plot(ds.df['year'], ds.df['data'], color='C0', zorder=99)
axs[3].set_yticks(np.arange(0.0, 1.5, 0.2))
axs[3].set_title('Global Temperature, change from 1850-1900 ($\!^\circ\!$C)', loc='left')

axs[0].set_xticks([])
axs[1].set_xticks([])
axs[2].set_xticks([])
axs[3].set_xticks(np.arange(1960, 2030, 10))

plt.subplots_adjust(hspace=0.3)

sns.despine(right=True, top=True, left=True, bottom=True)

plt.savefig(figure_dir / "multi_indicator.png", dpi=300)
plt.savefig(figure_dir / "multi_indicator.svg", dpi=300)
plt.savefig(figure_dir / "multi_indicator.pdf", dpi=300)
plt.close()


# PLOT
STANDARD_PARAMETER_SET = {
    'axes.axisbelow': False,
    'axes.labelsize': 10,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
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

fig, axs = plt.subplots(4, 3, sharex=True)
fig.set_size_inches(12, 8)

for ds in ghg_annual:
    axs[0][0].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[0][0].set_yticks(np.arange(340, 430, 20))
axs[0][0].tick_params(labelbottom=False, length=0)
axs[0][0].set_title('Carbon Dioxide (ppm)', loc='left')

for ds in ch4_annual:
    axs[1][0].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[1][0].set_yticks(np.arange(1650, 1951, 50))
axs[1][0].tick_params(labelbottom=False, length=0)
axs[1][0].set_title('Methane (ppb)', loc='left')

for ds in n2o_annual:
    axs[2][0].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[2][0].set_yticks(np.arange(300, 350, 10))
axs[2][0].tick_params(labelbottom=False, length=0)
axs[2][0].set_title('Nitrous Oxide (ppb)', loc='left')

for ds in tas_annual:
    axs[3][0].plot(ds.df['year'], ds.df['data'], color='C0', zorder=99)
axs[3][0].set_yticks(np.arange(0.0, 1.7, 0.2))
axs[3][0].set_title('Global Temperature Change ($\!^\circ\!$C)', loc='left')

axs[0][0].set_xticks([])
axs[1][0].set_xticks([])
axs[2][0].set_xticks([])
axs[3][0].set_xticks(np.arange(1955, 2030, 10))

# Next column
for ds in ohc_annual:
    axs[0][1].plot(ds.df['year'], ds.df['data'], color='C0', zorder=99)
axs[0][1].set_yticks(np.arange(-300.0, 150.0, 100.))
axs[0][1].tick_params(labelbottom=False, length=0)
axs[0][1].set_title('Ocean Heat Content (ZJ)', loc='left')

for ds in sealevel_annual:
    axs[1][1].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[1][1].set_yticks(np.arange(0.0, 120.0, 20.))
axs[1][1].tick_params(labelbottom=False, length=0)
axs[1][1].set_title('Sea Level (mm)', loc='left')

for ds in seaice_annual:
    axs[2][1].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[2][1].set_yticks(np.arange(-2, 2, 0.5))
axs[2][1].tick_params(labelbottom=False, length=0)
axs[2][1].set_title('Arctic Sea-ice Extent (million km$^2$)', loc='left')

for ds in seaicesh_annual:
    axs[3][1].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[3][1].set_yticks(np.arange(-2, 2, 0.5))
axs[3][1].set_title('Antarctic Sea-ice Extent (million km$^2$)', loc='left')

axs[0][1].set_xticks([])
axs[1][1].set_xticks([])
axs[2][1].set_xticks([])
axs[3][1].set_xticks(np.arange(1960, 2030, 10))
axs[3][1].set_xlim(1955,final_year+0.99)

# Next column
for ds in glacier_annual:
    axs[0][2].plot(ds.df['year'], ds.df['data'], color='C0', zorder=99)
axs[0][2].set_yticks(np.arange(-30.0, 10.0, 5.))
axs[0][2].tick_params(labelbottom=False, length=0)
axs[0][2].set_title('Glacier Ice (m w.e.)', loc='left')

for ds in greenland_annual:
    axs[1][2].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[1][2].set_yticks(np.arange(-5000.0, 3000.0, 1000.))
axs[1][2].tick_params(labelbottom=False, length=0)
axs[1][2].set_title('Greenland Ice Sheet (Gt)', loc='left')

for ds in antarctic_annual:
    axs[2][2].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[2][2].set_yticks(np.arange(-3000.0, 2000., 1000.))
axs[2][2].tick_params(labelbottom=False, length=0)
axs[2][2].set_title('Antarctic Ice Sheet (Gt)', loc='left')

for ds in ph_annual:
    axs[3][2].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[3][2].set_yticks(np.arange(8.04, 8.125, 0.02))
axs[3][2].set_title('Ocean pH', loc='left')

axs[0][2].set_xticks([])
axs[1][2].set_xticks([])
axs[2][2].set_xticks([])
axs[3][2].set_xticks(np.arange(1960, 2030, 10))
axs[3][2].set_xlim(1955,final_year+0.99)

plt.subplots_adjust(hspace=0.3)

sns.despine(right=True, top=True, left=True, bottom=True)

plt.savefig(figure_dir / "multi_indicator_all.png", dpi=300)
plt.savefig(figure_dir / "multi_indicator_all.svg", dpi=300)
plt.savefig(figure_dir / "multi_indicator_all.pdf", dpi=300)
plt.close()

# PLOT
STANDARD_PARAMETER_SET = {
    'axes.axisbelow': False,
    'axes.labelsize': 10,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
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

fig, axs = plt.subplots(4, sharex=True)
fig.set_size_inches(6, 8)

for ds in ghg_annual:
    axs[0].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[0].set_yticks(np.arange(340, 430, 20))
axs[0].tick_params(labelbottom=False, length=0)
axs[0].set_title('Carbon Dioxide (ppm)', loc='left')

for ds in ohc_annual:
    axs[1].plot(ds.df['year'], ds.df['data'], color='C0', zorder=99)
axs[1].set_yticks(np.arange(-300.0, 150.0, 100.))
axs[1].tick_params(labelbottom=False, length=0)
axs[1].set_title('Ocean Heat Content, change from 2005-2020 (ZJ)', loc='left')

for ds in sealevel_annual:
    axs[2].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[2].set_yticks(np.arange(0.0, 120.0, 20.))
axs[2].tick_params(labelbottom=False, length=0)
axs[2].set_title('Sea Level (mm)', loc='left')

for ds in tas_annual:
    axs[3].plot(ds.df['year'], ds.df['data'], color='C0', zorder=99)
axs[3].set_yticks(np.arange(0.0, 1.5, 0.2))
axs[3].set_title('Global Temperature, change from 1850-1900 ($\!^\circ\!$C)', loc='left')

axs[0].set_xticks([])
axs[1].set_xticks([])
axs[2].set_xticks([])
axs[3].set_xticks(np.arange(1960, 2030, 10))

plt.subplots_adjust(hspace=0.3)

sns.despine(right=True, top=True, left=True, bottom=True)

plt.savefig(figure_dir / "multi_indicator.png", dpi=300)
plt.savefig(figure_dir / "multi_indicator.svg", dpi=300)
plt.savefig(figure_dir / "multi_indicator.pdf", dpi=300)
plt.close()


# PLOT SIX PANEL
STANDARD_PARAMETER_SET = {
    'axes.axisbelow': False,
    'axes.labelsize': 10,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
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

fig, axs = plt.subplots(3, 2, sharex=True)
fig.set_size_inches(12, 8)

for ds in ghg_annual:
    axs[0][0].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[0][0].set_yticks(np.arange(340, 430, 20))
axs[0][0].tick_params(labelbottom=False, length=0)
axs[0][0].set_title('Carbon Dioxide (ppm)', loc='left')

for ds in tas_annual:
    axs[1][0].plot(ds.df['year'], ds.df['data'], color='C0', zorder=99)
axs[1][0].set_yticks(np.arange(0.0, 1.6, 0.5))
axs[1][0].tick_params(labelbottom=False, length=0)
axs[1][0].set_title('Global Temperature Change ($\!^\circ\!$C)', loc='left')

for ds in ohc_annual:
    axs[2][0].plot(ds.df['year'], ds.df['data'], color='C0', zorder=99)
axs[2][0].set_yticks(np.arange(-300.0, 150.0, 100.))
axs[2][0].set_title('Ocean Heat Content (ZJ)', loc='left')

axs[0][0].set_xticks([])
axs[1][0].set_xticks([])
axs[2][0].set_xticks(np.arange(1955, 2030, 10))

# Next column
for ds in sealevel_annual:
    axs[0][1].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[0][1].set_yticks(np.arange(0.0, 121.0, 20.))
axs[0][1].tick_params(labelbottom=False, length=0)
axs[0][1].set_title('Sea Level (mm)', loc='left')

for ds in seaice_annual:
    axs[1][1].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)
axs[1][1].set_yticks(np.arange(-2, 2, 0.5))

for ds in seaicesh_annual:
    axs[1][1].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99, alpha=0.5)
axs[1][1].set_yticks(np.arange(-2.5, 2, 0.5))
axs[1][1].tick_params(labelbottom=False, length=0)
axs[1][1].text(1978,0.9,'Arctic',ha='right',color='C0', zorder=99)
axs[1][1].text(1978,-0.05,'Antarctic',ha='right',color='C0', zorder=99, alpha=0.5)

axs[1][1].set_title('Arctic and Antarctic Sea-ice Extent (million km$^2$)', loc='left')

for ds in glacier_annual:
    axs[2][1].plot(ds.df['year'], ds.df['data'], color='C0', zorder=99)
axs[2][1].set_yticks(np.arange(-30.0, 10.0, 5.))
axs[2][1].set_title('Glacier Ice (m w.e.)', loc='left')


axs[0][1].set_xticks([])
axs[1][1].set_xticks([])
axs[2][1].set_xticks(np.arange(1960, 2030, 10))
axs[2][1].set_xlim(1955,final_year+0.99)

# Next column

plt.subplots_adjust(hspace=0.3)

sns.despine(right=True, top=True, left=True, bottom=True)

plt.savefig(figure_dir / "multi_indicator_six.png", dpi=300)
plt.savefig(figure_dir / "multi_indicator_six.svg", dpi=300)
plt.savefig(figure_dir / "multi_indicator_six.pdf", dpi=300)

plt.close()


STANDARD_PARAMETER_SET = {
    'axes.axisbelow': False,
    'axes.labelsize': 10,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'axes.edgecolor': 'None',
    'axes.facecolor': 'None',

    'axes.grid.axis': 'y',
    'grid.color': 'None',
    'grid.alpha': 0.5,

    'axes.labelcolor': 'None',

    'axes.spines.left': False,
    'axes.spines.right': False,
    'axes.spines.top': False,

    'figure.facecolor': 'white',
    'lines.solid_capstyle': 'round',
    'patch.edgecolor': 'w',
    'patch.force_edgecolor': True,
    'text.color': 'dimgrey',

    'xtick.bottom': True,
    'xtick.color': 'None',
    'xtick.direction': 'out',
    'xtick.top': False,
    'xtick.labelbottom': True,

    'ytick.major.width': 0.4,
    'ytick.color': 'None',
    'ytick.direction': 'out',
    'ytick.left': False,
    'ytick.right': False
}

sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

fig, axs = plt.subplots(7, 2, sharex=True, gridspec_kw={'width_ratios': [5, 1]})
fig.set_size_inches(16, 12)

for ds in ghg_annual:
    axs[0][1].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)

for ds in tas_annual:
    axs[1][1].plot(ds.df['year'], ds.df['data'], color='C0', zorder=99)

for ds in ohc_annual:
    axs[2][1].plot(ds.df['year'], ds.df['data'], color='C0', zorder=99)

for ds in sealevel_annual:
    axs[3][1].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)

for ds in ph_annual:
    axs[4][1].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)

for ds in seaice_annual:
    axs[5][1].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)

for ds in glacier_annual:
    axs[6][1].plot(ds.get_year_axis(), ds.df['data'], color='C0', zorder=99)

plt.show()