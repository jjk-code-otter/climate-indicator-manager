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

from typing import List
from pathlib import Path
import xarray as xa
import climind.data_types.grid as gd
from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts


def read_annual_grid(filename: List[Path], metadata: CombinedMetadata) -> gd.GridAnnual:
    df = xa.open_dataset(filename[0])
    metadata['history'].append(f"Gridded dataset created from file {metadata['filename']} "
                               f"downloaded from {metadata['url']}")
    return gd.GridAnnual(df, metadata)
