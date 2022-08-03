from pathlib import Path
import xarray as xa
import numpy as np
import climind.data_types.grid as gd
import climind.data_types.timeseries as ts
import copy


def find_latest(out_dir: Path, filename_with_wildcards: str) -> str:
    """
    Find the most recent file that matches

    Parameters
    ----------
    filename_with_wildcards : str
        Filename including wildcards
    out_dir : Path
        Path of data directory

    Returns
    -------

    """
    # look in directory to find all matching
    list_of_files = list(out_dir.glob(filename_with_wildcards))
    list_of_files.sort()
    out_filename = list_of_files[-1]
    return out_filename


def read_ts(out_dir: Path, metadata: dict, **kwargs):
    filename_with_wildcards = metadata['filename'][0]
    filename = find_latest(out_dir, filename_with_wildcards)

    construction_metadata = copy.deepcopy(metadata)

    if metadata['type'] == 'timeseries':
        if metadata['time_resolution'] == 'monthly':
            return read_monthly_ts(filename, construction_metadata)
        elif metadata['time_resolution'] == 'annual':
            return read_annual_ts(filename, construction_metadata)
        else:
            raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')
    elif metadata['type'] == 'gridded':
        if 'grid_resolution' in kwargs:
            if kwargs['grid_resolution'] == 1:
                return read_monthly_1x1_grid(filename, construction_metadata)
            if kwargs['grid_resolution'] == 5:
                return read_monthly_grid(filename, construction_metadata)
        else:
            return read_monthly_grid(filename, construction_metadata)


def read_monthly_grid(filename: str, metadata):
    df = xa.open_dataset(filename)

    number_of_months = len(df.time.data)
    target_grid = np.zeros((number_of_months, 36, 72))

    for m in range(number_of_months):
        target_grid[m, :, :] = df.anom.data[m, 0, :, :]

    # shift longitudes to match HadCRUT convention of -180 to 180
    target_grid = np.roll(target_grid, 36, 2)

    latitudes = np.linspace(-87.5, 87.5, 36)
    longitudes = np.linspace(-177.5, 177.5, 72)
    times = df.time.data

    ds = gd.make_xarray(target_grid, times, latitudes, longitudes)

    # update encoding
    for key in ds.data_vars:
        ds[key].encoding.update({'zlib': True, '_FillValue': -1e30})

    return gd.GridMonthly(ds, metadata)


def read_monthly_1x1_grid(filename: str, metadata):
    df = read_monthly_grid(filename, metadata)
    df = df.df
    # regrid to 1x1
    lats = np.arange(-89.5, 90.5, 1.0)
    lons = np.arange(-179.5, 180.5, 1.0)

    # Copy 5-degree grid cell value into all one degree cells
    grid = np.repeat(df.tas_mean, 5, 1)
    grid = np.repeat(grid, 5, 2)

    df = gd.make_xarray(grid, df.time.data, lats, lons)

    return gd.GridMonthly(df, metadata)


def read_monthly_ts(filename: str, metadata: dict):
    """
    Read in monthly file

    Parameters
    ----------
    filename : str
        Filename for monthly file
    metadata : dict
        Dictionary containing metadata
    Returns
    -------
    ts.TimeSeriesMonthly
    """
    years = []
    months = []
    anomalies = []

    with open(filename, 'r') as f:
        for line in f:
            columns = line.split()
            years.append(int(columns[0]))
            months.append(int(columns[1]))
            anomalies.append(float(columns[2]))

    metadata['history'] = [f'Time series created from file {filename}']

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: str, metadata: dict):
    """
    Read in annual file

    Parameters
    ----------
    filename : str
        Filename for annual file
    metadata : dict
        Dictionary containing metadata
    Returns
    -------
    ts.TimeSeriesAnnual
    """
    years = []
    anomalies = []

    with open(filename, 'r') as f:
        for line in f:
            columns = line.split()
            years.append(int(columns[0]))
            anomalies.append(float(columns[1]))

    metadata['history'] = [f'Time series created from file {filename}']

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata)
