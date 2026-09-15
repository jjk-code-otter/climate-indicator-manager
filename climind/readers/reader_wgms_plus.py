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
from typing import List
import pandas as pd

import climind.data_types.timeseries as ts
from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata, **kwargs) -> ts.TimeSeriesAnnual:
    value_column = "gt_cumsum"
    unc_column = "gt_cumsum_sigma"

    if 'sea_level_equivalent' in kwargs and kwargs['sea_level_equivalent'] is True:
        value_column = "mmsle_cumsum"
        unc_column = "mmsle_cumsum_sigma"
        metadata['units'] = 'mm'

    df = pd.read_csv(filename[0])

    years = df["year"].tolist()
    data = df[value_column].tolist()
    uncertainty = df[unc_column].tolist()
    uncertainty = [x*1.96 for x in uncertainty] # expand to 95% to match WGMS graph

    metadata.creation_message()

    return ts.TimeSeriesAnnual(years, data, uncertainty=uncertainty, metadata=metadata)
