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
import xarray
from pathlib import Path
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from climind.config.config import DATA_DIR, CLIMATOLOGY
from climind.definitions import METADATA_DIR
import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt


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

    Returns
    -------
    None
    """
    # This is a pain, but we need to do some magic to convince cartopy that the data
    # are continuous across the dateline
    data = dataset[var]
    lon = dataset.coords['longitude']
    lon_idx = data.dims.index('longitude')
    wrap_data, wrap_lon = pt.add_cyclic_point(data.values, coord=lon, axis=lon_idx)

    plt.figure(figsize=(16, 9))
    proj = ccrs.EqualEarth(central_longitude=0)

    wmo_cols = ['#2a0ad9', '#264dff', '#3fa0ff', '#72daff', '#aaf7ff', '#e0ffff',
                '#ffffbf', '#fee098', '#ffad73', '#f76e5e', '#d82632', '#a50022']

    wmo_levels = [-3, -2, -1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1, 2, 3]

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
    cbar.set_label(r'Temperature difference ($\degree$C)', rotation=0, fontsize=15)

    p.axes.coastlines()
    p.axes.set_global()

    plt.title(f'{title}', pad=20, fontdict={'fontsize': 20})
    plt.savefig(f'{image_filename}.png')
    plt.savefig(f'{image_filename}.pdf')
    plt.close()


def plot_climatology_differences(all_datasets, p1, p2):
    processed_datasets = []

    for ds in all_datasets:
        annual = ds.make_annual()
        annual = annual.running_average(30)

        # calculate the time period diffs
        selection_1981 = annual.get_year_range(p1, p1)
        selection_1991 = annual.get_year_range(p2, p2)
        selection_1991.df.year.data[0] = selection_1981.df.year.data[0]
        diff = selection_1991.df - selection_1981.df

        annual.df = diff
        processed_datasets.append(annual)

        nice_map(diff,
                 project_dir / "Figures" / f"clim_difference_{p2}_{p1}_{ds.metadata['name']}.png",
                 f"Difference for {p2 - 29}-{p2} minus {p1 - 29}-{p1} for {ds.metadata['name']}")

    pt.dashboard_map(project_dir / "Figures", processed_datasets, f"clim_summary.png", "Median difference")
    pt.dashboard_uncertainty_map(project_dir / "Figures", processed_datasets, f"clim_uncertainty.png", "Range")


if __name__ == "__main__":
    project_dir = DATA_DIR / "ManagedData"
    data_dir = project_dir / "Data"
    ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    METADATA_DIR = (ROOT_DIR / "..").resolve() / "climind" / "metadata_files"

    archive = dm.DataArchive.from_directory(METADATA_DIR)

    ts_archive = archive.select(
        {
            'variable': 'tas',
            'type': 'gridded',
            'time_resolution': 'monthly',
            'name': ['HadCRUT5', 'GISTEMP', 'NOAAGlobalTemp', 'Berkeley Earth', 'ERA5', 'JRA-55']
        }
    )

    all_datasets = ts_archive.read_datasets(data_dir, grid_resolution=5)

    #    plot_climatology_differences(all_datasets, 1990, 2020)
    plot_climatology_differences(all_datasets, 2010, 2020)
