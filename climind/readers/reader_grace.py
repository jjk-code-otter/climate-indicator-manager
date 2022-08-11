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
            return read_monthly_ts(filename, construction_metadata, **kwargs)
        elif metadata['time_resolution'] == 'annual':
            return read_annual_ts(filename, construction_metadata, **kwargs)
        else:
            raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')
    elif metadata['type'] == 'gridded':
        raise NotImplementedError


def read_monthly_ts(filename: Path, metadata: CombinedMetadata, **kwargs):

    if 'first_difference' in kwargs:
        first_diff = kwargs['first_difference']
    else:
        first_diff = False

    dates = []
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
            diny = 1 + int(365. * (decimal_year - year_int))
            month = int(np.rint(12. * (decimal_year - year_int) + 1.0))

            dates.append(f'{year_int} {diny:03d}')

            years.append(year_int)
            months.append(month)
            data.append(float(columns[1]))

    dates = pd.to_datetime(dates, format='%Y %j')
    years2 = dates.year.tolist()
    months2 = dates.month.tolist()

    dico = {'year': years, 'month': months, 'data': data}
    df = pd.DataFrame(dico)

    if first_diff:
        df['data'] = df.diff()['data']
        data = df['data'].values.tolist()

    metadata['history'] = [f"Time series created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]

    return ts.TimeSeriesMonthly(years2, months2, data, metadata=metadata)


def read_annual_ts(filename: Path, metadata: CombinedMetadata, **kwargs):
    monthly = read_monthly_ts(filename, metadata, **kwargs)
    annual = monthly.make_annual(cumulative=True)
    return annual
