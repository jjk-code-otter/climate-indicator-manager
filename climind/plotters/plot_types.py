from pathlib import Path
import cartopy.crs as ccrs
from cartopy.util import add_cyclic_point
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import seaborn as sns
import numpy as np

FANCY_UNITS = {"degC": r"$\!^\circ\!$C",
               "zJ": "zJ",
               "millionkm2": "million km$^2$",
               "ph": "pH",
               "mwe": "m.w.e"}


def set_lo_hi_ticks(limits, spacing):
    """
    Given axis limits and a preferred spacing, calculate new high and low values and a set of ticks

    Parameters
    ----------
    limits: list
        the lower and upper limits of the current axis
    spacing: float
        The preferred tick spacing

    Returns
    -------

    """
    lo = spacing * (1 + (limits[0] // spacing))
    hi = spacing * (1 + (limits[1] // spacing))
    ticks = np.arange(lo, hi, spacing)

    return lo, hi, ticks


def get_first_and_last_years(all_datasets):
    """
    Extract the first and last years from a list of data sets
    Parameters
    ----------
    all_datasets

    Returns
    -------
    int, int
        First and last years
    """
    first_years = []
    last_years = []
    for ds in all_datasets:
        first_years.append(ds.df['year'].tolist()[0])
        last_years.append(ds.df['year'].tolist()[-1])
    first_year = np.min(first_years)
    last_year = np.max(last_years)

    return first_year, last_year


def caption_builder(all_datasets):
    first_year, last_year = get_first_and_last_years(all_datasets)

    ds = all_datasets[-1]

    number_to_word = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
                      'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen']

    caption = f"{ds.metadata['time_resolution']} {ds.metadata['long_name']} ({ds.metadata['units']}"
    if not ds.metadata['actual']:
        caption += f", difference from the {ds.metadata['climatology_start']}-{ds.metadata['climatology_end']} average"
    caption += ") "
    caption += f" from {first_year}-{last_year}. "
    if len(all_datasets) > 1:
        caption += f"Data are from the following {number_to_word[len(all_datasets)]} data sets: "
    else:
        caption += f"Data are from "

    dataset_names_for_caption = []
    for ds in all_datasets:
        dataset_names_for_caption.append(f"{ds.metadata['name']}")

    caption += ', '.join(dataset_names_for_caption)
    caption += '.'

    return caption


def pink_plot(out_dir: Path, all_datasets: list, image_filename: str, title: str):
    sns.set(font='Franklin Gothic Book', rc={
        'axes.axisbelow': False,
        'axes.labelsize': 20,
        'xtick.labelsize': 15,
        'ytick.labelsize': 15,
        'axes.edgecolor': '#6b001d',
        'axes.facecolor': 'None',

        'axes.grid.axis': 'y',
        'grid.color': '#6b001d',
        'grid.alpha': 0.5,

        'axes.labelcolor': '#6b001d',

        'axes.spines.left': False,
        'axes.spines.right': False,
        'axes.spines.top': False,

        'figure.facecolor': 'black',
        'lines.solid_capstyle': 'round',
        'patch.edgecolor': 'w',
        'patch.force_edgecolor': True,
        'text.color': '#6b001d',

        'xtick.bottom': True,
        'xtick.color': '#6b001d',
        'xtick.direction': 'out',
        'xtick.top': False,

        'ytick.major.width': 0.4,
        'ytick.color': '#6b001d',
        'ytick.direction': 'out',
        'ytick.left': True,
        'ytick.right': False})

    zords = []

    cols = ['#4a0014', '#6e001e', '#9c022c', '#bf0034', '#f70043', '#ff2b65', '#abcdef']

    plt.figure(figsize=[16, 9])
    for i, ds in enumerate(all_datasets):
        # col = ds.metadata['colour']
        col = cols[i]
        zord = ds.metadata['zpos']
        zords.append(zord)
        plt.plot(ds.df['year'], ds.df['data'], label=ds.metadata['name'], color=col, zorder=zord)
    ds = all_datasets[-1]

    sns.despine(right=True, top=True, left=True)

    plt.xlim(1845, 2025)
    plt.ylim(-0.4, 1.4)

    plot_units = ds.metadata['units']
    if plot_units in FANCY_UNITS:
        plot_units = FANCY_UNITS[plot_units]
    plt.xlabel('Year')
    plt.ylabel(plot_units, rotation=0, labelpad=10)

    plt.yticks(np.arange(-0.2, 1.4, 0.2))
    plt.xticks(np.arange(1860, 2040, 20))

    plt.legend()
    # get handles and labels
    handles, labels = plt.gca().get_legend_handles_labels()
    # specify order of items in legend
    order = np.flip(np.argsort(zords))
    # add legend to plot
    leg = plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order], frameon=False, prop={'size': 20})
    for line in leg.get_lines():
        line.set_linewidth(3.0)

    ylim = plt.gca().get_ylim()
    yloc = ylim[1] + 0.02 * (ylim[1] - ylim[0])

    if ds.metadata['actual']:
        subtitle = ''
    else:
        subtitle = f"Compared to {ds.metadata['climatology_start']}-" \
                   f"{ds.metadata['climatology_end']} average"

    plt.text(plt.gca().get_xlim()[0], yloc, subtitle, fontdict={'fontsize': 30})
    plt.gca().set_title(title, pad=45, fontdict={'fontsize': 40}, loc='left')

    plt.savefig(out_dir / image_filename, transparent=True)
    plt.close()
    return


def dark_plot(out_dir: Path, all_datasets: list, image_filename: str, title: str):
    sns.set(font='Franklin Gothic Book', rc={
        'axes.axisbelow': False,
        'axes.labelsize': 20,
        'xtick.labelsize': 15,
        'ytick.labelsize': 15,
        'axes.edgecolor': 'lightgrey',
        'axes.facecolor': 'None',

        'axes.grid.axis': 'y',
        'grid.color': 'dimgrey',
        'grid.alpha': 0.5,

        'axes.labelcolor': 'lightgrey',

        'axes.spines.left': False,
        'axes.spines.right': False,
        'axes.spines.top': False,

        'figure.facecolor': 'black',
        'lines.solid_capstyle': 'round',
        'patch.edgecolor': 'w',
        'patch.force_edgecolor': True,
        'text.color': 'lightgrey',

        'xtick.bottom': True,
        'xtick.color': 'lightgrey',
        'xtick.direction': 'out',
        'xtick.top': False,

        'ytick.major.width': 0.4,
        'ytick.color': 'lightgrey',
        'ytick.direction': 'out',
        'ytick.left': True,
        'ytick.right': False})

    zords = []
    plt.figure(figsize=[16, 9])
    for i, ds in enumerate(all_datasets):
        col = ds.metadata['colour']
        if col == 'dimgrey':
            col = '#eeeeee'
        zord = ds.metadata['zpos']
        zords.append(zord)
        plt.plot(ds.df['year'], ds.df['data'], label=ds.metadata['name'], color=col, zorder=zord)
    ds = all_datasets[-1]

    sns.despine(right=True, top=True, left=True)

    plot_units = ds.metadata['units']
    if plot_units in FANCY_UNITS:
        plot_units = FANCY_UNITS[plot_units]
    plt.xlabel('Year')
    plt.ylabel(plot_units, rotation=0, labelpad=10)

    ylims = plt.gca().get_ylim()
    ylo = 0.2 * (1 + (ylims[0] // 0.2))
    yhi = 0.2 * (1 + (ylims[1] // 0.2))

    plt.yticks(np.arange(ylo, yhi, 0.2))
    # plt.yticks(np.arange(-0.2, 1.4, 0.2))
    plt.xticks(np.arange(1860, 2040, 20))

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
    yloc = ylim[1] + 0.02 * (ylim[1] - ylim[0])

    if ds.metadata['actual']:
        subtitle = ''
    else:
        subtitle = f"Compared to {ds.metadata['climatology_start']}-" \
                   f"{ds.metadata['climatology_end']} average"

    plt.text(plt.gca().get_xlim()[0], yloc, subtitle, fontdict={'fontsize': 30})
    plt.gca().set_title(title, pad=45, fontdict={'fontsize': 40}, loc='left')

    plt.savefig(out_dir / image_filename)
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.close()
    return


def neat_plot(out_dir: Path, all_datasets: list, image_filename: str, title: str) -> str:
    """
    Create the standard annual plot

    Parameters
    ----------
    out_dir: Path
        Directory to which the figure will be written
    all_datasets: list
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

    caption = caption_builder(all_datasets)

    zords = []
    plt.figure(figsize=[16, 9])
    for i, ds in enumerate(all_datasets):
        col = ds.metadata['colour']
        zord = ds.metadata['zpos']
        zords.append(zord)
        plt.plot(ds.df['year'], ds.df['data'], label=ds.metadata['name'], color=col, zorder=zord, linewidth=3)
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

    if ds.metadata['variable'] in ['ohc', 'glacier']:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 5.0)

    if ds.metadata['variable'] == 'ph':
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 0.01)

    if ds.metadata['variable'] in ['mhw', 'mcs']:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 10.)

    if ds.metadata['variable'] in ['greenland']:
        ylo, yhi, yticks = set_lo_hi_ticks(ylims, 50.)

    xlims = plt.gca().get_xlim()
    xlo, xhi, xticks = set_lo_hi_ticks(xlims, 20.)
    if len(xticks) < 3:
        xlo, xhi, xticks = set_lo_hi_ticks(xlims, 10.)

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

    plt.savefig(out_dir / image_filename, bbox_inches=Bbox([[0.8, 0], [14.5, 9]]))
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))
    plt.close()
    return caption


def decade_plot(out_dir: Path, all_datasets: list, image_filename: str, title: str):
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

    zords = []
    plt.figure(figsize=[16, 9])
    for i, ds in enumerate(all_datasets):
        col = ds.metadata['colour']
        zord = ds.metadata['zpos']
        zords.append(zord)
        plt.plot(ds.df['year'], ds.df['data'], label=ds.metadata['name'], color=col, zorder=zord,
                 alpha=0.0)

        for j in range(len(ds.df['year'])):
            plt.plot([ds.df['year'][j] - 9, ds.df['year'][j]],
                     [ds.df['data'][j], ds.df['data'][j]], color=col, zorder=zord)

        pass
    ds = all_datasets[-1]
    sns.despine(right=True, top=True, left=True)

    plot_units = ds.metadata['units']
    if plot_units in FANCY_UNITS:
        plot_units = FANCY_UNITS[plot_units]
    plt.xlabel('Year')
    plt.ylabel(plot_units, rotation=0, labelpad=10)

    ylims = plt.gca().get_ylim()
    ylo = 0.2 * (1 + (ylims[0] // 0.2))
    yhi = 0.2 * (1 + (ylims[1] // 0.2))

    plt.yticks(np.arange(ylo, yhi, 0.2))
    # plt.yticks(np.arange(-0.2, 1.4, 0.2))
    plt.xticks(np.arange(1860, 2040, 20))

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
    return


def neat_plot2(out_dir: Path, all_datasets: list, image_filename: str, title: str):
    sns.set(font='Franklin Gothic Book', rc={
        'axes.axisbelow': False,
        'axes.labelsize': 20,
        'xtick.labelsize': 15,
        'ytick.labelsize': 15,
        'axes.edgecolor': 'lightgrey',
        'axes.facecolor': 'None',

        'axes.grid': False,

        'axes.labelcolor': 'dimgrey',

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

        'ytick.color': 'dimgrey',
        'ytick.direction': 'out',
        'ytick.left': True,
        'ytick.right': False})

    #    colours = ["#444444",
    #               "#e69f00",
    #               "#56b4e9",
    #               "#009e73",
    #               "#d55e00",
    #               "#0072b2"]

    zords = []
    plt.figure(figsize=[16, 9])
    for i, ds in enumerate(all_datasets):
        col = ds.metadata['colour']
        zord = ds.metadata['zpos']
        zords.append(zord)
        plt.plot(ds.df['year'], ds.df['data'], label=ds.metadata['name'], color=col, zorder=zord)
    ds = all_datasets[-1]

    sns.despine(right=True, top=True)

    plot_units = ds.metadata['units']
    if plot_units in FANCY_UNITS:
        plot_units = FANCY_UNITS[plot_units]
    plt.xlabel('Year')
    plt.ylabel(plot_units, rotation=0, labelpad=10)

    plt.yticks(np.arange(-0.2, 1.4, 0.2))
    plt.xticks(np.arange(1860, 2040, 20))

    plt.legend()
    # get handles and labels
    handles, labels = plt.gca().get_legend_handles_labels()
    # specify order of items in legend
    order = np.flip(np.argsort(zords))
    # add legend to plot
    leg = plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order], frameon=False, prop={'size': 20})
    for line in leg.get_lines():
        line.set_linewidth(3.0)

    ylim = plt.gca().get_ylim()
    yloc = ylim[1] + 0.02 * (ylim[1] - ylim[0])

    if ds.metadata['actual']:
        subtitle = ''
    else:
        subtitle = f"Compared to {ds.metadata['climatology_start']}-" \
                   f"{ds.metadata['climatology_end']} average"

    plt.text(plt.gca().get_xlim()[0], yloc, subtitle, fontdict={'fontsize': 30})
    plt.gca().set_title(title, pad=45, fontdict={'fontsize': 40}, loc='left')

    plt.savefig(out_dir / image_filename)
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.close()
    return


def monthly_plot(out_dir: Path, all_datasets: list, image_filename: str, title: str) -> str:
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

    caption = caption_builder(all_datasets)

    zords = []
    plt.figure(figsize=[16, 9])
    for i, ds in enumerate(all_datasets):
        col = ds.metadata['colour']
        zord = ds.metadata['zpos']
        zords.append(zord)
        plt.plot(ds.df['year'] + (ds.df['month'] - 1) / 12., ds.df['data'],
                 label=ds.metadata['name'], color=col,
                 zorder=zord)
    ds = all_datasets[-1]

    sns.despine(right=True, top=True, left=True)

    plot_units = ds.metadata['units']
    if plot_units in FANCY_UNITS:
        plot_units = FANCY_UNITS[plot_units]
    plt.xlabel('Year')
    plt.ylabel(plot_units, rotation=90, labelpad=23)

    ylims = plt.gca().get_ylim()
    if ds.metadata['variable'] in ['tas', 'lsat', 'sst']:
        ylo = 0.2 * (1 + (ylims[0] // 0.2))
        yhi = 0.2 * (1 + (ylims[1] // 0.2))
        plt.yticks(np.arange(ylo, yhi, 0.2))
        plt.xticks(np.arange(2014, 2023, 1))
    elif ds.metadata['variable'] == 'co2':
        ylo = 10. * (1 + (ylims[0] // 10.))
        yhi = 10. * (1 + (ylims[1] // 10.))
        plt.yticks(np.arange(ylo, yhi, 10.))
        plt.xticks(np.arange(1950, 2023, 10))

    # plt.yticks(np.arange(-0.2, 1.4, 0.2))

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

    plt.savefig(out_dir / image_filename, bbox_inches=Bbox([[0.8, 0], [14.5, 9]]))
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.savefig(out_dir / image_filename.replace('png', 'svg'))
    plt.close()
    return caption


def marine_heatwave_plot(out_dir: Path, all_datasets: list, image_filename: str, title: str) -> str:
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
        plt.plot(ds.df['year'], ds.df['data'], label='Marine cold spells', color=col, zorder=zord, linewidth=3)
    for i, ds in enumerate(mhw):
        col = ds.metadata['colour']
        zord = ds.metadata['zpos']
        zords.append(zord)
        plt.plot(ds.df['year'], ds.df['data'], label='Marine heatwaves', color=col, zorder=zord, linewidth=3)
    ds = mcs[-1]

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
    return "Figure showing the percentage of ocean area affected by marine heatwaves and marine cold spells each year since 1982"


def arctic_sea_ice_plot(out_dir: Path, all_datasets: list, image_filename: str, title: str) -> str:
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

    march_colors = ['#56b4e9', '#009e73']
    september_colors = ['#e69f00', '#d55e00']

    zords = []
    plt.figure(figsize=[16, 9])
    for i, ds in enumerate(all_datasets):
        subds = ds.make_annual_by_selecting_month(3)
        plt.plot(subds.df['year'], subds.df['data'], label=f"{ds.metadata['name']} March",
                 color=march_colors[i], linewidth=3)

    for i, ds in enumerate(all_datasets):
        subds = ds.make_annual_by_selecting_month(9)
        plt.plot(subds.df['year'], subds.df['data'], label=f"{ds.metadata['name']} September",
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


def antarctic_sea_ice_plot(out_dir: Path, all_datasets: list, image_filename: str, title: str) -> str:
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

    february_colors = ['#e69f00', '#d55e00']
    september_colors = ['#56b4e9', '#009e73']

    zords = []
    plt.figure(figsize=[16, 9])
    for i, ds in enumerate(all_datasets):
        subds = ds.make_annual_by_selecting_month(2)
        plt.plot(subds.df['year'], subds.df['data'], label=f"{ds.metadata['name']} February",
                 color=february_colors[i], linewidth=3)

    for i, ds in enumerate(all_datasets):
        subds = ds.make_annual_by_selecting_month(9)
        plt.plot(subds.df['year'], subds.df['data'], label=f"{ds.metadata['name']} September",
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

    return


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

    # wmo_levels = [-10, -5, -3, -2, -1, -0.5, 0, 0.5, 1, 2, 3, 5, 10]
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


