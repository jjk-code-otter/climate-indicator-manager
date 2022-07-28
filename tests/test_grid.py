import pytest
import numpy as np
import pandas as pd
import climind.data_types.grid as gd
from xarray import Dataset
from unittest.mock import call


@pytest.fixture
def monthly_grid():
    nmonths = 12 * (1 + 2022 - 1850)

    test_grid = np.zeros((nmonths, 36, 72))
    lo = 12 * (1981 - 1850)
    hi = 12 * (2011 - 1850)
    test_grid[lo:hi, :, :] = 1.0

    lats = np.arange(-87.5, 90.0, 5.0)
    lons = np.arange(-177.5, 180.0, 5.0)
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=nmonths)

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

        transfer, nsteps, loind, hiind = gd.get_1d_transfer(original_x0, original_dx,
                                                            new_x0, new_dx, index)

        lo = ((new_x0 + index * new_dx) - original_x0) // original_dx
        hi = ((new_x0 + (index + 1) * new_dx) - original_x0) // original_dx

        assert len(transfer) == 5
        for i in transfer:
            assert i == 1.0 or i == 0.5
        assert nsteps == 5
        assert loind == lo
        assert hiind == hi


def test_1d_transfer_1_25offset_to_1():
    original_x0 = -90.0 - 0.5 * 1.25
    original_dx = 1.25

    new_x0 = -90.0
    new_dx = 1.0

    for index in range(180):

        transfer, nsteps, loind, hiind = gd.get_1d_transfer(original_x0, original_dx,
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

        transfer, nsteps, loind, hiind = gd.get_1d_transfer(original_x0, original_dx,
                                                            new_x0, new_dx, index)

        assert len(transfer) == 5
        for i in transfer:
            assert i == 1.0
        assert nsteps == 5
        assert loind == index * 5
        assert hiind == (index + 1) * 5 - 1

    original_x0 = -180.0
    original_dx = 1.0

    new_x0 = -180.0
    new_dx = 5.0

    for index in range(72):

        transfer, nsteps, loind, hiind = gd.get_1d_transfer(original_x0, original_dx,
                                                            new_x0, new_dx, index)

        assert len(transfer) == 5
        for i in transfer:
            assert i == 1.0
        assert nsteps == 5
        assert loind == index * 5
        assert hiind == (index + 1) * 5 - 1


def test_1d_transfer_5_to_5():
    original_x0 = -180.0
    original_dx = 5.0

    new_x0 = -180.0
    new_dx = 5.0

    for index in range(72):
        transfer, nsteps, loind, hiind = gd.get_1d_transfer(original_x0, original_dx,
                                                            new_x0, new_dx, index)

        assert len(transfer) == 1
        for i in transfer:
            assert i == 1.0
        assert nsteps == 1
        assert loind == index
        assert hiind == index


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


def test_make_gridmonthly():
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


def test_make_gridannual():
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
