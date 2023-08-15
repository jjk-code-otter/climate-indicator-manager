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

import pytest
from pathlib import Path
from shapely.geometry import Polygon
import xarray as xa
import geopandas as gp
import numpy as np
import pandas as pd

import climind.data_types.grid as gd
from climind.data_manager.metadata import DatasetMetadata, CollectionMetadata, CombinedMetadata
from xarray import Dataset


@pytest.fixture
def test_dataset_attributes():
    attributes = {'url': ['test_url'],
                  'filename': ['test_filename', 'test_filename VVVV'],
                  'type': 'gridded',
                  'time_resolution': 'monthly',
                  'space_resolution': 999,
                  'climatology_start': 1961,
                  'climatology_end': 1990,
                  'actual': False,
                  'derived': False,
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher',
                  'history': [],
                  'notes': 'This says BBBB'
                  }

    return attributes


@pytest.fixture
def test_collection_attributes():
    attributes = {"name": "test_name",
                  "display_name": "HadCRUT5",
                  "version": "5.0.1.0",
                  "variable": "tas",
                  "units": "degC",
                  "citation": [
                      f"Morice, C.P., J.J. Kennedy, N.A. Rayner, J.P. Winn, E. Hogan, R.E. Killick, "
                      f"R.J.H. Dunn, T.J. Osborn, P.D. Jones and I.R. Simpson (in press) An updated "
                      f"assessment of near-surface temperature change from 1850: the HadCRUT5 dataset. "
                      f"Journal of Geophysical Research (Atmospheres) doi:10.1029/2019JD032361"],
                  "citation_url": ["kttps://notaurul"],
                  "data_citation": [""],
                  "acknowledgement": "Version VVVV of the data set was downloaded AAAA in the year of our lord YYYY",
                  "colour": "#444444",
                  "zpos": 99
                  }

    return attributes


@pytest.fixture
def test_combo(test_dataset_attributes, test_collection_attributes):
    ds = DatasetMetadata(test_dataset_attributes)
    cl = CollectionMetadata(test_collection_attributes)
    combo = CombinedMetadata(ds, cl)
    return combo


@pytest.fixture
def monthly_grid_2(test_combo):
    number_of_months = 12 * (1 + 2022 - 1850)

    test_grid = np.zeros((number_of_months, 36, 72))
    for i in range(number_of_months):
        test_grid[i, :, :] = (i % 12) + 1.0

    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=number_of_months)

    test_ds = gd.make_xarray(test_grid, times, lats, lons)
    test_grid_monthly = gd.GridMonthly(test_ds, test_combo)
    return test_grid_monthly


@pytest.fixture
def monthly_grid(test_combo):
    number_of_months = 12 * (1 + 2022 - 1850)

    test_grid = np.zeros((number_of_months, 36, 72))
    lo = 12 * (1981 - 1850)
    hi = 12 * (2011 - 1850)
    test_grid[lo:hi, :, :] = 1.0

    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=number_of_months)

    test_ds = gd.make_xarray(test_grid, times, lats, lons)
    test_grid_monthly = gd.GridMonthly(test_ds, test_combo)
    return test_grid_monthly


def test_select_year_and_month(monthly_grid):
    selection = monthly_grid.select_year_and_month(1982, 7)
    assert selection.df.time.dt.year.data[0] == 1982
    assert selection.df.time.dt.month.data[0] == 7
    assert selection.metadata['history'][-1] == 'Selected single month 07/1982'


def test_get_last_month(monthly_grid):
    last_month = monthly_grid.get_last_month()
    assert last_month.year == 2022
    assert last_month.month == 12


def test_rebaseline(monthly_grid):
    monthly_grid.rebaseline(1981, 2010)

    assert monthly_grid.metadata['climatology_start'] == 1981
    assert monthly_grid.metadata['climatology_end'] == 2010
    assert monthly_grid.metadata['history'][0] == 'Rebaselined to 1981-2010'

    # anomalies are -1 outside climatology
    for month in range(12):
        assert monthly_grid.df.tas_mean.data[month, 0, 0] == -1.0
    # and anomalies are 0 inside climatology
    for month in range(12):
        month0 = 12 * (1981 - 1850)
        assert monthly_grid.df.tas_mean.data[month0 + month, 0, 0] == 0.0


def test_make_annual(monthly_grid_2):
    annual = monthly_grid_2.make_annual()

    assert isinstance(annual, gd.GridAnnual)
    assert annual.df.tas_mean.shape[0] == monthly_grid_2.df.tas_mean.shape[0] / 12
    assert annual.df.tas_mean.values[0, 0, 0] == np.mean(range(1, 13))
    assert annual.metadata['history'][-1] == 'Calculated annual average'


def test_update_history(monthly_grid):
    monthly_grid.update_history('test message #1')
    monthly_grid.update_history('test message #2')
    assert len(monthly_grid.metadata['history']) == 2
    assert monthly_grid.metadata['history'][0] == 'test message #1'
    assert monthly_grid.metadata['history'][-1] == 'test message #2'


@pytest.fixture
def annual_grid(test_combo):
    test_grid = np.zeros((12, 36, 72))
    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    #    times = np.arange(1., 13., 1.0)
    times = pd.date_range(start=f'1850-01-01', freq='1YS', periods=12)

    test_ds = gd.make_xarray(test_grid, times, lats, lons)
    test_ds = test_ds.groupby('time.year').mean(dim='time')

    test_grid_annual = gd.GridAnnual(test_ds, test_combo)
    return test_grid_annual


@pytest.fixture
def annual_grid_2(test_combo):
    test_grid = np.zeros((12, 36, 72)) + 1.0
    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = pd.date_range(start=f'1851-01-01', freq='1YS', periods=12)

    test_ds = gd.make_xarray(test_grid, times, lats, lons)
    test_ds = test_ds.groupby('time.year').mean(dim='time')

    test_grid_annual = gd.GridAnnual(test_ds, test_combo)

    return test_grid_annual


@pytest.fixture
def annual_grid_3(test_combo):
    test_grid = np.zeros((12, 36, 72))
    for i in range(12):
        test_grid[i, :, :] = i
    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = pd.date_range(start=f'1851-01-01', freq='1YS', periods=12)

    test_ds = gd.make_xarray(test_grid, times, lats, lons)
    test_ds = test_ds.groupby('time.year').mean(dim='time')

    test_grid_annual = gd.GridAnnual(test_ds, test_combo)

    return test_grid_annual


def test_running_average(annual_grid_3):
    test_ds = annual_grid_3.running_average(3)
    for i in range(0, 2):
        assert np.isnan(test_ds.df['tas_mean'].data[i, 0, 0])
    for i in range(2, 12):
        assert test_ds.df['tas_mean'].data[i, 0, 0] == i - 1.0


def test_running_average_longer(annual_grid_3):
    test_ds = annual_grid_3.running_average(5)
    for i in range(0, 4):
        assert np.isnan(test_ds.df['tas_mean'].data[i, 0, 0])
    for i in range(4, 12):
        assert test_ds.df['tas_mean'].data[i, 0, 0] == i - 2.0


def test_median_of_datasets(annual_grid, annual_grid_2):
    all_datasets = [annual_grid, annual_grid_2]
    test_median = gd.median_of_datasets(all_datasets)

    assert test_median.df['tas_mean'].data[0, 0, 0] == 0.0
    for i in range(1, 12):
        assert test_median.df['tas_mean'].data[i, 0, 0] == 0.5
    assert test_median.df['tas_mean'].data[12, 0, 0] == 1.0

    assert test_median.df['tas_mean'].data.shape[0] == 13
    assert test_median.get_start_year() == 1850
    assert test_median.get_end_year() == 1862


def test_range_of_datasets(annual_grid, annual_grid_2):
    all_datasets = [annual_grid, annual_grid_2]
    test_median = gd.range_of_datasets(all_datasets)

    assert test_median.df['tas_mean'].data[0, 0, 0] == 0.0
    for i in range(1, 12):
        assert test_median.df['tas_mean'].data[i, 0, 0] == 1.0 / 2.
    assert test_median.df['tas_mean'].data[12, 0, 0] == 0.0

    assert test_median.df['tas_mean'].data.shape[0] == 13
    assert test_median.get_start_year() == 1850
    assert test_median.get_end_year() == 1862


def test_get_first_year_and_last_years(annual_grid):
    test_start_date = annual_grid.get_start_year()
    test_end_date = annual_grid.get_end_year()
    assert test_start_date == 1850
    assert test_end_date == 1861


def test_get_first_year_and_last_years_from_list_of_datasets(annual_grid, annual_grid_2):
    all_datasets = [annual_grid, annual_grid_2]
    test_start_date, test_end_date = gd.get_start_and_end_year(all_datasets)
    assert test_start_date == 1850
    assert test_end_date == 1862


def test_basic_write_grid(annual_grid, tmpdir):
    filename = Path(tmpdir) / 'test.nc'
    metadata_filename = Path(tmpdir) / 'test_metadata.json'

    annual_grid.write_grid(filename)

    assert filename.exists()
    assert not metadata_filename.exists()


def test_write_grid_with_metadata(annual_grid, tmpdir):
    filename = Path(tmpdir) / 'test.nc'
    metadata_filename = Path(tmpdir) / 'test_metadata.json'
    new_name = 'newish_name'

    annual_grid.write_grid(filename, metadata_filename=metadata_filename, name=new_name)

    assert filename.exists()
    assert metadata_filename.exists()


def test_select_year_range(test_combo):
    target_grid = np.zeros((2002 - 1995 + 1, 36, 72))
    latitudes = np.arange(-87.5, 90.0, 5.0)
    longitudes = np.arange(-177.5, 180.0, 5.0)
    years = np.arange(1995, 2002.0001, 1)

    ds = xa.Dataset({
        'tas_mean': xa.DataArray(
            data=target_grid,
            dims=['year', 'latitude', 'longitude'],
            coords={'year': years, 'latitude': latitudes, 'longitude': longitudes},
            attrs={'long_name': '2m air temperature', 'units': 'K'}
        )
    },
        attrs={'project': 'NA'}
    )

    test_grid_annual = gd.GridAnnual(ds, test_combo)

    subset = test_grid_annual.select_year_range(1999, 2000)

    assert subset.df.tas_mean.shape == (2, 36, 72)
    assert subset.df.year.values[0] == 1999
    assert subset.df.year.values[1] == 2000




def test_1d_transfer_1_25offset_to_5():
    original_x0 = -90.0 - 0.5 * 1.25
    original_dx = 1.25

    new_x0 = -90.0
    new_dx = 5.0

    for index in range(36):

        transfer, number_of_steps, low_index, high_index = gd.get_1d_transfer(original_x0, original_dx,
                                                                              new_x0, new_dx, index)

        lo = ((new_x0 + index * new_dx) - original_x0) // original_dx
        hi = ((new_x0 + (index + 1) * new_dx) - original_x0) // original_dx

        assert len(transfer) == 5
        for i in transfer:
            assert i == 1.0 or i == 0.5
        assert number_of_steps == 5
        assert low_index == lo
        assert high_index == hi


def test_1d_transfer_1_25offset_to_1():
    original_x0 = -90.0 - 0.5 * 1.25
    original_dx = 1.25

    new_x0 = -90.0
    new_dx = 1.0

    for index in range(180):

        transfer, number_of_steps, low_index, high_index = gd.get_1d_transfer(original_x0, original_dx,
                                                                              new_x0, new_dx, index)

        if index == 0:
            assert transfer[0] == 0.5
            assert transfer[1] == (1 - 0.625) / 1.25
        if index == 179:
            assert transfer[1] == 0.5
            assert transfer[0] == (1 - 0.625) / 1.25

        assert np.sum(transfer) == pytest.approx(0.8, 0.0001)


def test_1d_transfer_1_to_5():
    original_x0 = -90.0
    original_dx = 1.0

    new_x0 = -90.0
    new_dx = 5.0

    for index in range(36):

        transfer, number_of_steps, low_index, high_index = gd.get_1d_transfer(original_x0, original_dx,
                                                                              new_x0, new_dx, index)

        assert len(transfer) == 5
        for i in transfer:
            assert i == 1.0
        assert number_of_steps == 5
        assert low_index == index * 5
        assert high_index == (index + 1) * 5 - 1

    original_x0 = -180.0
    original_dx = 1.0

    new_x0 = -180.0
    new_dx = 5.0

    for index in range(72):

        transfer, number_of_steps, low_index, high_index = gd.get_1d_transfer(original_x0, original_dx,
                                                                              new_x0, new_dx, index)

        assert len(transfer) == 5
        for i in transfer:
            assert i == 1.0
        assert number_of_steps == 5
        assert low_index == index * 5
        assert high_index == (index + 1) * 5 - 1


def test_1d_transfer_5_to_5():
    original_x0 = -180.0
    original_dx = 5.0

    new_x0 = -180.0
    new_dx = 5.0

    for index in range(72):
        transfer, number_of_steps, low_index, high_index = gd.get_1d_transfer(original_x0, original_dx,
                                                                              new_x0, new_dx, index)

        assert len(transfer) == 1
        for i in transfer:
            assert i == 1.0
        assert number_of_steps == 1
        assert low_index == index
        assert high_index == index


def test_simple_regrid():
    test_grid = np.zeros((180, 360)) + 1.0

    for xx in range(72):
        for yy in range(36):
            lox = xx * 5
            hix = (xx + 1) * 5
            loy = yy * 5
            hiy = (yy + 1) * 5
            test_grid[loy:hiy, lox:hix] = yy

    result_grid = gd.simple_regrid(test_grid, -180.0, -90.0, 1.0, 5.0)

    for yy in range(36):
        assert result_grid[yy, 0] == yy


def test_make_grid():
    test_grid = np.zeros((12, 36, 72))
    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = np.arange(1., 13., 1.0)

    test_ds = gd.make_xarray(test_grid, times, lats, lons)

    assert isinstance(test_ds, Dataset)


def test_make_grid_monthly(test_combo):
    test_grid = np.zeros((12, 36, 72))
    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=12)

    test_ds = gd.make_xarray(test_grid, times, lats, lons)

    test_grid_monthly = gd.GridMonthly(test_ds, test_combo)
    assert isinstance(test_grid_monthly, gd.GridMonthly)

    test_grid_monthly = gd.GridMonthly(test_ds, None)
    assert isinstance(test_grid_monthly, gd.GridMonthly)
    assert 'name' in test_grid_monthly.metadata


def test_make_grid_annual():
    test_grid = np.zeros((12, 36, 72))
    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = np.arange(1., 13., 1.0)

    test_ds = gd.make_xarray(test_grid, times, lats, lons)

    test_grid_annual = gd.GridAnnual(test_ds, {})
    assert isinstance(test_grid_annual, gd.GridAnnual)

    test_grid_annual = gd.GridAnnual(test_ds, None)
    assert isinstance(test_grid_annual, gd.GridAnnual)
    assert 'name' in test_grid_annual.metadata


def test_rank_annual():
    test_grid = np.zeros((12, 36, 72))
    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = np.arange(1., 13., 1.0)

    for i in range(12):
        test_grid[i, :, :] = i
        test_grid[i, 9, 7] = 12 - i

    test_ds = gd.make_xarray(test_grid, times, lats, lons)

    test_grid_annual = gd.GridAnnual(test_ds, {})

    test_ranked = test_grid_annual.rank()

    assert test_ranked.df['tas_mean'].data[11, 0, 0] == 1
    assert test_ranked.df['tas_mean'].data[11, 9, 7] == 12


def test_rank_annual_with_missing():
    test_grid = np.zeros((12, 36, 72))
    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = np.arange(1., 13., 1.0)

    for i in range(10):
        test_grid[i, :, :] = i
        test_grid[i, 9, 7] = 12 - i

    test_grid[10, :, :] = np.nan
    test_grid[11, :, :] = np.nan

    test_ds = gd.make_xarray(test_grid, times, lats, lons)

    test_grid_annual = gd.GridAnnual(test_ds, {})

    test_ranked = test_grid_annual.rank()

    assert test_ranked.df['tas_mean'].data[9, 0, 0] == 1
    assert test_ranked.df['tas_mean'].data[9, 9, 7] == 10


@pytest.fixture
def shapes():
    data_dictionary = {
        'region': [
            'world',
            'nh',
            'sh'
        ],
        'geometry': [
            Polygon([(-180, -90), (-180, 90), (180, 90), (180, -90), (-180, -90)]),
            Polygon([(-180, 0), (180, 0), (180, 90), (-180, 90), (-180, 0)]),
            Polygon([(-180, -90), (180, -90), (180, 0), (-180, 0), (-180, -90)])
        ]
    }
    whole_world = gp.GeoDataFrame(data_dictionary,
                                  geometry=data_dictionary['geometry'],
                                  crs="EPSG:4326")
    return whole_world


def test_calculate_regional_average(shapes, test_combo):
    test_grid = np.zeros((12, 36, 72))

    test_grid[:, 0:18, :] = -1.0
    test_grid[:, 18:, :] = 1.0

    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=12)

    test_ds = gd.make_xarray(test_grid, times, lats, lons)

    test_grid_monthly = gd.GridMonthly(test_ds, test_combo)

    ts = test_grid_monthly.calculate_regional_average(shapes, 0, land_only=False)
    for i in range(12):
        assert ts.df['data'][i] == pytest.approx(0.0, 0.000001)

    ts = test_grid_monthly.calculate_regional_average(shapes, 1, land_only=False)
    for i in range(12):
        assert ts.df['data'][i] == pytest.approx(1.0, 0.000001)

    ts = test_grid_monthly.calculate_regional_average(shapes, 2, land_only=False)
    for i in range(12):
        assert ts.df['data'][i] == pytest.approx(-1.0, 0.000001)

    test_grid[:, :, :] = 1.0
    test_ds = gd.make_xarray(test_grid, times, lats, lons)
    test_grid_monthly = gd.GridMonthly(test_ds, test_combo)
    ts = test_grid_monthly.calculate_regional_average(shapes, 0, land_only=True)
    for i in range(12):
        assert ts.df['data'][i] == pytest.approx(1.0, 0.000001)


def test_calculate_regional_average_missing(shapes, test_combo):
    test_grid = np.zeros((12, 36, 72))

    test_grid[:, 0:18, :] = -1.0
    test_grid[:, 18:, :] = 1.0

    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = pd.date_range(start='1850-01-01', freq='1MS', periods=12)

    test_ds = gd.make_xarray(test_grid, times, lats, lons)

    test_grid_monthly = gd.GridMonthly(test_ds, test_combo)

    ts = test_grid_monthly.calculate_regional_average_missing(shapes, 0, land_only=False)
    for i in range(12):
        assert ts.df['data'][i] == pytest.approx(0.0, 0.000001)

    ts = test_grid_monthly.calculate_regional_average_missing(shapes, 1, land_only=False)
    for i in range(12):
        assert ts.df['data'][i] == pytest.approx(1.0, 0.000001)

    ts = test_grid_monthly.calculate_regional_average_missing(shapes, 2, land_only=False)
    for i in range(12):
        assert ts.df['data'][i] == pytest.approx(-1.0, 0.000001)

    test_grid[:, :, :] = 1.0
    test_ds = gd.make_xarray(test_grid, times, lats, lons)
    test_grid_monthly = gd.GridMonthly(test_ds, test_combo)
    ts = test_grid_monthly.calculate_regional_average_missing(shapes, 0, land_only=True)
    for i in range(12):
        assert ts.df['data'][i] == pytest.approx(1.0, 0.000001)


def test_calculate_non_uniform_regional_average(shapes, test_combo):
    test_grid = np.zeros((12, 36, 72))
    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    # use grid cell values that are the inverse of cos(latitude)
    # area average is then easy to calculate
    sum_of_weights = 0.0
    for i in range(36):
        test_grid[:, i, :] = 1. / np.cos(np.deg2rad(lats[i]))
        sum_of_weights += np.cos(np.deg2rad(lats[i]))

    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=12)
    test_ds = gd.make_xarray(test_grid, times, lats, lons)
    test_grid_monthly = gd.GridMonthly(test_ds, test_combo)

    ts = test_grid_monthly.calculate_regional_average(shapes, 0, land_only=False)
    for i in range(12):
        assert ts.df['data'][i] == pytest.approx(36. / sum_of_weights, 0.000001)

    ts = test_grid_monthly.calculate_regional_average(shapes, 1, land_only=False)
    for i in range(12):
        assert ts.df['data'][i] == pytest.approx(36. / sum_of_weights, 0.000001)

    ts = test_grid_monthly.calculate_regional_average(shapes, 2, land_only=False)
    for i in range(12):
        assert ts.df['data'][i] == pytest.approx(36. / sum_of_weights, 0.000001)
