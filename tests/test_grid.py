import pytest
import numpy as np
import climind.data_types.grid as gd
from xarray import Dataset


def test_log_activity():
    def mini():
        return ''

    fn = gd.log_activity(mini)
    assert fn() == ''


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
