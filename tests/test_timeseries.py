import pytest
import numpy as np
import json
import itertools
from pathlib import Path
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
    anoms = []

    for y, m in itertools.product(range(1850, 2023), range(1, 13)):
        years.append(y)
        months.append(m)
        anoms.append(float(y))

    return ts.TimeSeriesMonthly(years, months, anoms)


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
    anoms = []

    for y, m in itertools.product(range(1850, 2023), range(1, 13)):
        years.append(y)
        months.append(m)
        anoms.append(float(m))

    return ts.TimeSeriesMonthly(years, months, anoms)


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


def test_make_annual_by_selecting_month(monthly_data_is_month):
    a = monthly_data_is_month.make_annual_by_selecting_month(1)

    nyears = 2022 - 1850 + 1

    assert isinstance(a, ts.TimeSeriesAnnual)
    for i in range(nyears):
        assert a.df['data'][i] == 1
    assert a.df['year'][0] == 1850
    assert len(a.df['data']) == nyears
    assert a.metadata['history'][-1] == 'Extracted January from each year'


def test_rebaseline_monthly(simple_monthly):
    """Simple rebaselining of monthly series"""
    simple_monthly.rebaseline(1961, 1961)

    for m in range(1, 13):
        assert simple_monthly.df[(simple_monthly.df['year'] == 1850) &
                                 (simple_monthly.df['month'] == m)]['data'][m - 1] == 1850 - 1961
    assert simple_monthly.metadata['history'][-1] == 'Rebaselined to 1961-1961'


def test_rebaseline_annual(simple_monthly):
    annual = simple_monthly.make_annual()
    annual.rebaseline(1981, 2010)
    assert annual.df['data'][0] == (1850 - (1981 + 2010) / 2.)
    assert annual.metadata['history'][-2] == 'Calculated annual average'
    assert annual.metadata['history'][-1] == 'Rebaselined to 1981-2010'


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


def test_ranking_monthly_with_all_keyword(simple_monthly):
    for i in range(21):
        rank = simple_monthly.get_rank_from_year_and_month(2022 - i, 12, all=True)
        assert rank == 12 * i + 1


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


def test_select_year_range(simple_annual):
    chomp = simple_annual.select_year_range(1999, 2011)

    assert isinstance(chomp, ts.TimeSeriesAnnual)
    assert chomp.df['year'][0] == 1999
    assert chomp.df['year'][2011 - 1999] == 2011
