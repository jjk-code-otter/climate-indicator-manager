from pathlib import Path
import xarray as xa
import climind.data_types.timeseries as ts
import climind.data_types.grid as gd
import numpy as np
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
        print(kwargs)
        if 'grid_resolution' in kwargs:
            if kwargs['grid_resolution'] == 5:
                raise NotImplementedError
            if kwargs['grid_resolution'] == 1:
                raise NotImplementedError
        else:
            raise NotImplementedError

def read_monthly_ts(filename: str, metadata: CombinedMetadata):
    years = []
    months = []
    anomalies = []

    with open(filename, 'r') as f:
        f.readline()
        for line in f:
            columns = line.split(',')
            year = columns[0][0:4]
            month = columns[0][5:]

            years.append(int(year))
            months.append(int(month))
            if columns[1] != '':
                anomalies.append(float(columns[1]))
            else:
                anomalies.append(np.nan)

    metadata['history'] = [f'Time series created from file {filename}']

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: str, metadata: CombinedMetadata):
    years = []
    anomalies = []

    with open(filename, 'r') as f:
        f.readline()
        for line in f:
            columns = line.split()
            year = columns[0][0:4]
            years.append(int(year))
            if columns[1] != '':
                anomalies.append(float(columns[1]))
            else:
                anomalies.append(np.nan)

    metadata['history'] = [f'Time series created from file {filename}']

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata)
