import pytest
from shapely.geometry import Polygon
import geopandas as gp
import numpy as np
import pandas as pd
import climind.data_types.grid as gd
from xarray import Dataset
from unittest.mock import call


@pytest.fixture
def monthly_grid_2():
    number_of_months = 12 * (1 + 2022 - 1850)

    test_grid = np.zeros((number_of_months, 36, 72))
    for i in range(number_of_months):
        test_grid[i, :, :] = (i % 12) + 1.0

    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=number_of_months)

    test_ds = gd.make_xarray(test_grid, times, lats, lons)
    test_grid_monthly = gd.GridMonthly(test_ds, {'name': 'test_name',
                                                 'history': [],
                                                 'climatology_start': 1961,
                                                 'climatology_end': 1990})
    return test_grid_monthly


@pytest.fixture
def monthly_grid():
    number_of_months = 12 * (1 + 2022 - 1850)

    test_grid = np.zeros((number_of_months, 36, 72))
    lo = 12 * (1981 - 1850)
    hi = 12 * (2011 - 1850)
    test_grid[lo:hi, :, :] = 1.0

    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=number_of_months)

    test_ds = gd.make_xarray(test_grid, times, lats, lons)
    test_grid_monthly = gd.GridMonthly(test_ds, {'name': 'test_name',
                                                 'history': [],
                                                 'climatology_start': 1961,
                                                 'climatology_end': 1990})
    return test_grid_monthly


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
def annual_grid():
    test_grid = np.zeros((12, 36, 72))
    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = np.arange(1., 13., 1.0)

    test_ds = gd.make_xarray(test_grid, times, lats, lons)

    test_grid_annual = gd.GridAnnual(test_ds, {'name': 'test_name'})

    return test_grid_annual


def test_log_activity(mocker):
    def mini():
        return ''

    m = mocker.patch('logging.info')
    fn = gd.log_activity(mini)
    assert fn() == ''
    m.assert_called_once_with('Running: mini')


def test_log_with_args(mocker, annual_grid):
    def mini(arg1, kw=''):
        return ''

    m = mocker.patch('logging.info')
    fn = gd.log_activity(mini)
    assert fn(annual_grid, kw='test') == ''

    calls = [call('Running: mini'),
             call('on test_name'),
             call('With arguments:'),
             call('And keyword arguments:')]

    m.assert_has_calls(calls, any_order=True)


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


def test_make_grid_monthly():
    test_grid = np.zeros((12, 36, 72))
    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = np.arange(1., 13., 1.0)

    test_ds = gd.make_xarray(test_grid, times, lats, lons)

    test_grid_monthly = gd.GridMonthly(test_ds, {})
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


def test_calculate_regional_average(shapes):
    test_grid = np.zeros((12, 36, 72))

    test_grid[:, 0:18, :] = -1.0
    test_grid[:, 18:, :] = 1.0

    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=12)

    test_ds = gd.make_xarray(test_grid, times, lats, lons)

    test_grid_monthly = gd.GridMonthly(test_ds, {'history': []})

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
    test_grid_monthly = gd.GridMonthly(test_ds, {'history': []})
    ts = test_grid_monthly.calculate_regional_average(shapes, 0, land_only=True)
    for i in range(12):
        assert ts.df['data'][i] == pytest.approx(1.0, 0.000001)


def test_calculate_non_uniform_regional_average(shapes):
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
    test_grid_monthly = gd.GridMonthly(test_ds, {'history': []})

    ts = test_grid_monthly.calculate_regional_average(shapes, 0, land_only=False)
    for i in range(12):
        assert ts.df['data'][i] == pytest.approx(36. / sum_of_weights, 0.000001)

    ts = test_grid_monthly.calculate_regional_average(shapes, 1, land_only=False)
    for i in range(12):
        assert ts.df['data'][i] == pytest.approx(36. / sum_of_weights, 0.000001)

    ts = test_grid_monthly.calculate_regional_average(shapes, 2, land_only=False)
    for i in range(12):
        assert ts.df['data'][i] == pytest.approx(36. / sum_of_weights, 0.000001)
