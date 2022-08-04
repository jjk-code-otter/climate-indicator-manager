from pathlib import Path

import numpy as np
import pandas as pd
import climind.data_types.timeseries as ts
import copy

from climind.data_manager.metadata import CombinedMetadata


def read_ts(out_dir: Path, metadata: CombinedMetadata, **kwargs):
    filename = out_dir / metadata['filename'][0]

    construction_metadata = copy.deepcopy(metadata)

    if metadata['type'] == 'timeseries':
        if metadata['time_resolution'] == 'monthly':
            return read_monthly_ts(filename, construction_metadata)
        elif metadata['time_resolution'] == 'annual':
            return read_annual_ts(filename, construction_metadata)
        else:
            raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')
    elif metadata['type'] == 'gridded':
        raise NotImplementedError


def read_monthly_ts(filename: Path, metadata: CombinedMetadata):

    years = []
    months = []
    data = []

    with open(filename, 'r') as in_file:
        for i in range(31):
            in_file.readline()

        for line in in_file:
            columns = line.split()
            decimal_year = float(columns[0])
            year_int = int(decimal_year)
            month = int(np.rint(12. * (decimal_year - year_int) + 1.0))

            years.append(year_int)
            months.append(month)
            data.append(float(columns[1]))

    dico = {'year': years, 'month': months, 'data': data}
    df = pd.DataFrame(dico)
    df['data'] = df.diff()['data']

    data = df['data'].values.tolist()

    metadata['history'] = [f'Time series created from file {filename}']

    return ts.TimeSeriesMonthly(years, months, data, metadata=metadata)


def read_annual_ts(filename: Path, metadata: CombinedMetadata):
    monthly = read_monthly_ts(filename, metadata)
    annual = monthly.make_annual(cumulative=True)
    return annual
