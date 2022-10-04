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

import copy
import pkg_resources
import itertools
import xarray as xa
import numpy as np
import logging
import regionmask
from pathlib import Path
from datetime import datetime
from climind.data_manager.metadata import CombinedMetadata
import climind.data_types.timeseries as ts


def get_1d_transfer(zero_point_original, grid_space_original,
                    zero_point_target, grid_space_target, index_in_original):
    """
    Find the overlapping grid spacings for a new grid based on an index in the old grid
    
    Parameters
    ----------
    zero_point_original
    grid_space_original
    zero_point_target
    grid_space_target
    index_in_original

    Returns
    -------

    """
    llon = zero_point_target + index_in_original * grid_space_target
    hlon = zero_point_target + (index_in_original + 1) * grid_space_target

    mlon_lo = (llon - zero_point_original) / grid_space_original
    mlon_hi = (hlon - zero_point_original) / grid_space_original

    lonindexlo = int(np.floor(mlon_lo))
    lonindexhi = int(np.floor(mlon_hi))

    final_cell = (hlon - (zero_point_original + lonindexhi * grid_space_original)) / grid_space_original

    if final_cell == 0:
        lonindexhi -= 1
        final_cell = (hlon - (zero_point_original + lonindexhi * grid_space_original)) / grid_space_original

    nlonsteps = lonindexhi - lonindexlo + 1

    transfer_lon = np.zeros((nlonsteps)) + 1.0
    if nlonsteps == 1:
        transfer_lon[0] = grid_space_target / grid_space_original
    else:
        transfer_lon[0] = ((zero_point_original + (lonindexlo + 1) * grid_space_original) - llon) / grid_space_original
        transfer_lon[nlonsteps - 1] = final_cell

    return transfer_lon, nlonsteps, lonindexlo, lonindexhi


def simple_regrid(ingrid, lon0, lat0, dx, target_dy):
    nlat = int(180 / target_dy)
    nlon = int(360 / target_dy)
    outgrid = np.zeros((nlat, nlon))

    for xlon, ylat in itertools.product(range(nlon), range(nlat)):
        # Longitudes
        y0 = -180.0
        transfer_lon, nlonsteps, lolon, hilon = get_1d_transfer(lon0, dx, y0, target_dy, xlon)
        # Latitudes
        y0 = -90.0
        transfer_lat, nlatsteps, lolat, hilat = get_1d_transfer(lat0, dx, y0, target_dy, ylat)

        transfer_lon = np.repeat(np.reshape(transfer_lon, (1, nlonsteps)), nlatsteps, 0)
        transfer_lat = np.repeat(np.reshape(transfer_lat, (nlatsteps, 1)), nlonsteps, 1)

        transfer = transfer_lat * transfer_lon

        outgrid[ylat, xlon] = np.sum(ingrid[lolat:hilat + 1, lolon:hilon + 1] * transfer) / np.sum(transfer)

    return outgrid


def make_xarray(target_grid, times, latitudes, longitudes):
    """
    Make a xarray Dataset for a regular lat-lon grid from a numpy grid (ntime, nlat, nlon),
    and arrays of time (ntime), latitude (nlat) and longitude (nlon).

    Parameters
    ----------
    target_grid:
        numpy array of shape (ntime, nlat, nlon)
    times:
        Array of times, shape (ntime)
    latitudes:
        Array of latitudes, shape (nlat)
    longitudes
        Array of longitudes, shape (nlon)

    Returns
    -------

    """
    ds = xa.Dataset({
        'tas_mean': xa.DataArray(
            data=target_grid,
            dims=['time', 'latitude', 'longitude'],
            coords={'time': times, 'latitude': latitudes, 'longitude': longitudes},
            attrs={'long_name': '2m air temperature', 'units': 'K'}
        )
    },
        attrs={'project': 'NA'}
    )

    return ds


def log_activity(in_function):
    """
    Decorator function to log name of function run and with which arguments.
    This aims to provide some traceability in the output.

    Parameters
    ----------
    in_function: function
        The function to be decorated

    Returns
    -------
    function
    """

    def wrapper(*args, **kwargs):
        logging.info(f"Running: {in_function.__name__}")
        msg = []
        for a in args:
            if isinstance(a, GridMonthly) or isinstance(a, GridAnnual):
                logging.info(f"on {a.metadata['name']}")
            msg.append(str(a))
        if len(msg) > 0:
            logging.info(f"With arguments:")
            logging.info(', '.join(msg))

        msg = []
        for k in kwargs:
            msg.append(str(k))
        if len(msg) > 0:
            logging.info(f"And keyword arguments:")
            logging.info(', '.join(msg))
        return in_function(*args, **kwargs)

    return wrapper


def rank_array(in_array) -> int:

    in_array[np.isnan(in_array)] = -9999.9999

    ntime = len(in_array)
    temp = in_array.argsort()
    ranks = np.empty_like(temp)
    ranks[temp] = np.arange(ntime)
    rank = ntime - ranks
    return rank


class GridMonthly:

    def __init__(self, input_data: xa.Dataset, metadata: CombinedMetadata):
        """

        Parameters
        ----------
        input_data: xa.Dataset
            xarray dataset
        metadata: CombinedMetadata
            CombinedMetadata object
        """
        self.df = input_data

        if metadata is None:
            self.metadata = {"name": "", "history": []}
        else:
            self.metadata = metadata

    def rebaseline(self, y1: int, y2: int):

        dsg = self.df.groupby('time.month')
        gb = self.df.sel(time=slice(f'{y1}-01-01', f'{y2}-12-31')).groupby('time.month')
        clim = gb.mean(dim='time')
        anom = dsg - clim

        self.df = anom

        self.metadata['climatology_start'] = y1
        self.metadata['climatology_end'] = y2
        self.metadata['actual'] = False
        self.metadata['derived'] = True
        self.update_history(f'Rebaselined to {y1}-{y2}')

        return anom

    def make_annual(self):
        """
        Calculate an annual average from a monthly grid

        Returns
        -------
        GridAnnual
            Return annual average of the grid
        """
        dsg = self.df.groupby('time.year').mean(dim='time')

        annual = GridAnnual(dsg, self.metadata)
        annual.update_history('Calculated annual average')
        annual.metadata['time_resolution'] = 'annual'
        annual.metadata['derived'] = True

        return annual

    def calculate_regional_average(self, regions, region_number, land_only=True):
        """
        Calculate a regional average from the grid. The region is specified by a geopandas
        Geodataframe and the index (region_number) of the chosen shape. By default, the output
        is masked to land areas only, this can be switched off by setting land_only to False.

        Parameters
        ----------
        regions: Geodataframe
            geopandas Geodataframe specifying the region to be average over
        region_number: int
            the index of the particular region in the Geodataframe
        land_only: bool
            By defauly output is masked to land areas only, to calculate a full area average set
            land_only to False

        Returns
        -------
        ts.TimeSeriesMonthly
            Returns time series of area averages.
        """
        mask = regionmask.mask_3D_geopandas(regions,
                                            self.df.longitude,
                                            self.df.latitude, drop=False, overlap=True)
        r1 = mask.sel(region=region_number)
        selected_variable = self.df.tas_mean.where(r1)

        if land_only:
            land_110 = regionmask.defined_regions.natural_earth_v5_0_0.land_110
            land_mask = land_110.mask_3D(self.df.longitude, self.df.latitude)
            land_mask = land_mask.sel(region=0)
            selected_variable = selected_variable.where(land_mask)

        weights = np.cos(np.deg2rad(selected_variable.latitude))
        regional_ts = selected_variable.weighted(weights).mean(dim=("latitude", "longitude"))

        # It's such a struggle extracting time information from these blasted xarrays
        years = regional_ts.time.dt.year.data.tolist()
        months = regional_ts.time.dt.month.data.tolist()
        data = regional_ts.values.tolist()

        timeseries_metadata = copy.deepcopy(self.metadata)
        timeseries_metadata['type'] = 'timeseries'
        timeseries_metadata['history'].append('Calculated area-average')
        out_series = ts.TimeSeriesMonthly(years, months, data, timeseries_metadata)

        return out_series

    def update_history(self, message: str):
        """
        Update the history metadata

        Parameters
        ----------
        message : str
            Message to be added to history

        Returns
        -------
        None
        """
        self.metadata['history'].append(message)


class GridAnnual:

    def __init__(self, input_data, metadata: CombinedMetadata):
        """

        Parameters
        ----------
        input_data: xa.Dataset
            xarray dataset
        metadata: CombinedMetadata
            CombinedMetadata object
        """
        self.df = input_data

        if metadata is None:
            self.metadata = {"name": "", "history": []}
        else:
            self.metadata = metadata

    def update_history(self, message: str):
        """
        Update the history metadata

        Parameters
        ----------
        message : str
            Message to be added to history

        Returns
        -------
        None
        """
        self.metadata['history'].append(message)

    def write_grid(self, filename: Path, metadata_filename: Path = None, name: str = None):
        if metadata_filename is not None:
            if name is not None:
                self.metadata['name'] = name
            self.metadata['filename'] = [str(filename.name)]
            self.metadata['url'] = [""]
            self.metadata['reader'] = "reader_standard_grid"
            self.metadata['fetcher'] = "fetcher_no_url"
            self.metadata['history'].append(f"Wrote to file {str(filename.name)}")
            self.metadata.write_metadata(metadata_filename)

        now = datetime.today()
        climind_version = pkg_resources.get_distribution("climind").version

        self.df.to_netcdf(filename, format="NETCDF4")

    def select_year_range(self, start_year: int, end_year: int):
        """
        Select a year range

        Parameters
        ----------
        start_year
        end_year

        Returns
        -------

        """
        self.df = self.df.where(self.df['year'] >= start_year, drop=True)
        self.df = self.df.where(self.df.year <= end_year, drop=True)
        self.update_history(f'Selected year range {start_year} to {end_year}')

        return self

    def rank(self):
        output = copy.deepcopy(self)
        out_grid = np.zeros(output.df['tas_mean'].data.shape)
        for xx, yy in itertools.product(range(72), range(36)):
            selection = output.df['tas_mean'].data[:, yy, xx]
            rank = rank_array(selection)
            out_grid[:, yy, xx] = rank
        output.df['tas_mean'].data = out_grid
        return output
