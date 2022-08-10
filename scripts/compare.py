from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import numpy as np

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

import climind.data_manager.processing as dm


def read_new(new_name, ds):
    filename = DATA_DIR / 'New folder' / f'new_{new_name}_{ds}.csv'
    with open(filename, 'r') as f:
        for line in f:
            if 'time,year,data' in line:
                break

        years = []
        anoms = []

        for line in f:
            if 'end data' in line:
                break
            else:
                columns = line.split(',')
                years.append(int(columns[1]))
                anoms.append(float(columns[2]))

    input_data = {'Year': years, 'data': anoms}

    df = pd.DataFrame(input_data)

    return df


def calculate_trends(all_datasets: list, y1: int, y2: int):
    """
    given a set of data sets, return the mean, min and max trends from the data sets calculated
    using OLS between the chosen years.

    Parameters
    ----------
    all_datasets : list
        list of data sets
    y1 : int
        first year for trend
    y2 : int
        last year for trend

    Returns
    -------

    """
    all_trends = []

    for ds in all_datasets:
        subset = ds.loc[(ds['Year'] >= y1) & (ds['Year'] <= y2) & (~ds['data'].isnull())]

        if len(subset) > 25:
            trends = np.polyfit(subset['Year'], subset['data'], 1)
            all_trends.append(trends[0] * 10.)

    # calculate the mean trend and max and min trends
    mean_trend = np.mean(all_trends)
    max_trend = np.max(all_trends)
    min_trend = np.min(all_trends)

    return mean_trend, min_trend, max_trend


def calculate_ranks(all_datasets: list, y1: int):
    """
    given a set of data sets, return the min and max ranks from the data sets.

    Parameters
    ----------
    all_datasets : list
        list of data sets
    y1 : int
        year to calculate trends for

    Returns
    -------

    """
    all_ranks = []

    for ds in all_datasets:
        ranked = ds.rank(method='min', ascending=False)
        subrank = ranked[ds['Year'] == y1]['data']
        if len(subrank) == 0:
            rank = None
        else:
            rank = int(subrank.iloc[0])

        all_ranks.append(rank)

    # calculate the mean trend and max and min trends
    max_rank = np.max(all_ranks)
    min_rank = np.min(all_ranks)

    return min_rank, max_rank


def calculate_values(all_datasets: list, y1: int):
    """
    given a set of data sets, return the mean min and max values from the data sets for specified year.

    Parameters
    ----------
    all_datasets : list
        list of data sets
    y1 : int
        year to calculate values for

    Returns
    -------

    """
    all_ranks = []

    for ds in all_datasets:
        value = ds[ds['Year'] == y1]['data']
        all_ranks.append(value.values[0])

    # calculate the mean trend and max and min trends
    mean_rank = np.mean(all_ranks)
    max_rank = np.max(all_ranks)
    min_rank = np.min(all_ranks)

    return mean_rank, min_rank, max_rank


def trends_plot(out_dir, superset, image_filename, title, names,
                extra_series=None, extra_name=None):
    if extra_series is not None:
        superset.append(extra_series)
        names.append(extra_name)

    colours = ['#f33d3d', '#ffd465', '#9dd742',
               '#84d1cd', '#848dd1', '#cf84d1', '#b4b4b4']
    sns.set(font='Franklin Gothic Book', rc={
        'axes.axisbelow': False,
        'axes.labelsize': 25,
        'xtick.labelsize': 15,
        'ytick.labelsize': 25,
        'axes.edgecolor': 'lightgrey',
        'axes.facecolor': 'None',

        #        'axes.grid.axis': 'y',
        #        'grid.color': 'lightgrey',
        'grid.alpha': 0.0,

        'axes.labelcolor': 'dimgrey',

        'axes.spines.left': True,
        'axes.spines.right': False,
        'axes.spines.top': False,
        'axes.spines.bottom': False,

        'figure.facecolor': 'white',
        'lines.solid_capstyle': 'round',
        'patch.edgecolor': 'w',
        'patch.force_edgecolor': True,
        'text.color': 'dimgrey',

        'xtick.bottom': False,
        'xtick.top': False,
        'xtick.labelbottom': False,

        'ytick.major.width': 0.4,
        'ytick.color': 'dimgrey',
        'ytick.direction': 'out',
        'ytick.left': False,
        'ytick.right': False})

    plt.figure(figsize=[16, 9])

    plt.plot([1901, 2022], [0., 0.], color='lightgrey')

    grey = True

    for start_end in [[1901, 1930],
                      [1931, 1960],
                      [1961, 1990],
                      [1991, 2021]]:

        y1 = start_end[0]
        y2 = start_end[1]

        if grey:
            grey = False
            rect = patches.Rectangle((y1, -0.2), y2 - y1 + 1, 1.2, color='#eeeeee')
            plt.gca().add_patch(rect)
        else:
            grey = True

        # calculate trend for each data set
        for pos_ind, all_datasets in enumerate(superset):
            mean_trend, min_trend, max_trend = calculate_trends(all_datasets, y1, y2)
            min_rank, max_rank = calculate_ranks(all_datasets, 2021)
            mean_value, min_value, max_value = calculate_values(all_datasets, 2021)

            print(f'{names[pos_ind]}  2021 {mean_value:.2f} ({min_value:.2f}-{max_value:.2f}), rank: {min_rank}-{max_rank}')
            print(f'{start_end[0]}-{start_end[1]} {mean_trend:.2f} ({min_trend:.2f}-{max_trend:.2f})')

            interset_delta = 0.4
            width = (30. - 2 * interset_delta) / 7.
            rect_xstart = y1 + interset_delta + (width * pos_ind)
            mid_point = rect_xstart + width / 2.
            delta = 0.3
            section_mid_point = (y2 + y1) / 2.

            plt.text(section_mid_point, -0.25, f'Trends', fontsize=25, ha='center')
            plt.text(section_mid_point, -0.30, f'{y1}-{y2}', fontsize=25, ha='center')

            # plot a coloured bar
            rect = patches.Rectangle((rect_xstart + delta, 0), width - 2 * delta, mean_trend,
                                     linewidth=0, edgecolor=None, facecolor=colours[pos_ind])
            plt.gca().add_patch(rect)
            plt.plot([mid_point, mid_point], [min_trend, max_trend], color='black')

    for name_index, name in enumerate(names):
        plt.text(1902, 0.55 - name_index * 0.05, name,
                 fontsize=25, ha='left', color=colours[name_index])

        # plot the uncertainty range
    plt.ylabel('Trend ($\!^\circ\!$C/decade)', labelpad=10)
    plt.yticks(np.arange(-0.2, 0.8, 0.2))
    plt.gca().set_ylim(-0.2, 0.6)

    plt.gca().set_title(title, pad=45, fontdict={'fontsize': 40}, loc='left')

    plt.savefig(out_dir / image_filename)
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))
    #    plt.show()
    plt.close()


def neat_plot(out_dir: Path, all_datasets: list, image_filename: str, title: str, names: list):
    sns.set(font='Franklin Gothic Book', rc={
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

        'ytick.major.width': 0.4,
        'ytick.color': 'dimgrey',
        'ytick.direction': 'out',
        'ytick.left': False,
        'ytick.right': False})

    fancy_units = {"degC": "$\!^\circ\!$C", "zJ": "zJ"}

    colours = ['#2a2a2a', '#e69f00', '#56b4e9', '#888888', '#0072b2', '#d55e00']

    zords = []
    plt.figure(figsize=[16, 9])
    for i, ds in enumerate(all_datasets):
        col = colours[i]
        zord = 10 - i
        zords.append(zord)
        plt.plot(ds['Year'], ds['data'], label=names[i], color=col, zorder=zord)
    sns.despine(right=True, top=True, left=True)

    plot_units = 'degC'
    if plot_units in fancy_units:
        plot_units = fancy_units[plot_units]
    plt.xlabel('Year')
    plt.ylabel(plot_units, rotation=0, labelpad=10)

    ylims = plt.gca().get_ylim()
    ylo = 0.2 * (1 + (ylims[0] // 0.2))
    yhi = 0.2 * (1 + (ylims[1] // 0.2))
    yticks = np.arange(ylo, yhi, 0.2)

    if len(yticks) > 10:
        ylo = 0.5 * (1 + (ylims[0] // 0.5))
        yhi = 0.5 * (1 + (ylims[1] // 0.5))
        yticks = np.arange(ylo, yhi, 0.5)

    xlims = plt.gca().get_xlim()
    xlo = 20 * (1 + (xlims[0] // 20))
    xhi = 20 * (1 + (xlims[1] // 20))

    plt.yticks(yticks)
    # plt.yticks(np.arange(-0.2, 1.4, 0.2))
    plt.xticks(np.arange(xlo, xhi, 20))

    plt.tick_params(
        axis='y',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        left=False,  # ticks along the bottom edge are off
        right=False,  # ticks along the top edge are off
        labelright=False)

    plt.legend()
    # get handles and labels
    handles, labels = plt.gca().get_legend_handles_labels()
    # specify order of items in legend
    order = np.flip(np.argsort(zords))
    # add legend to plot
    leg = plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order],
                     frameon=False, prop={'size': 20}, labelcolor='linecolor',
                     handlelength=0, handletextpad=0.3, loc="upper left", bbox_to_anchor=(0.02, 0.96))
    for line in leg.get_lines():
        line.set_linewidth(3.0)
    for item in leg.legendHandles:
        item.set_visible(False)

    ylim = plt.gca().get_ylim()
    yloc = ylim[1] + 0.005 * (ylim[1] - ylim[0])

    subtitle = f"Compared to {1981}-{2010} average"

    plt.text(plt.gca().get_xlim()[0], yloc, subtitle, fontdict={'fontsize': 30})
    plt.gca().set_title(title, pad=35, fontdict={'fontsize': 40}, loc='left')

    plt.savefig(out_dir / image_filename)
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))
    plt.close()
    return


def make_plot(datasets, new_datasets, region_name, ds_names):
    colours = ['red', 'green', 'blue', 'yellow', 'black', 'purple']

    fig, axs = plt.subplots(6)
    fig.set_size_inches(18.5, 10.5)
    for i, ds in enumerate(datasets):
        axs[i].plot(ds['Year'], ds['data'], color=colours[i], label=ds_names[i])
        axs[i].plot(new_datasets[i]['Year'], new_datasets[i]['data'], color=colours[i], linestyle='dashed')

    plt.legend()
    plt.savefig(DATA_DIR / 'New folder' / f'compare_{region_name}.png')
    plt.close()


if __name__ == '__main__':

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR
    data_dir = project_dir / "Data"

    region_names = ['wmorai', 'wmoraii', 'wmoraiii', 'wmoraiv', 'wmorav', 'wmoravi',
                    'north_africa', 'west_africa', 'central_africa',
                    'east_africa', 'southern_africa', 'indian_ocean']
    data_sets = ['HadCRUT5 analysis', 'NOAAGlobalTemp', 'GISTEMP',
                 'Berkeley Earth', 'ERA-5', 'JRA-55']

    new_region_names = ['Africa', 'Asia', 'South America',
                        'North America', 'South-West Pacific', 'Europe',
                        'North Africa', 'West Africa', 'Central Africa',
                        'Eastern Africa', 'Southern Africa', 'Indian Ocean']
    new_data_sets = ['HadCRUT5', 'NOAAGlobalTemp', 'GISTEMP',
                     'Berkeley Earth', 'ERA5', 'JRA-55']

    ras = ['I', 'II', 'III', 'IV', 'V', 'VI']

    superset1 = []
    superset2 = []

    for region_count, name in enumerate(region_names):

        all_datasets = []
        for ds in data_sets:
            filename = DATA_DIR / 'New folder' / f'{name}_{ds}.csv'
            if filename.exists():
                df = pd.read_csv(filename)
                df = df.rename(columns={f'{ds} (degC)': 'data'})
                all_datasets.append(df)

        all_new_datasets = []
        for ds in new_data_sets:
            new_name = new_region_names[region_count]
            df = read_new(new_name, ds)
            all_new_datasets.append(df)

        # Pick out the datasets we want to use. i.e. ERA5 from the new run.
        best_datasets = []
        for dataset_index in range(len(all_datasets)):
            if dataset_index == 4:
                best_datasets.append(all_new_datasets[dataset_index])
            else:
                best_datasets.append(all_datasets[dataset_index])

        if region_count < 6:
            superset1.append(best_datasets)
        else:
            superset2.append(best_datasets)

        make_plot(all_datasets, all_new_datasets, name, new_data_sets)

        if region_count < 6:
            title = f'WMO RA {ras[region_count]} {new_region_names[region_count]}'
        else:
            title = f'{new_region_names[region_count]}'

        neat_plot(DATA_DIR / 'New folder', best_datasets,
                  f'fixed_{name}.png',
                  title, new_data_sets)

    # Sub-region
    trends_plot(DATA_DIR / 'New folder', superset2,
                f'trends_africa.png',
                '', new_region_names[6:12],
                extra_series=superset1[0], extra_name='Africa')

    archive = dm.DataArchive.from_directory(metadata_dir)
    ts_archive = archive.select({'variable': 'tas', 'type': 'timeseries', 'time_resolution': 'monthly'})
    all_datasets = ts_archive.read_datasets(data_dir)
    anns = []
    for ds in all_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        annual.select_year_range(1850, 2021)
        annual = annual.df
        annual = annual.rename(columns={'year': 'Year'})
        anns.append(annual)

    # Continental
    trends_plot(DATA_DIR / 'New folder', superset1,
                f'trends_continental.png',
                '', new_region_names[0:6],
                extra_series=anns, extra_name='Globe')
