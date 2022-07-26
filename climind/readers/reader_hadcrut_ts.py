from pathlib import Path
import xarray as xa
import climind.data_types.timeseries as ts
import climind.data_types.grid as gd
import numpy as np
import copy
import itertools


def read_ts(out_dir: Path, metadata: dict, **kwargs):
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
                return read_monthly_grid(filename, construction_metadata)
            if kwargs['grid_resolution'] == 1:
                return read_monthly_1x1_grid(filename, construction_metadata)
        else:
            return read_monthly_grid(filename, construction_metadata)


def read_monthly_grid(filename: str, metadata):
    df = xa.open_dataset(filename)
    return gd.GridMonthly(df, metadata)


def read_monthly_1x1_grid(filename: str, metadata):
    df = xa.open_dataset(filename)
    # regrid to 1x1
    ntime = df.tas_mean.shape[0]

    grid = np.zeros((ntime, 180, 360))
    lats = np.arange(-89.5, 90.5, 1.0)
    lons = np.arange(-179.5, 180.5, 1.0)

    # Copy 5-degree grid cell value into all one degree cells
    grid = np.repeat(df.tas_mean, 5, 1)
    grid = np.repeat(grid, 5, 2)

    df = gd.make_xarray(grid, df.time.data, lats, lons)

    return gd.GridMonthly(df, metadata)


def read_monthly_ts(filename: str, metadata: dict):
    years = []
    months = []
    anomalies = []

    with open(filename, 'r') as f:
        f.readline()
        for line in f:
            columns = line.split(',')
            year = columns[0][0:4]
            month = columns[0][5:7]

            years.append(int(year))
            months.append(int(month))
            if columns[1] != '':
                anomalies.append(float(columns[1]))
            else:
                anomalies.append(np.nan)

    metadata['history'] = [f'Time series created from file {filename}']

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: str, metadata: dict):
    monthly = read_monthly_ts(filename, metadata)
    annual = monthly.make_annual()

    return annual
