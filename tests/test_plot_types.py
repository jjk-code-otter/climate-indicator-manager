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

import matplotlib.pyplot as plt

import climind.data_types.timeseries as ts

import climind.plotters.plot_utils as pu
import climind.plotters.plot_types as pt


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


def test_trend(simple_annual_datasets):
    mean_trend, min_trend, max_trend = pu.calculate_trends(simple_annual_datasets, 1850, 2022)

    assert mean_trend == pytest.approx(0.2)
    assert min_trend == pytest.approx(0.0)
    assert max_trend == pytest.approx(0.4)


def test_calculate_ranks(simple_annual_datasets):
    min_rank, max_rank = pu.calculate_ranks(simple_annual_datasets, 2022)

    assert min_rank == 1
    assert max_rank == 1


def test_calculate_ranks_missing_year(simple_annual_datasets):
    with pytest.raises(ValueError):
        min_rank, max_rank = pu.calculate_ranks(simple_annual_datasets, 2029)


def test_calculate_values(simple_annual_datasets):
    mean_value, min_value, max_value = pu.calculate_values(simple_annual_datasets, 2022)

    assert mean_value == float(2022 - 1850) * 0.01 * 2.0
    assert min_value == 0.0
    assert max_value == float(2022 - 1850) * 0.01 * 4.0


def test_get_first_and_last_years(simple_annual_datasets):
    first, last = pu.get_first_and_last_years(simple_annual_datasets)

    assert first == 1850
    assert last == 2022


def test_caption(simple_annual_datasets):
    i = 1
    for ds in simple_annual_datasets:
        ds.metadata['time_resolution'] = 'monthly'
        ds.metadata['long_name'] = 'caspar'
        ds.metadata['units'] = 'moon'
        ds.metadata['actual'] = False
        ds.metadata['climatology_start'] = 1961
        ds.metadata['climatology_end'] = 1990
        ds.metadata['name'] = f'dataset{i}'
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

    mock_axis.get_ylim.return_value = [-11., 14.]
    ds = Tiny('ohc')
    test_lo, test_hi, test_ticks = pt.set_yaxis(mock_axis, ds)
    assert test_lo == pytest.approx(-10, 6)
    assert test_hi == pytest.approx(15, 6)
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


def test_set_xaxis(mocker):
    mock_axis = mocker.MagicMock()

    mock_axis.get_xlim.return_value = [1849, 2023]
    ds = Tiny('ph')
    test_lo, test_hi, test_ticks = pt.set_xaxis(mock_axis)
    assert test_lo == pytest.approx(1860, 6)
    assert test_hi == pytest.approx(2020, 6)
    assert len(test_ticks) == 9

    mock_axis.get_xlim.return_value = [1989, 2023]
    test_lo, test_hi, test_ticks = pt.set_xaxis(mock_axis)
    assert test_lo == pytest.approx(1990, 6)
    assert test_hi == pytest.approx(2020, 6)
    assert len(test_ticks) == 4


def test_add_labels(mocker):

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
