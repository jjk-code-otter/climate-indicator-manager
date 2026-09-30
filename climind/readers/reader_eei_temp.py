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
import itertools
import xarray as xa
import numpy as np
from typing import List

import climind.data_types.grid as gd
import climind.data_types.timeseries as ts

from climind.data_manager.metadata import CombinedMetadata

from climind.readers.generic_reader import read_ts

def read_annual_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:

    conversion = 1.0

    df = xa.open_dataset(filename[0])

    if metadata['name'] == 'Miniere EEI':
        mask = ~np.isnan(df['Minere_et_al_2023'].values)
        years = df.time.dt.year.data[mask].tolist()
        data = (df['Minere_et_al_2023'] * conversion).values[mask].tolist()
        years = [x+14 for x in years]
        uncertainty = (df['Minere_et_al_2023_Uncertainty'] * conversion).data[mask].tolist()
        out_ts = ts.TimeSeriesAnnual(years, data, metadata=metadata, uncertainty=uncertainty)
    elif metadata['name'] == 'Copernicus EEI':
        mask = ~np.isnan(df['von_schuckmann_et_al_2023'].values)
        years = df.time.dt.year.data[mask].tolist()
        data = (df['von_schuckmann_et_al_2023'] * conversion).values[mask].tolist()
        years = [x+14 for x in years]
        uncertainty = (df['von_schuckmann_et_al_2023_Uncertainty'] * conversion).data[mask].tolist()
        out_ts = ts.TimeSeriesAnnual(years, data, metadata=metadata, uncertainty=uncertainty)
    elif metadata['name'] == 'CERES EEI':
        mask = ~np.isnan(df['toa_net_flux'].values)
        years = df.time.dt.year.data[mask].tolist()
        data = (df['toa_net_flux'] * conversion).values[mask].tolist()
        years = [x+14 for x in years]
        uncertainty = (df['toa_net_flux_Uncertainty'] * conversion).data[mask].tolist()
        out_ts = ts.TimeSeriesAnnual(years, data, metadata=metadata, uncertainty=uncertainty)

    return out_ts
