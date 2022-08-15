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
import xarray as xa
import numpy as np
import climind.data_types.grid as gd
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
        if 'grid_resolution' in kwargs:
            if kwargs['grid_resolution'] == 5:
                return read_monthly_5x5_grid(filename, construction_metadata)
            if kwargs['grid_resolution'] == 1:
                return read_monthly_1x1_grid(filename, construction_metadata)
        else:
            return read_monthly_grid(filename, construction_metadata)


def read_monthly_grid(filename: str, metadata: CombinedMetadata):
    df = xa.open_dataset(filename)
    df = df.rename({'tempanomaly': 'tas_mean',
                    'lat': 'latitude',
                    'lon': 'longitude'})
    metadata['history'] = [f"Gridded dataset created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]
    return gd.GridMonthly(df, metadata)


def read_monthly_1x1_grid(filename: str, metadata: CombinedMetadata):
    """
    Convert 2x2 grid to 1x1 grid by copying 2x2 value into all 4 1x1 grid cells it
    contains

    Parameters
    ----------
    filename
    metadata

    Returns
    -------

    """
    gistemp = xa.open_dataset(filename)

    target_grid = np.repeat(gistemp.tempanomaly, 2, 1)
    target_grid = np.repeat(target_grid, 2, 2)

    latitudes = np.linspace(-89.5, 89.5, 180)
    longitudes = np.linspace(-179.5, 179.5, 360)
    times = gistemp.time.data

    ds = gd.make_xarray(target_grid, times, latitudes, longitudes)

    # update encoding
    for key in ds.data_vars:
        ds[key].encoding.update({'zlib': True, '_FillValue': -1e30})

    metadata['history'] = [f"Gridded dataset created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]
    metadata['history'].append("Regridded to 1 degree latitude-longitude resolution")

    return gd.GridMonthly(ds, metadata)


def read_monthly_5x5_grid(filename: str, metadata: CombinedMetadata):
    gistemp = xa.open_dataset(filename)
    number_of_months = len(gistemp.time.data)
    target_grid = np.zeros((number_of_months, 36, 72))

    for m in range(number_of_months):
        print(f'month: {m}')
        for xx in range(72):
            for yy in range(36):

                transfer = np.zeros((3, 3)) + 1.0

                if xx % 2 == 0:
                    transfer[:, 2] = transfer[:, 2] * 0.5
                    lox = int(5 * (xx / 2))
                    hix = lox + 2
                else:
                    transfer[:, 0] = transfer[:, 0] * 0.5
                    lox = int(5 * ((xx - 1) / 2) + 2)
                    hix = lox + 2

                if yy % 2 == 0:
                    transfer[2, :] = transfer[2, :] * 0.5
                    loy = int(5 * (yy / 2))
                    hiy = loy + 2
                else:
                    transfer[0, :] = transfer[0, :] * 0.5
                    loy = int(5 * ((yy - 1) / 2) + 2)
                    hiy = loy + 2

                selection = gistemp.tempanomaly.data[m, loy:hiy + 1, lox:hix + 1]
                index = (~np.isnan(selection))
                if np.count_nonzero(index) > 0:
                    weighted = transfer[index] * selection[index]
                    grid_mean = np.sum(weighted) / np.sum(transfer[index])
                else:
                    grid_mean = np.nan
                target_grid[m, yy, xx] = grid_mean

    latitudes = np.linspace(-87.5, 87.5, 36)
    longitudes = np.linspace(-177.5, 177.5, 72)
    times = gistemp.time.data

    ds = gd.make_xarray(target_grid, times, latitudes, longitudes)

    # update encoding
    for key in ds.data_vars:
        ds[key].encoding.update({'zlib': True, '_FillValue': -1e30})

    metadata['history'] = [f"Gridded dataset created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]
    metadata['history'].append("Regridded to 5 degree latitude-longitude resolution")

    return gd.GridMonthly(ds, metadata)


def read_monthly_ts(filename: str, metadata: CombinedMetadata):
    years = []
    months = []
    anomalies = []

    with open(filename, 'r') as f:
        for i in range(2):
            f.readline()
        for line in f:
            columns = line.split(',')
            for i in range(1, 13):
                if columns[i] != '***':
                    years.append(int(columns[0]))
                    months.append(int(i))
                    anomalies.append(float(columns[i]))

    metadata['history'] = [f"Time series created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: str, metadata: CombinedMetadata):
    years = []
    anomalies = []

    with open(filename, 'r') as f:
        for i in range(2):
            f.readline()
        for line in f:
            columns = line.split(',')
            if columns[13] != '***':
                years.append(int(columns[0]))
                anomalies.append(float(columns[13]))

    metadata['history'] = [f"Time series created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata)
