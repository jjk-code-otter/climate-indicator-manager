#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2026 John Kennedy
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
import matplotlib.pyplot as plt
from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

import climind.data_types.timeseries as ts
from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts


def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:

    df = pd.read_excel(
        filename[0],
        sheet_name="Global Carbon Budget",
        header=21
    )

    unc = None

    if metadata['name'] == "gcb_land_sink":
        data = df["land sink"].values
        unc = data * 0.0 + 0.5 * 1.645
    elif metadata['name'] == "gcb_ocean_sink":
        data = df["ocean sink"].values
        unc = data * 0.0 + 0.4 * 1.645
    elif metadata['name'] == "gcb_atmosphere":
        data = df["atmospheric growth"].values
    elif metadata['name'] == "gcb_cement_sink":
        data = df["cement carbonation sink"].values
    elif metadata['name'] == "gcb_land_use":
        data = df["land-use change emissions"].values
        unc = data * 0.0 + 0.7 * 1.645
    elif metadata['name'] == "gcb_fossil":
        data = df["fossil emissions excluding carbonation"].values
        unc = data * 0.05 * 1.645
    else:
        raise ValueError(f"Unknown dataset name {metadata['name']}")

    years = df.Year

    metadata.creation_message()

    if unc is not None:
        return ts.TimeSeriesAnnual(years, data, metadata=metadata, uncertainty=unc)
    else:
        return ts.TimeSeriesAnnual(years, data, metadata=metadata)