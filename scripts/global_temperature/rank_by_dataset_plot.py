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
import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt
import climind.stats.utils as utils

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

if __name__ == "__main__":
    final_year = 2025

    project_dir = DATA_DIR / "ManagedData"
    ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    METADATA_DIR = (ROOT_DIR / "..").resolve() / "climind" / "metadata_files"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    figure_dir = project_dir / 'Figures'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

    archive = dm.DataArchive.from_directory(metadata_dir)
    ts_archive = archive.select({
        'variable': 'tas',
        'type': 'timeseries',
        'time_resolution': 'monthly',
        #'name': ['HadCRUT5', 'GISTEMP', 'NOAA v6', 'ERA5', 'Berkeley Earth Hires', 'JRA-3Q']
        'name': [
            'tempNOAA', 'tempGISTEMP', 'tempERA5',
            'tempJRA3Q', 'tempBerkeley', 'tempHadCRUT5',
            'tempDCENT', 'tempCMST',
            'CMA_GMST',
            #            'COBE-STEMP3', 'Kadow', 'GloSAT', 'Calvert 2024'
        ],
    })

    all_datasets = ts_archive.read_datasets(data_dir)

    for ds in all_datasets:
        ds.select_year_range(1970, 2025)

    pt.rank_by_dataset(figure_dir, all_datasets, 'rank_by_dataset.png', '', overlay=True)
    pt.rank_by_dataset(figure_dir, all_datasets, 'rank_by_dataset_long.png', '', overlay=False, n_months=252)
