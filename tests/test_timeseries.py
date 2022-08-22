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
import numpy as np
import json
import itertools
from pathlib import Path
from climind.data_manager.metadata import DatasetMetadata, CollectionMetadata, CombinedMetadata
import climind.data_types.timeseries as ts


@pytest.fixture
def simple_monthly():
    """
    Produces a monthly time series from 1850 to 2022. Data for each month are equal to the year in
    which the month falls
    Returns
    -------

    """
    years = []
    months = []
    anomalies = []

    for y, m in itertools.product(range(1850, 2023), range(1, 13)):
        years.append(y)
        months.append(m)
        anomalies.append(float(y))

    return ts.TimeSeriesMonthly(years, months, anomalies)


@pytest.fixture
def monthly_data_is_month():
    """
    Produces a monthly time series from 1850 to 2022. Data for each month are equal to the year in
    which the month falls
    Returns
    -------

    """
    years = []
    months = []
    anomalies = []

    for y, m in itertools.product(range(1850, 2023), range(1, 13)):
        years.append(y)
        months.append(m)
        anomalies.append(float(m))

    return ts.TimeSeriesMonthly(years, months, anomalies)


@pytest.fixture
def simple_annual():
    """
    Produces an annual time series from 1850 to 2022.
    Returns
    -------

    """
    years = []
    anoms = []

    for y in range(1850, 2023):
        years.append(y)
        anoms.append(float(y) / 1000.)

    return ts.TimeSeriesAnnual(years, anoms)


def test_creation_monthly():
    f = ts.TimeSeriesMonthly([1999, 1999], [1, 2], [2.0, 3.0])

    assert isinstance(f, ts.TimeSeriesMonthly)
    assert f.df['year'][0] == 1999


def test_creation_monthly_with_metadata():
    with open(Path('test_data') / 'gistemp.json') as f:
        collection_metadata = json.load(f)
    metadata = collection_metadata['datasets'][1]

    f = ts.TimeSeriesMonthly([1999, 1999], [1, 2], [2.0, 3.0], metadata=metadata)

    assert isinstance(f, ts.TimeSeriesMonthly)
    assert f.metadata['space_resolution'] == 999
    assert f.df['year'][0] == 1999


def test_make_annual():
    """Create annual series from monthly series and check history is updated"""
    f = ts.TimeSeriesMonthly([1999, 1999], [1, 2], [2.0, 3.0])
    a = f.make_annual()
    assert isinstance(a, ts.TimeSeriesAnnual)
    assert a.df['data'][0] == 2.5
    assert a.df['year'][0] == 1999
    assert a.metadata['history'][-1] == 'Calculated annual average'


def test_make_annual_cumulative():
    """Create annual series from monthly series and check history is updated"""
    f = ts.TimeSeriesMonthly([1999, 1999], [1, 2], [2.0, 3.0])
    a = f.make_annual(cumulative=True)
    assert isinstance(a, ts.TimeSeriesAnnual)
    assert a.df['data'][0] == 5.0
    assert a.df['year'][0] == 1999
    assert a.metadata['history'][-1] == 'Calculated annual average'


def test_make_annual_by_selecting_month(monthly_data_is_month):
    a = monthly_data_is_month.make_annual_by_selecting_month(1)

    number_of_years = 2022 - 1850 + 1

    assert isinstance(a, ts.TimeSeriesAnnual)
    for i in range(number_of_years):
        assert a.df['data'][i] == 1
    assert a.df['year'][0] == 1850
    assert len(a.df['data']) == number_of_years
    assert a.metadata['history'][-1] == 'Extracted January from each year'


def test_rebaseline_monthly(simple_monthly):
    """Simple rebaselining of monthly series"""
    simple_monthly.rebaseline(1961, 1961)

    for m in range(1, 13):
        assert simple_monthly.df[(simple_monthly.df['year'] == 1850) &
                                 (simple_monthly.df['month'] == m)]['data'][m - 1] == 1850 - 1961
    assert simple_monthly.metadata['history'][-1] == 'Rebaselined to 1961-1961'


def test_select_year_range_subset(simple_monthly):
    test_ts = simple_monthly.select_year_range(1903, 1981)
    assert test_ts.df['year'][0] == 1903
    assert test_ts.df['year'][len(test_ts.df) - 1] == 1981


def test_select_year_range_finish_after(simple_monthly):
    test_ts = simple_monthly.select_year_range(1903, 2099)
    assert test_ts.df['year'][0] == 1903
    assert test_ts.df['year'][len(test_ts.df) - 1] == 2022


def test_select_year_range_start_before(simple_monthly):
    test_ts = simple_monthly.select_year_range(1755, 1981)
    assert test_ts.df['year'][0] == 1850
    assert test_ts.df['year'][len(test_ts.df) - 1] == 1981


# Annual

def test_manual_baseline_monthly(simple_monthly):
    simple_monthly.manually_set_baseline(2001, 2030)

    assert simple_monthly.metadata['climatology_start'] == 2001
    assert simple_monthly.metadata['climatology_end'] == 2030


def test_get_value_monthly(simple_monthly):
    for y in range(1850, 2023):
        for m in range(1, 13):
            assert simple_monthly.get_value(y, m) == y


def test_get_value_monthly_non_existent_month(simple_monthly):
    assert simple_monthly.get_value(2072, 3) is None


def test_get_value_monthly_with_duplicate_raises_key_error(simple_monthly):
    simple_monthly.df['month'][1] = 1
    with pytest.raises(KeyError):
        _ = simple_monthly.get_value(1850, 1)


def test_add_offset_monthly(simple_monthly):
    simple_monthly.add_offset(0.3)
    for i in range(len(simple_monthly.df)):
        assert simple_monthly.df['data'][i] == simple_monthly.df['year'][i] + 0.3


def test_zero_on_month(simple_monthly):
    simple_monthly.zero_on_month(1870, 3)
    for i in range(len(simple_monthly.df)):
        assert simple_monthly.df['data'][i] == simple_monthly.df['year'][i] - 1870.


# Annual tests

def test_rebaseline_annual(simple_monthly):
    annual = simple_monthly.make_annual()
    annual.rebaseline(1981, 2010)
    assert annual.df['data'][0] == (1850 - (1981 + 2010) / 2.)
    assert annual.metadata['history'][-2] == 'Calculated annual average'
    assert annual.metadata['history'][-1] == 'Rebaselined to 1981-2010'


def test_manual_baseline_annual(simple_annual):
    simple_annual.manually_set_baseline(2001, 2030)
    assert simple_annual.metadata['climatology_start'] == 2001
    assert simple_annual.metadata['climatology_end'] == 2030


def test_multiple_steps(simple_monthly):
    """Test that consecutive operations appear in the history attribute"""
    simple_monthly.rebaseline(1961, 1990)
    annual = simple_monthly.make_annual()

    assert annual.metadata['history'][-1] == 'Calculated annual average'
    assert annual.metadata['history'][-2] == 'Rebaselined to 1961-1990'


def test_get_value_from_year(simple_annual):
    val = simple_annual.get_value_from_year(2022)
    assert val == 2022 / 1000.


def test_get_value_from_year_no_match(simple_annual):
    val = simple_annual.get_value_from_year(2055)
    assert val is None


def test_ranking_annual(simple_annual):
    rank = simple_annual.get_rank_from_year(2022)
    assert rank == 1

    rank = simple_annual.get_rank_from_year(1850)
    assert rank == 2022 - 1850 + 1


def test_ranking_annual_no_match(simple_annual):
    rank = simple_annual.get_rank_from_year(2029)
    assert rank is None


def test_ranking_with_ties_annual(simple_annual):
    simple_annual.df['data'][2022 - 1850] = 2021. / 1000.
    rank2 = simple_annual.get_rank_from_year(2022)
    rank1 = simple_annual.get_rank_from_year(2021)
    assert rank1 == rank2
    assert rank1 == 1
    assert rank2 == 1
    rank3 = simple_annual.get_rank_from_year(2020)
    assert rank3 == 3


def test_get_year_from_rank_annual(simple_annual):
    year = simple_annual.get_year_from_rank(1)
    assert len(year) == 1
    assert year[0] == 2022

    year = simple_annual.get_year_from_rank(3)
    assert len(year) == 1
    assert year[0] == 2020


def test_ranking_monthly(simple_monthly):
    for i in range(21):
        rank = simple_monthly.get_rank_from_year_and_month(2022 - i, 12)
        assert rank == i + 1


def test_ranking_monthly_with_non_existent_date_returns_none(simple_monthly):
    assert simple_monthly.get_rank_from_year_and_month(2099, 3) is None


def test_ranking_monthly_with_all_keyword(simple_monthly):
    for i in range(21):
        rank = simple_monthly.get_rank_from_year_and_month(2022 - i, 12, versus_all_months=True)
        assert rank == 12 * i + 1


def test_get_year_range_monthly(simple_monthly):
    first_year, last_year = simple_monthly.get_first_and_last_year()
    assert first_year == 1850
    assert last_year == 2022


def test_get_year_range_annual(simple_annual):
    first_year, last_year = simple_annual.get_first_and_last_year()
    assert first_year == 1850
    assert last_year == 2022


def test_rolling_average(simple_annual):
    ma = simple_annual.running_mean(10)

    assert isinstance(ma, ts.TimeSeriesAnnual)
    assert ma.metadata['derived']
    assert ma.metadata['history'] != ''
    assert ma.df['data'][2022 - 1850] == np.mean(np.arange(2022 - 9, 2023)) / 1000.


def test_add_offset(simple_annual):
    simple_annual.add_offset(99.)
    assert simple_annual.df['data'][0] == 1850. / 1000. + 99.

    simple_annual.add_offset(-13.)
    assert simple_annual.df['data'][2022 - 1850] == 2022. / 1000. + 99. - 13.

    simple_annual.add_offset(0.)
    assert simple_annual.df['data'][2022 - 1850] == 2022. / 1000. + 99. - 13.


def test_select_decade(simple_annual):
    simple_decade = simple_annual.select_decade()

    assert simple_decade.df['year'][0] == 1850
    assert simple_decade.df['year'][17] == 2020

    assert simple_decade.metadata['derived']
    assert simple_decade.metadata['history'] != ''


def test_select_decade_nonzero_end(simple_annual):
    simple_decade = simple_annual.select_decade(end_year=5)

    assert simple_decade.df['year'][0] == 1855
    assert simple_decade.df['year'][16] == 2015

    assert simple_decade.metadata['derived']
    assert simple_decade.metadata['history'] != ''


def test_select_year_range_annual(simple_annual):
    chomp = simple_annual.select_year_range(1999, 2011)

    assert isinstance(chomp, ts.TimeSeriesAnnual)
    assert chomp.df['year'][0] == 1999
    assert chomp.df['year'][2011 - 1999] == 2011


def test_select_year_range_monthly(simple_monthly):
    chomp = simple_monthly.select_year_range(1999, 2011)

    assert isinstance(chomp, ts.TimeSeriesMonthly)
    assert chomp.df['year'][0] == 1999
    assert chomp.df['year'][12 * (2011 - 1999)] == 2011


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
                  'history': [],
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher'}

    global_attributes = {'name': '',
                         'version': '',
                         'variable': 'ohc',
                         'units': 'zJ',
                         'citation': [''],
                         'data_citation': [''],
                         'colour': '',
                         'zpos': 99}

    dataset_metadata = DatasetMetadata(attributes)
    collection_metadata = CollectionMetadata(global_attributes)

    return CombinedMetadata(dataset_metadata, collection_metadata)


def test_write_csv_monthly(simple_monthly, test_metadata, tmpdir):
    simple_monthly.metadata = test_metadata
    simple_monthly.manually_set_baseline(1901, 2000)
    test_filename = Path(tmpdir) / 'test.csv'
    simple_monthly.write_csv(test_filename)

    assert test_filename.exists()


def test_write_csv_monthly_no_runon_line(simple_monthly, test_metadata, tmpdir):
    """ make your bugs into tests - make sure there are no missing lines or run-on lines """
    simple_monthly.metadata = test_metadata
    simple_monthly.manually_set_baseline(1901, 2000)
    test_filename = Path(tmpdir) / 'test.csv'
    simple_monthly.write_csv(test_filename)

    with open(test_filename, 'r') as f:
        for line in f:
            assert line != 'type,month,intlong_name,data,ohc,zJ\n'
            assert line != '\n'


def test_write_csv_monthly_with_metadata(simple_monthly, test_metadata, tmpdir):
    simple_monthly.metadata = test_metadata
    simple_monthly.manually_set_baseline(1901, 2000)
    test_filename = Path(tmpdir) / 'test.csv'
    test_metadata_filename = Path(tmpdir) / 'test_metadata.json'
    simple_monthly.write_csv(test_filename, metadata_filename=test_metadata_filename)

    assert test_filename.exists()
    assert test_metadata_filename.exists()


def test_write_csv_annual(simple_annual, test_metadata, tmpdir):
    simple_annual.metadata = test_metadata
    simple_annual.manually_set_baseline(1901, 2000)
    test_filename = Path(tmpdir) / 'test.csv'
    simple_annual.write_csv(test_filename)

    assert test_filename.exists()


def test_write_csv_annual_no_blank_lines(simple_annual, test_metadata, tmpdir):
    simple_annual.metadata = test_metadata
    simple_annual.manually_set_baseline(1901, 2000)
    test_filename = Path(tmpdir) / 'test.csv'
    simple_annual.write_csv(test_filename)

    with open(test_filename, 'r') as f:
        for line in f:
            assert line != '\n'


def test_write_csv_annual_with_metadata(simple_annual, test_metadata, tmpdir):
    simple_annual.metadata = test_metadata
    simple_annual.manually_set_baseline(1901, 2000)
    test_filename = Path(tmpdir) / 'test.csv'
    test_metadata_filename = Path(tmpdir) / 'test_metadata.json'
    simple_annual.write_csv(test_filename, metadata_filename=test_metadata_filename)

    assert test_filename.exists()
    assert test_metadata_filename.exists()
