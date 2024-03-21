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
import climind.data_types.timeseries as ts
from climind.readers.generic_reader import get_last_modified_time
import copy

from climind.data_manager.metadata import CombinedMetadata


def read_ts(out_dir: Path, metadata: CombinedMetadata, **kwargs):
    filenames = []
    for filename in out_dir.glob(metadata['filename'][0]):
        filenames.append(filename)
    filenames.sort()
    filename = filenames[-1]

    construction_metadata = copy.deepcopy(metadata)
    construction_metadata.dataset['last_modified'] = [get_last_modified_time(filename)]

    if metadata['type'] == 'timeseries':
        if metadata['time_resolution'] == 'monthly':
            raise NotImplementedError
        elif metadata['time_resolution'] == 'annual':
            return read_annual_ts(filename, construction_metadata)
        else:
            raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')
    elif metadata['type'] == 'gridded':
        raise NotImplementedError


def read_annual_ts(filename: Path, metadata: CombinedMetadata) -> ts.TimeSeriesAnnual:
    df = xa.open_dataset(filename)

#    conversion = 1.0/1e9
    conversion = 361e6 * 0.864 * 1e6 / 1e21

    # Double uncertainties to get 95% range
    if metadata['variable'] == 'ohc':
        raise Exception
    elif metadata['variable'] == 'ohc2k':
        if metadata['name'] == 'Miniere':
            mask = ~np.isnan(df['ohc_Miniere_et_al_2023'].values)
            years = df.time_2023.dt.year.data[mask].tolist()
            data = (df['ohc_Miniere_et_al_2023'] * conversion).values[mask].tolist()
            uncertainty = (df['ohc_uncertainty_Miniere_et_al_2023'] * conversion).data[mask].tolist()
        elif metadata['name'] == 'Cheng TEMP':
            mask = ~np.isnan(df['ohc_IAP_Cheng_et_al_2017'].values)
            years = df.time_2023.dt.year.data[mask].tolist()
            data = (df['ohc_IAP_Cheng_et_al_2017'] * conversion).values[mask].tolist()
            uncertainty = (df['ohc_uncertainty_IAP_Cheng_et_al_2017'] * conversion).data[mask].tolist()
        elif metadata['name'] == 'JMA TEMP':
            mask = ~np.isnan(df['ohc_JMA_Ishii_et_al_2017'].values)
            years = df.time_2023.dt.year.data[mask].tolist()
            data = (df['ohc_JMA_Ishii_et_al_2017'] * conversion).values[mask].tolist()
            uncertainty = (df['ohc_uncertainty_JMA_Ishii_et_al_2017'] * conversion).data[mask].tolist()
        elif metadata['name'] == 'GCOS2k TEMP':
            mask = ~np.isnan(df['ohc_von_Schuckmann_et_al_2023'].values)
            years = df.time_2020.dt.year.data[mask].tolist()
            data = (df['ohc_von_Schuckmann_et_al_2023'] * conversion).values[mask].tolist()
            uncertainty = (df['ohc_uncertainty_von_Schuckmann_et_al_2023'] * conversion).data[mask].tolist()
    else:
        raise ValueError(f"Variable {metadata['variable']} unrecognised")

    metadata.creation_message()

    return ts.TimeSeriesAnnual(years, data, metadata=metadata, uncertainty=uncertainty)
