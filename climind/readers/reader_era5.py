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
import itertools
import xarray as xa
import numpy as np
import climind.data_types.grid as gd
import climind.data_types.timeseries as ts
import copy
from climind.data_manager.metadata import CombinedMetadata


def find_latest(out_dir: Path, filename_with_wildcards: str) -> Path:
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
    filename_with_wildcards = filename_with_wildcards.replace('YYYYMMMM', '*')
    list_of_files = list(out_dir.glob(filename_with_wildcards))
    list_of_files.sort()
    out_filename = list_of_files[-1]
    return out_filename


def read_ts(out_dir: Path, metadata: CombinedMetadata, **kwargs):
    construction_metadata = copy.deepcopy(metadata)
    if metadata['type'] == 'timeseries':
        filename_with_wildcards = metadata['filename'][0]
        filename = find_latest(out_dir, filename_with_wildcards)

        if metadata['time_resolution'] == 'monthly':
            return read_monthly_ts(filename, construction_metadata)
        elif metadata['time_resolution'] == 'annual':
            return read_annual_ts(filename, construction_metadata)
        else:
            raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')

    elif metadata['type'] == 'gridded':

        filename = out_dir / metadata['filename'][0]

        if 'grid_resolution' in kwargs:
            if kwargs['grid_resolution'] == 5:
                return read_monthly_5x5_grid(filename, construction_metadata)
            if kwargs['grid_resolution'] == 1:
                return read_monthly_1x1_grid(filename, construction_metadata)
        else:
            return read_monthly_grid(filename, construction_metadata)


def read_monthly_5x5_grid(filename, metadata):
    combo = read_grid(filename)

    number_of_months = combo.t2m.data.shape[0]

    # transfer matrix for regridding, there are 20 quarter degree grid
    # cells in a 5 degree grid cell, however, the ERA5 grid is offset half a
    # grid cell because the first grid cell centre is at the North Pole and
    # the last is at the South Pole
    transfer = np.zeros((21, 21)) + 1
    transfer[0, :] = transfer[0, :] * 0.5
    transfer[20, :] = transfer[20, :] * 0.5
    transfer[:, 0] = transfer[:, 0] * 0.5
    transfer[:, 20] = transfer[:, 20] * 0.5

    transfer_sum = np.sum(transfer)

    enlarged_array = np.zeros((721, 1441))

    target_grid = np.zeros((number_of_months, 36, 72))

    for m in range(number_of_months):

        if len(combo.t2m.data.shape) == 3:
            enlarged_array[:, 0:1440] = combo.t2m.data[m, :, :]
            enlarged_array[:, 1440] = combo.t2m.data[m, :, 0]
        else:
            if np.isnan(combo.t2m.data[m, 0, 0, 0]):
                enlarged_array[:, 0:1440] = combo.t2m.data[m, :, :, 1]
                enlarged_array[:, 1440] = combo.t2m.data[m, :, 0, 1]
            else:
                enlarged_array[:, 0:1440] = combo.t2m.data[m, :, :, 0]
                enlarged_array[:, 1440] = combo.t2m.data[m, :, 0, 0]

        for xx, yy in itertools.product(range(72), range(36)):
            lox = xx * 20
            hix = (xx + 1) * 20
            loy = yy * 20
            hiy = (yy + 1) * 20
            weighted = transfer * enlarged_array[loy:hiy + 1, lox:hix + 1]
            grid_mean = np.sum(weighted) / transfer_sum
            target_grid[m, yy, xx] = grid_mean

    # flip and shift target_grid to match HadCRUT-like coords lat -90 to 90 and lon -180 to 180
    target_grid = np.flip(target_grid, 1)
    target_grid = np.roll(target_grid, 36, 2)

    latitudes = np.linspace(-87.5, 87.5, 36)
    longitudes = np.linspace(-177.5, 177.5, 72)
    times = combo.time.data

    ds = gd.make_xarray(target_grid, times, latitudes, longitudes)

    # update encoding
    for key in ds.data_vars:
        ds[key].encoding.update({'zlib': True, '_FillValue': -1e30})

    metadata['history'] = [f"Gridded dataset created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]
    metadata['history'].append("Regridded to 5 degree latitude-longitude resolution")

    return gd.GridMonthly(ds, metadata)


def read_monthly_1x1_grid(filename, metadata):
    combo = read_grid(filename)

    number_of_months = combo.t2m.data.shape[0]

    # transfer matrix for regridding, there are 4 quarter degree grid
    # cells in a 1 degree grid cell, however, the ERA5 grid is offset half a
    # grid cell because the first grid cell centre is at the North Pole and
    # the last is at the South Pole
    transfer = np.zeros((5, 5)) + 1
    transfer[0, :] = transfer[0, :] * 0.5
    transfer[4, :] = transfer[4, :] * 0.5
    transfer[:, 0] = transfer[:, 0] * 0.5
    transfer[:, 4] = transfer[:, 4] * 0.5

    transfer_sum = np.sum(transfer)

    enlarged_array = np.zeros((721, 1441))

    target_grid = np.zeros((number_of_months, 180, 360))

    for m in range(number_of_months):

        if len(combo.t2m.data.shape) == 3:
            enlarged_array[:, 0:1440] = combo.t2m.data[m, :, :]
            enlarged_array[:, 1440] = combo.t2m.data[m, :, 0]
        else:
            if np.isnan(combo.t2m.data[m, 0, 0, 0]):
                enlarged_array[:, 0:1440] = combo.t2m.data[m, :, :, 1]
                enlarged_array[:, 1440] = combo.t2m.data[m, :, 0, 1]
            else:
                enlarged_array[:, 0:1440] = combo.t2m.data[m, :, :, 0]
                enlarged_array[:, 1440] = combo.t2m.data[m, :, 0, 0]

        for xx, yy in itertools.product(range(360), range(180)):
            lox = xx * 4
            hix = (xx + 1) * 4
            loy = yy * 4
            hiy = (yy + 1) * 4
            weighted = transfer * enlarged_array[loy:hiy + 1, lox:hix + 1]
            grid_mean = np.sum(weighted) / transfer_sum
            target_grid[m, yy, xx] = grid_mean

    # flip and shift target_grid to match HadCRUT-like coords lat -90 to 90 and lon -180 to 180
    target_grid = np.flip(target_grid, 1)
    target_grid = np.roll(target_grid, 180, 2)

    latitudes = np.linspace(-89.5, 89.5, 180)
    longitudes = np.linspace(-179.5, 179.5, 360)
    times = combo.time.data

    ds = gd.make_xarray(target_grid, times, latitudes, longitudes)

    # update encoding
    for key in ds.data_vars:
        ds[key].encoding.update({'zlib': True, '_FillValue': -1e30})

    metadata['history'] = [f"Gridded dataset created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]
    metadata['history'].append("Regridded to 1 degree latitude-longitude resolution")

    return gd.GridMonthly(ds, metadata)


def read_monthly_grid(filename: str, metadata):
    combo = read_grid(filename)
    metadata['history'] = [f"Gridded dataset created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]
    return gd.GridMonthly(combo, metadata)


def read_grid(filename: str):
    dataset_list = []
    for year in range(1979, 2030):
        filled_filename = Path(str(filename).replace('YYYY', f'{year}'))
        if filled_filename.exists():
            dataset_list.append(xa.open_dataset(filled_filename))
    combo = xa.concat(dataset_list, dim='time')

    return combo


def read_monthly_ts(filename: Path, metadata: CombinedMetadata):
    years = []
    months = []
    anomalies = []

    with open(filename, 'r') as f:
        for _ in range(9):
            f.readline()

        for line in f:
            columns = line.split(',')
            year = columns[0][0:4]
            month = columns[0][4:6]

            years.append(int(year))
            months.append(int(month))
            anomalies.append(float(columns[1]))

    selected_file = filename.name
    selected_url = metadata['url'][0].split('/')
    selected_url = selected_url[0:-1]
    selected_url.append(selected_file)
    selected_url = '/'.join(selected_url)

    yyyy = selected_file[33:37]
    mmmm = selected_file[37:39]

    selected_url = selected_url.replace('YYYY', yyyy)
    selected_url = selected_url.replace('MMMM', mmmm)

    metadata['filename'][0] = selected_file
    metadata['url'][0] = selected_url

    metadata['history'] = [f"Time series created from file {selected_file} "
                           f"downloaded from {selected_url}"]

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: Path, metadata: CombinedMetadata):
    monthly = read_monthly_ts(filename, metadata)
    annual = monthly.make_annual()

    return annual
