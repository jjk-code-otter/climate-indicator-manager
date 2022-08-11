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

    df = pd.read_excel(filename)
    df = df.rename(columns={'Cumulative ice mass change (Gt)': 'data'})

    # Clip out missing data, which constitute quite a lof the of series
    df = df[~np.isnan(df['data'])]

    df['data'] = df.diff()['data']

    decimal_year = df['Year'].values
    year_int = decimal_year.astype(int)
    months = np.rint(12. * (decimal_year - year_int) + 1.0).astype(int)

    years = year_int.tolist()
    months = months.tolist()

    if not first_diff:
        df['data'] = df.cumsum()['data']

    mass_balance = df['data'].tolist()

    metadata['history'] = [f"Time series created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]

    return ts.TimeSeriesMonthly(years, months, mass_balance, metadata=metadata)


def read_annual_ts(filename: Path, metadata: CombinedMetadata, **kwargs):
    monthly = read_monthly_ts(filename, metadata, **kwargs)
    annual = monthly.make_annual(cumulative=True)
    return annual
