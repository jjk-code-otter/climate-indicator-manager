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

from climind.config.config import DATA_DIR, CLIMATOLOGY
from climind.definitions import METADATA_DIR
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

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


def read_nsidc_daily(sea_ice_file, final_year):
    df = pd.read_csv(sea_ice_file, skiprows=[1])
    df.columns = df.columns.str.replace(' ', '')
    df['date'] = pd.to_datetime(dict(year=df['Year'], month=df['Month'], day=df['Day']))
    df = df.set_index('date')

    # Ensure there is an entry for every day from the start to the end
    t_index = pd.DatetimeIndex(pd.date_range(start='1979-01-01', end=f'{final_year}-12-31', freq='D'))
    df_rsmpld = df.reindex(t_index, method=None)
    df = df_rsmpld

    df.Year = t_index.year
    df.Month = t_index.month
    df.Day = t_index.day

    return df


def calculate_climatology(climatology_start_year, climatology_end_year, df):
    # Calculate climatology and fill out repeating climatology to full length of series
    df2 = df[df['Year'] >= climatology_start_year]
    df2 = df2[df2['Year'] <= climatology_end_year]

    climatology = df2.groupby([df2.index.month, df2.index.day]).mean()
    climatology = climatology.Extent[zip(df.index.month, df.index.day)]
    climatology.index = df.index

    climatology_stdev = df2.groupby([df2.index.month, df2.index.day]).std()
    climatology_stdev = climatology_stdev.Extent[zip(df.index.month, df.index.day)]
    climatology_stdev.index = df.index

    return climatology, climatology_stdev


def calculate_historical_stats(year_to_exclude, df):
    # Remove chosen year and calculate stats (max, min) on the remainder
    df3 = df[df['Year'] != year_to_exclude]

    climatology_max = df3.groupby([df3.index.month, df3.index.day]).max()
    climatology_max = climatology_max.Extent[zip(df.index.month, df.index.day)]
    climatology_max.index = df.index

    climatology_min = df3.groupby([df3.index.month, df3.index.day]).min()
    climatology_min = climatology_min.Extent[zip(df.index.month, df.index.day)]
    climatology_min.index = df.index

    climatology_mean = df3.groupby([df3.index.month, df3.index.day]).mean()
    climatology_mean = climatology_mean.Extent[zip(df.index.month, df.index.day)]
    climatology_mean.index = df.index

    climatology_stdev = df3.groupby([df3.index.month, df3.index.day]).std()
    climatology_stdev = climatology_stdev.Extent[zip(df.index.month, df.index.day)]
    climatology_stdev.index = df.index

    return climatology_min, climatology_max, climatology_mean, climatology_stdev


def plot_timeseries(df, project_dir, image_filename, variable, xlabel, ylabel, title, subtitle):
    # Plot simple anomaly series
    plt.figure(figsize=(16, 9))

    dfplot = df[df[variable].notna()]  # Drop the gaps so it plots nicely data are every other day at start
    plt.plot(dfplot[variable], color='red')

    plt.gca().set_xlabel(xlabel)
    plt.gca().set_ylabel(ylabel)
    plt.gca().set_title(title, pad=35, fontdict={'fontsize': 35},
                        loc='left')
    ylim = plt.gca().get_ylim()
    yloc = ylim[1] + 0.025 * (ylim[1] - ylim[0])
    plt.text(plt.gca().get_xlim()[0], yloc, subtitle, fontdict={'fontsize': 20})

    plt.savefig(project_dir / 'Figures' / image_filename)
    plt.close()


def plot_simple_timeseries(df, project_dir, image_filename):
    plot_timeseries(df, project_dir, image_filename,
                    'anomalies', 'Date', 'million km$^2$',
                    'Daily Antarctic Sea-ice Extent 1979-2023 (million km$^2$)',
                    'Difference from 1991-2020 average')


def plot_stdev_timeseries(df, project_dir, image_filename):
    plot_timeseries(df, project_dir, image_filename,
                    'standard_deviations', 'Date', 'Standard deviations',
                    'Daily Antarctic Sea-ice Extent 1979-2023',
                    'Standard deviations from the 1991-2020 mean')


def plot_one_in_a(df, project_dir, image_filename, log=True):
    # Plot simple anomaly series
    plt.figure(figsize=(16, 9))

    dfplot = df[df['one_in_a'].notna()]  # Drop the gaps so it plots nicely data are every other day at start
    plt.plot(dfplot.one_in_a, color='red')
    if log:
        plt.yscale('log')

    from matplotlib.ticker import ScalarFormatter
    ax = plt.gca()
    ax.set_yticks([1, 10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000])
    for axis in [ax.yaxis]:
        formatter = ScalarFormatter()
        formatter.set_scientific(False)
        axis.set_major_formatter(formatter)

    plt.gca().set_xlabel('Date')
    plt.gca().set_ylabel('One in how many years?')
    plt.gca().set_title('Daily Antarctic Sea-ice Extent 1979-2023', pad=35, fontdict={'fontsize': 35},
                        loc='left')
    ylim = plt.gca().get_ylim()
    yloc = ylim[1] + 0.025 * (ylim[1] - ylim[0])
    plt.text(plt.gca().get_xlim()[0], yloc,
             'Expressed as a one-in-N year event',
             fontdict={'fontsize': 20})

    plt.savefig(project_dir / 'Figures' / image_filename)
    plt.close()


def plot_annual_cycle(df, project_dir, image_filename, stdev=False, nh=False):
    # Plot annual cycle plot
    plt.figure(figsize=(16, 9))

    # Annual cycle
    if stdev:
        plt.plot(df[df['Year'] == final_year].climatology + df[df['Year'] == final_year].stdev, color='lightgrey')
        plt.plot(df[df['Year'] == final_year].climatology - df[df['Year'] == final_year].stdev, color='lightgrey')
    else:
        plt.plot(df[df['Year'] == final_year].cmin, color='lightgrey')
        plt.plot(df[df['Year'] == final_year].cmax, color='lightgrey')
    plt.plot(df[df['Year'] == final_year].Extent, color='red', linewidth=3)
    plt.plot(df[df['Year'] == final_year].climatology, color='black')

    # Anomalies
    if stdev:
        plt.plot(df[df['Year'] == final_year].stdev, color='lightgrey')
        plt.plot(-1 * df[df['Year'] == final_year].stdev, color='lightgrey')
    else:
        plt.plot(df[df['Year'] == final_year].cmax - df[df['Year'] == final_year].climatology, color='lightgrey')
        plt.plot(df[df['Year'] == final_year].cmin - df[df['Year'] == final_year].climatology, color='lightgrey')
    plt.plot(0 * df[df['Year'] == final_year].climatology, color='black')
    plt.plot(df[df['Year'] == final_year].Extent - df[df['Year'] == final_year].climatology, color='red', linewidth=3)
    sns.despine(right=True, top=True, left=True)

    print(min(df[df['Year'] == final_year].Extent - df[df['Year'] == final_year].climatology))
    print(min(df[df['Year'] == final_year].Extent - df[df['Year'] == final_year].cmin))

    if nh:
        plt.gca().set_yticks([-4, -3, -2, -1, 0, 1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18])
    else:
        plt.gca().set_yticks([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 10, 15, 20, 25])

    plt.gca().set_xlabel('Date')
    plt.gca().set_ylabel('million km$^2$')
    if nh:
        plt.gca().set_title('Daily Arctic Sea-ice Extent 1979-2023 (million km$^2$)', pad=35,
                            fontdict={'fontsize': 35},
                            loc='left')
    else:
        plt.gca().set_title('Daily Antarctic Sea-ice Extent 1979-2023 (million km$^2$)', pad=35,
                            fontdict={'fontsize': 35},
                            loc='left')

    ylim = plt.gca().get_ylim()
    xlim = plt.gca().get_xlim()
    if nh:
        yloc = ylim[1] + 0.05 * (ylim[1] - ylim[0])
        plt.text(plt.gca().get_xlim()[0], yloc,
                 '1 million km$^2$ is the area of Egypt, 10 million km$^2$ is about the area of Canada',
                 fontdict={'fontsize': 20})
    else:
        yloc = ylim[1] - 0.09 * (ylim[1] - ylim[0])
        plt.text(plt.gca().get_xlim()[0], yloc,
                 '1 million km$^2$ is the area of Egypt, 10 million km$^2$ is about the area of Canada',
                 fontdict={'fontsize': 20})

    if stdev:
        yloc = ylim[0] + 0.82 * (ylim[1] - ylim[0])
        xloc = xlim[0] + 0.65 * (xlim[1] - xlim[0])
        plt.text(xloc, yloc, 'Mean plus standard deviation', color='lightgrey', fontdict={'fontsize': 18})

        yloc = ylim[0] + 0.73 * (ylim[1] - ylim[0])
        xloc = xlim[0] + 0.65 * (xlim[1] - xlim[0])
        plt.text(xloc, yloc, 'Mean minus standard deviation', color='lightgrey', fontdict={'fontsize': 18})
    else:
        if nh:
            yloc = ylim[0] + 0.97 * (ylim[1] - ylim[0])
            xloc = xlim[0] + 0.155 * (xlim[1] - xlim[0])
            plt.text(xloc, yloc, 'Record high', color='lightgrey', fontdict={'fontsize': 18})

            yloc = ylim[0] + 0.74 * (ylim[1] - ylim[0])
            xloc = xlim[0] + 0.155 * (xlim[1] - xlim[0])
            plt.text(xloc, yloc, 'Record low', color='lightgrey', fontdict={'fontsize': 18})
        else:
            yloc = ylim[0] + 0.85 * (ylim[1] - ylim[0])
            xloc = xlim[0] + 0.65 * (xlim[1] - xlim[0])
            plt.text(xloc, yloc, 'Record high', color='lightgrey', fontdict={'fontsize': 18})

            yloc = ylim[0] + 0.7 * (ylim[1] - ylim[0])
            xloc = xlim[0] + 0.65 * (xlim[1] - xlim[0])
            plt.text(xloc, yloc, 'Record low', color='lightgrey', fontdict={'fontsize': 18})

    if nh:
        yloc = ylim[0] + 0.43 * (ylim[1] - ylim[0])
        xloc = xlim[0] + 0.62 * (xlim[1] - xlim[0])
        plt.text(xloc, yloc, '2023 actual extent', color='red', fontdict={'fontsize': 18})

        yloc = ylim[0] + 0.08 * (ylim[1] - ylim[0])
        xloc = xlim[0] + 0.62 * (xlim[1] - xlim[0])
        plt.text(xloc, yloc, '2023 difference from long-term mean', color='red', fontdict={'fontsize': 18})
    else:
        yloc = ylim[0] + 0.63 * (ylim[1] - ylim[0])
        xloc = xlim[0] + 0.62 * (xlim[1] - xlim[0])
        plt.text(xloc, yloc, '2023 actual extent', color='red', fontdict={'fontsize': 18})

        yloc = ylim[0] + 0.05 * (ylim[1] - ylim[0])
        xloc = xlim[0] + 0.62 * (xlim[1] - xlim[0])
        plt.text(xloc, yloc, '2023 difference from long-term mean', color='red', fontdict={'fontsize': 18})

    if nh:
        plt.gca().set_ylim(-5, 19)
    else:
        plt.gca().set_ylim(-5, 22)

    plt.savefig(project_dir / 'Figures' / image_filename)
    plt.close()


project_dir = DATA_DIR / "ManagedData"
data_dir = project_dir / "Data"

sea_ice_file = data_dir / "NSIDC SH" / "S_seaice_extent_daily_v3.0.csv"

final_year = 2023

df = read_nsidc_daily(sea_ice_file, final_year)
climatology, climatology_stdev = calculate_climatology(1991, 2020, df)
climatology_min, climatology_max, full_series_mean, full_series_stdev = calculate_historical_stats(final_year, df)

# Copy results back into main dataframe
df['climatology'] = climatology
df['cmax'] = climatology_max
df['cmin'] = climatology_min
df['anomalies'] = df.Extent - climatology
df['standard_deviations'] = df.anomalies / climatology_stdev
df['stdev'] = climatology_stdev

sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

# Do some plots
plot_simple_timeseries(df, project_dir, 'antarctic_daily_long_view.png')
plot_stdev_timeseries(df, project_dir, 'antarctic_daily_long_view_stdev.png')
plot_annual_cycle(df, project_dir, 'antarctic_daily.png')
plot_annual_cycle(df, project_dir, 'antarctic_daily_stdev.png', stdev=True)

df['anomalies2'] = df.Extent - full_series_mean
df['standard_deviations2'] = df.anomalies2 / full_series_stdev

import scipy.stats

p_values = scipy.stats.norm.sf(abs(df['standard_deviations2'])) * 2
df['one_in_a'] = 1.0 / p_values

plot_one_in_a(df, project_dir, 'antarctic_daily_one_in_a.png')
plot_one_in_a(df, project_dir, 'antarctic_daily_one_in_a_non_log.png', log=False)

# Plot a histogram
import numpy as np

n, bins, patches = plt.hist(df.standard_deviations2, bins=50, density=True)
sigma = 1.0
mu = 0.0
y = ((1 / (np.sqrt(2 * np.pi) * sigma)) *
     np.exp(-0.5 * (1 / sigma * (bins - mu)) ** 2))
plt.plot(bins, y, '--')
plt.savefig(project_dir / 'Figures' / 'antarctic_sea_ice_histogram')
plt.close()

sea_ice_file = data_dir / "NSIDC" / "N_seaice_extent_daily_v3.0.csv"

final_year = 2023

df = read_nsidc_daily(sea_ice_file, final_year)
climatology, climatology_stdev = calculate_climatology(1991, 2020, df)
climatology_min, climatology_max, full_series_mean, full_series_stdev = calculate_historical_stats(final_year, df)

# Copy results back into main dataframe
df['climatology'] = climatology
df['cmax'] = climatology_max
df['cmin'] = climatology_min
df['anomalies'] = df.Extent - climatology
df['standard_deviations'] = df.anomalies / climatology_stdev
df['stdev'] = climatology_stdev

sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

# Do some plots
plot_timeseries(df, project_dir, 'arctic_daily_long_view.png',
                'anomalies', 'Date', 'million km$^2$',
                'Daily Arctic Sea-ice Extent 1979-2023 (million km$^2$)',
                'Difference from 1991-2020 average')
plot_annual_cycle(df, project_dir, 'arctic_daily.png', nh=True)
