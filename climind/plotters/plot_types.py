#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2022 John Kennedy
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
import shutil
from pathlib import Path
from datetime import datetime, date

import cartopy.crs as ccrs
import xarray
from cartopy.util import add_cyclic_point
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.transforms import Bbox
import seaborn as sns
import numpy as np
from typing import List, Union, Tuple

from climind.data_types.timeseries import TimeSeriesMonthly, TimeSeriesAnnual, TimeSeriesIrregular, \
    get_list_of_unique_variables, superset_dataset_list, AveragesCollection
from climind.data_types.grid import GridMonthly, GridAnnual, process_datasets
from climind.plotters.plot_utils import calculate_trends, calculate_ranks, calculate_values, set_lo_hi_ticks, \
    caption_builder, map_caption_builder

FANCY_UNITS = {"degC": r"$\!^\circ\!$C",
               "zJ": "zJ",
               "millionkm2": "million km$^2$",
               "ph": "pH",
               "mwe": "m.w.e"}

STANDARD_PARAMETER_SET = {
    'axes.axisbelow': False,
    'axes.labelsize': 23,
    'xtick.labelsize': 23,
    'ytick.labelsize': 23,
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


def accumulate(in_array):
    """
    Calculate the accumulated mean for an array so that the nth value is
    the mean of the first n values in the input array.

    Parameters
    ----------
    in_array

    Returns
    -------

    """
    n_months = len(in_array)
    accumulator = np.zeros(n_months)
    for i in range(n_months):
        accumulator[i] = np.mean(in_array[0:i + 1])
    return accumulator


def equivalence(key):
    lookup = {
        'tas': 'Globe (land and ocean)',
        'wmo_ra_1': 'Africa',
        'wmo_ra_2': 'Asia',
        'wmo_ra_3': 'South America',
        'wmo_ra_4': 'North America',
        'wmo_ra_5': 'Southwest Pacific',
        'wmo_ra_6': 'Europe',

        'africa_subregion_1': 'North Africa',
        'africa_subregion_2': 'West Africa',
        'africa_subregion_3': 'Central Africa',
        'africa_subregion_4': 'Eastern Africa',
        'africa_subregion_5': 'Southern Africa',
        'africa_subregion_6': 'Indian Ocean',

        'lac_subregion_1': 'South America',
        'lac_subregion_2': 'Mexico and Central America',
        'lac_subregion_3': 'Caribbean',
        'lac_subregion_4': 'Mexico',
        'lac_subregion_5': 'Central America',
        'lac_subregion_6': 'Latin America and Caribbean',

        'arab_subregion_1': 'League of Arab States',
        'arab_subregion_2': 'North Africa LAS',
        'arab_subregion_3': 'East Africa LAS',
        'arab_subregion_4': 'Middle East LAS'
    }
    return lookup[key]


def add_data_sets(axis, all_datasets: List[Union[TimeSeriesAnnual, TimeSeriesMonthly, TimeSeriesIrregular]],
                  dark: bool = False, marker=False) -> List[int]:
    """
    Given a list of data sets, plot each one on the provided axis.

    Parameters
    ----------
    axis: Matplotlib axis
        Set of Matplotlib axes for plotting on
    all_datasets: List[Union[TimeSeriesAnnual, TimeSeriesMonthly, TimeSeriesIrregular]]
        list of data sets to be plotted on the axes
    dark: bool
        Set to True to plot in the dark style (charcoal background, light coloured lines)

    Returns
    -------
    List[int]
        List of the zorder of the plotted data sets
    """
    zords = []
    for i, ds in enumerate(all_datasets):
        col = ds.metadata['colour']
        if col == 'dimgrey' and dark:
            col = '#eeeeee'
        zord = ds.metadata['zpos']
        zords.append(zord)

        x_values = ds.get_year_axis()
        date_range = ds.get_string_date_range()

        linewidth = 3
        if len(x_values) > 180:
            linewidth = 1

        if marker:
            axis.plot(x_values, ds.df['data'],
                      label=f"{ds.metadata['display_name']} ({date_range})",
                      color=col, zorder=zord, linewidth=linewidth, marker='o')
        else:
            axis.plot(x_values, ds.df['data'],
                      label=f"{ds.metadata['display_name']} ({date_range})",
                      color=col, zorder=zord, linewidth=linewidth)

        if 'uncertainty' in ds.df.columns:
            axis.fill_between(x_values,
                              ds.df['data'] + ds.df['uncertainty'],
                              ds.df['data'] - ds.df['uncertainty'],
                              color=col, alpha=0.1)

    return zords


def get_levels_and_palette(variable: str):
    if variable == 'tas_mean':
        wmo_cols = ['#13055e', '#2a0ad9', '#264dff', '#3fa0ff', '#72daff', '#aaf7ff', '#e0ffff',
                    '#ffffbf', '#fee098', '#ffad73', '#f76e5e', '#d82632', '#a50022', '#47000f']
        wmo_levels = [-5, -3, -2, -1, -0.5, -0.25, 0, 0.25, 0.5, 1, 2, 3, 5]
    elif variable == 'pre':
        wmo_cols = ['#543005', '#8c510a', '#bf812d', '#dfc27d', '#f6e8c3', '#f5f5f5',
                    '#c7eae5', '#80cdc1', '#35978f', '#01665e', '#003c30']
        wmo_levels = [-110, -90, -70, -50, -30, -10, 10, 30, 50, 70, 90, 110]
    else:
        wmo_cols = ['#2a0ad9', '#264dff', '#3fa0ff', '#72daff', '#aaf7ff', '#e0ffff',
                    '#ffffbf', '#fee098', '#ffad73', '#f76e5e', '#d82632', '#a50022']
        wmo_levels = [-5, -3, -2, -1, -0.5, -0.25, 0, 0.25, 0.5, 1, 2, 3, 5]

    return wmo_levels, wmo_cols


def add_labels(axis, dataset: Union[TimeSeriesAnnual, TimeSeriesMonthly, TimeSeriesIrregular]) -> str:
    """
    Add labels to the x and y axes

    Parameters
    ----------
    axis: Matplotlib axis
        set of matplotlib axes
    dataset: Union[TimeSeriesAnnual, TimeSeriesMonthly, TimeSeriesIrregular]
        Data set which will be used to specify the units on the y axis
    Returns
    -------
    str
        Units of the y-axis
    """
    plot_units = dataset.metadata['units']
    if plot_units in FANCY_UNITS:
        plot_units = FANCY_UNITS[plot_units]
    axis.set_xlabel('Year')
    axis.set_ylabel(plot_units, rotation=90, labelpad=10)
    return plot_units


def set_yaxis(axis, dataset: Union[TimeSeriesAnnual, TimeSeriesMonthly, TimeSeriesIrregular]) -> Tuple[
    float, float, np.ndarray]:
    """
    Work out the extents of the y axis and the tick values

    Parameters
    ----------
    axis: Matplotlib axis
        Matplotlib axis
    dataset: Union[TimeSeriesAnnual, TimeSeriesMonthly, TimeSeriesIrregular]
        Time series which contains one of the datasets being plotted

    Returns
    -------
    Tuple[float, float, np.ndarray]
        The lowest and highest points on the y axis and an array of tick values for the major ticks on the y axis.
    """
    ylims = axis.get_ylim()
    ylo, yhi, yticks = set_lo_hi_ticks(ylims, 0.2)
    if len(yticks) > 10:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 0.5)
    if len(yticks) > 10:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 1.0)

    if dataset.metadata['variable'] in ['glacier', 'n2o', 'ch4rate']:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 5.0)

    if dataset.metadata['variable'] in ['ohc', 'ohc2k', 'ch4']:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 50.0)

    if dataset.metadata['variable'] == 'ph':
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 0.01)

    if dataset.metadata['variable'] in ['co2', 'sealevel']:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 10.)

    if dataset.metadata['variable'] in ['mhw', 'mcs']:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 10.)

    if dataset.metadata['variable'] in ['greenland', 'antarctica']:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 1000.)

    return ylo, yhi, yticks


def set_xaxis(axis) -> Tuple[float, float, np.ndarray]:
    """
    Work out the extents of the x axis and the tick values

    Parameters
    ----------
    axis: Matplotlib axis
        The axis on which everything is being plotted

    Returns
    -------
    Tuple[float, float, np.ndarray]
        The lowest and highest points on the y axis and an array of tick values for the major ticks on the y axis.
    """
    xlims = axis.get_xlim()
    xlo, xhi, xticks = set_lo_hi_ticks(xlims, 20.)
    if len(xticks) < 3:
        xlo, xhi, xticks = set_lo_hi_ticks(xlims, 10.)
    if len(xticks) < 3:
        xlo, xhi, xticks = set_lo_hi_ticks(xlims, 1.)

    return xlo, xhi, xticks


def after_plot(zords: List[int], ds: Union[TimeSeriesAnnual, TimeSeriesMonthly, TimeSeriesIrregular],
               title: str) -> None:
    """
    Add fancy stuff to the plots after all the data lines have been plotted.

    Parameters
    ----------
    zords: List[int]
        List of the zorders of the data sets
    ds: Union[TimeSeriesAnnual, TimeSeriesMonthly, TimeSeriesIrregular]
        Example dataset of the datasets plotted, used to determine where to plot the legend and the
        climatology period
    title: str
        Title for the plot

    Returns
    -------
    None
    """
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
    loc = "upper left"
    bbox_to_anchor = (0.02, 0.96)
    if ds.metadata['variable'] in ['greenland', 'antarctica', 'mcs', 'arctic_ice', 'ph', 'glacier']:
        loc = "upper right"
        bbox_to_anchor = (0.96, 0.96)
    leg = plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order],
                     frameon=False, prop={'size': 20}, labelcolor='linecolor',
                     handlelength=0, handletextpad=0.3, loc=loc, bbox_to_anchor=bbox_to_anchor)
    for line in leg.get_lines():
        line.set_linewidth(3.0)
    for item in leg.legendHandles:
        item.set_visible(False)

    ylim = plt.gca().get_ylim()
    yloc = ylim[1] + 0.005 * (ylim[1] - ylim[0])

    if ds.metadata['actual']:
        subtitle = ''
    else:
        subtitle = f"Compared to {ds.metadata['climatology_start']}-" \
                   f"{ds.metadata['climatology_end']} average"

    current_time = f"Created: {datetime.today()}"
    plt.gcf().text(.90, .012, current_time[0:28], ha='right',
                   bbox={'facecolor': 'w', 'edgecolor': None})

    plt.text(plt.gca().get_xlim()[0], yloc, subtitle, fontdict={'fontsize': 30})
    plt.gca().set_title(title, pad=35, fontdict={'fontsize': 40}, loc='left')


# time series
def dark_plot(out_dir: Path, all_datasets: List[Union[TimeSeriesAnnual, TimeSeriesMonthly, TimeSeriesIrregular]],
              image_filename: str,
              title: str) -> str:
    """
    Plot the data sets in the dark style - charcoal background with light coloured lines. Tron like.

    Parameters
    ----------
    out_dir: Path
        Directory to which the plot will be written
    all_datasets: List[Union[TimeSeriesAnnual, TimeSeriesMonthly, TimeSeriesIrregular]]
        List of datasets to be plotted
    image_filename: str
        Name for the file to be written. Should end with .png
    title: str
        Title for the plot

    Returns
    -------
    str
        Caption for the figure
    """
    return neat_plot(out_dir, all_datasets, image_filename, title, dark=True)


def neat_plot(out_dir: Path, all_datasets: List[Union[TimeSeriesAnnual, TimeSeriesMonthly, TimeSeriesIrregular]],
              image_filename: str, title: str, dark: bool = False, yrange: List[float] = None) -> str:
    """
    Create the standard annual plot

    Parameters
    ----------
    out_dir: Path
        Directory to which the figure will be written
    all_datasets: List[Union[TimeSeriesAnnual, TimeSeriesMonthly, TimeSeriesIrregular]]
        list of datasets to be plotted
    image_filename: str
        filename for the figure. Must end in .png
    title: str
        title for the plot
    dark: bool
        set to True to plot using a dark background

    Returns
    -------
    str
        Caption for the figure is returned
    """
    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

    if dark:
        this_parameter_set = copy.deepcopy(STANDARD_PARAMETER_SET)
        this_parameter_set['grid.color'] = '#696969'
        this_parameter_set['figure.facecolor'] = '#000000'
        this_parameter_set['text.color'] = '#d3d3d3'
        this_parameter_set['xtick.color'] = '#d3d3d3'
        this_parameter_set['ytick.color'] = '#d3d3d3'
        sns.set(font='Franklin Gothic Book', rc=this_parameter_set)

    caption = caption_builder(all_datasets)

    plt.figure(figsize=[16, 9])
    zords = add_data_sets(plt.gca(), all_datasets, dark=dark)
    ds = all_datasets[-1]

    sns.despine(right=True, top=True, left=True)

    add_labels(plt.gca(), ds)

    if yrange is not None:
        plt.gca().set_ylim(yrange[0], yrange[1])

    _, _, yticks = set_yaxis(plt.gca(), ds)
    _, _, xticks = set_xaxis(plt.gca())
    plt.yticks(yticks)
    plt.xticks(xticks)

    after_plot(zords, ds, title)

    plt.savefig(out_dir / image_filename, bbox_inches=Bbox([[0.8, 0], [14.5, 9]]))
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))
    plt.close('all')
    return caption


def records_plot(out_dir: Path, all_datasets: List[TimeSeriesAnnual], image_filename: str, title: str,
                 dark: bool = False) -> str:
    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

    caption = caption_builder(all_datasets)

    plt.figure(figsize=[16, 9])

    record_margins = []
    for ds in all_datasets:
        rds = ds.record_margins()
        rds.df.data = rds.df.data - 0.0
        record_margins.append(rds)

    zords = add_data_sets(plt.gca(), record_margins, dark=dark, marker=True)

    ds = all_datasets[-1]

    sns.despine(right=True, top=True, left=True)

    add_labels(plt.gca(), ds)

    _, _, yticks = set_yaxis(plt.gca(), ds)
    _, _, xticks = set_xaxis(plt.gca())
    plt.yticks(yticks)
    plt.xticks(xticks)

    after_plot(zords, ds, title)

    plt.savefig(out_dir / image_filename, bbox_inches=Bbox([[0.8, 0], [14.5, 9]]))
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))
    plt.close('all')
    return caption


def decade_plot(out_dir: Path, all_datasets: List[TimeSeriesAnnual], image_filename: str, title: str) -> str:
    """
    Decadal plot

    Parameters
    ----------
    out_dir: Path
        Path of the directory to which the image will be written
    all_datasets: List[TimeSeriesAnnual]
        List of datasets of type :class:`.TimeSeriesAnnual` to be plotted.
    image_filename: str
        Name for the image file, should end in .png
    title: str
        Title for the image, will appear at the top of the figure

    Returns
    -------
    str
        Caption for the figure
    """
    caption = ""

    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

    zords = []
    plt.figure(figsize=[16, 9])
    for i, ds in enumerate(all_datasets):
        col = ds.metadata['colour']
        zord = ds.metadata['zpos']
        zords.append(zord)
        plt.plot(ds.df['year'], ds.df['data'], label=ds.metadata['display_name'], color=col, zorder=zord,
                 alpha=0.0)

        for j in range(len(ds.df['year'])):
            plt.plot([ds.df['year'][j] - 9, ds.df['year'][j]],
                     [ds.df['data'][j], ds.df['data'][j]], color=col, zorder=zord)

    ds = all_datasets[-1]
    sns.despine(right=True, top=True, left=True)

    add_labels(plt.gca(), ds)

    _, _, yticks = set_yaxis(plt.gca(), ds)
    _, _, xticks = set_xaxis(plt.gca())
    plt.yticks(yticks)
    plt.xticks(xticks)

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

    if ds.metadata['actual']:
        subtitle = ''
    else:
        subtitle = f"Compared to {ds.metadata['climatology_start']}-" \
                   f"{ds.metadata['climatology_end']} average"

    plt.text(plt.gca().get_xlim()[0], yloc, subtitle, fontdict={'fontsize': 30})
    plt.gca().set_title(title, pad=35, fontdict={'fontsize': 40}, loc='left')

    plt.savefig(out_dir / image_filename)
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))
    plt.close('all')
    return caption


def monthly_plot(out_dir: Path, all_datasets: List[TimeSeriesMonthly], image_filename: str, title: str) -> str:
    """
    Create the standard monthly plot

    Parameters
    ----------
    out_dir: Path
        Path of directory to which the image will be written
    all_datasets: List[TimeSeriesMonthly]
        List of datasets of type :class:`.TimeSeriesMonthly` to plot
    image_filename: str
        File name for the image
    title: str
        Title which will appear at the top of the figure.

    Returns
    -------
    str
        Caption for the figure
    """
    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

    caption = caption_builder(all_datasets)

    plt.figure(figsize=[16, 9])
    zords = add_data_sets(plt.gca(), all_datasets)

    ds = all_datasets[-1]

    sns.despine(right=True, top=True, left=True)

    add_labels(plt.gca(), ds)

    _, _, yticks = set_yaxis(plt.gca(), ds)
    _, _, xticks = set_xaxis(plt.gca())
    plt.yticks(yticks)
    plt.xticks(xticks)

    after_plot(zords, ds, title)

    plt.savefig(out_dir / image_filename, bbox_inches=Bbox([[0.8, 0], [14.5, 9]]))
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))
    plt.close('all')
    return caption


def marine_heatwave_plot(out_dir: Path, all_datasets: List[TimeSeriesAnnual], image_filename: str, _) -> str:
    """
    Marine heatwave and coldspell plot, which shows the ocean area affected by marine heatwaves and coldspells
    annually since the early 1980s

    Parameters
    ----------
    out_dir: Path
        Path of the directory to which the image will be written
    all_datasets: List[TimeSeriesAnnual]
        List of data sets of type :class:`.TimeSeriesAnnual` to plot
    image_filename: str
        File name for the image, should end in .png

    Returns
    -------
    str
        Caption for the figure
    """
    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

    mcs = []
    mhw = []
    for ds in all_datasets:
        if ds.metadata['variable'] == 'mcs':
            mcs.append(ds)
        if ds.metadata['variable'] == 'mhw':
            mhw.append(ds)

    zords = []
    plt.figure(figsize=[16, 9])
    for i, ds in enumerate(mcs):
        col = ds.metadata['colour']
        zord = ds.metadata['zpos']
        zords.append(zord)
        start_year, end_year = ds.get_first_and_last_year()
        date_range = f"{start_year}-{end_year}"
        plt.plot(ds.df['year'], ds.df['data'], label=f'Marine cold spells ({date_range})', color=col, zorder=zord,
                 linewidth=3)
    for i, ds in enumerate(mhw):
        col = ds.metadata['colour']
        zord = ds.metadata['zpos']
        zords.append(zord)
        plt.plot(ds.df['year'], ds.df['data'], label=f'Marine heatwaves ({date_range})', color=col, zorder=zord,
                 linewidth=3)

    sns.despine(right=True, top=True, left=True)

    plot_units = '%'
    plt.xlabel('Year')
    plt.ylabel(plot_units, rotation=0, labelpad=10)

    plt.gca().set_ylim(0, 65)
    yticks = np.arange(0, 101, 10)

    xlims = plt.gca().get_xlim()
    _, _, xticks = set_lo_hi_ticks(xlims, 5.)

    plt.yticks(yticks)
    plt.xticks(xticks)

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
    loc = "upper left"
    bbox_to_anchor = (0.02, 0.96)

    leg = plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order],
                     frameon=False, prop={'size': 30}, labelcolor='linecolor',
                     handlelength=0, handletextpad=0.3, loc=loc, bbox_to_anchor=bbox_to_anchor)
    for line in leg.get_lines():
        line.set_linewidth(3.0)
    for item in leg.legendHandles:
        item.set_visible(False)

    ylim = plt.gca().get_ylim()
    yloc = ylim[1] + 0.005 * (ylim[1] - ylim[0])

    title = 'Area affected by marine heatwaves and cold spells'
    subtitle = '% of ocean area affected, 1982-2021'

    plt.text(plt.gca().get_xlim()[0], yloc, subtitle, fontdict={'fontsize': 30})
    plt.gca().set_title(title, pad=35, fontdict={'fontsize': 40}, loc='left')

    plt.savefig(out_dir / image_filename, bbox_inches=Bbox([[0.8, 0], [14.5, 9]]))
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))
    plt.close('all')
    return "Figure showing the percentage of ocean area affected by " \
           "marine heatwaves and marine cold spells each year since 1982"


def arctic_sea_ice_plot(out_dir: Path, all_datasets: List[TimeSeriesMonthly], image_filename: str, _) -> str:
    """
    Generate figure showing the March and September sea ice extent anomalies for the input datasets.

    Parameters
    ----------
    out_dir: Path
        Directory to which the image will be written
    all_datasets: List[TimeSeriesMonthly]
        List of data sets of type :class:`.TimeSeriesMonthly` to be plotted
    image_filename: str
        File name for the image, should end in .png.

    Returns
    -------
    str
        Caption for the figure
    """
    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

    march_colors = ['#56b4e9', '#009e73', '#5473ff']
    september_colors = ['#e69f00', '#d55e00', '#ff6b54']

    plt.figure(figsize=[16, 9])
    for i, ds in enumerate(all_datasets):
        subds = ds.make_annual_by_selecting_month(3)
        start_year, end_year = subds.get_first_and_last_year()
        date_range = f"{start_year}-{end_year}"
        plt.plot(subds.df['year'], subds.df['data'], label=f"{ds.metadata['name']} March ({date_range})",
                 color=march_colors[i], linewidth=3)

    for i, ds in enumerate(all_datasets):
        subds = ds.make_annual_by_selecting_month(9)
        start_year, end_year = subds.get_first_and_last_year()
        date_range = f"{start_year}-{end_year}"
        plt.plot(subds.df['year'], subds.df['data'], label=f"{ds.metadata['name']} September ({date_range})",
                 color=september_colors[i], linewidth=3)

    ds = all_datasets[-1]

    sns.despine(right=True, top=True, left=True)

    plot_units = add_labels(plt.gca(), ds)

    _, _, yticks = set_yaxis(plt.gca(), ds)
    xlims = plt.gca().get_xlim()
    _, _, xticks = set_lo_hi_ticks(xlims, 5.)
    plt.yticks(yticks)
    plt.xticks(xticks)

    plt.tick_params(
        axis='y',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        left=False,  # ticks along the bottom edge are off
        right=False,  # ticks along the top edge are off
        labelright=False)

    plt.legend()
    # get handles and labels
    handles, labels = plt.gca().get_legend_handles_labels()
    # add legend to plot
    loc = "upper right"
    bbox_to_anchor = (0.96, 0.96)
    leg = plt.legend(handles, labels,
                     frameon=False, prop={'size': 20}, labelcolor='linecolor',
                     handlelength=0, handletextpad=0.3, loc=loc, bbox_to_anchor=bbox_to_anchor)
    for line in leg.get_lines():
        line.set_linewidth(3.0)
    for item in leg.legendHandles:
        item.set_visible(False)

    ylim = plt.gca().get_ylim()
    yloc = ylim[1] + 0.005 * (ylim[1] - ylim[0])

    title = f'Arctic sea-ice extent ({plot_units})'
    subtitle = f"Difference from {ds.metadata['climatology_start']}-" \
               f"{ds.metadata['climatology_end']} average"

    plt.text(plt.gca().get_xlim()[0], yloc, subtitle, fontdict={'fontsize': 30})
    plt.gca().set_title(title, pad=35, fontdict={'fontsize': 40}, loc='left')

    plt.savefig(out_dir / image_filename, bbox_inches=Bbox([[0.8, 0], [14.5, 9]]))
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))
    plt.close('all')

    caption = f"Arctic sea ice extent (shown as differences from the " \
              f"{ds.metadata['climatology_start']}-{ds.metadata['climatology_end']} average) " \
              f"from 1979 to {end_year}. Two months are shown - March and September - " \
              f"at the annual maximum and minimum extents respectively."

    return caption


def antarctic_sea_ice_plot(out_dir: Path, all_datasets: List[TimeSeriesMonthly], image_filename: str, _) -> str:
    """
    Generate figure showing the February and September Antarctic sea ice extent anomalies for the input datasets.

    Parameters
    ----------
    out_dir: Path
        Directory to which the image will be written
    all_datasets: List[TimeSeriesMonthly]
        List of data sets of type :class:`.TimeSeriesMonthly` to be plotted
    image_filename: str
        File name for the image, should end in .png.

    Returns
    -------
    str
        Caption for the figure
    """
    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

    february_colors = ['#e69f00', '#d55e00', '#ff6b54']
    september_colors = ['#56b4e9', '#009e73', '#5473ff']

    plt.figure(figsize=[16, 9])
    for i, ds in enumerate(all_datasets):
        subds = ds.make_annual_by_selecting_month(2)
        start_year, end_year = subds.get_first_and_last_year()
        date_range = f"{start_year}-{end_year}"
        plt.plot(subds.df['year'], subds.df['data'], label=f"{ds.metadata['name']} February ({date_range})",
                 color=february_colors[i], linewidth=3)

    for i, ds in enumerate(all_datasets):
        subds = ds.make_annual_by_selecting_month(9)
        start_year, end_year = subds.get_first_and_last_year()
        date_range = f"{start_year}-{end_year}"
        plt.plot(subds.df['year'], subds.df['data'], label=f"{ds.metadata['name']} September ({date_range})",
                 color=september_colors[i], linewidth=3)

    ds = all_datasets[-1]

    sns.despine(right=True, top=True, left=True)

    plot_units = ds.metadata['units']
    if plot_units in FANCY_UNITS:
        plot_units = FANCY_UNITS[plot_units]
    plt.xlabel('Year')
    plt.ylabel(plot_units, rotation=90, labelpad=10)

    ylims = plt.gca().get_ylim()
    _, _, yticks = set_lo_hi_ticks(ylims, 0.2)
    if len(yticks) > 10:
        _, _, yticks = set_lo_hi_ticks(ylims, 0.5)

    xlims = plt.gca().get_xlim()
    _, _, xticks = set_lo_hi_ticks(xlims, 5.)

    plt.yticks(yticks)
    plt.xticks(xticks)

    plt.tick_params(
        axis='y',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        left=False,  # ticks along the bottom edge are off
        right=False,  # ticks along the top edge are off
        labelright=False)

    plt.legend()
    # get handles and labels
    handles, labels = plt.gca().get_legend_handles_labels()
    # add legend to plot
    loc = "upper left"
    bbox_to_anchor = (0.05, 0.96)
    leg = plt.legend(handles, labels,
                     frameon=False, prop={'size': 20}, labelcolor='linecolor',
                     handlelength=0, handletextpad=0.3, loc=loc, bbox_to_anchor=bbox_to_anchor)
    for line in leg.get_lines():
        line.set_linewidth(3.0)
    for item in leg.legendHandles:
        item.set_visible(False)

    ylim = plt.gca().get_ylim()
    yloc = ylim[1] + 0.005 * (ylim[1] - ylim[0])

    title = f'Antarctic sea-ice extent ({plot_units})'
    subtitle = f"Difference from {ds.metadata['climatology_start']}-" \
               f"{ds.metadata['climatology_end']} average"

    plt.text(plt.gca().get_xlim()[0], yloc, subtitle, fontdict={'fontsize': 30})
    plt.gca().set_title(title, pad=35, fontdict={'fontsize': 40}, loc='left')

    plt.savefig(out_dir / image_filename, bbox_inches=Bbox([[0.8, 0], [14.5, 9]]))
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))
    plt.close('all')

    caption = f"Antarctic sea ice extent (shown as differences from the " \
              f"{ds.metadata['climatology_start']}-{ds.metadata['climatology_end']} average) " \
              f"from 1979 to {end_year}. Two months are shown - September and February - " \
              f"at the annual maximum and minimum extents respectively."

    return caption


def cherry_plot(out_dir: Path, all_datasets: List[Union[TimeSeriesAnnual, TimeSeriesMonthly, TimeSeriesIrregular]],
                image_filename: str, title: str) -> str:
    cherry_params = {
        'axes.axisbelow': False,
        'axes.labelsize': 20,
        'xtick.labelsize': 15,
        'ytick.labelsize': 0,
        'axes.edgecolor': '#d13d64',
        'axes.facecolor': 'None',

        'axes.grid.axis': 'x',
        'grid.color': '#d13d64',
        'grid.alpha': 0.2,

        'axes.labelcolor': '#d13d64',

        'axes.spines.left': False,
        'axes.spines.right': False,
        'axes.spines.top': False,
        'axes.spines.bottom': False,

        'figure.facecolor': 'white',
        'lines.solid_capstyle': 'round',
        'patch.edgecolor': 'w',
        'patch.force_edgecolor': True,
        'text.color': 'dimgrey',

        'xtick.bottom': True,
        'xtick.color': '#d13d64',
        'xtick.direction': 'out',
        'xtick.top': False,
        'xtick.labelbottom': True,

        'ytick.major.width': 0.4,
        'ytick.color': '#d13d64',
        'ytick.direction': 'out',
        'ytick.left': False,
        'ytick.right': False
    }

    sns.set(font='Franklin Gothic Book', rc=cherry_params)

    ds = all_datasets[0]

    plt.figure(figsize=[16, 8])
    date_range = ds.get_string_date_range()
    col = ds.metadata['colour']

    plt.scatter(ds.df['year'], ds.df['data'], s=100, alpha=0.4,
                label=f"{ds.metadata['display_name']} ({date_range})",
                color=col, zorder=10, linewidth=1)

    sns.despine(right=True, top=True, left=True, bottom=True)

    march15 = date(2003, 3, 15).timetuple().tm_yday
    april1 = date(2003, 4, 1).timetuple().tm_yday
    april15 = date(2003, 4, 15).timetuple().tm_yday
    may1 = date(2003, 5, 1).timetuple().tm_yday

    xlims = plt.gca().get_xlim()
    xlims = [xlims[0] - 45, xlims[1]]

    plt.plot(xlims, [march15, march15], color='#d13d64', zorder=1)
    plt.plot(xlims, [april1, april1], color='#d13d64', zorder=1)
    plt.plot(xlims, [april15, april15], color='#d13d64', zorder=1)
    plt.plot(xlims, [may1, may1], color='#d13d64', zorder=1)

    plt.text(xlims[0], march15 + 1, 'March 15', color='#d13d64')
    plt.text(xlims[0], april1 + 1, 'April 1', color='#d13d64')
    plt.text(xlims[0], april15 + 1, 'April 15', color='#d13d64')
    plt.text(xlims[0], may1 + 1, 'May 1', color='#d13d64')

    plt.gca().set_title(title, pad=35, fontdict={'fontsize': 40},
                        color='#d13d64', x=0.37, y=0.95)

    plt.savefig(out_dir / image_filename, bbox_inches=Bbox([[0.8, 0], [14.5, 9]]))
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))
    plt.close('all')

    return ''


def trends_plot(out_dir: Path, in_all_datasets: List[TimeSeriesAnnual],
                image_filename: str, title: str, order: list = []) -> str:
    """
    Trend figure which shows the mean and range of the trends from the input data sets over four 30-year periods:
    1901-1930, 1931-1960, 1961-1990 and 1991-present. This is set up to work with WMO RA and Africa Subregion
    timeseries.

    Parameters
    ----------
    out_dir: Path
        Path of the directory to which the figure will be written
    in_all_datasets: List[TimeSeriesAnnual]
        List of data sets of type :class:`.TimeSeriesAnnual` to be plotted
    image_filename: str
        File name for the output figure
    title: str
        Title of the figure, appears at the top of the figure
    order: list
        The order in which the variables will be plotted, from left to right, in each sub-block

    Returns
    -------
    str
        Caption for the figure
    """
    final_year = 2023
    print_trends = False

    caption = f'Figure shows the trends for four sub-periods (1901-1930, 1931-1960, 1961-1990 and 1991-{final_year}. ' \
              f'Coloured bars show the mean trend for each region and the black vertical lines indicate the range ' \
              f'of different estimates.'

    # get list of all unique variables
    variables = get_list_of_unique_variables(in_all_datasets)
    names = []
    for variable in variables:
        names.append(equivalence(variable))
    superset = superset_dataset_list(in_all_datasets, variables)
    series_count = len(superset)

    colours = ['#f33d3d', '#ffd465', '#9dd742',
               '#84d1cd', '#848dd1', '#cf84d1', '#b4b4b4']
    sns.set(font='Franklin Gothic Book', rc={
        'axes.axisbelow': False,
        'axes.labelsize': 25,
        'xtick.labelsize': 15,
        'ytick.labelsize': 25,
        'axes.edgecolor': 'lightgrey',
        'axes.facecolor': 'None',

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

    # switch variable that alternates the drawing of a grey background on the trend plots
    grey_background = True

    for start_end in [[1901, 1930],
                      [1931, 1960],
                      [1961, 1990],
                      [1991, final_year]]:

        y1 = start_end[0]
        y2 = start_end[1]

        if grey_background:
            grey_background = False
            rect = patches.Rectangle((y1, -0.2), y2 - y1 + 1, 1.2, color='#eeeeee')
            plt.gca().add_patch(rect)
        else:
            grey_background = True

        # calculate trend for each data set
        for i in range(series_count):
            pos_ind = variables.index(order[i])
            all_datasets = superset[pos_ind]

            mean_trend, min_trend, max_trend = calculate_trends(all_datasets, y1, y2)
            min_rank, max_rank = calculate_ranks(all_datasets, final_year)
            mean_value, min_value, max_value = calculate_values(all_datasets, final_year)

            if print_trends:
                print(f'{names[pos_ind]}  {final_year} {mean_value:.2f} ({min_value:.2f}-{max_value:.2f}), '
                      f'rank: {min_rank}-{max_rank}')
                print(f'{start_end[0]}-{start_end[1]} {mean_trend:.2f} ({min_trend:.2f}-{max_trend:.2f})')

            interset_delta = 0.4
            width = (30. - 2 * interset_delta) / float(series_count)
            rect_xstart = y1 + interset_delta + (width * i)
            mid_point = rect_xstart + width / 2.
            delta = 0.3
            section_mid_point = (y2 + y1) / 2.

            plt.text(section_mid_point, -0.25, 'Trends', fontsize=25, ha='center')
            plt.text(section_mid_point, -0.30, f'{y1}-{y2}', fontsize=25, ha='center')

            # plot a coloured bar
            rect = patches.Rectangle((rect_xstart + delta, 0), width - 2 * delta, mean_trend,
                                     linewidth=0, edgecolor=None, facecolor=colours[i])
            plt.gca().add_patch(rect)
            plt.plot([mid_point, mid_point], [min_trend, max_trend], color='black')

    for i in range(series_count):
        name_index = variables.index(order[i])
        name = names[name_index]
        plt.text(1902, 0.55 - name_index * 0.05, name, fontsize=25, ha='left', color=colours[i])

        # plot the uncertainty range
    plt.ylabel(r'Trend ($\!^\circ\!$C/decade)', labelpad=5)
    plt.yticks(np.arange(-0.2, 0.8, 0.2))
    plt.gca().set_ylim(-0.2, 0.6)

    current_time = f"Created: {datetime.today()}"
    plt.gcf().text(.02, 0.012, current_time[0:28], ha='left',
                   bbox={'facecolor': 'w', 'edgecolor': None})

    plt.gca().set_title(title, pad=45, fontdict={'fontsize': 40}, loc='left')

    plt.savefig(out_dir / image_filename, bbox_inches=Bbox([[0.2, 0], [14.5, 9]]))
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))
    plt.close('all')

    return caption


def show_premade_image(out_dir: Path, in_all_datasets: List[TimeSeriesAnnual],
                       image_filename: str, title: str,
                       original_filename: str = '', caption: str = ''):
    from climind.config.config import DATA_DIR
    source_dir = DATA_DIR / 'ManagedData' / 'Figures'

    for extension in ['.png', '.svg', '.pdf']:
        source_file = source_dir / original_filename.replace('.png', extension)

        if source_dir.exists():
            shutil.copy(source_file,
                        out_dir / image_filename.replace('.png', extension))
        else:
            raise FileNotFoundError(f'{extension} version of file {source_file} does not exist')

    return caption


# Maps
def quick_and_dirty_map(dataset: xarray.Dataset, image_filename: Path) -> None:
    """
    Quick and very rough map plotter which plots the last field in an xarray Dataset

    Parameters
    ----------
    dataset: xarray.Dataset
        xarray Dataset to be plotted.
    image_filename: Path
        Path for the output file
    Returns
    -------
    None
    """
    plt.figure()
    proj = ccrs.PlateCarree()
    p = dataset.tas_mean[-1].plot(transform=proj,
                                  subplot_kws={'projection': proj},
                                  levels=[-3, -2, -1, 0, 1, 2, 3])
    p.axes.coastlines()
    plt.title("")
    plt.savefig(image_filename, bbox_inches='tight')
    plt.close('all')


def nice_map(dataset: xarray.Dataset, image_filename: Path, title: str, var: str = 'tas_mean') -> None:
    """
    Plot a nice looking map (relatively speaking) of the last field in an xarray dataset.

    Parameters
    ----------
    dataset: xarray.Dataset
        Data set to be plotted
    image_filename: Path
        Name for output file
    title: str
        Title for the plot
    var: str
        Variabel to plot from the dataset
        Variabel to plot from the dataset

    Returns
    -------
    None
    """
    # This is a pain, but we need to do some magic to convince cartopy that the data
    # are continuous across the dateline
    data = dataset[var]
    lon = dataset.coords['longitude']
    lon_idx = data.dims.index('longitude')
    wrap_data, wrap_lon = add_cyclic_point(data.values, coord=lon, axis=lon_idx)

    plt.figure(figsize=(16, 9))
    proj = ccrs.EqualEarth(central_longitude=0)

    if var == 'pre':
        wmo_levels = [-110, -90, -70, -50, -30, -10, 10, 30, 50, 70, 90, 110]
        wmo_cols = ['#543005', '#8c510a', '#bf812d', '#dfc27d', '#f6e8c3', '#f5f5f5',
                    '#c7eae5', '#80cdc1', '#35978f', '#01665e', '#003c30']
    elif 'precip_quantiles' in var:
        wmo_levels = [0, 0.1, 0.2, 0.8, 0.9, 1]
        wmo_cols = ['#543005', '#bf812d', '#e5e5e5', '#35978f', '#003c30']
    elif var == 'sealevel':
        wmo_levels = [-300, -250, -200, -150, -100, -50, 0, 50, 100, 150, 200, 250, 300]
        wmo_cols = ['#2a0ad9', '#264dff', '#3fa0ff', '#72daff', '#aaf7ff', '#e0ffff',
                    '#ffffbf', '#fee098', '#ffad73', '#f76e5e', '#d82632', '#a50022']
    elif var == 'sealeveltrend':
        wmo_levels = [-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]
        wmo_cols = ['#2a0ad9', '#264dff', '#3fa0ff', '#72daff', '#aaf7ff', '#e0ffff',
                    '#ffffbf', '#fee098', '#ffad73', '#f76e5e', '#d82632', '#a50022']
    else:
        wmo_levels = [-5, -3, -2, -1, -0.5, -0.25, 0, 0.25, 0.5, 1, 2, 3, 5]
        wmo_cols = ['#2a0ad9', '#264dff', '#3fa0ff', '#72daff', '#aaf7ff', '#e0ffff',
                    '#ffffbf', '#fee098', '#ffad73', '#f76e5e', '#d82632', '#a50022']

    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_subplot(111, projection=proj, aspect='auto')

    p = ax.contourf(wrap_lon, dataset.latitude, wrap_data[-1, :, :],
                    transform=ccrs.PlateCarree(),
                    levels=wmo_levels,
                    colors=wmo_cols,
                    extend='both'
                    )

    cbar = plt.colorbar(p, orientation='horizontal', fraction=0.06, pad=0.04)

    cbar.ax.tick_params(labelsize=15)
    cbar.set_ticks(wmo_levels)
    cbar.set_ticklabels(wmo_levels)
    if var == 'pre':
        cbar.set_label(r'Precipitation difference from 1981-2010 average (mm)', rotation=0, fontsize=15)
    elif 'precip_quantiles' in var:
        cbar.set_label(r'Precipitation quantile based on 1991-2020', rotation=0, fontsize=15)
    elif var == 'sealevel':
        cbar.set_label(r'Sea level difference from long term mean average (mm)', rotation=0, fontsize=15)
    elif var == 'sealeveltrend':
        cbar.set_label(r'Sea level trend (mm/year)', rotation=0, fontsize=15)
    else:
        cbar.set_label(r'Temperature difference from 1981-2010 average ($\degree$C)', rotation=0, fontsize=15)

    p.axes.coastlines()
    p.axes.set_global()

    plt.title(f'{title}', pad=20, fontdict={'fontsize': 20})
    plt.savefig(f'{image_filename}.png')
    plt.savefig(f'{image_filename}.pdf')
    plt.close('all')


def plot_map_by_year_and_month(dataset: GridMonthly, year: int, month: int, image_filename: Path, title: str,
                               var: str = 'tas_mean') -> None:
    """
    Plot map for specified year and month

    Parameters
    ----------
    dataset: GridMonthly
        :class:`.GridMonthly` to be plotted
    year: int
        Year to be plotted
    month: int
        Month in year to be plotted
    image_filename: Path
        Path to output file
    title: str
        Title for the plot
    var: str
        Variable to be plotted

    Returns
    -------
    None
    """
    selection = dataset.df.sel(time=slice(f'{year}-{month:02d}-01',
                                          f'{year}-{month:02d}-28'))

    nice_map(selection, image_filename, title, var=var)


def dashboard_map_generic(out_dir: Path, all_datasets: List[GridAnnual], image_filename: str, title: str,
                          grid_type: str, region: list = None) -> str:
    """
    Plot generic style map for the dashboard. Type must be one of "mean", "rank", or "unc".

    Parameters
    ----------
    out_dir: Path
        Output directory to which the image will be written
    all_datasets: List[GridAnnual]
        List of :class:`.GridAnnual` datasets to be plotted
    image_filename: str
        Filename for output file
    title: str
        Title for the plot
    grid_type: str
        Indicates how the datasets in the input list should be combined, 'mean', 'rank' or 'unc'
    region: list
        four member list specifying the western, eastern, southern, and northern extents of the region to be plotted.

    Returns
    -------
    str
        Caption for the figure
    """
    if grid_type == 'mean' or grid_type == 'rank':
        dataset = process_datasets(all_datasets, 'median')
    elif grid_type == 'unc':
        dataset = process_datasets(all_datasets, 'range')
    elif grid_type == 'single':
        dataset = all_datasets[0]
    else:
        raise RuntimeError(f'Unknown type {grid_type}')

    last_months = []
    for ds in all_datasets:
        year_month = "-".join(ds.metadata['last_month'].split('-')[0:2])
        last_months.append(f"{ds.metadata['display_name']} to {year_month}")
    ds = all_datasets[-1]

    main_variable_list = list(dataset.df.keys())
    main_variable = main_variable_list[0]

    data = dataset.df[main_variable]
    lon = dataset.df.coords['longitude']
    lon_idx = data.dims.index('longitude')
    wrap_data, wrap_lon = add_cyclic_point(data.values, coord=lon, axis=lon_idx)

    plt.figure(figsize=(16, 9))

    if region is not None:
        if region[1] > 180:
            proj = ccrs.PlateCarree(central_longitude=180)
        else:
            proj = ccrs.PlateCarree(central_longitude=0)
    else:
        proj = ccrs.EqualEarth(central_longitude=0)

    if grid_type in ['mean', 'single']:
        wmo_levels, wmo_cols = get_levels_and_palette(main_variable)
    elif grid_type == 'unc':
        wmo_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    elif grid_type == 'rank':
        wmo_cols = ["#ffffff", "#feb24c", "#fd8d3c", "#f03b20", "#bd0026"]
        wmo_cols = list(reversed(wmo_cols))
        wmo_levels = [0.5, 1.5, 3.5, 5.5, 10.5, 20.5]

    if main_variable == 'sealeveltrend':
        wmo_levels = [-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]
        wmo_cols = ['#2a0ad9', '#264dff', '#3fa0ff', '#72daff', '#aaf7ff', '#e0ffff',
                    '#ffffbf', '#fee098', '#ffad73', '#f76e5e', '#d82632', '#a50022']
    if 'precip_quantiles' in main_variable:
        wmo_levels = [0, 0.1, 0.2, 0.8, 0.9, 1]
        wmo_cols = ['#543005', '#bf812d', '#e5e5e5', '#35978f', '#003c30']

    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_subplot(111, projection=proj, aspect='auto')
    if grid_type in ['mean', 'rank', 'single']:
        p = ax.contourf(wrap_lon, dataset.df.latitude, wrap_data[0, :, :],
                        transform=ccrs.PlateCarree(),
                        levels=wmo_levels,
                        colors=wmo_cols,
                        extend='both'
                        )
    elif grid_type == 'unc':
        p = ax.contourf(wrap_lon, dataset.df.latitude, wrap_data[0, :, :],
                        transform=ccrs.PlateCarree(),
                        levels=wmo_levels,
                        cmap='YlGnBu',
                        extend='max'
                        )

    cbar = plt.colorbar(p, orientation='horizontal', fraction=0.06, pad=0.04)

    cbar.ax.tick_params(labelsize=15)
    cbar.set_ticks(wmo_levels)
    cbar.set_ticklabels(wmo_levels)

    # Add the datasets used and their last months
    plt.gcf().text(.075, .012, ",".join(last_months),
                   bbox={'facecolor': 'w', 'edgecolor': None}, fontsize=10)

    # Add a Created tag to let people know when it was created
    current_time = f"Created: {datetime.today()}"
    plt.gcf().text(.90, .012, current_time[0:28], ha='right',
                   bbox={'facecolor': 'w', 'edgecolor': None})

    label_text = f"Temperature difference from " \
                 f"{ds.metadata['climatology_start']}-{ds.metadata['climatology_end']} average ($\degree$C)"
    if grid_type == 'unc':
        label_text = r'Temperature anomaly half-range ($\degree$C)'
    if main_variable == 'sealeveltrend':
        label_text = r'Sea level trend (mm/year)'
    if 'precip_quantiles' in main_variable:
        label_text = r'Precipitation quantile relative to 1991-2020'
    cbar.set_label(label_text, rotation=0, fontsize=15)

    p.axes.coastlines()
    if region is not None:
        if region[1] > 180:
            temp_proj = ccrs.PlateCarree()
            p.axes.set_extent(region, crs=temp_proj)
            p.axes.set_aspect('equal')
        else:
            p.axes.set_extent(region, crs=proj)
            p.axes.set_aspect('equal')
    else:
        p.axes.set_global()

    plt.title(f'{title}', pad=20, fontdict={'fontsize': 20})
    plt.savefig(out_dir / f'{image_filename}')
    plt.savefig(out_dir / f'{image_filename}'.replace('.png', '.pdf'))
    plt.savefig(out_dir / f'{image_filename}'.replace('.png', '.svg'))
    plt.close('all')

    caption = map_caption_builder(all_datasets, grid_type)

    return caption


def dashboard_map_single(out_dir: Path, all_datasets: List[GridAnnual], image_filename: str, title: str) -> str:
    return dashboard_map_generic(out_dir, all_datasets, image_filename, title, 'single')


def dashboard_map(out_dir: Path, all_datasets: List[GridAnnual], image_filename: str, title: str) -> str:
    return dashboard_map_generic(out_dir, all_datasets, image_filename, title, 'mean')


def dashboard_uncertainty_map(out_dir: Path, all_datasets: List[GridAnnual], image_filename: str, title: str) -> str:
    return dashboard_map_generic(out_dir, all_datasets, image_filename, title, 'unc')


def dashboard_rank_map(out_dir: Path, all_datasets: List[GridAnnual], image_filename: str, title: str) -> str:
    return dashboard_map_generic(out_dir, all_datasets, image_filename, title, 'rank')


def regional_dashboard_map(out_dir: Path, all_datasets: List[GridAnnual], image_filename: str, title: str,
                           west=None, east=None, south=None, north=None) -> str:
    region_extents = [west, east, south, north]
    return dashboard_map_generic(out_dir, all_datasets, image_filename, title, 'mean', region=region_extents)


def regional_dashboard_map_single(out_dir: Path, all_datasets: List[GridAnnual], image_filename: str, title: str,
                                  west=None, east=None, south=None, north=None) -> str:
    region_extents = [west, east, south, north]
    return dashboard_map_generic(out_dir, all_datasets, image_filename, title, 'single', region=region_extents)


def regional_dashboard_uncertainty_map(out_dir: Path, all_datasets: List[GridAnnual], image_filename: str, title: str,
                                       west=None, east=None, south=None, north=None) -> str:
    region_extents = [west, east, south, north]
    return dashboard_map_generic(out_dir, all_datasets, image_filename, title, 'unc', region=region_extents)


# Miscellany
def wave_plot(out_dir: Path, dataset: TimeSeriesMonthly, image_filename) -> None:
    """
    Wave plot with month on the x-axis from January to December and each year shown as a separate line
    showing the cumulative average for the year-to-date for that year.

    Parameters
    ----------
    out_dir: Path
        Path to the directory to which the image will be written.
    dataset: TimeSeriesMonthly
        :class:`.TimeSeriesMonthly` to plot.
    image_filename: str
        Name of the image file to be written.

    Returns
    -------
    None
    """
    first_year, last_year = dataset.get_first_and_last_year()

    plt.figure(figsize=[9, 9])

    df = copy.deepcopy(dataset.df)
    df = df[df['year'] >= last_year]
    df = df[df['year'] <= last_year]
    df = df.reset_index()
    n_months_last_year = len(df)

    all_accumulators = np.zeros((12, last_year - first_year))

    for year in range(first_year, last_year + 1):
        df = copy.deepcopy(dataset.df)
        df = df[df['year'] >= year]
        df = df[df['year'] <= year]
        df = df.reset_index()

        accumulator = accumulate(df['data'])
        n_months = len(df)

        if year < last_year and n_months == 12:
            all_accumulators[:, year - first_year] = accumulator - accumulator[n_months_last_year - 1]

        colour = 'lightgrey'
        lthk = 1
        if year >= 2015:
            colour = 'dodgerblue'  # 'indianred'
            lthk = 2
        if year == last_year:
            all_accumulators = all_accumulators + accumulator[n_months_last_year - 1]
            for y2 in range(1950, last_year):
                colour = 'orange'
                zod = -5
                if y2 in [1982, 1986, 1994, 1997, 2002, 2004, 2006, 2009, 2015, 2018, 1972, 1965, 1963, 1976, 2014,
                          1979]:
                    colour = 'darkred'
                    zod = -1
                plt.plot(range(n_months_last_year, 13), all_accumulators[n_months_last_year - 1:, y2 - first_year],
                         color=colour, linewidth=2, zorder=zod)
            colour = 'darkred'
            lthk = 3

        plt.plot(range(1, n_months + 1), accumulator, color=colour, linewidth=lthk)

    plt.gca().set_xlabel('Month')
    plt.gca().set_ylabel(FANCY_UNITS['degC'])
    plt.gca().set_ylim(0.20, 0.85)
    plt.xticks(np.arange(1, 13, 1))
    plt.title(dataset.metadata['display_name'])

    plt.savefig(out_dir / image_filename)
    plt.close('all')


def wave_multiple_plot(out_dir: Path, all_datasets: List[TimeSeriesMonthly], image_filename) -> None:
    """
    Wave plot with month on the x-axis from January to December and each year shown as a separate line
    showing the cumulative average for the year-to-date for that year.

    Parameters
    ----------
    out_dir: Path
        Path to the directory to which the image will be written.
    dataset: List[TimeSeriesMonthly]
        :class:`.TimeSeriesMonthly` to plot.
    image_filename: str
        Name of the image file to be written.

    Returns
    -------
    None
    """

    plt.figure(figsize=[9, 9])

    for dataset in all_datasets:
        first_year, last_year = dataset.get_first_and_last_year()

        df = copy.deepcopy(dataset.df)
        df = df[df['year'] >= last_year]
        df = df[df['year'] <= last_year]
        df = df.reset_index()
        n_months_last_year = len(df)

        all_accumulators = np.zeros((12, last_year - first_year))

        for year in range(first_year, last_year + 1):
            df = copy.deepcopy(dataset.df)
            df = df[df['year'] >= year]
            df = df[df['year'] <= year]
            df = df.reset_index()

            accumulator = accumulate(df['data'])
            n_months = len(df)

            if year < last_year and n_months == 12:
                all_accumulators[:, year - first_year] = accumulator - accumulator[n_months_last_year - 1]

            if year != 2016 and year != 2023:
                colour = '#aaaaaa'
                lthk = 1
            if year == 2016:
                colour = '#41b6c4'
                lthk = 2

            if year == last_year:
                all_accumulators = all_accumulators + accumulator[n_months_last_year - 1]
                for y2 in range(1950, last_year):
                    colour = 'orange'
                    zod = -5
                    if y2 in [1982, 1986, 1994, 1997, 2002, 2004, 2006, 2009, 2015, 2018, 1972, 1965, 1963, 1976, 2014,
                              1979]:
                        colour = 'darkred'
                        zod = -1
                    if n_months > 8:
                        pass
                        # plt.plot(range(n_months_last_year, 13),
                        #          all_accumulators[n_months_last_year - 1:, y2 - first_year],
                        #          color=colour, linewidth=2, zorder=zod, alpha=0.2)
                colour = 'darkred'
                lthk = 3

            plt.plot(range(1, n_months + 1), accumulator, color=colour, linewidth=lthk, zorder=year)

    # Draw 1.5C line
    plt.plot([1, 12], [1.5 - 0.69, 1.5 - 0.69], color='black', linewidth=2)
    plt.fill_between([1, 12], [1.5 - 0.54, 1.5 - 0.54], [1.5 - 0.79, 1.5 - 0.79], color='green', alpha=0.1)
    plt.gcf().text(0.86, 0.85, r"~1.5$\!^\circ\!$C range", color='green', fontsize=20, ha='right', alpha=0.5)

    import matplotlib.patheffects as PathEffects
    peb = PathEffects.withStroke(linewidth=1.5, foreground="#555555")

    plt.gcf().text(0.45, 0.710, '2016', fontsize=30, color='#41b6c4')
    plt.gcf().text(0.50, 0.415, '2023', fontsize=30, color='darkred')
    plt.gcf().text(0.54, 0.200, 'Other years', fontsize=30, color='#aaaaaa', ha='center', path_effects=[peb])

    plt.gca().set_xlabel('Average from January to Month')
    plt.gca().set_ylabel(f"{FANCY_UNITS['degC']} difference from 1981-2010")
    plt.gca().set_ylim(0.30, 0.85)
    plt.xticks(np.arange(1, 13, 1),
               ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])
    plt.title('Year-to-date Global Temperature Anomalies 1850-2023', fontsize=25, y=1.04)

    plt.gcf().text(.075, .012, "With HadCRUT5, NOAAGlobalTemp, GISTEMP, Berkeley Earth, ERA5, and JRA-55",
                   bbox={'facecolor': 'w', 'edgecolor': None}, fontsize=10)

    # plt.gcf().text(.90, .012, 'by @micefearboggis', ha='right', bbox={'facecolor': 'w', 'edgecolor': None})

    plt.savefig(out_dir / image_filename, bbox_inches='tight', pad_inches=0.2)
    plt.savefig(out_dir / image_filename.replace('.png', '.svg'), bbox_inches='tight', pad_inches=0.2)
    plt.close('all')


def rising_tide_plot(out_dir: Path, dataset: TimeSeriesMonthly, image_filename) -> None:
    """
    Rising tide plot with month on the x-axis from January to December and each year shown as a separate line
    showing the monthly averages that year.

    Parameters
    ----------
    out_dir: Path
        Path to the directory to which the image will be written.
    dataset: TimeSeriesMonthly
        :class:`.TimeSeriesMonthly` to plot.
    image_filename: str
        Name of the image file to be written.

    Returns
    -------
    None
    """
    first_year, last_year = dataset.get_first_and_last_year()

    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

    plt.figure(figsize=[9, 9])

    df = copy.deepcopy(dataset.df)
    df = df[df['year'] >= last_year]
    df = df[df['year'] <= last_year]
    df = df.reset_index()

    for year in range(first_year, last_year + 1):
        df = copy.deepcopy(dataset.df)
        df = df[df['year'] >= year]
        df = df[df['year'] <= year]
        df = df.reset_index()

        accumulator = df['data']
        n_months = len(df)

        colour = 'lightgrey'
        lthk = 1
        if year >= 2015:
            colour = 'dodgerblue'
            lthk = 2
        if year == last_year:
            colour = 'darkred'
            lthk = 3

        plt.plot(range(1, n_months + 1), accumulator, color=colour, linewidth=lthk)

    plt.gca().set_xlabel('Month')
    plt.gca().set_ylabel(FANCY_UNITS['degC'])
    plt.gca().set_ylim(-1.5, 1.5)
    plt.xticks(np.arange(1, 13, 1),
               ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])
    plt.title(dataset.metadata['display_name'], fontsize=20)

    plt.savefig(out_dir / image_filename)
    plt.close('all')


def rising_tide_multiple_plot(out_dir: Path, all_datasets: List[TimeSeriesMonthly], image_filename) -> None:
    """
    Rising tide plot with month on the x-axis from January to December and each year shown as a separate line
    showing the monthly averages that year.

    Parameters
    ----------
    out_dir: Path
        Path to the directory to which the image will be written.
    dataset: TimeSeriesMonthly
        :class:`.TimeSeriesMonthly` to plot.
    image_filename: str
        Name of the image file to be written.

    Returns
    -------
    None
    """

    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

    plt.figure(figsize=[9, 9])

    for dataset in all_datasets:
        first_year, last_year = dataset.get_first_and_last_year()
        for year in range(first_year, last_year + 1):
            df = copy.deepcopy(dataset.df)
            df = df[df['year'] >= year]
            df = df[df['year'] <= year]
            df = df.reset_index()

            accumulator = df['data']
            n_months = len(df)

            colours = ['#ffffcc', '#c7e9b4', '#7fcdbb', '#41b6c4', '#1d91c0', '#225ea8', '#0c2c84']

            if year < 1970:
                cindex = 0
            if year >= 1970 and year < 1980:
                cindex = 1
            if year >= 1980 and year < 1990:
                cindex = 2
            if year >= 1990 and year < 2000:
                cindex = 3
            if year >= 2000 and year < 2010:
                cindex = 4
            if year >= 2010 and year < 2020:
                cindex = 5
            if year >= 2020:
                cindex = 6

            colour = colours[cindex]

            lthk = 1
            if year >= 2035:
                colour = 'dodgerblue'
                lthk = 2
            if year == last_year:
                colour = 'darkred'
                lthk = 3

            plt.plot(range(1, n_months + 1), accumulator, color=colour, linewidth=lthk, zorder=year)

    plt.gca().set_xlabel('Month')
    plt.gca().set_ylabel(f"{FANCY_UNITS['degC']} difference from 1981-2010")
    plt.gca().set_ylim(-1.5, 1.2)
    plt.xticks(np.arange(1, 13, 1),
               ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])
    plt.title('Monthly Global Temperature Anomalies 1850-2023', fontsize=25, y=1.04)

    import matplotlib.patheffects as PathEffects

    pew = PathEffects.withStroke(linewidth=1.5, foreground="w")
    peb = PathEffects.withStroke(linewidth=1.5, foreground="b")

    plt.gcf().text(0.52, 0.31, '1850-1969', color=colours[0], fontsize=30, ha='center', path_effects=[peb])
    plt.gcf().text(0.52, 0.41, '1970s', color=colours[1], fontsize=30, ha='center', path_effects=[peb])
    plt.gcf().text(0.52, 0.47, '1980s', color=colours[2], fontsize=30, ha='center', path_effects=[peb])
    plt.gcf().text(0.52, 0.53, '1990s', color=colours[3], fontsize=30, ha='center', path_effects=[peb])
    plt.gcf().text(0.52, 0.57, '2000s', color=colours[4], fontsize=30, ha='center', path_effects=[pew])
    plt.gcf().text(0.52, 0.61, '2010s', color=colours[5], fontsize=30, ha='center', path_effects=[pew])
    plt.gcf().text(0.52, 0.65, '2020s', color=colours[6], fontsize=30, ha='center', path_effects=[pew])

    plt.gcf().text(0.52, 0.81, '2023', color='darkred', fontsize=30, ha='center', path_effects=[pew])

    plt.gcf().text(.075, .012, "With HadCRUT5, NOAAGlobalTemp, GISTEMP, Berkeley Earth, ERA5, and JRA-55",
                   bbox={'facecolor': 'w', 'edgecolor': None}, fontsize=10)

    # plt.gcf().text(.90, .012, 'by @micefearboggis', ha='right', bbox={'facecolor': 'w', 'edgecolor': None})

    plt.savefig(out_dir / image_filename, bbox_inches='tight', pad_inches=0.2)
    plt.savefig(out_dir / image_filename.replace('.png', '.svg'), bbox_inches='tight', pad_inches=0.2)
    plt.close('all')


def preindustrial_summary_plot(out_dir: Path, in_all_datasets: List[Union[TimeSeriesAnnual]],
                               image_filename: str, title: str) -> str:
    variables = get_list_of_unique_variables(in_all_datasets)

    plt.figure(figsize=[16, 9])

    for i, v in enumerate(variables):
        all_datasets = []
        for ds in in_all_datasets:
            if ds.metadata['variable'] == v:
                all_datasets.append(ds)

        holder = AveragesCollection(all_datasets)
        holder.expand = True
        holder.widest = True

        plt.fill_between([i, i + 1],
                         [holder.lower_range(), holder.lower_range()],
                         [holder.upper_range(), holder.upper_range()],
                         color='#7ea0f7'
                         )

        holder.widest = False

        plt.fill_between([i, i + 1],
                         [holder.lower_range(), holder.lower_range()],
                         [holder.upper_range(), holder.upper_range()],
                         color='#466dcf'
                         )

        holder.expand = False

        plt.fill_between([i, i + 1],
                         [holder.lower_range(), holder.lower_range()],
                         [holder.upper_range(), holder.upper_range()],
                         color='#173c99'
                         )

        plt.plot([i, i + 1], [holder.best_estimate(), holder.best_estimate()], color='black', linewidth=2)

        plt.text(i + 0.5, 0, equivalence(v), ha='center', va='center', fontsize=20)

    ylims = plt.gca().get_ylim()
    ylims = [ylims[0], ylims[1]]
    if ylims[1] < 0.1:
        ylims[1] = 0.1
    plt.gca().set_ylim(ylims[0], ylims[1])

    plt.savefig(out_dir / image_filename, bbox_inches=Bbox([[0.2, 0], [14.5, 9]]))
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))

    plt.close('all')

    caption = ''
    return caption
