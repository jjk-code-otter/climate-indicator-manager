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
from datetime import datetime
from typing import Union, Optional
import copy
from climind.data_manager.metadata import CombinedMetadata
from climind.data_types.timeseries import TimeSeriesAnnual, TimeSeriesMonthly
from climind.data_types.grid import GridMonthly


def get_reader_script_name(metadata: Union[CombinedMetadata, dict], **kwargs) -> Optional[str]:
    """
    Get the name of the reader function for the provided metadata combination

    Parameters
    ----------
    metadata: Union[CombinedMetadata, dict]
        contains the metadata required to chose the reader script
    kwargs:

    Returns
    -------
    str
    """
    chosen_reader_script = None

    if metadata['type'] == 'timeseries':

        if metadata['time_resolution'] == 'monthly':
            chosen_reader_script = 'read_monthly_ts'
        elif metadata['time_resolution'] == 'annual':
            chosen_reader_script = 'read_annual_ts'

    elif metadata['type'] == 'gridded':

        if metadata['time_resolution'] == 'monthly':
            chosen_reader_script = 'read_monthly_grid'
        elif metadata['time_resolution'] == 'annual':
            chosen_reader_script = 'read_annual_grid'

        if 'grid_resolution' in kwargs:
            if kwargs['grid_resolution'] == 5:
                chosen_reader_script = 'read_monthly_5x5_grid'
            if kwargs['grid_resolution'] == 1:
                chosen_reader_script = 'read_monthly_1x1_grid'

    return chosen_reader_script


def get_module(package_name: str, script_name: str):
    """
    Get the module from the package name and the script name

    Parameters
    ----------
    package_name: str
        String containing the package path as a dot separated string
    script_name: str
        Name of the script to import

    Returns
    -------
    The imported module
    """
    ext = '.'.join([package_name, script_name])
    module = __import__(ext, fromlist=[None])
    return module


def get_last_modified_time(file: Path) -> Optional[str]:
    """
    Get update time of file if it exists, else None
    Parameters
    ----------
    file: Path
        File path

    Returns
    -------
    Optional[str]
        string containing last updated time for the file or None if it does not exist
    """
    last_updated = None
    if file.exists():
        last_updated = file.stat().st_mtime
        last_updated = datetime.fromtimestamp(last_updated).strftime("%Y-%m-%d %H:%M:%S")

    return last_updated


def read_ts(out_dir: Path, metadata: CombinedMetadata, **kwargs) -> Union[
    TimeSeriesMonthly, TimeSeriesAnnual, GridMonthly]:
    """
    Generic reader for the data sets. This works out which reader is needed, imports and runs it.
    If a particular reader is not available (e.g. because the data is only a timeseries and not a grid)
    then it raises a not implemented error.

    Parameters
    ----------
    out_dir: Path
        Path of the directory in which the data are to be found
    metadata: CombinedMetadata
        Metadata describing the required dataset
    kwargs: dict
        Optional arguments as required for particular data sets

    Returns
    -------

    """
    script_name = metadata['reader']
    module = get_module('climind.readers', script_name)

    filename = []
    last_modified_times = []
    for name in metadata['filename']:
        file = out_dir / name
        filename.append(file)
        last_modified_times.append(get_last_modified_time(file))

    construction_metadata = copy.deepcopy(metadata)
    construction_metadata.dataset['last_modified'] = last_modified_times

    chosen_reader_script = get_reader_script_name(metadata, **kwargs)

    if chosen_reader_script is None:
        raise RuntimeError("Reader does not exist for this combination of metadata")

    if hasattr(module, chosen_reader_script):
        return getattr(module, chosen_reader_script)(filename, construction_metadata, **kwargs)
    else:
        raise NotImplementedError(f"Reader {chosen_reader_script} not implemented for this data set {metadata['name']}")
