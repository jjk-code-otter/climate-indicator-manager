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
import copy
import itertools
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import climind.data_types.timeseries as ts
import climind.data_types.grid as gd
from climind.data_manager.metadata import DatasetMetadata, CollectionMetadata, CombinedMetadata

import climind.plotters.plot_utils as pu
import climind.plotters.plot_types as pt


@pytest.fixture
def simple_monthly_grid(test_metadata):
    number_of_months = 12
    latitudes = np.linspace(-87.5, 87.5, 36)
    longitudes = np.linspace(-177.5, 177.5, 72)
    times = pd.date_range(start=f'1850-01-01', freq='1MS', periods=number_of_months)
    target_grid = np.zeros((number_of_months, 36, 72))

    ds = gd.make_xarray(target_grid, times, latitudes, longitudes)

    return gd.GridMonthly(ds, test_metadata)


@pytest.fixture
def simple_annual_datasets():
    """
    Produces an annual time series from 1850 to 2022.
    Returns
    -------

    """
    all_datasets = []
    for i in range(5):
        years = []
        anoms = []
        for y in range(1850, 2023):
            years.append(y)
            anoms.append(0.01 * float(i) * float(y - 1850))

        all_datasets.append(ts.TimeSeriesAnnual(years, anoms))

    return all_datasets


@pytest.fixture
def regional_annual_datasets(annual_metadata):
    """
    Produces an annual time series from 1850 to 2022.
    Returns
    -------

    """
    region_names = ['tas', 'wmo_ra_1', 'wmo_ra_2', 'wmo_ra_3', 'wmo_ra_4', 'wmo_ra_5', 'wmo_ra_6']

    all_datasets = []

    for region in range(7):

        for i in range(6):
            years = []
            anoms = []
            for y in range(1900, 2023):
                years.append(y)
                anoms.append(0.01 * float(i) * float(y - 1900))

            this_metadata = copy.deepcopy(annual_metadata)
            this_metadata['variable'] = region_names[region]

            all_datasets.append(ts.TimeSeriesAnnual(years, anoms, metadata=this_metadata))

    return all_datasets


@pytest.mark.parametrize("limit_1, limit_2, spacing, expected_lo, expected_hi", [
    (0.1, 1.3, 0.5, 0.5, 1.5),
    (0.1, 1.3, 0.1, 0.2, 1.3),
    (-1.1, 1.3, 0.2, -1.0, 1.4)
])
def test_set_lo_hi_ticks(limit_1, limit_2, spacing, expected_lo, expected_hi):
    limits = [limit_1, limit_2]

    lo, hi, ticks = pu.set_lo_hi_ticks(limits, spacing)

    # need to use approximately equal assertion because the boundaries aren't quite perfect
    assert lo == pytest.approx(expected_lo)
    assert hi == pytest.approx(expected_hi)


@pytest.fixture
def complex_annual_datasets():
    """
    Produces an annual time series from 1850 to 2022.
    Returns
    -------

    """
    all_datasets = []
    for i in range(5):
        years = []
        anoms = []
        for y in range(1850, 2023):
            years.append(y)
            anom = 0.05
            if y == 2022 - i:
                anom = 0.10
            anoms.append(anom)

        all_datasets.append(ts.TimeSeriesAnnual(years, anoms))

    return all_datasets


@pytest.fixture
def annual_metadata():
    attributes = {'url': ['test_url'],
                  'filename': ['test_filename'],
                  'type': 'timeseries',
                  'long_name': 'Global mean temperature',
                  'time_resolution': 'annual',
                  'space_resolution': 999,
                  'climatology_start': 1961,
                  'climatology_end': 1990,
                  'actual': False,
                  'derived': False,
                  'history': ['step1', 'step2'],
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher'}

    global_attributes = {'name': '',
                         'display_name': 'nonunique name',
                         'version': '',
                         'variable': 'tas',
                         'units': 'degC',
                         'citation': ['cite1', 'cite2'],
                         'citation_url': ['cite1', 'cite2'],
                         'data_citation': [''],
                         'colour': 'dimgrey',
                         'zpos': 99}

    dataset_metadata = DatasetMetadata(attributes)
    collection_metadata = CollectionMetadata(global_attributes)

    return CombinedMetadata(dataset_metadata, collection_metadata)


@pytest.fixture
def annual_datalist(annual_metadata):
    """
    Produces an annual time series from 1850 to 2022.
    Returns
    -------

    """
    datalist = []
    for i in range(1, 4):
        year = []
        anoms = []
        unc = []
        for y in range(1850, 2023):
            year.append(y)
            anoms.append(float(i))
            unc.append(0.1)
        datalist.append(ts.TimeSeriesAnnual(year, anoms,
                                            copy.deepcopy(annual_metadata),
                                            uncertainty=unc))

    return datalist


@pytest.fixture
def test_metadata():
    attributes = {'url': ['test_url'],
                  'filename': ['test_filename'],
                  'type': 'gridded',
                  'long_name': 'Ocean heat content',
                  'time_resolution': 'monthly',
                  'space_resolution': 999,
                  'climatology_start': 1961,
                  'climatology_end': 1990,
                  'actual': False,
                  'derived': False,
                  'history': ['step1', 'step2'],
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher'}

    global_attributes = {'name': '',
                         'display_name': '',
                         'version': '',
                         'variable': 'ohc',
                         'units': 'zJ',
                         'citation': ['cite1', 'cite2'],
                         'citation_url': ['cite1', 'cite2'],
                         'data_citation': [''],
                         'colour': 'dimgrey',
                         'zpos': 99}

    dataset_metadata = DatasetMetadata(attributes)
    collection_metadata = CollectionMetadata(global_attributes)

    return CombinedMetadata(dataset_metadata, collection_metadata)


@pytest.fixture
def monthly_datalist(test_metadata):
    """
    Produces a monthly time series from 1850 to 2022. Data for each month are equal to the year in
    which the month falls
    Returns
    -------

    """
    datalist = []
    for i in range(3):
        years = []
        months = []
        anomalies = []

        for y, m in itertools.product(range(1850, 2023), range(1, 13)):
            years.append(y)
            months.append(m)
            anomalies.append(float(y) / 100.)

        datalist.append(ts.TimeSeriesMonthly(years, months, anomalies, metadata=test_metadata))
    return datalist


def test_add_data_sets(annual_datalist):
    plt.figure(figsize=[16, 9])
    test_output = pt.add_data_sets(plt.gca(), annual_datalist, dark=True)

    # check that all the annual datasest were added
    for i in range(len(annual_datalist)):
        x_plot, y_plot = plt.gca().lines[i].get_xydata().T
        for year in range(1850, 2023):
            assert x_plot[year - 1850] == year
            assert y_plot[year - 1850] == float(i + 1)
    plt.close()

    assert len(test_output) == len(annual_datalist)


def test_neat_plot(annual_datalist, tmpdir):
    test_caption = pt.neat_plot(tmpdir, annual_datalist, 'test.png', 'Title words')

    assert 'Annual Global mean temperature' in test_caption
    assert '(&deg;C, difference from the 1961-1990 average)' in test_caption

    assert (tmpdir / 'test.png').exists()
    assert (tmpdir / 'test.pdf').exists()
    assert (tmpdir / 'test.svg').exists()


def test_marine_heat_plot(annual_datalist, tmpdir):
    annual_datalist = annual_datalist[0:2]
    annual_datalist[0].metadata['variable'] = 'mhw'
    annual_datalist[1].metadata['variable'] = 'mcs'

    test_caption = pt.marine_heatwave_plot(tmpdir, annual_datalist, 'test.png', '')

    assert 'marine heatwave' in test_caption
    assert 'marine cold spell' in test_caption

    assert (tmpdir / 'test.png').exists()
    assert (tmpdir / 'test.pdf').exists()
    assert (tmpdir / 'test.svg').exists()


def test_arctic_sea_ice_plot(monthly_datalist, tmpdir):
    for i in range(len(monthly_datalist)):
        monthly_datalist[i].metadata['variable'] = 'arctic_ice'
    test_caption = pt.arctic_sea_ice_plot(tmpdir, monthly_datalist, 'test.png', '')

    assert 'September' in test_caption
    assert 'March' in test_caption

    assert (tmpdir / 'test.png').exists()
    assert (tmpdir / 'test.pdf').exists()
    assert (tmpdir / 'test.svg').exists()


def test_antarctic_sea_ice_plot(monthly_datalist, tmpdir):
    for i in range(len(monthly_datalist)):
        monthly_datalist[i].metadata['variable'] = 'antarctic_ice'
    test_caption = pt.antarctic_sea_ice_plot(tmpdir, monthly_datalist, 'test.png', '')

    assert 'September' in test_caption
    assert 'February' in test_caption

    assert (tmpdir / 'test.png').exists()
    assert (tmpdir / 'test.pdf').exists()
    assert (tmpdir / 'test.svg').exists()


def test_dark_plot(annual_datalist, tmpdir):
    test_caption = pt.dark_plot(tmpdir, annual_datalist, 'test.png', 'Title words')

    assert 'Annual Global mean temperature' in test_caption
    assert '(&deg;C, difference from the 1961-1990 average)' in test_caption

    assert (tmpdir / 'test.png').exists()
    assert (tmpdir / 'test.pdf').exists()
    assert (tmpdir / 'test.svg').exists()


def test_decadal_plot(annual_datalist, tmpdir):
    decadal = []
    for ds in annual_datalist:
        dec = ds.running_mean(10)
        dec.select_decade()
        decadal.append(dec)

    test_caption = pt.decade_plot(tmpdir, decadal, 'test.png', 'Decadal words')

    assert (tmpdir / 'test.png').exists()
    assert (tmpdir / 'test.pdf').exists()
    assert (tmpdir / 'test.svg').exists()

    print(test_caption)
    pass


def test_monthly_plot(monthly_datalist, tmpdir):
    test_caption = pt.monthly_plot(tmpdir, monthly_datalist, 'test.png', 'Title words')

    assert 'Monthly Ocean heat content' in test_caption
    assert '(zJ, difference from the 1961-1990 average)' in test_caption

    assert (tmpdir / 'test.png').exists()
    assert (tmpdir / 'test.pdf').exists()
    assert (tmpdir / 'test.svg').exists()


def test_calculate_highest_year_and_values(complex_annual_datasets):
    uniques, values = pu.calculate_highest_year_and_values(complex_annual_datasets)

    assert uniques == [2018, 2019, 2020, 2021, 2022]
    for entry in values:
        assert entry == [0.05, 0.10]


def test_trend(simple_annual_datasets):
    mean_trend, min_trend, max_trend = pu.calculate_trends(simple_annual_datasets, 1850, 2022)

    assert mean_trend == pytest.approx(0.2)
    assert min_trend == pytest.approx(0.0)
    assert max_trend == pytest.approx(0.4)


def test_calculate_ranks(simple_annual_datasets):
    min_rank, max_rank = pu.calculate_ranks(simple_annual_datasets, 2022)

    assert min_rank == 1
    assert max_rank == 1


def test_calculate_ranks_missing_year(annual_datalist):
    with pytest.raises(ValueError):
        _, _ = pu.calculate_ranks(annual_datalist, 2029)


def test_calculate_values(simple_annual_datasets):
    mean_value, min_value, max_value = pu.calculate_values(simple_annual_datasets, 2022)

    assert mean_value == float(2022 - 1850) * 0.01 * 2.0
    assert min_value == 0.0
    assert max_value == float(2022 - 1850) * 0.01 * 4.0

def test_calculate_values_ipcc_style(simple_annual_datasets):
    mean_value, min_value, max_value = pu.calculate_values_ipcc_style(simple_annual_datasets, 2022)

    delta = 0.5631748300567634

    assert mean_value == float(2022 - 1850) * 0.01 * 2.0
    assert min_value == pytest.approx(0.0 - delta, 0.0001)
    assert max_value == pytest.approx(float(2022 - 1850) * 0.01 * 4.0 + delta, 0.0001)


def test_get_first_and_last_years(simple_annual_datasets):
    first, last = pu.get_first_and_last_years(simple_annual_datasets)

    assert first == 1850
    assert last == 2022


def test_caption_writer(simple_annual_datasets):
    i = 1
    for ds in simple_annual_datasets:
        ds.metadata['time_resolution'] = 'monthly'
        ds.metadata['long_name'] = 'caspar'
        ds.metadata['units'] = 'moon'
        ds.metadata['actual'] = False
        ds.metadata['climatology_start'] = 1961
        ds.metadata['climatology_end'] = 1990
        ds.metadata['name'] = f'dataset{i}'
        ds.metadata['display_name'] = f'dataset{i}'
        i += 1

    caption = pu.caption_builder(simple_annual_datasets)

    assert '1961-1990' in caption
    assert '1850-2022' in caption

    assert 'Data are from the following five data sets' in caption

    caption = pu.caption_builder(simple_annual_datasets[0:1])

    assert '1961-1990' in caption
    assert '1850-2022' in caption

    assert 'Data are from dataset1' in caption


class Tiny:
    def __init__(self, variable):
        self.metadata = {'variable': variable}


def test_set_yaxis(mocker):
    mock_axis = mocker.MagicMock()

    mock_axis.get_ylim.return_value = [8.04, 8.15]
    ds = Tiny('ph')
    test_lo, test_hi, test_ticks = pt.set_yaxis(mock_axis, ds)
    assert test_lo == pytest.approx(8.04, 6)
    assert test_hi == pytest.approx(8.15, 6)
    assert len(test_ticks) == 12

    mock_axis.get_ylim.return_value = [-110., 140.]
    ds = Tiny('ohc')
    test_lo, test_hi, test_ticks = pt.set_yaxis(mock_axis, ds)
    assert test_lo == pytest.approx(-100, 6)
    assert test_hi == pytest.approx(150, 6)
    assert len(test_ticks) == 5

    mock_axis.get_ylim.return_value = [-5., 75.]
    ds = Tiny('mhw')
    test_lo, test_hi, test_ticks = pt.set_yaxis(mock_axis, ds)
    assert test_lo == pytest.approx(0.0, 6)
    assert test_hi == pytest.approx(80., 6)
    assert len(test_ticks) == 8

    mock_axis.get_ylim.return_value = [-1230., 3279.]
    ds = Tiny('greenland')
    test_lo, test_hi, test_ticks = pt.set_yaxis(mock_axis, ds)
    assert test_lo == pytest.approx(-1000., 6)
    assert test_hi == pytest.approx(3000., 6)
    assert len(test_ticks) == 5

    mock_axis.get_ylim.return_value = [-25.2, 5.]
    ds = Tiny('glacier')
    test_lo, test_hi, test_ticks = pt.set_yaxis(mock_axis, ds)
    assert test_lo == pytest.approx(-25., 6)
    assert test_hi == pytest.approx(10., 6)
    assert len(test_ticks) == 7


def test_set_xaxis(mocker):
    mock_axis = mocker.MagicMock()

    mock_axis.get_xlim.return_value = [1849, 2023]
    test_lo, test_hi, test_ticks = pt.set_xaxis(mock_axis)
    assert test_lo == pytest.approx(1860, 6)
    assert test_hi == pytest.approx(2020, 6)
    assert len(test_ticks) == 9

    mock_axis.get_xlim.return_value = [1989, 2023]
    test_lo, test_hi, test_ticks = pt.set_xaxis(mock_axis)
    assert test_lo == pytest.approx(1990, 6)
    assert test_hi == pytest.approx(2020, 6)
    assert len(test_ticks) == 4


def test_add_labels():
    plt.figure()
    dataset = Tiny('ohc')
    dataset.metadata['units'] = 'degC'
    pt.add_labels(plt.gca(), dataset)
    assert plt.gca().get_xlabel() == 'Year'
    assert plt.gca().get_ylabel() == r"$\!^\circ\!$C"

    dataset.metadata['units'] = 'empty'
    pt.add_labels(plt.gca(), dataset)
    assert plt.gca().get_xlabel() == 'Year'
    assert plt.gca().get_ylabel() == r"empty"


def test_map_caption(simple_annual_datasets):
    i = 1
    for ds in simple_annual_datasets:
        ds.metadata['time_resolution'] = 'monthly'
        ds.metadata['long_name'] = 'caspar'
        ds.metadata['units'] = 'degC'
        ds.metadata['actual'] = False
        ds.metadata['climatology_start'] = 1961
        ds.metadata['climatology_end'] = 1990
        ds.metadata['name'] = f'dataset{i}'
        ds.metadata['display_name'] = f'dataset{i}'
        i += 1

    test_caption = pu.map_caption_builder(simple_annual_datasets, 'mean')

    assert 'Monthly caspar anomaly' in test_caption
    assert '(&deg;C, difference from the 1961-1990 average)' in test_caption
    assert 'Data shown are the median of the following five data sets: dataset1, dataset2, dataset3, dataset4, dataset5.' in test_caption

    test_caption = pu.map_caption_builder(simple_annual_datasets, 'rank')

    assert 'Monthly caspar rank' in test_caption
    assert '(&deg;C)' in test_caption
    assert 'Data shown are the median rank of the following five data sets: dataset1, dataset2, dataset3, dataset4, dataset5.' in test_caption

    test_caption = pu.map_caption_builder(simple_annual_datasets, 'unc')

    assert 'Monthly caspar uncertainty' in test_caption
    assert '(&deg;C)' in test_caption
    assert 'Data shown are the half-range of the following five data sets: dataset1, dataset2, dataset3, dataset4, dataset5.' in test_caption


def test_quick_and_dirty_map(simple_monthly_grid, tmpdir):
    filename = tmpdir / 'test.png'
    pt.quick_and_dirty_map(simple_monthly_grid.df, filename)
    assert filename.exists()


def test_nice_map(simple_monthly_grid, tmpdir):
    filename = tmpdir / 'test'
    filename2 = tmpdir / 'test.png'
    pt.nice_map(simple_monthly_grid.df, filename, 'Words to test title')
    assert filename2.exists()


def test_plot_map_by_year_and_month(simple_monthly_grid, tmpdir):
    filename = tmpdir / 'test'
    filename2 = tmpdir / 'test.png'
    pt.plot_map_by_year_and_month(simple_monthly_grid, 1850, 5, filename, '')
    assert filename2.exists()


def test_generic_map(simple_monthly_grid, tmpdir):
    annual_grid = simple_monthly_grid.make_annual()
    test_caption = pt.dashboard_map(tmpdir, [annual_grid], 'test.png', 'title words')
    assert (tmpdir / 'test.png').exists()

    assert 'Annual Ocean heat content anomaly' in test_caption
    assert '(zJ, difference from the 1961-1990 average)' in test_caption
    assert 'Data shown are the median of the following one data sets:' in test_caption

    test_caption = pt.dashboard_rank_map(tmpdir, [annual_grid], 'test.png', 'title words')
    assert (tmpdir / 'test.png').exists()

    assert 'Annual Ocean heat content rank' in test_caption
    assert '(zJ)' in test_caption
    assert 'Data shown are the median rank of the following one data sets:' in test_caption

    test_caption = pt.dashboard_uncertainty_map(tmpdir, [annual_grid], 'test.png', 'title words')
    assert (tmpdir / 'test.png').exists()

    assert 'Annual Ocean heat content uncertainty' in test_caption
    assert '(zJ)' in test_caption
    assert 'Data shown are the half-range of the following one data sets:' in test_caption


def test_wave_plot(monthly_datalist, tmpdir):
    monthly_dataset = monthly_datalist[0]
    pt.wave_plot(tmpdir, monthly_dataset, 'test.png')
    assert (tmpdir / 'test.png').exists()


# def test_trend_plot(regional_annual_datasets, tmpdir):
#     test_caption = pt.trends_plot(tmpdir, regional_annual_datasets, 'test.png', 'test words',
#                                   order=["wmo_ra_1", "wmo_ra_2", "wmo_ra_3", "wmo_ra_4", "wmo_ra_5", "wmo_ra_6", "tas"])
#
#     assert (tmpdir / 'test.png').exists()
#
#     assert 'Figure shows' in test_caption
