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
import xarray as xa
import numpy as np
from typing import Tuple

import climind.data_types.grid as gd
import climind.data_types.timeseries as ts
from climind.readers.generic_reader import get_last_modified_time
from climind.data_manager.metadata import CombinedMetadata
import copy


def find_latest(out_dir: Path, filename_with_wildcards: str) -> Path:
    """
    Find the most recent file that matches

    Parameters
    ----------
    filename_with_wildcards : str
        Filename including wildcards
    out_dir : Path
        Path of data directory

    Returns
    -------
    Path
        Path of latest file that matches the filename with wildcards in the directory
    """
    # look in directory to find all matching
    list_of_files = list(out_dir.glob(filename_with_wildcards))
    list_of_files.sort()
    out_filename = list_of_files[-1]
    return out_filename


def get_latest_filename_and_url(filename: Path, url: str) -> Tuple[str, str]:
    """
    Get the filename and url from a filled filename Path and URL with placeholders

    Parameters
    ----------
    filename: Path
        Path of filename
    url: str
        URL to be replaced

    Returns
    -------
    Tuple[str, str]
        The filename and the url with placeholders replaced
    """
    selected_file = filename.name
    selected_url = url.split('/')
    selected_url = selected_url[0:-1]
    selected_url.append(selected_file)
    selected_url = '/'.join(selected_url)

    return selected_file, selected_url


def read_ts(out_dir: Path, metadata: CombinedMetadata, **kwargs):
    filename_with_wildcards = metadata['filename'][0]
    filename = find_latest(out_dir, filename_with_wildcards)

    last_modified = get_last_modified_time(filename)

    construction_metadata = copy.deepcopy(metadata)
    construction_metadata.dataset['last_modified'] = [last_modified]

    if metadata['type'] == 'timeseries':
        if metadata['time_resolution'] == 'monthly':
            return read_monthly_ts(filename, construction_metadata)
        elif metadata['time_resolution'] == 'annual':
            return read_annual_ts(filename, construction_metadata)
        else:
            raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')
    elif metadata['type'] == 'gridded':
        if 'grid_resolution' in kwargs:
            if kwargs['grid_resolution'] == 1:
                return read_monthly_1x1_grid(filename, construction_metadata)
            if kwargs['grid_resolution'] == 5:
                return read_monthly_grid(filename, construction_metadata)
        else:
            return read_monthly_grid(filename, construction_metadata)


def read_monthly_grid(filename: Path, metadata: CombinedMetadata) -> gd.GridMonthly:
    df = xa.open_dataset(filename)

    number_of_months = len(df.time.data)
    target_grid = np.zeros((number_of_months, 36, 72))

    for m in range(number_of_months):
        target_grid[m, :, :] = df.anom.data[m, 0, :, :]

    # shift longitudes to match HadCRUT convention of -180 to 180
    target_grid = np.roll(target_grid, 36, 2)

    latitudes = np.linspace(-87.5, 87.5, 36)
    longitudes = np.linspace(-177.5, 177.5, 72)
    times = df.time.data

    ds = gd.make_xarray(target_grid, times, latitudes, longitudes)

    # update encoding
    for key in ds.data_vars:
        ds[key].encoding.update({'zlib': True, '_FillValue': -1e30})

    metadata.creation_message()

    return gd.GridMonthly(ds, metadata)


def read_monthly_1x1_grid(filename: Path, metadata: CombinedMetadata) -> gd.GridMonthly:
    df = read_monthly_grid(filename, metadata)
    df = df.df
    # regrid to 1x1
    lats = np.arange(-89.5, 90.5, 1.0)
    lons = np.arange(-179.5, 180.5, 1.0)

    # Copy 5-degree grid cell value into all one degree cells
    grid = np.repeat(df.tas_mean, 5, 1)
    grid = np.repeat(grid, 5, 2)

    df = gd.make_xarray(grid, df.time.data, lats, lons)

    metadata.creation_message()
    metadata['history'].append("Regridded to 1 degree latitude-longitude resolution")

    return gd.GridMonthly(df, metadata)


def read_monthly_ts(filename: Path, metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    """
    Read in monthly file

    Parameters
    ----------
    filename : Path
        Path of monthly file
    metadata : dict
        Dictionary containing metadata
    Returns
    -------
    ts.TimeSeriesMonthly
    """
    years = []
    months = []
    anomalies = []
    uncertainties = []

    with open(filename, 'r') as f:
        for line in f:
            columns = line.split()
            years.append(int(columns[0]))
            months.append(int(columns[1]))
            anomalies.append(float(columns[2]))
            uncertainties.append(np.sqrt(float(columns[3])))

    selected_file, selected_url = get_latest_filename_and_url(filename, metadata['url'][0])

    metadata['filename'][0] = selected_file
    metadata['url'][0] = selected_url

    metadata.creation_message()

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata, uncertainty=uncertainties)


def read_annual_ts(filename: Path, metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    """
    Read in annual file

    Parameters
    ----------
    filename : Path
        Filename for annual file
    metadata : dict
        Dictionary containing metadata
    Returns
    -------
    ts.TimeSeriesAnnual
    """
    years = []
    anomalies = []
    uncertainties = []

    with open(filename, 'r') as f:
        for line in f:
            columns = line.split()
            years.append(int(columns[0]))
            anomalies.append(float(columns[1]))
            uncertainties.append(np.sqrt(float(columns[2])))

    selected_file, selected_url = get_latest_filename_and_url(filename, metadata['url'][0])

    metadata['filename'][0] = selected_file
    metadata['url'][0] = selected_url

    metadata.creation_message()

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata, uncertainty=uncertainties)
