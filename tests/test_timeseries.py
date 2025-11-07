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

import pandas as pd
import numpy as np
import itertools
from datetime import date
from pathlib import Path
from unittest.mock import call
from climind.data_manager.metadata import DatasetMetadata, CollectionMetadata, CombinedMetadata
import climind.data_types.timeseries as ts


# Fixtures
@pytest.fixture
def simple_irregular(test_metadata):
    test_metadata = copy.deepcopy(test_metadata)
    test_metadata['name'] = 'original'
    test_metadata['time_resolution'] = 'irregular'
    test_metadata['type'] = 'timeseries'

    test_metadata['variable'] = 'sealevel'
    test_metadata['units'] = 'mm'

    number_of_times = 520
    dates = pd.date_range(start='1993-01-01', freq='1W', periods=number_of_times)

    years = dates.year.tolist()
    months = dates.month.tolist()
    days = dates.day.tolist()

    data = []
    uncertainty = []
    for i in range(number_of_times):
        data.append(float(years[i] * 100 + months[i]))
        uncertainty.append(1.37)

    return ts.TimeSeriesIrregular(years, months, days, data, metadata=test_metadata, uncertainty=uncertainty)


@pytest.fixture
def simple_irregular_time_shifted(test_metadata):
    test_metadata = copy.deepcopy(test_metadata)
    test_metadata['name'] = 'shift'
    test_metadata['time_resolution'] = 'irregular'
    test_metadata['type'] = 'timeseries'

    test_metadata['variable'] = 'sealevel'
    test_metadata['units'] = 'mm'

    number_of_times = 520
    dates = pd.date_range(start='1992-01-01', freq='1W', periods=number_of_times)

    years = dates.year.tolist()
    months = dates.month.tolist()
    days = dates.day.tolist()

    data = []
    uncertainty = []
    for i in range(number_of_times):
        data.append(float(years[i] * 100 + months[i]))
        uncertainty.append(1.37)

    return ts.TimeSeriesIrregular(years, months, days, data, metadata=test_metadata, uncertainty=uncertainty)


@pytest.fixture
def daily_irregular(test_metadata):
    test_metadata['time_resolution'] = 'irregular'
    test_metadata['type'] = 'timeseries'

    test_metadata['variable'] = 'antarctic_ice'
    test_metadata['units'] = 'millionkm2'

    number_of_times = 365 * 40 + 10
    dates = pd.date_range(start='1979-01-01', freq='1D', periods=number_of_times)

    years = dates.year.tolist()
    months = dates.month.tolist()
    days = dates.day.tolist()

    data = []
    uncertainty = []
    for i in range(number_of_times):
        data.append(float(years[i] * 100 + months[i]))
        uncertainty.append(1.37)

    return ts.TimeSeriesIrregular(years, months, days, data, metadata=test_metadata, uncertainty=uncertainty)


@pytest.fixture
def simple_monthly(test_metadata):
    """
    Produces a monthly time series from 1850 to 2022. Data for each month are equal to the year in
    which the month falls
    Returns
    -------

    """
    test_metadata = copy.deepcopy(test_metadata)

    years = []
    months = []
    anomalies = []

    for y, m in itertools.product(range(1850, 2023), range(1, 13)):
        years.append(y)
        months.append(m)
        anomalies.append(float(y))

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=test_metadata)


@pytest.fixture
def simple_monthly_time_shifted(test_metadata):
    """
    Produces a monthly time series from 1850 to 2022. Data for each month are equal to the year in
    which the month falls
    Returns
    -------

    """
    test_metadata = copy.deepcopy(test_metadata)

    years = []
    months = []
    anomalies = []

    for y, m in itertools.product(range(1900, 2033), range(1, 13)):
        years.append(y)
        months.append(m)
        anomalies.append(float(y))

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=test_metadata)


@pytest.fixture
def simple_monthly_values_are_months(test_metadata):
    """
    Produces a monthly time series from 1850 to 2022. Data for each month are equal to the year in
    which the month falls
    Returns
    -------

    """
    test_metadata = copy.deepcopy(test_metadata)

    years = []
    months = []
    anomalies = []

    for y, m in itertools.product(range(1850, 2023), range(1, 13)):
        years.append(y)
        months.append(m)
        anomalies.append(float(m))

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=test_metadata)


@pytest.fixture
def uncertainty_monthly(test_metadata):
    """
    Produces a monthly time series from 1850 to 2022. Data for each month are equal to the year in
    which the month falls
    Returns
    -------

    """
    years = []
    months = []
    anomalies = []
    uncertainties = []

    for y, m in itertools.product(range(1850, 2023), range(1, 13)):
        years.append(y)
        months.append(m)
        anomalies.append(float(y))
        uncertainties.append(0.3)

    return ts.TimeSeriesMonthly(years, months, anomalies,
                                metadata=test_metadata, uncertainty=uncertainties)


@pytest.fixture
def monthly_data_is_month(test_metadata):
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

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=test_metadata)


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


@pytest.fixture
def simple_annual_time_shifted(annual_metadata):
    """
    Produces an annual time series from 1850 to 2022.
    Returns
    -------

    """
    annual_metadata = copy.deepcopy(annual_metadata)

    years = []
    anoms = []

    for y in range(1900, 2033):
        years.append(y)
        anoms.append(float(y) / 1000.)

    return ts.TimeSeriesAnnual(years, anoms, metadata=annual_metadata)


@pytest.fixture
def uncertainty_annual(annual_metadata):
    """
    Produces an annual time series from 1850 to 2022.
    Returns
    -------

    """
    years = []
    anoms = []
    uncertainties = []

    for y in range(1850, 2023):
        years.append(y)
        anoms.append(float(y) / 1000.)
        uncertainties.append(0.77)

    return ts.TimeSeriesAnnual(years, anoms,
                               metadata=annual_metadata, uncertainty=uncertainties)


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
def annual_datalist(annual_metadata):
    """
    Produces an annual time series from 1850 to 2022.
    Returns
    -------

    """
    years1 = []
    years2 = []
    years3 = []
    anoms1 = []
    anoms2 = []
    anoms3 = []

    for y in range(1850, 2023):
        years1.append(y)
        anoms1.append(1.0)
    for y in range(1855, 2018):
        years2.append(y)
        anoms2.append(2.0)
    for y in range(1851, 2023):
        years3.append(y)
        anoms3.append(6.0)

    datalist = [ts.TimeSeriesAnnual(years1, anoms1, copy.deepcopy(annual_metadata)),
                ts.TimeSeriesAnnual(years2, anoms2, copy.deepcopy(annual_metadata)),
                ts.TimeSeriesAnnual(years3, anoms3, copy.deepcopy(annual_metadata))]

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
                         'colour': '',
                         'zpos': 99}

    dataset_metadata = DatasetMetadata(attributes)
    collection_metadata = CollectionMetadata(global_attributes)

    return CombinedMetadata(dataset_metadata, collection_metadata)


def test_log_activity(mocker):
    def mini():
        return ''

    m = mocker.patch('logging.info')
    fn = ts.log_activity(mini)
    assert fn() == ''
    m.assert_called_once_with('Running: mini')


def test_log_with_args(mocker, simple_annual):
    def mini(arg1, kw=''):
        return ''

    m = mocker.patch('logging.info')
    fn = ts.log_activity(mini)
    simple_annual.metadata['name'] = 'test_name'
    assert fn(simple_annual, kw='test') == ''

    calls = [call('Running: mini'),
             call('on test_name'),
             call('With arguments:'),
             call('And keyword arguments:')]

    m.assert_has_calls(calls, any_order=True)


# Base TimeSeries class
def test_basic_timeseries_creation_raises_type_error(annual_metadata):
    with pytest.raises(TypeError):
        _ = ts.TimeSeries(metadata=annual_metadata)


# Free-floating functions
def test_make_combined_series(annual_datalist):
    # Found cases where time ordering of the output depended on the order of the lists so
    # test now permutes the input dataset list
    for permutation in list(itertools.permutations(annual_datalist)):
        test_result = ts.make_combined_series(permutation)
        assert len(test_result.metadata['history']) == 6
        assert test_result.df['data'][0] == 1.0
        assert test_result.df['data'][1] == 3.5
        assert test_result.df['data'][2022 - 1850] == 3.5
        assert test_result.df['uncertainty'][5] == np.sqrt((np.sqrt(7.0) * 1.645) ** 2 + 0.12 ** 2)
        for i in range(len(test_result.df)):
            assert test_result.df['year'][i] == 1850 + i


def test_get_list_of_unique_variables(annual_datalist):
    test_list = ts.get_list_of_unique_variables(annual_datalist)

    assert isinstance(test_list, list)
    assert len(test_list) == 1
    assert test_list[0] == 'tas'

    annual_datalist[0].metadata['variable'] = 'ohc'
    test_list = ts.get_list_of_unique_variables(annual_datalist)
    assert isinstance(test_list, list)
    assert len(test_list) == 2
    assert 'tas' in test_list
    assert 'ohc' in test_list


def test_superset(annual_datalist):
    variable_list = ts.get_list_of_unique_variables(annual_datalist)
    test_set = ts.superset_dataset_list(annual_datalist, variable_list)

    assert isinstance(test_set, list)
    assert len(test_set) == 1
    assert len(test_set[0]) == 3

    annual_datalist[0].metadata['variable'] = 'ohc'
    variable_list = ts.get_list_of_unique_variables(annual_datalist)
    test_set = ts.superset_dataset_list(annual_datalist, variable_list)

    assert isinstance(test_set, list)
    assert len(test_set) == 2
    assert len(test_set[0]) == 1
    assert len(test_set[1]) == 2


# Irregular time series
def test_make_monthly(simple_irregular):
    test_monthly = simple_irregular.make_monthly()
    assert isinstance(test_monthly, ts.TimeSeriesMonthly)
    assert test_monthly.df['data'][0] == 199301.
    assert 'Calculated monthly average' in test_monthly.metadata['history'][-1]
    assert test_monthly.metadata['time_resolution'] == 'monthly'
    assert test_monthly.metadata['derived']


def test_update_history_irregular(simple_irregular):
    test_message = 'snoopy is a dog'
    simple_irregular.update_history(test_message)
    assert simple_irregular.metadata['history'][-1] == test_message


def test_irregular_start_and_end_dates(simple_irregular):
    start_date, end_date = simple_irregular.get_start_and_end_dates()

    assert start_date == pd.Timestamp('1993-01-03 00:00:00')
    assert end_date == pd.Timestamp('2002-12-15 00:00:00')


def test_irregular_select_year_range(simple_irregular):
    simple_irregular = simple_irregular.select_year_range(1995, 2000)
    start_date, end_date = simple_irregular.get_start_and_end_dates()

    assert start_date == pd.Timestamp('1995-01-01 00:00:00')
    assert end_date == pd.Timestamp('2000-12-31 00:00:00')


def test_irregular_get_first_and_last_year(simple_irregular):
    start_date, end_date = simple_irregular.get_first_and_last_year()

    assert start_date == 1993
    assert end_date == 2002


def test_generate_dates_irregular(simple_irregular):
    dates = simple_irregular.generate_dates('days since 1993-01-01 00:00:00.0')
    assert dates[0] == 2
    assert dates[1] - dates[0] == 7


def test_write_csv_irregular(simple_irregular, tmpdir):
    test_filename = Path(tmpdir) / 'test_irregular.csv'
    test_metadata_filename = Path(tmpdir) / 'test_irregular_metadata.csv'

    simple_irregular.write_csv(test_filename)
    assert test_filename.exists()

    # check there are no missing lines
    with open(test_filename, 'r') as f:
        for line in f:
            assert line != '\n'

    simple_irregular.write_csv(test_filename, metadata_filename=test_metadata_filename)
    assert test_filename.exists()
    assert test_metadata_filename.exists()


def test_get_year_axis_irregular(simple_irregular):
    test_axis = simple_irregular.get_year_axis()
    assert test_axis[0] == simple_irregular.df['year'][0] + (simple_irregular.df['day'][0] - 1) / 365
    assert test_axis[1] == simple_irregular.df['year'][1] + (simple_irregular.df['day'][1] - 1) / 365
    assert len(test_axis) == len(simple_irregular.df)


def test_get_string_date_range_irregular(simple_irregular):
    test_range = simple_irregular.get_string_date_range()
    assert test_range == '1993.01.03-2002.12.15'


def test_rebaseline(daily_irregular):
    # Data values are YYYYMM so any month's anomaly will be Y1Y100 - Y2Y200 where Y1 is the ob year and Y2 is the
    # climatology average year
    daily_irregular.rebaseline(2004, 2004)
    for i in range(365):
        assert daily_irregular.df.data[i] == 197900. - 200400.

    daily_irregular.rebaseline(2000, 2004)
    for i in range(365):
        assert daily_irregular.df.data[i] == 197900. - (200000. + 200100. + 200200. + 200300. + 200400.) / 5.


# Monthly times series
def test_creation_monthly(test_metadata):
    f = ts.TimeSeriesMonthly([1999, 1999], [1, 2], [2.0, 3.0], metadata=test_metadata)

    assert isinstance(f, ts.TimeSeriesMonthly)
    assert f.df['year'][0] == 1999


def test_creation_monthly_with_metadata(test_metadata):
    f = ts.TimeSeriesMonthly([1999, 1999], [1, 2], [2.0, 3.0], metadata=test_metadata)

    assert isinstance(f, ts.TimeSeriesMonthly)
    assert f.metadata['space_resolution'] == test_metadata['space_resolution']
    assert f.df['year'][0] == 1999


def test_creation_monthly_with_uncertainty(uncertainty_monthly):
    assert 'uncertainty' in uncertainty_monthly.df.columns
    assert uncertainty_monthly.df['uncertainty'][0] == 0.3


def test_make_annual(test_metadata):
    """Create annual series from monthly series and check history is updated"""
    f = ts.TimeSeriesMonthly([1999, 1999], [1, 2], [2.0, 3.0], metadata=test_metadata)
    a = f.make_annual()
    assert isinstance(a, ts.TimeSeriesAnnual)
    assert a.df['data'][0] == 2.5
    assert a.df['year'][0] == 1999
    assert 'Calculated annual average' in a.metadata['history'][-1]


def test_make_annual_cumulative(test_metadata):
    """Create annual series from monthly series and check history is updated"""
    f = ts.TimeSeriesMonthly([1999, 1999], [1, 2], [2.0, 3.0], metadata=test_metadata)
    a = f.make_annual(cumulative=True)
    assert isinstance(a, ts.TimeSeriesAnnual)
    assert a.df['data'][0] == 5.0
    assert a.df['year'][0] == 1999
    assert 'Calculated annual value' in a.metadata['history'][-1]


def test_make_annual_by_selecting_month(monthly_data_is_month):
    a = monthly_data_is_month.make_annual_by_selecting_month(1)

    number_of_years = 2022 - 1850 + 1

    assert isinstance(a, ts.TimeSeriesAnnual)
    for i in range(number_of_years):
        assert a.df['data'][i] == 1
    assert a.df['year'][0] == 1850
    assert len(a.df['data']) == number_of_years
    assert a.metadata['history'][-1] == 'Calculated annual series by extracting January from each year'


def test_rebaseline_monthly(simple_monthly):
    """Simple rebaselining of monthly series"""
    simple_monthly.rebaseline(1961, 1961)

    for m in range(1, 13):
        assert simple_monthly.df[(simple_monthly.df['year'] == 1850) &
                                 (simple_monthly.df['month'] == m)]['data'][m - 1] == 1850 - 1961
    assert 'Rebaselined to 1961-1961' in simple_monthly.metadata['history'][-1]


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


def test_manual_baseline_monthly(simple_monthly):
    simple_monthly.manually_set_baseline(2001, 2030)

    assert simple_monthly.metadata['climatology_start'] == 2001
    assert simple_monthly.metadata['climatology_end'] == 2030


def test_get_value_monthly(simple_monthly):
    for y in range(1850, 2023):
        for m in range(1, 13):
            assert simple_monthly.get_value(y, m) == y


def test_get_uncertainty_monthly(uncertainty_monthly):
    for y in range(1850, 2023):
        for m in range(1, 13):
            assert uncertainty_monthly.get_uncertainty(y, m) == 0.3


def test_get_uncertainty_monthly_no_uncertainty_in_ts(simple_monthly):
    for y in range(1850, 2023):
        for m in range(1, 13):
            assert simple_monthly.get_uncertainty(y, m) is None


def test_get_value_monthly_non_existent_month(simple_monthly, uncertainty_monthly):
    assert simple_monthly.get_value(2072, 3) is None
    assert uncertainty_monthly.get_uncertainty(2072, 3) is None


def test_get_value_monthly_with_duplicate_raises_key_error(simple_monthly, uncertainty_monthly):
    simple_monthly.df['month'][1] = 1
    with pytest.raises(KeyError):
        _ = simple_monthly.get_value(1850, 1)

    uncertainty_monthly.df['month'][1] = 1
    with pytest.raises(KeyError):
        _ = uncertainty_monthly.get_uncertainty(1850, 1)


def test_add_offset_monthly(simple_monthly):
    simple_monthly.add_offset(0.3)
    for i in range(len(simple_monthly.df)):
        assert simple_monthly.df['data'][i] == simple_monthly.df['year'][i] + 0.3


def test_zero_on_month(simple_monthly):
    simple_monthly.zero_on_month(1870, 3)
    for i in range(len(simple_monthly.df)):
        assert simple_monthly.df['data'][i] == simple_monthly.df['year'][i] - 1870.


def test_get_start_and_end_dates(simple_monthly):
    start_date, end_date = simple_monthly.get_start_and_end_dates()

    assert start_date.year == 1850
    assert start_date.month == 1

    assert end_date.year == 2022
    assert end_date.month == 12


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
            assert 'history,G,"step1"history,G,"step2"' not in line
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


def test_select_year_range_monthly(simple_monthly):
    chomp = simple_monthly.select_year_range(1999, 2011)

    assert isinstance(chomp, ts.TimeSeriesMonthly)
    assert chomp.df['year'][0] == 1999
    assert chomp.df['year'][12 * (2011 - 1999)] == 2011


def test_make_monthly_from_df(simple_monthly):
    df = simple_monthly.df
    metadata = simple_monthly.metadata

    test_ds = ts.TimeSeriesMonthly.make_from_df(df, metadata)

    assert 'uncertainty' not in test_ds.df.columns


def test_make_monthly_from_df_with_uncertainty(uncertainty_monthly):
    df = uncertainty_monthly.df
    metadata = uncertainty_monthly.metadata

    test_ds = ts.TimeSeriesMonthly.make_from_df(df, metadata)

    assert 'uncertainty' in test_ds.df.columns


def test_get_year_axis_monthly(simple_monthly):
    test_axis = simple_monthly.get_year_axis()

    assert test_axis[0] == 1850.0
    assert test_axis[(2022 - 1850 + 1) * 12 - 1] == 2022.0 + 11. / 12.


def test_get_string_date_range_monthly(simple_monthly):
    test_range = simple_monthly.get_string_date_range()
    assert test_range == '1850.01-2022.12'


def test_calculate_climatology(simple_monthly_values_are_months):
    test_climatology = simple_monthly_values_are_months.calculate_climatology(1991, 2020)

    for month in range(1, 13):
        assert test_climatology.month[month - 1] == month
        assert test_climatology.climatology[month - 1] == float(month)



def test_running_mean_monthly(simple_monthly_values_are_months):
    test_running = simple_monthly_values_are_months.running_mean(12)
    assert test_running.df.data[11] == np.mean([x for x in range(1, 13)])
    # First 11 entries are NaNs for a 12-month running average
    for i in range(11):
        assert np.isnan(test_running.df.data[i])

    test_running = simple_monthly_values_are_months.running_mean(6)
    assert test_running.df.data[5] == np.mean([x for x in range(1, 7)])
    # First 5 entries are NaNs for a 6-month running average
    for i in range(5):
        assert np.isnan(test_running.df.data[i])


def test_running_mean_centred_monthly(simple_monthly_values_are_months):
    test_running = simple_monthly_values_are_months.running_mean(12, centred=True)

    assert test_running.df.data[11] == np.mean([x for x in range(1, 13)])
    assert test_running.df.year[11] == 1850

    test_running = simple_monthly_values_are_months.running_mean(24, centred=True)
    assert test_running.df.data[23] == np.mean([x for x in range(1, 13)])
    assert test_running.df.year[23] == 1850.5


# Annual tests
def test_record_margins(simple_annual):
    margins = simple_annual.record_margins()

    # first element is nan
    assert np.isnan(margins.df.data[0])

    for i in range(1, len(margins.df.data)):
        assert pytest.approx(1 / 1000, 0.0001) == margins.df.data[i]


def test_record_margins_negative(simple_annual):
    simple_annual.df.data = -1 * simple_annual.df.data
    margins = simple_annual.record_margins()

    # first element is nan
    assert np.isnan(margins.df.data[0])

    for i in range(1, len(margins.df.data)):
        assert pytest.approx(-1 / 1000, 0.0001) == margins.df.data[i]


def test_record_margins_with_nonrecord(simple_annual):
    simple_annual.df.data[120] = simple_annual.df.data[118]
    margins = simple_annual.record_margins()

    # first element is nan
    assert np.isnan(margins.df.data[0])

    for i in range(1, len(margins.df.data)):
        if i == 120:
            assert np.isnan(margins.df.data[i])
        elif i == 121:
            assert pytest.approx(2 / 1000, 0.0001) == margins.df.data[i]
        else:
            assert pytest.approx(1 / 1000, 0.0001) == margins.df.data[i]


def test_make_from_df(uncertainty_annual):
    annual = ts.TimeSeriesAnnual.make_from_df(uncertainty_annual.df, uncertainty_annual.metadata)
    assert isinstance(annual, ts.TimeSeriesAnnual)
    assert 'uncertainty' in annual.df.columns
    assert annual.df['uncertainty'][0] == 0.77


def test_annual_with_uncertainty(uncertainty_annual):
    assert 'uncertainty' in uncertainty_annual.df.columns
    assert uncertainty_annual.df['uncertainty'][0] == 0.77


def test_rebaseline_annual(simple_monthly):
    annual = simple_monthly.make_annual()
    annual.rebaseline(1981, 2010)
    assert annual.df['data'][0] == (1850 - (1981 + 2010) / 2.)
    assert 'Calculated annual average' in annual.metadata['history'][-2]
    assert 'Rebaselined to 1981-2010' in annual.metadata['history'][-1]


def test_manual_baseline_annual(simple_annual):
    simple_annual.manually_set_baseline(2001, 2030)
    assert simple_annual.metadata['climatology_start'] == 2001
    assert simple_annual.metadata['climatology_end'] == 2030


def test_multiple_steps(simple_monthly):
    """Test that consecutive operations appear in the history attribute"""
    simple_monthly.rebaseline(1961, 1990)
    annual = simple_monthly.make_annual()

    assert 'Calculated annual average' in annual.metadata['history'][-1]
    assert 'Rebaselined to 1961-1990' in annual.metadata['history'][-2]


def test_get_value_from_year(simple_annual):
    val = simple_annual.get_value_from_year(2022)
    assert val == 2022 / 1000.


def test_get_uncertainty_from_year(uncertainty_annual):
    val = uncertainty_annual.get_uncertainty_from_year(2022)
    assert val == 0.77


def test_get_uncertainty_from_ts_with_no_uncertainty(simple_annual):
    val = simple_annual.get_uncertainty_from_year(2022)
    assert val is None


def test_get_value_from_year_no_match(simple_annual):
    val = simple_annual.get_value_from_year(2055)
    assert val is None


def test_get_uncertainty_from_year_no_match(uncertainty_annual):
    val = uncertainty_annual.get_uncertainty_from_year(2055)
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


def test_rolling_average_centre(simple_annual):
    ma = simple_annual.running_mean(10, centred=True)

    assert isinstance(ma, ts.TimeSeriesAnnual)
    assert ma.metadata['derived']
    assert ma.metadata['history'] != ''
    assert ma.df['data'][2022 - 1850] == np.mean(np.arange(2022 - 9, 2023)) / 1000.
    assert ma.df['year'][2022 - 1850] == np.mean(np.arange(2022 - 9, 2023))


def test_rolling_average_stdev(simple_annual):
    ma = simple_annual.running_stdev(10)

    assert isinstance(ma, ts.TimeSeriesAnnual)
    assert ma.metadata['derived']
    assert ma.metadata['history'] != ''
    assert pytest.approx(np.std(np.arange(2022 - 9, 2023), ddof=1) / 1000.) == ma.df['data'][2022 - 1850]


def test_rolling_average_stdev_centre(simple_annual):
    ma = simple_annual.running_stdev(10, centred=True)

    assert isinstance(ma, ts.TimeSeriesAnnual)
    assert ma.metadata['derived']
    assert ma.metadata['history'] != ''
    assert pytest.approx(np.std(np.arange(2022 - 9, 2023), ddof=1) / 1000.) == ma.df['data'][2022 - 1850]
    assert ma.df['year'][2022 - 1850] == np.mean(np.arange(2022 - 9, 2023))


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


def test_write_simple_csv(simple_annual, test_metadata, tmpdir):
    simple_annual.metadata = test_metadata
    simple_annual.manually_set_baseline(1901, 2000)
    test_filename = Path(tmpdir) / 'test.csv'
    simple_annual.write_simple_csv(test_filename)

    assert test_filename.exists()


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


def test_write_csv_annual_with_uncertainty(uncertainty_annual, tmpdir):
    uncertainty_annual.manually_set_baseline(1901, 2000)
    test_filename = Path(tmpdir) / 'test.csv'
    uncertainty_annual.write_csv(test_filename)

    assert test_filename.exists()

    found_it = False
    with open(test_filename, 'r') as f:
        for line in f:
            if 'time,year,data,uncertainty' in line:
                found_it = True

    assert found_it


def test_get_year_axis_annual(simple_annual):
    test_axis = simple_annual.get_year_axis()
    for i in range(len(test_axis)):
        assert test_axis[i] == simple_annual.df['year'][i]


def test_get_string_date_range_annual(simple_annual):
    test_range = simple_annual.get_string_date_range()
    assert test_range == '1850-2022'


def test_time_average(simple_annual):
    test_climatology = simple_annual.time_average(1991, 2020)
    assert test_climatology == np.mean([x for x in range(1991,2021)]) / 1000.


def test_running_trend(simple_annual):
    test_moving_average = simple_annual.running_trend(10)
    for i in range(9):
        assert np.isnan(test_moving_average.df.data[i])
    assert test_moving_average.df.data[9] == pytest.approx(1859.0/1000.0, 0.00001)

def test_running_lowess(simple_annual):
    test_moving_average = simple_annual.running_lowess()
    for i in range(10):
        assert np.isnan(test_moving_average.df.data[i])
    assert test_moving_average.df.data[10] == pytest.approx(1860.0/1000.0, 0.00001)

def test_lowess(simple_annual):
    test_moving_average = simple_annual.lowess()
    for i in range(173):
        assert test_moving_average.df.data[i] == pytest.approx((i+1850)/1000.0, 0.00001)


def test_add_year(simple_annual, uncertainty_annual):
    test_year = 2023
    test_value = 3.987
    test_uncertainty = 0.77

    assert simple_annual.get_value_from_year(test_year) is None
    assert uncertainty_annual.get_value_from_year(test_year) is None

    simple_annual.add_year(test_year, test_value)
    assert simple_annual.get_value_from_year(test_year) == test_value

    uncertainty_annual.add_year(test_year, test_value, test_uncertainty)
    assert uncertainty_annual.get_value_from_year(test_year) == test_value
    assert uncertainty_annual.get_uncertainty_from_year(test_year) == test_uncertainty


def test_add_year_year_already_exists_raises_warning(simple_annual, uncertainty_annual):
    test_year = 2020
    test_value = 3.987
    test_uncertainty = 0.77

    with pytest.warns():
        simple_annual.add_year(test_year, test_value)
    with pytest.warns():
        uncertainty_annual.add_year(test_year, test_value)


def test_write_dataset_summary_file(simple_annual, simple_annual_time_shifted, tmpdir):
    # Returns None with no file creation if there list is empty
    all_datasets = []
    filename = tmpdir / 'test.csv'
    df = ts.write_dataset_summary_file(all_datasets, filename)
    assert df is None
    assert not (filename.exists())

    simple_annual.metadata['name'] = 'one'
    simple_annual_time_shifted.metadata['name'] = 'two'

    # Creates a file if the list is not empty
    all_datasets = [simple_annual, simple_annual_time_shifted]
    filename = tmpdir / 'test.csv'
    df = ts.write_dataset_summary_file(all_datasets, filename)
    assert isinstance(df, pd.DataFrame)
    assert filename.exists()

    # Check file contents are as expected
    with open(filename) as f:
        line = f.readline()
        assert line == 'year,one,two\n'
        line = f.readline()
        assert line == '1850,1.8500,\n'
        last_line = f.readlines()[-1]
        assert last_line == '2032,,2.0320\n'


def test_write_dataset_summary_file_monthly(simple_monthly, simple_monthly_time_shifted, tmpdir):
    simple_monthly.metadata['name'] = 'one'
    simple_monthly_time_shifted.metadata['name'] = 'two'

    # Creates a file if the list is not empty
    all_datasets = [simple_monthly, simple_monthly_time_shifted]
    filename = tmpdir / 'test_monthly.csv'
    df = ts.write_dataset_summary_file(all_datasets, filename)
    assert isinstance(df, pd.DataFrame)
    assert filename.exists()

    # Check file contents are as expected
    with open(filename) as f:
        line = f.readline()
        assert line == 'year,month,one,two\n'
        line = f.readline()
        assert line == '1850,1,1850.0000,\n'
        last_line = f.readlines()[-1]
        assert last_line == '2032,12,,2032.0000\n'


def test_write_dataset_summary_file_irregular(simple_irregular, tmpdir):
    simple_irregular.metadata['name'] = 'one'
    all_datasets = [simple_irregular]
    filename = tmpdir / 'test_irregular.csv'
    df = ts.write_dataset_summary_file(all_datasets, filename)
    assert df is None
    assert not (filename.exists())


def test_equalise_irregular_datasets(simple_irregular, simple_irregular_time_shifted):
    time_units = 'days since 1800-01-01 00:00:00.0'
    simple_irregular.df['time'] = simple_irregular.generate_dates(time_units)
    simple_irregular_time_shifted.df['time'] = simple_irregular_time_shifted.generate_dates(time_units)

    combined = [simple_irregular, simple_irregular_time_shifted]
    equalised_combo = ts.equalise_datasets(combined)

    assert isinstance(equalised_combo, pd.DataFrame)
    assert len(equalised_combo) == 520 + 52
    assert equalised_combo['year'][0] == 1992
    assert equalised_combo['year'][520 + 52 - 1] == 2002


def test_equalise_monthly_datasets(simple_monthly, simple_monthly_time_shifted):
    time_units = 'days since 1800-01-01 00:00:00.0'
    simple_monthly.df['time'] = simple_monthly.generate_dates(time_units)
    simple_monthly_time_shifted.df['time'] = simple_monthly_time_shifted.generate_dates(time_units)

    combined = [simple_monthly, simple_monthly_time_shifted]
    equalised_combo = ts.equalise_datasets(combined)

    assert isinstance(equalised_combo, pd.DataFrame)
    assert len(equalised_combo) == 12 * (2032 - 1850 + 1)
    assert equalised_combo['year'][0] == 1850
    assert equalised_combo['year'][12 * (2032 - 1850 + 1) - 1] == 2032


def test_create_common_dataframe_raises_error_with_no_flags_set():
    with pytest.raises(ValueError):
        ts.create_common_dataframe([])


def test_equalise_annual_datasets(simple_annual, simple_annual_time_shifted):
    time_units = 'days since 1800-01-01 00:00:00.0'
    simple_annual.df['time'] = simple_annual.generate_dates(time_units)
    simple_annual_time_shifted.df['time'] = simple_annual_time_shifted.generate_dates(time_units)

    combined = [simple_annual, simple_annual_time_shifted]
    equalised_combo = ts.equalise_datasets(combined)

    assert isinstance(equalised_combo, pd.DataFrame)
    assert len(equalised_combo) == 2032 - 1850 + 1
    assert equalised_combo['year'][0] == 1850
    assert equalised_combo['year'][2032 - 1850] == 2032


def test_equalise_single_dataset(simple_annual):
    time_units = 'days since 1800-01-01 00:00:00.0'
    simple_annual.df['time'] = simple_annual.generate_dates(time_units)

    combined = [simple_annual]
    equalised_combo = ts.equalise_datasets(combined)

    assert isinstance(equalised_combo, pd.DataFrame)
    assert len(equalised_combo) == len(simple_annual.df)
    assert equalised_combo['year'][0] == 1850
    assert equalised_combo['year'][2022 - 1850] == 2022


def test_write_dataset_summary_file_with_metadata(simple_annual, simple_annual_time_shifted, tmpdir):
    simple_annual.metadata['name'] = 'one'
    simple_annual_time_shifted.metadata['name'] = 'two'
    filename = tmpdir / 'test.csv'
    all_datasets = [simple_annual, simple_annual_time_shifted]

    ts.write_dataset_summary_file_with_metadata(all_datasets, filename)

    assert filename.exists()

    line = ''
    with open(filename, 'r') as f:
        while line != 'data\n':
            line = f.readline()

        column_names = f.readline()
        assert column_names == 'time,year,one,two\n'

        first_data = f.readline()
        assert first_data == '18262,1850,1.8500,\n'
        last_line = f.readlines()[-1]
        assert last_line == 'end data\n'


def test_write_dataset_summary_file_with_metadata_monthly(simple_monthly, simple_monthly_time_shifted, tmpdir):
    simple_monthly.metadata['name'] = 'one'
    simple_monthly_time_shifted.metadata['name'] = 'two'
    filename = tmpdir / 'test.csv'
    all_datasets = [simple_monthly, simple_monthly_time_shifted]

    ts.write_dataset_summary_file_with_metadata(all_datasets, filename)

    assert filename.exists()

    line = ''
    with open(filename, 'r') as f:
        while line != 'data\n':
            line = f.readline()

        column_names = f.readline()
        assert column_names == 'time,year,month,one,two\n'

        first_data = f.readline()
        assert first_data == '18262,1850,1,1850.0000,\n'

        last_line = f.readlines()[-1]
        assert last_line == 'end data\n'


def test_write_dataset_summary_file_with_metadata_irregular(simple_irregular, simple_irregular_time_shifted, tmpdir):
    simple_irregular.metadata['name'] = 'one'
    simple_irregular_time_shifted.metadata['name'] = 'two'
    filename = tmpdir / 'test.csv'
    all_datasets = [simple_irregular, simple_irregular_time_shifted]

    ts.write_dataset_summary_file_with_metadata(all_datasets, filename)

    assert filename.exists()

    line = ''
    with open(filename, 'r') as f:
        while line != 'data\n':
            line = f.readline()

        column_names = f.readline()
        assert column_names == 'time,year,month,day,one,two\n'

        first_data = f.readline()
        assert first_data == '70130,1992,1,5,,199201.0000\n'

        last_line = f.readlines()[-1]
        assert last_line == 'end data\n'


def test_averages_collection(simple_annual):
    annual1 = copy.deepcopy(simple_annual)
    annual1.df['data'] = -1.0

    annual2 = copy.deepcopy(simple_annual)
    annual2.df['data'] = 1.0

    ac = ts.AveragesCollection([annual1, annual2])

    assert ac.averages[0] == -1.0
    assert ac.averages[1] == 1.0

    assert ac.stdevs[0] == 0.0
    assert ac.stdevs[1] == 0.0

    assert ac.count() == 2
    assert ac.best_estimate() == 0.0
    assert ac.lower_range() == -1.0
    assert ac.upper_range() == 1.0
    assert ac.range() == 2.0

    ac.expand = True

    assert ac.count() == 2
    assert ac.best_estimate() == 0.0
    assert ac.lower_range() == -1.0
    assert ac.upper_range() == 1.0
    assert ac.range() == 2.0

    ac.widest = True

    assert ac.count() == 2
    assert ac.best_estimate() == 0.0
    assert ac.lower_range() == -1.0
    assert ac.upper_range() == 1.0
    assert ac.range() == 2.0
