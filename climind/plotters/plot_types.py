from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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

    plt.xlabel('Year')
    plt.ylabel('$\!^\circ\!$C', rotation=0, labelpad=10)

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

    plt.text(plt.gca().get_xlim()[0], yloc, 'Compared to 1850-1900 average', fontdict={'fontsize': 30})
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

    plt.xlabel('Year')
    plt.ylabel('$\!^\circ\!$C', rotation=0, labelpad=10)

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

    plt.text(plt.gca().get_xlim()[0], yloc, 'Compared to 1850-1900 average', fontdict={'fontsize': 30})
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

    plt.xlabel('Year')
    plt.ylabel('$\!^\circ\!$C', rotation=0, labelpad=10)

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

    plt.text(plt.gca().get_xlim()[0], yloc, 'Compared to 1850-1900 average', fontdict={'fontsize': 30})
    plt.gca().set_title(title, pad=35, fontdict={'fontsize': 40}, loc='left')

    plt.savefig(out_dir / image_filename)
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.close()
    return


def decade_plot(out_dir: Path, all_datasets: list, image_filename: str, title: str, climtitle: str):
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

    plt.xlabel('Year')
    plt.ylabel('$\!^\circ\!$C', rotation=0, labelpad=10)

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

    plt.text(plt.gca().get_xlim()[0], yloc, climtitle, fontdict={'fontsize': 30})
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

    plt.xlabel('Year')
    plt.ylabel('$\!^\circ\!$C', rotation=0, labelpad=10)

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

    plt.text(plt.gca().get_xlim()[0], yloc, 'Compared to 1850-1900 average', fontdict={'fontsize': 30})
    plt.gca().set_title(title, pad=45, fontdict={'fontsize': 40}, loc='left')

    plt.savefig(out_dir / image_filename)
    plt.savefig(out_dir / image_filename.replace('png', 'pdf'))
    plt.close()
    return

