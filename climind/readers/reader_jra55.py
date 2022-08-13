import itertools
from pathlib import Path
import xarray as xa
import pandas as pd
import numpy as np
import climind.data_types.timeseries as ts
import climind.data_types.grid as gd
import copy
from climind.data_manager.metadata import CombinedMetadata


def read_ts(out_dir: Path, metadata: CombinedMetadata, **kwargs):
    construction_metadata = copy.deepcopy(metadata)

    if metadata['type'] == 'timeseries':
        filename = out_dir / metadata['filename'][0]
        if metadata['time_resolution'] == 'monthly':
            return read_monthly_ts(filename, construction_metadata)
        elif metadata['time_resolution'] == 'annual':
            return read_annual_ts(filename, construction_metadata)
        else:
            raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')

    elif metadata['type'] == 'gridded':
        filenames = [out_dir / metadata['filename'][0],
                     out_dir / metadata['filename'][1]]
        if 'grid_resolution' in kwargs:
            if kwargs['grid_resolution'] == 5:
                return read_monthly_5x5_grid(filenames, construction_metadata)
            if kwargs['grid_resolution'] == 1:
                return read_monthly_1x1_grid(filenames, construction_metadata)
        else:
            return read_monthly_grid(filenames, construction_metadata)


def read_grid(filename: list):
    dataset_list = []

    for year in range(1958, 2020):

        filled_filename = str(filename[0]).replace('YYYY', f'{year}')
        filled_filename = Path(filled_filename)

        if not filled_filename.exists():
            pass
            # print(f'File {filled_filename} not available for {year}')
        else:
            field = xa.open_dataset(filled_filename, engine='cfgrib')
            field = field.rename({'t2m': 'tas_mean'})
            dataset_list.append(field)

    for year, month in itertools.product(range(2020, 2050), range(1, 13)):

        filled_filename = str(filename[1]).replace('YYYY', f'{year}')
        filled_filename = Path(filled_filename.replace('MMMM', f'{month:02d}'))

        if not filled_filename.exists():
            pass
            # print(f'File {filled_filename} not available for {year} {month:02d}')
        else:
            field = xa.open_dataset(filled_filename, engine='cfgrib')
            field = field.expand_dims('time')
            field = field.rename({'t2m': 'tas_mean'})
            dataset_list.append(field)

    combo = xa.concat(dataset_list, dim='time')
    return combo


def read_monthly_grid(filename: list, metadata: CombinedMetadata):
    ds = read_grid(filename)
    metadata['history'] = [f"Gridded dataset created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]
    return gd.GridMonthly(ds, metadata)


def read_monthly_5x5_grid(filename: list, metadata: CombinedMetadata):
    ds = read_grid(filename)

    jra55_125 = ds.tas_mean
    number_of_months = jra55_125.shape[0]

    target_grid = np.zeros((number_of_months, 36, 72))

    transfer = np.zeros((5, 5)) + 1.0
    transfer[0, :] = transfer[0, :] * 0.5
    transfer[4, :] = transfer[4, :] * 0.5
    transfer[:, 0] = transfer[:, 0] * 0.5
    transfer[:, 4] = transfer[:, 4] * 0.5

    transfer_sum = np.sum(transfer)

    for month in range(number_of_months):

        enlarged_array = np.zeros((145, 289))
        enlarged_array[:, 0:288] = jra55_125[month, :, :]
        enlarged_array[:, 288] = jra55_125[month, :, 0]

        for xx, yy in itertools.product(range(72), range(36)):
            lox = xx * 4
            hix = (xx + 1) * 4
            loy = yy * 4
            hiy = (yy + 1) * 4

            weighted = transfer * enlarged_array[loy:hiy + 1, lox:hix + 1]
            grid_mean = np.sum(weighted) / transfer_sum
            target_grid[month, yy, xx] = grid_mean

    # flip and shift target_grid to match HadCRUT-like coords lat -90 to 90 and lon -180 to 180
    target_grid = np.flip(target_grid, 1)
    target_grid = np.roll(target_grid, 36, 2)

    latitudes = np.linspace(-87.5, 87.5, 36)
    longitudes = np.linspace(-177.5, 177.5, 72)
    times = pd.date_range(start=f'{1958}-{1:02d}-01', freq='1MS', periods=number_of_months)

    ds = gd.make_xarray(target_grid, times, latitudes, longitudes)

    # update encoding
    for key in ds.data_vars:
        ds[key].encoding.update({'zlib': True, '_FillValue': -1e30})

    metadata['history'] = [f"Gridded dataset created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]
    metadata['history'].append("Regridded to 5 degree latitude-longitude resolution")

    return gd.GridMonthly(ds, metadata)


def read_monthly_1x1_grid(filename: list, metadata: CombinedMetadata):
    ds = read_grid(filename)

    jra55_125 = ds.tas_mean
    number_of_months = jra55_125.shape[0]

    target_grid = np.zeros((number_of_months, 180, 360))

    for month in range(number_of_months):
        enlarged_array = np.zeros((145, 289))
        enlarged_array[:, 0:288] = jra55_125[month, :, :]
        enlarged_array[:, 288] = jra55_125[month, :, 0]

        regridded = gd.simple_regrid(enlarged_array, -180. - 1.25 / 2., -90. - 1.25 / 2., 1.25, 1.0)

        target_grid[month, :, :] = regridded[:, :]

    # flip and shift target_grid to match HadCRUT-like coords lat -90 to 90 and lon -180 to 180
    target_grid = np.flip(target_grid, 1)
    target_grid = np.roll(target_grid, 180, 2)

    latitudes = np.linspace(-89.5, 89.5, 180)
    longitudes = np.linspace(-179.5, 179.5, 360)
    times = pd.date_range(start=f'{1958}-{1:02d}-01', freq='1MS', periods=number_of_months)

    ds = gd.make_xarray(target_grid, times, latitudes, longitudes)

    # update encoding
    for key in ds.data_vars:
        ds[key].encoding.update({'zlib': True, '_FillValue': -1e30})

    metadata['history'] = [f"Gridded dataset created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]
    metadata['history'].append("Regridded to 1 degree latitude-longitude resolution")

    return gd.GridMonthly(ds, metadata)


def read_monthly_ts(filename: str, metadata: CombinedMetadata):
    years = []
    months = []
    anomalies = []

    with open(filename, 'r') as f:
        for line in f:
            columns = line.split()
            year = columns[0][0:4]
            month = columns[0][5:7]

            years.append(int(year))
            months.append(int(month))
            anomalies.append(float(columns[1]))

    metadata['history'] = [f"Time series created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: str, metadata: CombinedMetadata):
    monthly = read_monthly_ts(filename, metadata)
    annual = monthly.make_annual()

    return annual
