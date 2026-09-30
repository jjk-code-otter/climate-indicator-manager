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
import xarray as xa
import numpy as np
from scipy.signal import savgol_filter

import climind.data_types.timeseries as ts

from climind.data_manager.metadata import CombinedMetadata
from climind.readers.generic_reader import read_ts



def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    df = xa.open_dataset(filename[0])

    mname = metadata['name']
    name_to_var = {
        "Chan Nino34" : ['DCENTI_SST', 'DCENTI_SST_en'],
        "Chan ESA Nino34" : ['ESACCI', None],
        "Chan ERSST6 Nino34" : ['ERSST6', None],
        "Chan HadSST4 Nino34" : ['HadSST4', 'HadSST4_en'],
        "Chan HadSST42 Nino34" : ['HadSST42', 'HadSST42_en'],
        "Chan COBESST3 Nino34" : ['COBESST3', 'COBESST3_en'],
        "Chan ERSST5 Nino34" : ['ERSST5', 'ERSST5_en'],
    }

    years = df.year.data

    nyears = len(years)
    years = np.repeat(years, 12).tolist()
    years = [int(x) for x in years]
    months = np.tile(np.arange(1, 13), nyears).tolist()
    months = [int(x) for x in months]
    data = np.ravel(df[name_to_var[mname][0]].values).tolist()

    if name_to_var[mname][1] is not None:
        ensemble = 1.96 * df[name_to_var[mname][1]].values
        spread = np.std(ensemble, axis=0)
        uncertainty = np.ravel(spread).tolist()

        #metadata.creation_message()
        out_ts = ts.TimeSeriesMonthly(years, months, data, uncertainty=uncertainty, metadata=metadata)
    else:
        out_ts = ts.TimeSeriesMonthly(years, months, data, metadata=metadata)

    return out_ts

