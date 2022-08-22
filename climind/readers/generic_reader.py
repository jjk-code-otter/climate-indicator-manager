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
import copy
from climind.data_manager.metadata import CombinedMetadata


def get_reader_script_name(metadata, **kwargs):
    chosen_reader_script = None

    if metadata['type'] == 'timeseries':

        if metadata['time_resolution'] == 'monthly':
            chosen_reader_script = 'read_monthly_ts'
        elif metadata['time_resolution'] == 'annual':
            chosen_reader_script = 'read_annual_ts'

    elif metadata['type'] == 'gridded':

        chosen_reader_script = 'read_monthly_grid'

        if 'grid_resolution' in kwargs:
            if kwargs['grid_resolution'] == 5:
                chosen_reader_script = 'read_monthly_5x5_grid'
            if kwargs['grid_resolution'] == 1:
                chosen_reader_script = 'read_monthly_1x1_grid'

    return chosen_reader_script


def read_ts(out_dir: Path, metadata: CombinedMetadata, **kwargs):
    script_name = metadata['reader']
    ext = '.'.join(['climind.readers', script_name])
    module = __import__(ext, fromlist=[None])

    filename = out_dir / metadata['filename'][0]
    construction_metadata = copy.deepcopy(metadata)

    chosen_reader_script = get_reader_script_name(metadata, **kwargs)

    if chosen_reader_script is None:
        raise RuntimeError("Reader does not exist for this combination of metadata")

    if hasattr(module, chosen_reader_script):
        return getattr(module, chosen_reader_script)(filename, construction_metadata)
    else:
        raise NotImplementedError(f"Reader {chosen_reader_script} not implemented for this data set {metadata['name']}")
