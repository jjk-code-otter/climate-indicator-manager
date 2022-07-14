import pytest
import itertools
import climind.data_types.timeseries as ts


@pytest.fixture
def simple_monthly():
    """
    Produces a monthly time series from 1850 to 2022.
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


def test_creation():
    f = ts.TimeSeriesMonthly([1999, 1999], [1, 2], [2.0, 3.0])


def test_make_annual():
    """Create annual series from monthly series and check history is updated"""
    f = ts.TimeSeriesMonthly([1999, 1999], [1, 2], [2.0, 3.0])
    a = f.make_annual()
    assert isinstance(a, ts.TimeSeriesAnnual)
    assert a.df['data'][0] == 2.5
    assert a.df['year'][0] == 1999
    assert a.metadata['history'][-1] == 'Calculated annual average'


def test_rebaseline_monthly(simple_monthly):
    """Simple rebaselining of monthly series"""
    simple_monthly.rebaseline(1961, 1961)

    for m in range(1, 13):
        assert simple_monthly.df[(simple_monthly.df['year'] == 1850) &
                                 (simple_monthly.df['month'] == m)]['data'][m-1] == 1850 - 1961
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


def test_ranking_annual(simple_annual):
    rank = simple_annual.get_rank_from_year(2022)
    assert rank == 1

    rank = simple_annual.get_rank_from_year(1850)
    assert rank == 2022 - 1850 + 1


def test_ranking_with_ties(simple_annual):
    simple_annual.df['data'][2022 - 1850] = 2021. / 1000.
    rank2 = simple_annual.get_rank_from_year(2022)
    rank1 = simple_annual.get_rank_from_year(2021)
    assert rank1 == rank2
    assert rank1 == 1
    assert rank2 == 1
    rank3 = simple_annual.get_rank_from_year(2020)
    assert rank3 == 3


def test_get_year_from_rank(simple_annual):
    year = simple_annual.get_year_from_rank(1)
    assert len(year) == 1
    assert year[0] == 2022

    year = simple_annual.get_year_from_rank(3)
    assert len(year) == 1
    assert year[0] == 2020
