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

def convert_to_percentages(ts, min_screen=90, max_screen=40):
    n_years = len(ts.df.data)

    years = np.array(ts.get_year_axis())
    datas = np.array(ts.df.data)

    year0 = years[0]
    yearz = years[-1]

    max_data = np.max(datas)
    min_data = np.min(datas)

    outstr = '100,0 0, 0'
    for i in range(n_years):
        year = 100 * (years[i] - year0) / (yearz - year0)
        data = min_screen + (max_screen - min_screen) * (datas[i] - min_data) / (max_data - min_data)

        outstr += f' {year:.2f}, {data:.2f}'

    return outstr

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
        'name': ['HadCRUT5']
    }
)
all_tas_datasets = tas_archive.read_datasets(data_dir)
tas_annual = []
for ds in all_tas_datasets:
    ds.rebaseline(1981, 2010)
    annual = ds.make_annual()
    tas_annual.append(annual)

tas_annual = tas_annual[0]
outstr = convert_to_percentages(tas_annual)

print("Global mean temperature")
print(outstr)

seaice_archive = archive.select({'variable': 'arctic_ice', 'type': 'timeseries', 'time_resolution': 'monthly'})
seaice_data = seaice_archive.read_datasets(data_dir)
seaice_annual = []
for ds in seaice_data:
    ds.rebaseline(1981, 2010)
    annual = ds.make_annual_by_selecting_month(9)
    seaice_annual.append(annual)

seaice_annual = seaice_annual[0]
outstr = convert_to_percentages(seaice_annual)

print("NH Arctic sea ice extent")
print(outstr)


ghg_archive = archive.select(
    {
        'variable': 'co2', 'type': 'timeseries', 'time_resolution': 'monthly',
        'name': 'WDCGG'
    }
)
ghg_annual = ghg_archive.read_datasets(data_dir)[0]
outstr = convert_to_percentages(ghg_annual)

print("CO2 monthly...")
print(outstr)


ohc_archive = archive.select(
    {
        'variable': 'ohc2k', 'type': 'timeseries', 'time_resolution': 'annual',
        'name': 'Miniere'
    }
)
ohc_annual = ohc_archive.read_datasets(data_dir)
for ds in ohc_annual:
    ds.rebaseline(2005, 2020)
    # ds.add_year(2022, 96.74878325523227, 8.430242333320507)
outstr = convert_to_percentages(ohc_annual[0])
print("OHC annual...")
print(outstr)

sealevel_archive = archive.select(
    {
        'variable': 'sealevel', 'type': 'timeseries', 'name': ['AVISO ftp']
    }
)
sealevel_annual = sealevel_archive.read_datasets(data_dir)
for ds in sealevel_annual:
    ds.select_year_range(1993,2023)
outstr = convert_to_percentages(sealevel_annual[0])
print("Sea level annual...")
print(outstr)


mhw_archive = archive.select(
    {
        "type": "timeseries", "variable": "mhw", "time_resolution": "annual"
    }
)
mhw_annual = mhw_archive.read_datasets(data_dir)
outstr = convert_to_percentages(mhw_annual[0])
print("Mean heatwave annual...")
print(outstr)


glacier_archive = archive.select(
    {
        'variable': 'glacier', 'type': 'timeseries', 'time_resolution': 'annual'
    }
)
glacier_annual = glacier_archive.read_datasets(data_dir)
outstr = convert_to_percentages(glacier_annual[0])
print("Glacier annual...")
print(outstr)

greenland_archive = archive.select(
    {
        'variable': 'greenland', 'type': 'timeseries', 'time_resolution': 'monthly', 'name': 'IMBIE 2021 Greenland'
    }
)
greenland_annual = greenland_archive.read_datasets(data_dir)
for ds in greenland_annual:
    ds.zero_on_month(2005, 7)
outstr = convert_to_percentages(greenland_annual[0])
print("Greenland annual...")
print(outstr)

antarctic_archive = archive.select(
    {
        'variable': 'antarctica', 'type': 'timeseries', 'time_resolution': 'monthly', 'name': 'IMBIE 2021 Antarctica'
    }
)
antarctic_annual = antarctic_archive.read_datasets(data_dir)
for ds in antarctic_annual:
    ds.zero_on_month(2005, 6)
outstr = convert_to_percentages(antarctic_annual[0])
print("Antarctic annual...")
print(outstr)

nino_archive = archive.select(
    {
        'variable': 'nino34', 'type': 'timeseries', 'time_resolution': 'monthly', 'name': 'Nino34'
    }
)
nino_annual = nino_archive.read_datasets(data_dir)
for ds in nino_annual:
    ds.rebaseline(1991, 2020)
    ds.select_year_range(1950, 2024)
outstr = convert_to_percentages(nino_annual[0])
print("Nino annual...")
print(outstr)



assert False

ohc_archive = archive.select(
    {
        'variable': 'ohc2k', 'type': 'timeseries', 'time_resolution': 'annual'
    }
)
ohc_annual = ohc_archive.read_datasets(data_dir)
for ds in ohc_annual:
    ds.rebaseline(2005, 2020)
    # ds.add_year(2022, 96.74878325523227, 8.430242333320507)

ph_archive = archive.select(
    {
        'variable': 'ph', 'type': 'timeseries', 'time_resolution': 'annual',
        'name': ['CMEMS']
    }
)
ph_annual = ph_archive.read_datasets(data_dir)

sealevel_archive = archive.select(
    {
        'variable': 'sealevel', 'type': 'timeseries', 'name': ['AVISO ftp', 'NASA Sealevel']
    }
)
sealevel_annual = sealevel_archive.read_datasets(data_dir)


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
