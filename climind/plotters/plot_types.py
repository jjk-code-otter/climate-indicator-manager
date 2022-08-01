from pathlib import Path
import cartopy.crs as ccrs
from cartopy.util import add_cyclic_point
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

FANCY_UNITS = {"degC": "$\!^\circ\!$C", "zJ": "zJ"}


def darker_plot(out_dir: Path, all_datasets: list, image_filename: str, title: str):
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
        col = ds.metadata['colour']
        col = cols[i]
        zord = ds.metadata['zpos']
        zords.append(zord)
        plt.plot(ds.df['year'], ds.df['data'], label=ds.metadata['name'], color=col, zorder=zord)
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
        if col == '#444444':
            col = '#eeeeee'
        zord = ds.metadata['zpos']
        zords.append(zord)
        plt.plot(ds.df['year'], ds.df['data'], label=ds.metadata['name'], color=col, zorder=zord)
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


def neat_plot(out_dir: Path, all_datasets: list, image_filename: str, title: str):
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
        plt.plot(ds.df['year'], ds.df['data'], label=ds.metadata['name'], color=col, zorder=zord)
    sns.despine(right=True, top=True, left=True)

    plot_units = ds.metadata['units']
    if plot_units in FANCY_UNITS:
        plot_units = FANCY_UNITS[plot_units]
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


def monthly_plot(out_dir: Path, all_datasets: list, image_filename: str, title: str):
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
        plt.plot(ds.df['year'] + (ds.df['month'] - 1) / 12., ds.df['data'],
                 label=ds.metadata['name'], color=col,
                 zorder=zord)
    sns.despine(right=True, top=True, left=True)

    plot_units = ds.metadata['units']
    if plot_units in FANCY_UNITS:
        plot_units = FANCY_UNITS[plot_units]
    plt.xlabel('Year')
    plt.ylabel(plot_units, rotation=0, labelpad=23)

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
        plt.xticks(np.arange(1980, 2023, 10))

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

    wmo_levels = [-10, -5, -3, -2, -1,    -0.5, 0, 0.5,    1, 2, 3, 5, 10]
    wmo_levels = [-5,  -3, -2, -1, -0.5, -0.25, 0, 0.25, 0.5, 1, 2, 3, 5]

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
    cbar.set_label('Temperature difference from 1981-2010 average ($\degree$C)', rotation=0, fontsize=15)

    p.axes.coastlines()
    p.axes.set_global()

    plt.title(f'{title}', pad=20, fontdict={'fontsize': 20})
    plt.savefig(f'{image_filename}.png')
    plt.savefig(f'{image_filename}.pdf')
    plt.close()
