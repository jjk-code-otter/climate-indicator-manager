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

from pathlib import Path
from typing import Tuple, List
import itertools
import pandas as pd
import xarray as xa
import numpy as np

import climind.data_types.grid as gd
import climind.data_types.timeseries as ts

import json
import copy

from climind.readers.generic_reader import get_last_modified_time
from climind.data_manager.metadata import CombinedMetadata
from climind.readers.generic_reader import read_ts

def read_irregular_ts(filenames: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:

    extents = []


    with open(filenames[0]) as f:
        input_data = json.load(f)

    climatology = np.array(input_data[-3]['data'])

    for entry in input_data:

        if entry['name'] not in ["1979-2000 mean", "plus 2σ", "minus 2σ"]:

            data = entry['data']
            while data[-1] is None:
                del data[-1]
            n = len(data)

            data = np.array(data) - climatology[0:n]

            extents.extend(data)

    n_days = len(extents)
    times = pd.date_range(start=f'1979-01-01', freq='1D', periods=n_days)

    years = times.year
    months = times.month
    days = times.day

    metadata.creation_message()

    return ts.TimeSeriesIrregular(years, months, days, extents, metadata=metadata)