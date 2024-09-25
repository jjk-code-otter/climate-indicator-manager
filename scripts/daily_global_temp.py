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
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt
import climind.stats.utils as utils

import climind.data_types.timeseries as ts

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR


def read_era_actual():
    filename = DATA_DIR / 'ManagedData' / 'Data' / 'ERA5' / 'era5_daily_series_2t_global.csv'

    years = []
    months = []
    days = []
    extents = []

    with open(filename, 'r') as f:
        for _ in range(19):
            f.readline()

        for line in f:
            columns = line.split(',')
            split_date = columns[0].split('-')

            year = int(split_date[0])
            month = int(split_date[1])
            day = int(split_date[2])

            years.append(year)
            months.append(month)
            days.append(day)
            extents.append(float(columns[1]))

    return ts.TimeSeriesIrregular(years, months, days, extents)


def get_era5_ensemble():
    era_ensemble_dir = DATA_DIR / 'ManagedData' / 'Data' / 'ERA5 ensemble'
    files = era_ensemble_dir.glob('era_5_ensemble*.csv')

    all_df = []

    for file in files:
        df = pd.read_csv(file)
        all_df.append(df)

    df = pd.concat(all_df, axis=0, ignore_index=True)

    all_ts = []
    for member in range(1,11):
        out_ts = ts.TimeSeriesIrregular(
            df.year.tolist(),
            df.month.tolist(),
            df.day.tolist(),
            df[f'member{member}'].tolist()
        )
        all_ts.append(out_ts)

    return all_ts


def get_jra55():
    jra_dir = DATA_DIR / 'JRA_temp'

    files = jra_dir.glob('tas_*.csv')

    all_df = []

    for file in files:
        df = pd.read_csv(file)
        all_df.append(df)

    df = pd.concat(all_df, axis=0, ignore_index=True)

    out_ts = ts.TimeSeriesIrregular(
        df.year.tolist(),
        df.month.tolist(),
        df.day.tolist(),
        df.data.tolist()
    )

    return out_ts


def get_jra3q():
    jra_dir = DATA_DIR / 'JRA_3Q_temp'

    files = jra_dir.glob('tas_*.csv')

    all_df = []

    for file in files:
        df = pd.read_csv(file)
        all_df.append(df)

    df = pd.concat(all_df, axis=0, ignore_index=True)

    out_ts = ts.TimeSeriesIrregular(
        df.year.tolist(),
        df.month.tolist(),
        df.day.tolist(),
        df.data.tolist()
    )

    return out_ts

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

final_year = 2023

project_dir = DATA_DIR / "ManagedData"
metadata_dir = METADATA_DIR

data_dir = project_dir / "Data"
fdata_dir = project_dir / "Formatted_Data"
figure_dir = project_dir / 'Figures'
log_dir = project_dir / 'Logs'
report_dir = project_dir / 'Reports'
report_dir.mkdir(exist_ok=True)

er_ensemble = get_era5_ensemble()

# Read in the whole archive then select the various subsets needed here
archive = dm.DataArchive.from_directory(metadata_dir)

ts_archive = archive.select({'variable': 'tas',
                             'type': 'timeseries',
                             'name': ['ERA5'],
                             'time_resolution': 'irregular'})

ds = ts_archive.read_datasets(data_dir)[0]

ts_archive = archive.select({'variable': 'tas',
                             'type': 'timeseries',
                             'name': ['Climate Reanalyzer'],
                             'time_resolution': 'irregular'})

cr = ts_archive.read_datasets(data_dir)[0]

# jr = get_jra55()

jra_tag = 'JRA-3Q'
# jra_tag = 'JRA-55'

jr = get_jra3q()
jra_extract_2023 = jr.select_year_range(2023, 2023)
jr = get_jra3q()
jra_extract_2024 = jr.select_year_range(2024, 2024)

er = read_era_actual()
era_extract_2023 = er.select_year_range(2023, 2023)
er = read_era_actual()
era_extract_2024 = er.select_year_range(2024, 2024)

sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)
plt.figure(figsize=(16, 9))

times = pd.date_range(start=f'2024-01-01', freq='1D', periods=365)

for erts in er_ensemble:
    chosen24 = copy.deepcopy(erts)
    chosen24.select_year_range(2024, 2024)
    chosen23 = copy.deepcopy(erts)
    chosen23.select_year_range(2023, 2023)

    plt.plot(times, chosen23.df.data-np.max(chosen24.df.data), color='black', alpha=0.3)
    plt.plot(times[0:208], chosen24.df.data-np.max(chosen24.df.data), color='black',alpha=0.3, linewidth=3)

plt.plot(times, jra_extract_2023.df.data - np.max(jra_extract_2024.df.data), color='blue')
plt.plot(times[0:204], jra_extract_2024.df.data - np.max(jra_extract_2024.df.data), color='blue', linewidth=3)
plt.plot(times, era_extract_2023.df.data - np.max(era_extract_2024.df.data), color='orange')
plt.plot(times[0:204], era_extract_2024.df.data - np.max(era_extract_2024.df.data), color='orange', linewidth=3)

from datetime import date
plt.gca().set_xlim(date(2024, 7, 1),date(2024,7, 31))
plt.gca().set_ylim(-0.53, 0.13)

plt.plot([date(2024, 7, 1),date(2024,7, 31)],[0,0],linestyle='--')

plt.title('Difference from highest daily global mean (K)', loc='left', fontsize=24)

plt.savefig(figure_dir / 'relative_to_max.png')
plt.close('all')


for erts in er_ensemble:
    chosen = copy.deepcopy(erts)
    chosen.select_year_range(2023, 2023)
    plt.plot(chosen.df.data-np.mean(chosen.df.data), color='lightgrey')
    chosen = copy.deepcopy(erts)
    chosen.select_year_range(2024, 2024)
    plt.plot(chosen.df.data-np.mean(chosen.df.data), color='lightgrey')

# plt.plot(jra_extract_2023.df.data - np.mean(jra_extract_2023.df.data), color='blue')
# plt.plot(jra_extract_2024.df.data - np.mean(jra_extract_2024.df.data), color='blue')
# plt.plot(era_extract_2023.df.data - np.mean(era_extract_2023.df.data), color='orange')
# plt.plot(era_extract_2024.df.data - np.mean(era_extract_2024.df.data), color='orange')
# plt.show()
# plt.close()


for erts in er_ensemble:
    chosen = copy.deepcopy(erts)
    chosen.select_year_range(2023, 2023)
    plt.plot(chosen.df.data - era_extract_2023.df.data, color='black', alpha=0.3)
    chosen = copy.deepcopy(erts)
    chosen.select_year_range(2024, 2024)
    plt.plot(chosen.df.data - era_extract_2024.df.data, color='black', alpha=0.3)

# plt.plot(jra_extract_2023.df.data - era_extract_2023.df.data, color='blue')
# plt.plot(jra_extract_2024.df.data - era_extract_2024.df.data, color='blue')
# plt.show()
# plt.close()

for erts in er_ensemble:
    chosen = copy.deepcopy(erts)
    chosen.select_year_range(2023, 2023)
    plt.plot(chosen.df.data, color='lightgrey')
    chosen = copy.deepcopy(erts)
    chosen.select_year_range(2024, 2024)
    plt.plot(chosen.df.data, color='lightgrey')

# plt.plot(jra_extract_2023.df.data, color='blue')
# plt.plot(jra_extract_2024.df.data, color='blue')
# plt.plot(era_extract_2023.df.data, color='orange')
# plt.plot(era_extract_2024.df.data, color='orange')
# plt.show()
# plt.close()

jr = get_jra3q()


sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)
plt.figure(figsize=(16, 9))

d = 0.12
plt.fill_between([0, 365], [1.5 + d, 1.5 + d], [1.5 - d, 1.5 - d], color='lightblue', alpha=0.5, zorder=0)
plt.fill_between([0, 365], [2 + d, 2 + d], [2 - d, 2 - d], color='lightblue', alpha=0.5, zorder=0)

for year in range(1940, 2024):
    ds2 = copy.deepcopy(ds)
    sub = ds2.select_year_range(year, year)

    zord = 99
    linewidth = 1
    if year == 2016:
        color = 'firebrick'
        linewidth = 3
    elif year == 2020:
        color = 'dodgerblue'
        linewidth = 3
    elif year == 2023:
        color = 'black'
        zord = 100
        linewidth = 3
    else:
        color = 'lightgrey'
        zord = 1

    plt.plot(sub.df.data, color=color, zorder=zord, linewidth=linewidth)

plt.gca().set_xlabel('Day in year (0-364')
plt.gca().set_ylabel('Daily anomaly (degC)')
plt.gca().set_title('Daily anomalies from ERA5 wrt 1850-1900', loc='left', fontsize=24)

plt.savefig(figure_dir / 'daily_anomalies_with_limits.png')
plt.savefig(figure_dir / 'daily_anomalies_with_limits.svg')
plt.close('all')

print(np.count_nonzero(ds.df.data > 1.5))
print(np.count_nonzero(ds.df.data > 1.5 + d))
print(np.count_nonzero(ds.df.data > 1.5 - d))

print(np.count_nonzero(ds.df.data > 2))
print(np.count_nonzero(ds.df.data > 2 + d))
print(np.count_nonzero(ds.df.data > 2 - d))

ds.rebaseline(1981, 2010)
ds = ds.select_year_range(1980, 2023)
cr.rebaseline(1981, 2010)
cr = cr.select_year_range(1980, 2023)
jr.rebaseline(1981, 2010)
jr = jr.select_year_range(1980, 2023)

plt.figure(figsize=(16, 9))
plt.plot(cr.df.date, ds.df.data - cr.df.data)
for y in range(1980, 2025):
    times = pd.date_range(start=f'{y}-01-01', freq='1D', periods=1)
    plt.plot([times[0], times[0]], [-0.3, 0.4], color='lightgrey', alpha=0.5)
plt.gca().set_xlabel('Date')
plt.gca().set_ylabel('Anomaly difference (degC)')
plt.gca().set_ylim(-0.3, 0.4)
plt.gca().set_title('Difference between daily global temperature anomalies from ERA5 and CFSR', loc='left', fontsize=24)

plt.savefig(figure_dir / 'daily_anomalies_diff.png')
plt.savefig(figure_dir / 'daily_anomalies_diff.svg')
plt.close('all')

plt.figure(figsize=(16, 9))
plt.plot(ds.df.date, ds.df.data - jr.df.data)
for y in range(1980, 2025):
    times = pd.date_range(start=f'{y}-01-01', freq='1D', periods=1)
    plt.plot([times[0], times[0]], [-0.3, 0.4], color='lightgrey', alpha=0.5)
plt.gca().set_xlabel('Date')
plt.gca().set_ylabel('Anomaly difference (degC)')
plt.gca().set_ylim(-0.3, 0.4)
plt.gca().set_title(f'Difference between daily global temperature anomalies from ERA5 and {jra_tag}', loc='left',
                    fontsize=24)

plt.savefig(figure_dir / f'daily_anomalies_diff_{jra_tag}.png')
plt.savefig(figure_dir / f'daily_anomalies_diff_{jra_tag}.svg')
plt.close('all')

plt.figure(figsize=(16, 9))

all_stds = []

for year in range(1980, 2024):
    ds2 = copy.deepcopy(ds)
    sub = ds2.select_year_range(year, year)

    jr2 = copy.deepcopy(jr)
    subjr = jr2.select_year_range(year, year)

    color = '#dddddd'
    zord = 1
    if year % 10 == 0:
        color = 'firebrick'
        zord = 99

    #    plt.plot((sub.df.data-subjr.df.data), color=color, zorder=zord)
    plt.plot((sub.df.data - subjr.df.data) - np.mean(sub.df.data - subjr.df.data), color=color, zorder=zord)

    all_stds.append(np.std(sub.df.data - subjr.df.data))  # / np.sqrt(2))

print("Average annual standard deviation of JRA-ERA diffs")
print(f"{1.96 * np.mean(all_stds):.3f}")

plt.gca().set_xlabel('Day in year (0-364')
plt.gca().set_ylabel('Daily anomaly difference (degC)')
plt.gca().set_title(f'Daily anomalies difference between {jra_tag} and ERA5', loc='left', fontsize=24)

plt.savefig(figure_dir / 'daily_anomalies_diffs.png')
plt.savefig(figure_dir / 'daily_anomalies_diffs.svg')
plt.close('all')
