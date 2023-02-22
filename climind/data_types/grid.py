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

import pandas as pd
import pkg_resources
import itertools
import xarray as xa
import numpy as np
import logging
import regionmask
from pathlib import Path
from datetime import datetime

from typing import List, Tuple, Callable

from climind.data_manager.metadata import CombinedMetadata
import climind.data_types.timeseries as ts


def get_1d_transfer(zero_point_original: float, grid_space_original: float,
                    zero_point_target: float, grid_space_target: float, index_in_original: int) -> tuple:
    """
    Find the overlapping grid spacings for a new grid based on an index in the old grid
    
    Parameters
    ----------
    zero_point_original: float
        longitude or latitude of the zero-indexed grid cell
    grid_space_original: float
        grid spacing in degrees
    zero_point_target: float
        longitude or latitude of the zero-indexed grid cells in the targe grid
    grid_space_target: float
        grid spacing in degrees of the target grid
    index_in_original: int
        index of the gridcell in the original grid
    Returns
    -------
    tuple
        Returns, the longitude of the first grid cell in the new grid, the number of steps,
        and the first and last indices on the new grid.
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


def simple_regrid(ingrid: np.ndarray, lon0: float, lat0: float, dx: float, target_dy: float) -> np.ndarray:
    """
    Perform a simple regridding, using a simple average of grid cells from the original grid
    that fall within the target grid cell.

    Parameters
    ----------
    ingrid: np.ndarray
        Starting grid which we want to regrid
    lon0: float
        Longitude of zero-indexed grid cell in longitudinal direction
    lat0: float
        Latitude of zero-indexed grid cell in latitudinal direction
    dx: float
        Grid spacing in degrees
    target_dy: float
        Target grid spacing
    Returns
    -------
    np.ndarray
        Returns regridded array.
    """
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


def make_xarray(target_grid, times, latitudes, longitudes) -> xa.Dataset:
    """
    Make a xarray Dataset for a regular lat-lon grid from a numpy grid (ntime, nlat, nlon),
    and arrays of time (ntime), latitude (nlat) and longitude (nlon).

    Parameters
    ----------
    target_grid: np.ndarray
        numpy array of shape (ntime, nlat, nlon)
    times: np.ndarray
        Array of times, shape (ntime)
    latitudes: np.ndarray
        Array of latitudes, shape (nlat)
    longitudes: np.ndarray
        Array of longitudes, shape (nlon)

    Returns
    -------
    xa.Dataset
        Dataset built from the input components
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


def make_standard_grid(out_grid: np.ndarray, start_date: datetime, freq: str, number_of_times: int) -> xa.Dataset:
    """
    Make the standard 5x5 grid from a numpy array, start date, temporal frequency and
    number of time steps.

    Parameters
    ----------
    out_grid: np.ndarray
        Numpy array containing the data. Shape should be (number_of_times, 36, 72)
    start_date: datetime
        Date of the first time step
    freq: str
        Temporal frequency
    number_of_times: int
        Number of time steps, should match the first dimension of the out_grid

    Returns
    -------
    xa.Dataset
        xarray Dataset containing the data in out_grid with the specified temporal
        frequency and number of time steps
    """
    times = pd.date_range(start=start_date, freq=freq, periods=number_of_times)
    latitudes = np.linspace(-87.5, 87.5, 36)
    longitudes = np.linspace(-177.5, 177.5, 72)

    dataset = make_xarray(out_grid, times, latitudes, longitudes)

    return dataset


def log_activity(in_function) -> Callable:
    """
    Decorator function to log name of function run and with which arguments.
    This aims to provide some traceability in the output.

    Parameters
    ----------
    in_function: Callable
        The function to be decorated

    Returns
    -------
    Callable
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


def rank_array(in_array: np.ndarray) -> int:
    """
    Rank array

    Parameters
    ----------
    in_array: np.ndarray
        Array to be ranked
    Returns
    -------
    int
    """
    in_array[np.isnan(in_array)] = -9999.9999

    ntime = len(in_array)
    temp = in_array.argsort()
    ranks = np.empty_like(temp)
    ranks[temp] = np.arange(ntime)
    rank = ntime - ranks
    return rank


class GridMonthly:
    """
    A :class:`GridMonthly` combines an xarray Dataset with a
    :class:`.CombinedMetadata` to bring together data and
    metadata in one object. It represents monthly averages of data on a regular grid.
    """
    def __init__(self, input_data: xa.Dataset, metadata: CombinedMetadata):
        """
        Create a :class:'.GridMonthly` object from an xarray
        Dataset and a :class:`.CombinedMetadata` object.

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
            self.metadata.dataset['last_month'] = str(self.get_last_month())

    def get_last_month(self) -> datetime:
        """
        Get the date of the last month in the dataset

        Returns
        -------
        datetime
            Date of the last month in the dataset
        """
        last_month = self.df.time.dt.date.data[-1]
        return last_month

    def rebaseline(self, first_year: int, final_year: int) -> xa.Dataset:
        """
        Change the baseline of the data to the period between first_year and final_year by
        subtracting the average of the available data between those two years (inclusive).

        Parameters
        ----------
        first_year: int
            First year of climatology period
        final_year: int
            Final year of climatology period

        Returns
        -------
        xa.Dataset
            Changes the dataset in place, but also returns the dataset if needed
        """
        dsg = self.df.groupby('time.month')
        gb = self.df.sel(time=slice(f'{first_year}-01-01', f'{final_year}-12-31')).groupby('time.month')
        clim = gb.mean(dim='time')
        anom = dsg - clim

        self.df = anom

        self.metadata['climatology_start'] = first_year
        self.metadata['climatology_end'] = final_year
        self.metadata['actual'] = False
        self.metadata['derived'] = True
        self.update_history(f'Rebaselined to {first_year}-{final_year}')

        return anom

    def make_annual(self):
        """
        Calculate an annual average from a monthly grid by taking the arithmetic mean of
        available monthly anomalies.

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

    def calculate_regional_average(self, regions, region_number, land_only=True) -> ts.TimeSeriesMonthly:
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

    def calculate_regional_average_missing(self, regions, region_number, threshold=0.3, land_only=True) -> ts.TimeSeriesMonthly:
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
        threshold: float
            If the area covered by data in the region drops below this threshold then NaN is returned.
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

        # copy the variable array, set values to one and missing data to zero then mask that
        missing = copy.deepcopy(self.df.tas_mean)
        replacer = (np.isnan(missing.data))
        missing.data[:,:,:] = 1.0
        missing.data[replacer] = 0.0
        missing = missing.where(r1)

        if land_only:
            land_110 = regionmask.defined_regions.natural_earth_v5_0_0.land_110
            land_mask = land_110.mask_3D(self.df.longitude, self.df.latitude)
            land_mask = land_mask.sel(region=0)
            selected_variable = selected_variable.where(land_mask)
            missing = missing.where(land_mask)

        weights = np.cos(np.deg2rad(selected_variable.latitude))
        regional_ts = selected_variable.weighted(weights).mean(dim=("latitude", "longitude"))
        missing_ts = missing.weighted(weights).mean(dim=("latitude", "longitude"))
        regional_ts[missing_ts < threshold] = np.nan

        # import matplotlib.pyplot as plt
        # plt.plot(missing_ts.data)
        # plt.plot(regional_ts)
        # plt.show()

        # It's such a struggle extracting time information from these blasted xarrays
        years = regional_ts.time.dt.year.data.tolist()
        months = regional_ts.time.dt.month.data.tolist()
        data = regional_ts.values.tolist()

        timeseries_metadata = copy.deepcopy(self.metadata)
        timeseries_metadata['type'] = 'timeseries'
        timeseries_metadata['history'].append('Calculated area-average')
        out_series = ts.TimeSeriesMonthly(years, months, data, timeseries_metadata)

        return out_series

    def update_history(self, message: str) -> None:
        """
        Update the history metadata with a message.

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
    """
    A :class:`GridAnnual` combines an xarray Dataset with a
    :class:`.CombinedMetadata` to bring together data and
    metadata in one object. It represents annual averages of data.
    """
    def __init__(self, input_data, metadata: CombinedMetadata):
        """
        Create an annual gridded data set from an xarray Dataset and
        :class:`.CombinedMetadata` object.

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

    def update_history(self, message: str) -> None:
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

    def write_grid(self, filename: Path, metadata_filename: Path = None, name: str = None) -> None:
        """
        Write the grid to file.

        Parameters
        ----------
        filename: Path
            Filename to write grid to
        metadata_filename: Path
            Filename to write metadata to
        name: str
            Optional name to give the data set being written. Note that names should be unique in any
            data archive.

        Returns
        -------
        None
        """
        if metadata_filename is not None:
            if name is not None:
                self.metadata['name'] = name
            self.metadata['filename'] = [str(filename.name)]
            self.metadata['url'] = [""]
            self.metadata['reader'] = "reader_standard_grid"
            self.metadata['fetcher'] = "fetcher_no_url"
            self.metadata['history'].append(f"Wrote to file {str(filename.name)}")
            self.metadata.write_metadata(metadata_filename)

        self.df.to_netcdf(filename, format="NETCDF4")

    def select_year_range(self, start_year: int, end_year: int):
        """
        Select a particular range of consecutive years from the data set and throw away the rest.

        Parameters
        ----------
        start_year: int
            First year of selection
        end_year: int
            Final year of selction

        Returns
        -------
        GridAnnual
            Returns a :class:`GridAnnual` containing only data within the specified year range.
        """
        self.df = self.df.where(self.df['year'] >= start_year, drop=True)
        self.df = self.df.where(self.df.year <= end_year, drop=True)
        self.update_history(f'Selected year range {start_year} to {end_year}')

        return self

    def get_year_range(self, start_year: int, end_year: int):
        """
        Select a range of consecutive years from the data set.

        Parameters
        ----------
        start_year: int
            start year
        end_year: int
            end year

        Returns
        -------
        GridAnnual
            Returns a :class:`GridAnnual` containing only data within the specified year range.
        """
        out = copy.deepcopy(self)

        out.df = out.df.where(out.df['year'] >= start_year, drop=True)
        out.df = out.df.where(out.df.year <= end_year, drop=True)
        out.update_history(f'Selected year range {start_year} to {end_year}')

        return out

    def rank(self):
        """
        Return a data set where the values are the ranks of each grid cell value.

        Returns
        -------
        GridAnnual
            Return a :class:`GridAnnual` containing the values as ranks from highest (1) to lowest.
        """
        output = copy.deepcopy(self)
        out_grid = np.zeros(output.df['tas_mean'].data.shape)
        for xx, yy in itertools.product(range(72), range(36)):
            selection = output.df['tas_mean'].data[:, yy, xx]
            rank = rank_array(selection)
            out_grid[:, yy, xx] = rank
        output.df['tas_mean'].data = out_grid
        return output

    def get_start_year(self) -> int:
        """
        Get the first year in the dataset

        Returns
        -------
        int
            First year in the dataset
        """
        start_date = self.df.year.data[0]
        return start_date

    def get_end_year(self) -> int:
        """
        Get the last year in the dataset

        Returns
        -------
        int
            Last year in the data set
        """
        end_date = self.df.year.data[-1]
        return end_date

    def running_average(self, n_year: int):
        """
        Calculate an n_year running average of the data in the dataset

        Parameters
        ----------
        n_year: int
            Number of years for which the running average is calculated

        Returns
        -------
        GridAnnual
            Annual gridded dataset which contains the running averages
        """
        self.df['tas_mean'] = self.df['tas_mean'].rolling(year=n_year).mean()
        self.update_history(f'Calculate rolling {n_year}-year average')
        return self


def get_start_and_end_year(all_datasets: List[GridAnnual]) -> Tuple[int, int]:
    """
    Given a list of :class:`GridAnnual` datasets, find the earliest start year and the latest end year

    Parameters
    ----------
    all_datasets: List[GridAnnual]
        List of datasets for which we want to find the first and last year
    Returns
    -------
    Tuple[int, int]
    """
    start_dates = []
    end_dates = []
    for ds in all_datasets:
        start_dates.append(ds.get_start_year())
        end_dates.append(ds.get_end_year())
    start_date = min(start_dates)
    end_date = max(end_dates)
    return start_date, end_date


def process_datasets(all_datasets: List[GridAnnual], grid_type: str) -> GridAnnual:
    """
    Calculate the median or range (depending on selected type) of a list of :class:`GridAnnual` data sets.
    Medians are calculated on a grid cell by grid cell basis based on all available data in the
    list of data sets.

    Parameters
    ----------
    all_datasets: List[GridAnnual]
        list of GridAnnual data sets
    grid_type: str
        Either 'median' or 'range'
    Returns
    -------
    GridAnnual
        Data set containing the median (or half-range) values from all the data sets supplied
    """
    start_date, end_date = get_start_and_end_year(all_datasets)
    number_of_years = end_date - start_date + 1

    # create a dataset from the earliest start date to the latest end date
    out_grid = np.zeros((number_of_years, 36, 72))

    # for each time step calculate the median of available data sets.
    for year in range(start_date, start_date + number_of_years):
        n_data_sets = len(all_datasets)
        stack = np.zeros((n_data_sets, 36, 72))
        for i, ds in enumerate(all_datasets):
            temp_df = ds.get_year_range(year, year)
            if temp_df.df['tas_mean'].data.shape[0] != 0:
                stack[i, :, :] = temp_df.df['tas_mean'].data[0, :, :]
            else:
                stack[i, :, :] = np.nan

        for xx, yy in itertools.product(range(72), range(36)):
            select = stack[:, yy, xx]
            if grid_type == 'median':
                out_grid[year - start_date, yy, xx] = np.median(select[~np.isnan(select)])
            elif grid_type == 'range':
                full_range = np.max(select[~np.isnan(select)]) - np.min(select[~np.isnan(select)])
                out_grid[year - start_date, yy, xx] = full_range / 2.

    dataset = make_standard_grid(out_grid, str(start_date), '1YS', number_of_years)
    dataset = dataset.groupby('time.year').mean(dim='time')
    dataset = GridAnnual(dataset, all_datasets[0].metadata)

    return dataset


def median_of_datasets(all_datasets: List[GridAnnual]) -> GridAnnual:
    """
    Calculate the median of a list of :class:`GridAnnual` data sets

    Parameters
    ----------
    all_datasets: List[GridAnnual]
        List of :class:`GridAnnual` datasets from which the medians will be calculated.
    Returns
    -------
    GridAnnual
    """
    return process_datasets(all_datasets, 'median')


def range_of_datasets(all_datasets: List[GridAnnual]) -> GridAnnual:
    """
    Calculate the half-range of a list of :class:`GridAnnual` data sets

    Parameters
    ----------
    all_datasets: List[GridAnnual]
        List of :class:`GridAnnual` datasets from which the ranges will be calculated.
    Returns
    -------
    GridAnnual
    """
    return process_datasets(all_datasets, 'range')
