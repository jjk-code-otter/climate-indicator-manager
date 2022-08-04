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
            return read_annual_ts(filename, construction_metadata)
        else:
            raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')
    elif metadata['type'] == 'gridded':
        raise NotImplementedError


def read_monthly_ts(filename: Path, metadata: CombinedMetadata):
    dates = []
    mass_balance = []

    with open(filename, 'r') as in_file:
        in_file.readline()
        for line in in_file:
            if int(line[0:4]) > 1985:
                columns = line.split(',')
                dates.append(columns[0])
                mass_balance.append(float(columns[1]))

    parsed_dates = pd.to_datetime(dates, format='%Y-%m-%d')
    years = parsed_dates.year.tolist()
    months = parsed_dates.month.tolist()

    dico = {'year': years, 'month': months, 'data': mass_balance}

    df = pd.DataFrame(dico)
    mdf_year = df.groupby(['year', 'month'])['year'].mean()
    mdf_month = df.groupby(['year', 'month'])['month'].mean()
    mdf_data = df.groupby(['year', 'month'])['data'].sum()

    years = mdf_year.values.tolist()
    months = mdf_month.values.tolist()
    mass_balance = mdf_data.values.tolist()

    metadata['history'] = [f'Time series created from file {filename}']

    return ts.TimeSeriesMonthly(years, months, mass_balance, metadata=metadata)


def read_annual_ts(filename: Path, metadata: CombinedMetadata):
    years = []
    mass_balance = []

    with open(filename, 'r') as in_file:
        in_file.readline()
        for line in in_file:
            columns = line.split(',')
            years.append(int(columns[0]))
            mass_balance.append(float(columns[1]))

    metadata['history'] = [f'Time series created from file {filename}']
    return ts.TimeSeriesAnnual(years, mass_balance, metadata=metadata)
