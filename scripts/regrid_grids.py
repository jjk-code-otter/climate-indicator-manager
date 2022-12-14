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
from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR
import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt

if __name__ == "__main__":
    project_dir = DATA_DIR / "ManagedData"
    data_dir = project_dir / "Data"

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

    all_annual = []
    for ds in all_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()

        new_name = f"{ds.metadata['name']}_5x5"

        data_output_dir = data_dir / new_name
        data_output_dir.mkdir(exist_ok=True)

        grid_filename = data_output_dir / f"{new_name}.nc"
        metadata_filename = METADATA_DIR / f"{new_name}.json"

        annual.write_grid(grid_filename,
                          metadata_filename=metadata_filename,
                          name=new_name)

        annual = annual.select_year_range(2021, 2021)
        all_annual.append(annual)

    cap = pt.dashboard_map(project_dir / 'Figures', all_annual, 'test.png', title='Spam')
