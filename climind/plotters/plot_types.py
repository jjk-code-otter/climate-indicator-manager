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
import itertools
from pathlib import Path

import cartopy.crs as ccrs
from cartopy.util import add_cyclic_point
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.transforms import Bbox
import seaborn as sns
import numpy as np
from typing import List, Union

from climind.data_types.timeseries import TimeSeriesMonthly, TimeSeriesAnnual
from climind.data_types.grid import GridAnnual
from climind.plotters.plot_utils import calculate_trends, calculate_ranks, calculate_values, set_lo_hi_ticks, \
    caption_builder, map_caption_builder

FANCY_UNITS = {"degC": r"$\!^\circ\!$C",
               "zJ": "zJ",
               "millionkm2": "million km$^2$",
               "ph": "pH",
               "mwe": "m.w.e"}

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


def add_data_sets(axis, all_datasets: List[Union[TimeSeriesAnnual, TimeSeriesMonthly]],
                  dark: bool = False) -> List[int]:
    """
    Given a list of data sets, plot each one on the provided axis.

    Parameters
    ----------
    axis: Matplotlib axis
        Set of Matplotlib axes for plotting on
    all_datasets: List[TimeSeriesAnnual]
        list of data sets to be plotted on the axes

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

        if isinstance(ds, TimeSeriesAnnual):
            x_values = ds.df['year']
            linewidth = 3
            start_year, end_year = ds.get_first_and_last_year()
            date_range = f"{start_year}-{end_year}"
        elif isinstance(ds, TimeSeriesMonthly):
            x_values = ds.df['year'] + (ds.df['month'] - 1) / 12.
            linewidth = 1
            start_date, end_date = ds.get_start_and_end_dates()
            date_range = f"{start_date.year}.{start_date.month:02d}-" \
                         f"{end_date.year}.{end_date.month:02d}"

        else:
            raise TypeError('Wrong kind of object')

        axis.plot(x_values, ds.df['data'], label=f"{ds.metadata['display_name']} ({date_range})",
                  color=col, zorder=zord, linewidth=linewidth)

        if 'uncertainty' in ds.df.columns:
            axis.fill_between(x_values,
                              ds.df['data'] + ds.df['uncertainty'],
                              ds.df['data'] - ds.df['uncertainty'],
                              color=col, alpha=0.1)

    return zords


def add_labels(axis, dataset):
    plot_units = dataset.metadata['units']
    if plot_units in FANCY_UNITS:
        plot_units = FANCY_UNITS[plot_units]
    axis.set_xlabel('Year')
    axis.set_ylabel(plot_units, rotation=90, labelpad=10)
    return plot_units


def set_yaxis(axis, dataset):
    ylims = axis.get_ylim()
    ylo, yhi, yticks = set_lo_hi_ticks(ylims, 0.2)
    if len(yticks) > 10:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 0.5)

    if dataset.metadata['variable'] in ['glacier', 'n2o']:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 5.0)

    if dataset.metadata['variable'] in ['ohc', 'ohc2k']:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 50.0)

    if dataset.metadata['variable'] == 'ph':
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 0.01)

    if dataset.metadata['variable'] in ['mhw', 'mcs', 'co2', 'ch4', 'sealevel']:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 10.)

    if dataset.metadata['variable'] in ['ch4']:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 50.)

    if dataset.metadata['variable'] in ['greenland', 'antarctica']:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 1000.)

    return ylo, yhi, yticks


def set_xaxis(axis):
    xlims = axis.get_xlim()
    xlo, xhi, xticks = set_lo_hi_ticks(xlims, 20.)
    if len(xticks) < 3:
        xlo, xhi, xticks = set_lo_hi_ticks(xlims, 10.)

    return xlo, xhi, xticks


def after_plot(zords, ds, title):
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

    plt.text(plt.gca().get_xlim()[0], yloc, subtitle, fontdict={'fontsize': 30})
    plt.gca().set_title(title, pad=35, fontdict={'fontsize': 40}, loc='left')


def dark_plot(out_dir: Path, all_datasets: list, image_filename: str, title: str):
    this_parameter_set = STANDARD_PARAMETER_SET
    this_parameter_set['grid.color'] = '#696969'
    this_parameter_set['figure.facecolor'] = '#000000'
    this_parameter_set['text.color'] = '#d3d3d3'
    this_parameter_set['xtick.color'] = '#d3d3d3'
    this_parameter_set['ytick.color'] = '#d3d3d3'

    sns.set(font='Franklin Gothic Book', rc=this_parameter_set)

    plt.figure(figsize=[16, 9])
    zords = add_data_sets(plt.gca(), all_datasets, dark=True)
    ds = all_datasets[-1]

    sns.despine(right=True, top=True, left=True)

    add_labels(plt.gca(), ds)

    ylo, yhi, yticks = set_yaxis(plt.gca(), ds)
    xlo, xhi, xticks = set_xaxis(plt.gca())
    plt.yticks(yticks)
    plt.xticks(xticks)

    after_plot(zords, ds, title)

    plt.savefig(out_dir / image_filename)
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.close()
    return ''


def neat_plot(out_dir: Path, all_datasets: List[TimeSeriesAnnual],
              image_filename: str, title: str) -> str:
    """
    Create the standard annual plot

    Parameters
    ----------
    out_dir: Path
        Directory to which the figure will be written
    all_datasets: List[TimeSeriesAnnual]
        list of datasets to be plotted
    image_filename: str
        filename for the figure. Must end in .png
    title: str
        title for the plot

    Returns
    -------
    str
        Caption for the figure is returned
    """
    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

    caption = caption_builder(all_datasets)

    plt.figure(figsize=[16, 9])
    zords = add_data_sets(plt.gca(), all_datasets)
    ds = all_datasets[-1]

    sns.despine(right=True, top=True, left=True)

    add_labels(plt.gca(), ds)

    ylo, yhi, yticks = set_yaxis(plt.gca(), ds)
    xlo, xhi, xticks = set_xaxis(plt.gca())
    plt.yticks(yticks)
    plt.xticks(xticks)

    after_plot(zords, ds, title)

    plt.savefig(out_dir / image_filename, bbox_inches=Bbox([[0.8, 0], [14.5, 9]]))
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))
    plt.close()
    return caption


def decade_plot(out_dir: Path, all_datasets: List[TimeSeriesAnnual], image_filename: str, title: str) -> str:
    """
    Decadal plot

    Parameters
    ----------
    out_dir: Path
        Path of the directory to which the image will be written
    all_datasets: List[TimeSeriesAnnual]
        List of datasets to be plotted.
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

    ylo, yhi, yticks = set_yaxis(plt.gca(), ds)
    xlo, xhi, xticks = set_xaxis(plt.gca())
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
    plt.close()
    return caption


def monthly_plot(out_dir: Path, all_datasets: List[TimeSeriesMonthly], image_filename: str, title: str) -> str:
    """
    Create the standard monthly plot

    Parameters
    ----------
    out_dir: Path
        Path of directory to which the image will be written
    all_datasets: List[TimeSeriesMonthly]
        List of datasets to plot
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

    ylo, yhi, yticks = set_yaxis(plt.gca(), ds)
    xlo, xhi, xticks = set_xaxis(plt.gca())
    plt.yticks(yticks)
    plt.xticks(xticks)

    after_plot(zords, ds, title)

    plt.savefig(out_dir / image_filename, bbox_inches=Bbox([[0.8, 0], [14.5, 9]]))
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))
    plt.close()
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
        List of data sets to plot
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
        plt.plot(ds.df['year'], ds.df['data'], label=f'Marine cold spells ({date_range})', color=col, zorder=zord, linewidth=3)
    for i, ds in enumerate(mhw):
        col = ds.metadata['colour']
        zord = ds.metadata['zpos']
        zords.append(zord)
        plt.plot(ds.df['year'], ds.df['data'], label=f'Marine heatwaves ({date_range})', color=col, zorder=zord, linewidth=3)

    sns.despine(right=True, top=True, left=True)

    plot_units = '%'
    plt.xlabel('Year')
    plt.ylabel(plot_units, rotation=0, labelpad=10)

    plt.gca().set_ylim(0, 65)
    yticks = np.arange(0, 65, 10)

    xlims = plt.gca().get_xlim()
    xlo, xhi, xticks = set_lo_hi_ticks(xlims, 5.)

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
    plt.close()
    return f"Figure showing the percentage of ocean area affected by " \
           f"marine heatwaves and marine cold spells each year since 1982"


def arctic_sea_ice_plot(out_dir: Path, all_datasets: List[TimeSeriesMonthly], image_filename: str, _) -> str:
    """
    Generate figure showing the March and September sea ice extent anomalies for the input datasets.

    Parameters
    ----------
    out_dir: Path
        Directory to which the image will be written
    all_datasets: List[TimeSeriesMonthly]
        List of data sets to be plotted
    image_filename: str
        File name for the image, should end in .png.

    Returns
    -------
    str
        Caption for the figure
    """
    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

    march_colors = ['#56b4e9', '#009e73', '#000000']
    september_colors = ['#e69f00', '#d55e00', '#000000']

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

    ylo, yhi, yticks = set_yaxis(plt.gca(), ds)
    xlo, xhi, xticks = set_xaxis(plt.gca())
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
    plt.close()
    return "Arctic sea ice extent (shown as differences from the 1981-2010 average) from 1979 to present. Two " \
           "months are shown - March and September - at the annual maximum and minimum extents respectively."


def antarctic_sea_ice_plot(out_dir: Path, all_datasets: List[TimeSeriesMonthly], image_filename: str, _) -> str:
    """
    Generate figure showing the February and September Antarctic sea ice extent anomalies for the input datasets.

    Parameters
    ----------
    out_dir: Path
        Directory to which the image will be written
    all_datasets: List[TimeSeriesMonthly]
        List of data sets to be plotted
    image_filename: str
        File name for the image, should end in .png.

    Returns
    -------
    str
        Caption for the figure
    """
    sns.set(font='Franklin Gothic Book', rc=STANDARD_PARAMETER_SET)

    february_colors = ['#e69f00', '#d55e00']
    september_colors = ['#56b4e9', '#009e73']

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
    ylo, yhi, yticks = set_lo_hi_ticks(ylims, 0.2)
    if len(yticks) > 10:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 0.5)

    xlims = plt.gca().get_xlim()
    xlo, xhi, xticks = set_lo_hi_ticks(xlims, 5.)

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
    plt.close()
    return "Antarctic sea ice extent (shown as differences from the 1981-2010 average) from 1979 to present. Two " \
           "months are shown - September and February - at the annual maximum and minimum extents respectively."


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
        List of data sets to be plotted
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
    caption = f'Figure shows the trends for four sub=periods (1901-1930, 1931-1960, 1961-1990 and 1991-present. ' \
              f'Coloured bars show the mean trend for each region and the black vertical lines indicate the range ' \
              f'of different estimates.'

    equivalence = {
        'tas': 'Globe',
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
    }

    # get list of all unique variables
    variables = []
    superset = []
    names = []
    for ds in in_all_datasets:
        if ds.metadata['variable'] not in variables:
            variables.append(ds.metadata['variable'])
            superset.append([])
            names.append(equivalence[ds.metadata['variable']])

    # build a list of lists, one for each unique variable
    for ds in in_all_datasets:
        i = variables.index(ds.metadata['variable'])
        superset[i].append(ds)

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
                      [1991, 2021]]:

        y1 = start_end[0]
        y2 = start_end[1]

        if grey_background:
            grey_background = False
            rect = patches.Rectangle((y1, -0.2), y2 - y1 + 1, 1.2, color='#eeeeee')
            plt.gca().add_patch(rect)
        else:
            grey_background = True

        # calculate trend for each data set
        for i in range(7):
            pos_ind = variables.index(order[i])
            all_datasets = superset[pos_ind]

            mean_trend, min_trend, max_trend = calculate_trends(all_datasets, y1, y2)
            min_rank, max_rank = calculate_ranks(all_datasets, 2021)
            mean_value, min_value, max_value = calculate_values(all_datasets, 2021)

            print(f'{names[pos_ind]}  2021 {mean_value:.2f} ({min_value:.2f}-{max_value:.2f}), '
                  f'rank: {min_rank}-{max_rank}')
            print(f'{start_end[0]}-{start_end[1]} {mean_trend:.2f} ({min_trend:.2f}-{max_trend:.2f})')

            interset_delta = 0.4
            width = (30. - 2 * interset_delta) / 7.
            rect_xstart = y1 + interset_delta + (width * i)
            mid_point = rect_xstart + width / 2.
            delta = 0.3
            section_mid_point = (y2 + y1) / 2.

            plt.text(section_mid_point, -0.25, f'Trends', fontsize=25, ha='center')
            plt.text(section_mid_point, -0.30, f'{y1}-{y2}', fontsize=25, ha='center')

            # plot a coloured bar
            rect = patches.Rectangle((rect_xstart + delta, 0), width - 2 * delta, mean_trend,
                                     linewidth=0, edgecolor=None, facecolor=colours[i])
            plt.gca().add_patch(rect)
            plt.plot([mid_point, mid_point], [min_trend, max_trend], color='black')

    for i in range(7):
        name_index = variables.index(order[i])
        name = names[name_index]
        plt.text(1902, 0.55 - name_index * 0.05, name, fontsize=25, ha='left', color=colours[i])

        # plot the uncertainty range
    plt.ylabel(r'Trend ($\!^\circ\!$C/decade)', labelpad=5)
    plt.yticks(np.arange(-0.2, 0.8, 0.2))
    plt.gca().set_ylim(-0.2, 0.6)

    plt.gca().set_title(title, pad=45, fontdict={'fontsize': 40}, loc='left')

    plt.savefig(out_dir / image_filename, bbox_inches=Bbox([[0.8, 0], [14.5, 9]]))
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))
    plt.close()

    return caption


def quick_and_dirty_map(dataset, image_filename):
    plt.figure()
    proj = ccrs.PlateCarree()
    p = dataset.tas_mean[-1].plot(transform=proj, robust=True,
                                  subplot_kws={'projection': proj},
                                  levels=[-3, -2, -1, 0, 1, 2, 3])
    p.axes.coastlines()
    plt.title(f'')
    plt.savefig(image_filename, bbox_inches='tight')
    plt.close()


def nice_map(dataset, image_filename, title, var='tas_mean'):
    # This is a pain, but we need to do some magic to convince cartopy that the data
    # are continuous across the dateline
    data = dataset[var]
    lon = dataset.coords['longitude']
    lon_idx = data.dims.index('longitude')
    wrap_data, wrap_lon = add_cyclic_point(data.values, coord=lon, axis=lon_idx)

    plt.figure(figsize=(16, 9))
    proj = ccrs.EqualEarth(central_longitude=0)

    wmo_cols = ['#2a0ad9', '#264dff', '#3fa0ff', '#72daff', '#aaf7ff', '#e0ffff',
                '#ffffbf', '#fee098', '#ffad73', '#f76e5e', '#d82632', '#a50022']

    wmo_levels = [-5, -3, -2, -1, -0.5, -0.25, 0, 0.25, 0.5, 1, 2, 3, 5]

    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_subplot(111, projection=proj, aspect='auto')
    p = ax.contourf(wrap_lon, dataset.latitude, wrap_data[-1, :, :],
                    transform=ccrs.PlateCarree(), robust=True,
                    levels=wmo_levels,
                    colors=wmo_cols, add_colorbar=False,
                    extend='both'
                    )

    cbar = plt.colorbar(p, orientation='horizontal', fraction=0.06, pad=0.04)

    cbar.ax.tick_params(labelsize=15)
    cbar.set_ticks(wmo_levels)
    cbar.set_ticklabels(wmo_levels)
    cbar.set_label(r'Temperature difference from 1981-2010 average ($\degree$C)', rotation=0, fontsize=15)

    p.axes.coastlines()
    p.axes.set_global()

    plt.title(f'{title}', pad=20, fontdict={'fontsize': 20})
    plt.savefig(f'{image_filename}.png')
    plt.savefig(f'{image_filename}.pdf')
    plt.close()


def plot_map_by_year_and_month(dataset, year, month, image_filename, title, var='tas_mean'):
    selection = dataset.df.sel(time=slice(f'{year}-{month:02d}-01',
                                          f'{year}-{month:02d}-28'))

    nice_map(selection, image_filename, title, var=var)


def dashboard_map(out_dir: Path, all_datasets: List[GridAnnual], image_filename: str, title: str) -> str:
    dataset = copy.deepcopy(all_datasets[0])

    out_grid = np.zeros((1, 36, 72))
    n_data_sets = len(all_datasets)
    stack = np.zeros((n_data_sets, 36, 72))
    for i, ds in enumerate(all_datasets):
        stack[i, :, :] = ds.df['tas_mean'].data[0, :, :]

    for xx, yy in itertools.product(range(72), range(36)):
        select = stack[:, yy, xx]
        out_grid[0, yy, xx] = np.median(select[~np.isnan(select)])

    dataset.df['tas_mean'].data = out_grid

    data = dataset.df['tas_mean']
    lon = dataset.df.coords['longitude']
    lon_idx = data.dims.index('longitude')
    wrap_data, wrap_lon = add_cyclic_point(data.values, coord=lon, axis=lon_idx)

    plt.figure(figsize=(16, 9))
    proj = ccrs.EqualEarth(central_longitude=0)

    wmo_cols = ['#2a0ad9', '#264dff', '#3fa0ff', '#72daff', '#aaf7ff', '#e0ffff',
                '#ffffbf', '#fee098', '#ffad73', '#f76e5e', '#d82632', '#a50022']

    wmo_levels = [-5, -3, -2, -1, -0.5, -0.25, 0, 0.25, 0.5, 1, 2, 3, 5]

    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_subplot(111, projection=proj, aspect='auto')
    p = ax.contourf(wrap_lon, dataset.df.latitude, wrap_data[0, :, :],
                    transform=ccrs.PlateCarree(), robust=True,
                    levels=wmo_levels,
                    colors=wmo_cols, add_colorbar=False,
                    extend='both'
                    )

    cbar = plt.colorbar(p, orientation='horizontal', fraction=0.06, pad=0.04)

    cbar.ax.tick_params(labelsize=15)
    cbar.set_ticks(wmo_levels)
    cbar.set_ticklabels(wmo_levels)
    cbar.set_label(r'Temperature difference from 1981-2010 average ($\degree$C)', rotation=0, fontsize=15)

    p.axes.coastlines()
    p.axes.set_global()

    plt.title(f'{title}', pad=20, fontdict={'fontsize': 20})
    plt.savefig(out_dir / f'{image_filename}')
    plt.savefig(out_dir / f'{image_filename}'.replace('.png', '.pdf'))
    plt.savefig(out_dir / f'{image_filename}'.replace('.png', '.svg'))
    plt.close()

    caption = map_caption_builder(all_datasets)

    return caption
