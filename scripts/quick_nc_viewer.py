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

from pathlib import Path
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.util import add_cyclic_point
import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt
from datetime import date
from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

if __name__ == '__main__':

    project_dir = DATA_DIR / "ManagedData"
    ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    METADATA_DIR = (ROOT_DIR / "..").resolve() / "climind" / "metadata_files"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    figure_dir = project_dir / 'Figures'
    log_dir = project_dir / 'Logs'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

    archive = dm.DataArchive.from_directory(metadata_dir)

    selection_metadata = {
        'variable': 'tas',
        'type': 'gridded',
        'time_resolution': 'monthly',
        'name': 'Kadow'
    }

    archive = archive.select(selection_metadata)

    datasets = archive.read_datasets(data_dir)

    dataset = datasets[0].df

    for year in range(1850,2025):

        dataset_selected = dataset.sel(time=slice(f'{year}-01', f'{year}-12'))

        fig, axs = plt.subplots(3, 4, subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0)},
                                figsize=(20, 9))
        proj = ccrs.PlateCarree()

        axs = axs.flatten()

        for i in range(12):
            data = dataset_selected.tas_mean[i][:, :]
            data, lons = add_cyclic_point(data, coord=dataset_selected['lon'])

            cs = axs[i].pcolormesh(
                lons, dataset_selected['lat'], data,
                transform=ccrs.PlateCarree(), vmin=-4, vmax=4, cmap='RdBu_r'
            )
            axs[i].coastlines()

        plt.title(f"{year}")
        plt.show()
        plt.close('all')
