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

from pathlib import Path
import os
import climind.data_manager.processing as dm
from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

if __name__ == "__main__":
    project_dir = DATA_DIR / "ManagedData"
    data_dir = project_dir / "Data"

    ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    METADATA_DIR = (ROOT_DIR / "..").resolve() / "climind" / "metadata_files"

    archive = dm.DataArchive.from_directory(METADATA_DIR)

    # Global mean temperature
    ts_archive = archive.select(
        #{'type': 'timeseries', 'name': ['HadCRUT5', 'Berkeley Earth Hires', 'ERA5']}
        {'type': 'timeseries', 'name': ['HadCRUT5', 'NOAA v6', 'Berkeley Earth Hires', 'ERA5']}
    )
    ts_archive.download(data_dir)

    # LSAT
    ts_archive = archive.select(
        #{'type': 'timeseries', 'name': ['Berkeley Earth LSAT', 'CRUTEM5']}
        {'type': 'timeseries', 'name': ['Berkeley Earth LSAT', 'CRUTEM5', 'NOAA LSAT v6', 'Berkeley Earth Hires LSAT']}
    )
    ts_archive.download(data_dir)

    # SST
    ts_archive = archive.select(
        #{'type': 'timeseries', 'name': ['HadSST4']}
        {'type': 'timeseries', 'name': ['HadSST4', 'ERSST v6']}
    )
    ts_archive.download(data_dir)

    # Sea level
    ts_archive = archive.select(
        {'type': 'timeseries', 'name': ['AVISO ftp']}
    )
    ts_archive.download(data_dir)

    # Ocean heat 700 and 2000m
    ts_archive = archive.select(
        {'type': 'timeseries', 'name': ['Cheng et al v4', 'Cheng et al 2k v4', 'Ishii', 'Ishii2k', 'Levitus',
                                          'Levitus2k']}
    )
    ts_archive.download(data_dir)

    # Arctic sea ice extent
    ts_archive = archive.select(
        #{'type': 'timeseries', 'time_resolution': 'monthly', 'name': ['NSIDC v4', 'OSI SAF v2p2', 'OSI SAF v2p3']}
        {'type': 'timeseries', 'time_resolution': 'monthly', 'name': ['NSIDC v4', 'OSI SAF v2p3']}
    )
    ts_archive.download(data_dir)

    # Antarctic sea ice extent
    ts_archive = archive.select(
        #{'type': 'timeseries', 'time_resolution': 'monthly', 'name': ['NSIDC v4 SH', 'OSI SAF SH v2p2', 'OSI SAF SH v2p3']}
        {'type': 'timeseries', 'time_resolution': 'monthly', 'name': ['NSIDC v4 SH', 'OSI SAF SH v2p3']}
    )
    ts_archive.download(data_dir)

    # Glaciers
    ts_archive = archive.select(
        {'type': 'timeseries', 'name': ['WGMS']}
    )
    ts_archive.download(data_dir)

    # Greenland ice sheet
    ts_archive = archive.select(
        {'type': 'timeseries', 'name': ['PROMICE2','GRACE Greenland']}
    )
    ts_archive.download(data_dir)

    # Indices
    ts_archive = archive.select(
        {'type': 'timeseries', 'variable': ['aao', 'ao', 'nao', 'pdo', 'oni', 'iod', 'nino34', 'soi', 'roni']}
    )
    ts_archive.download(data_dir)

    # Snow
    ts_archive = archive.select(
        {'type': 'timeseries', 'name': ['Rutgers NH','Rutgers NAM']}
    )
    ts_archive.download(data_dir)

    # TLT
    ts_archive = archive.select(
        {'type': 'timeseries', 'name': ['UAH', 'RSS']}
    )
    ts_archive.download(data_dir)

    # CO2
    ts_archive = archive.select(
        {'type': 'timeseries', 'name': ['Mauna Loa','Kennaook Cape Grim CO2']}
    )
    ts_archive.download(data_dir)

    # CH4
    ts_archive = archive.select(
        {'type': 'timeseries', 'name': ['NOAA CH4','Kennaook Cape Grim CH4']}
    )
    ts_archive.download(data_dir)

    # N2O
    ts_archive = archive.select(
        {'type': 'timeseries', 'name': ['Kennaook Cape Grim N2O']}
    )
    ts_archive.download(data_dir)

    # Marine heatwaves
    ts_archive = archive.select(
        {'type': 'timeseries', 'name': ['MHW','MCS']}
    )
    ts_archive.download(data_dir)

