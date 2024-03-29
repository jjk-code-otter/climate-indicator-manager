#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2024 John Kennedy
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
import numpy as np
from climind.data_manager.metadata import DatasetMetadata, CollectionMetadata, CombinedMetadata
import climind.data_types.timeseries as ts

import climind.stats.utils as utils


def test_get_latitudes():
    lats = utils.get_latitudes(1.0)
    assert len(lats) == 180
    assert lats[0] == -89.5
    assert lats[-1] == 89.5

    lats = utils.get_latitudes(5.0)
    assert len(lats) == 36
    assert lats[0] == -87.5
    assert lats[-1] == 87.5


def test_get_n_years_from_n_months():
    month = 12
    year = -1

    for n_months in range(200):
        month += 1
        if month > 12:
            month = 1
            year += 1

        n_years = utils.get_n_years_from_n_months(n_months)
        assert year == n_years

    assert utils.get_n_years_from_n_months(1) == 0
    assert utils.get_n_years_from_n_months(12) == 1
    assert utils.get_n_years_from_n_months(13) == 1
    assert utils.get_n_years_from_n_months(24) == 2
    assert utils.get_n_years_from_n_months(29) == 2


def test_monthly_to_annual():
    monthly_means = np.zeros((24, 3))
    monthly_means[:, 0] = np.arange(0.0, 24.0, 1.0)
    monthly_means[:, 1] = np.arange(0.0, 24.0, 1.0)
    monthly_means[:, 2] = np.arange(0.0, 24.0, 1.0)

    annual_means = utils.monthly_to_annual_array(monthly_means)

    for i in range(3):
        assert annual_means[0, i] == 66.0 / 12.
        assert annual_means[1, i] == 66.0 / 12. + 12.


def test_rolling_average():
    input_array = np.arange(0.0, 200.0, 1.0)

    rolled_array = utils.rolling_average(input_array, 10)

    for i in range(4):
        assert np.isnan(rolled_array[i])

    for i in range(6):
        assert np.isnan(rolled_array[-1 * i])

    assert rolled_array[4] == 45. / 10.
    assert rolled_array[-6] == 45. / 10. + 190.


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
                         'display_name': '',
                         'version': '',
                         'variable': 'tas',
                         'units': 'degC',
                         'citation': ['cite1', 'cite2'],
                         'citation_url': ['cite1', 'cite2'],
                         'data_citation': [''],
                         'colour': '',
                         'zpos': 99}

    dataset_metadata = DatasetMetadata(attributes)
    collection_metadata = CollectionMetadata(global_attributes)

    return CombinedMetadata(dataset_metadata, collection_metadata)


@pytest.fixture
def simple_annual(annual_metadata):
    """
    Produces an annual time series from 1850 to 2022.
    Returns
    -------

    """
    annual_metadata = copy.deepcopy(annual_metadata)

    years = []
    anoms = []

    for y in range(1850, 2023):
        years.append(y)
        anoms.append(float(y) / 1000.)

    return ts.TimeSeriesAnnual(years, anoms, metadata=annual_metadata)


def test_get_values(simple_annual):
    copy_annual = copy.deepcopy(simple_annual)
    copy_annual.df.data[0] = 5.0

    values = utils.get_values([simple_annual, copy_annual], 2022)
    assert values[0] == 2022 / 1000.
    assert values[1] == 2022 / 1000.

    values = utils.get_values([simple_annual, copy_annual], 1850)
    assert values[0] == 1850 / 1000.
    assert values[1] == 5.0


def test_get_ranks(simple_annual):
    copy_annual = copy.deepcopy(simple_annual)
    copy_annual.df.data[0] = 5.0

    values = utils.get_ranks([simple_annual, copy_annual], 2022)
    assert values[0] == 1
    assert values[1] == 2

    values = utils.get_ranks([simple_annual, copy_annual], 1850)
    assert values[0] == 2022 - 1850 + 1
    assert values[1] == 1


def test_table_by_year(simple_annual):
    copy_annual = copy.deepcopy(simple_annual)
    copy_annual.df.data[0] = 5.0

    table = utils.table_by_year([simple_annual, copy_annual], 2022)

    for i in range(20):
        line = table[28 * i: 28 * (i + 1)]
        assert line[-1:] == '\n'
        assert line[0:2] == '20'
        assert line[5:8] == '2.0'
        assert line[10] == '('
        assert line[13] == ')'

        assert line[16:19] == '2.0'
        assert line[21] == '('
        assert line[24] == ')'

    assert table[0:28] == '2002 2.00 (21)  2.00 (22)  \n'
    assert table[-28:] == '2022 2.02 ( 1)  2.02 ( 2)  \n'

    table = utils.table_by_year([simple_annual, copy_annual], 2023)
    assert table[-28:] == "2023 _.__ (__)  _.__ (__)  \n"


def test_record_margin_table_by_year(simple_annual):
    copy_annual = copy.deepcopy(simple_annual)
    copy_annual.df.data[0] = 5.0

    table = utils.record_margin_table_by_year([simple_annual, copy_annual], 2022)
    assert table[-28:] == '2022 0.00       ---------  \n'

    table = utils.record_margin_table_by_year([simple_annual, copy_annual], 2023)
    assert table[-28:] == '2023 XXXXXXXXX  XXXXXXXXX  \n'
    print()


def test_run_the_numbers(simple_annual, tmpdir):
    copy_annual = copy.deepcopy(simple_annual)
    copy_annual.df.data[0] = 5.0

    all_datasets = [simple_annual, copy_annual]

    utils.run_the_numbers(all_datasets, 2022, 'test_title', tmpdir)

    assert (tmpdir / 'test_title_2022.txt').exists()


def test_record_margins(simple_annual, tmpdir):
    copy_annual = copy.deepcopy(simple_annual)
    copy_annual.df.data[0] = 5.0

    all_datasets = [simple_annual, copy_annual]

    utils.record_margins(all_datasets, 2022, 'test_title_2', tmpdir)

    assert (tmpdir / 'test_title_2_2022.txt').exists()