from pathlib import Path
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
            raise NotImplementedError
        else:
            raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')
    elif metadata['type'] == 'gridded':
        raise NotImplementedError


def read_monthly_ts(filename: str, metadata: CombinedMetadata):
    years = []
    anomalies = []

    with open(filename, 'r') as f:
        f.readline()

        for line in f:
            columns = line.split()

            # This is "decimal year" which we convert in a rough and ready way
            decimal_year = float(columns[0])
            year_int = int(decimal_year)
            diny = 1 + int(365. * (decimal_year - year_int))

            years.append(f'{year_int} {diny:03d}')
            anomalies.append(float(columns[1]))

    dates = pd.to_datetime(years, format='%Y %j')
    years = dates.year.tolist()
    months = dates.month.tolist()

    dico = {'year': years, 'month': months, 'data': anomalies}

    df = pd.DataFrame(dico)
    mdf1 = df.groupby(['year', 'month'])['year'].mean()
    mdf2 = df.groupby(['year', 'month'])['data'].mean()
    mdf3 = df.groupby(['year', 'month'])['month'].mean()

    years = mdf1.values.tolist()
    months = mdf3.values.tolist()
    anomalies = mdf2.values.tolist()

    metadata['history'] = [f'Time series created from file {filename}']

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)