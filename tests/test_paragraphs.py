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
import itertools
import numpy as np
import climind.data_types.timeseries as ts
import climind.stats.paragraphs as pg
from climind.data_manager.metadata import CombinedMetadata, CollectionMetadata, DatasetMetadata


@pytest.fixture
def test_dataset_attributes():
    attributes = {'url': ['test_url'],
                  'filename': ['test_filename'],
                  'type': 'gridded',
                  'time_resolution': 'monthly',
                  'space_resolution': 999,
                  'climatology_start': 1961,
                  'climatology_end': 1990,
                  'actual': False,
                  'derived': False,
                  'history': [],
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher'
                  }

    return attributes


@pytest.fixture
def test_collection_attributes():
    attributes = {"name": "HadCRUT5",
                  "display_name": "HadCRUT5",
                  "version": "5.0.1.0",
                  "variable": "tas",
                  "units": "degC",
                  "citation": [
                      f"Morice, C.P., J.J. Kennedy, N.A. Rayner, J.P. Winn, E. Hogan, R.E. Killick, "
                      f"R.J.H. Dunn, T.J. Osborn, P.D. Jones and I.R. Simpson (in press) An updated "
                      f"assessment of near-surface temperature change from 1850: the HadCRUT5 dataset. "
                      f"Journal of Geophysical Research (Atmospheres) doi:10.1029/2019JD032361"],
                  "data_citation": [""],
                  "colour": "#444444",
                  "zpos": 99}

    return attributes


@pytest.fixture
def simple_monthly(test_dataset_attributes, test_collection_attributes):
    """
    Produces a monthly time series from 1850 to 2022. Data for each month are equal to the year in
    which the month falls
    Returns
    -------

    """
    metadata = CombinedMetadata(DatasetMetadata(test_dataset_attributes),
                                CollectionMetadata(test_collection_attributes))
    years = []
    months = []
    anomalies = []

    for y, m in itertools.product(range(1850, 2023), range(1, 13)):
        years.append(y)
        months.append(m)
        anomalies.append(float(y))

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata)


@pytest.fixture
def simple_annual(test_dataset_attributes, test_collection_attributes):
    """
    Produces an annual time series from 1850 to 2022.
    Returns
    -------

    """
    metadata = CombinedMetadata(DatasetMetadata(test_dataset_attributes),
                                CollectionMetadata(test_collection_attributes))
    years = []
    anoms = []
    for y in range(1850, 2023):
        years.append(y)
        anoms.append(float(y) / 1000.)
    return ts.TimeSeriesAnnual(years, anoms, metadata)


@pytest.fixture
def simple_annual_descending(test_dataset_attributes, test_collection_attributes):
    """
    Produces an annual time series from 1850 to 2022.
    Returns
    -------

    """
    metadata = CombinedMetadata(DatasetMetadata(test_dataset_attributes),
                                CollectionMetadata(test_collection_attributes))
    years = []
    anoms = []
    for y in range(1850, 2023):
        years.append(y)
        anoms.append(float(2022 - y) / 1000.)
    return ts.TimeSeriesAnnual(years, anoms, metadata)


def test_rank_ranges():
    test_text = pg.rank_ranges(1, 4)
    assert test_text == 'between the 1st and 4th'

    test_text = pg.rank_ranges(4, 1)
    assert test_text == 'between the 1st and 4th'

    test_text = pg.rank_ranges(3, 3)
    assert test_text == 'the 3rd'


# Just need a little class that can return some simple values when asked as
# a stand in for the TimeSeriesMonthly, TimeSeriesAnnual classes
class Tiny:
    def __init__(self, number):
        self.metadata = {'display_name': f'{number}'}


def test_dataset_name_list():
    all_datasets = []
    for i in range(1, 5):
        all_datasets.append(Tiny(i))
    test_text = pg.dataset_name_list(all_datasets)
    assert test_text == '1, 2, 3, and 4'

    all_datasets = []
    for i in range(1, 2):
        all_datasets.append(Tiny(i))
    test_text = pg.dataset_name_list(all_datasets)
    assert test_text == '1'

    all_datasets = []
    for i in range(1, 3):
        all_datasets.append(Tiny(i))
    test_text = pg.dataset_name_list(all_datasets)
    assert test_text == '1 and 2'


def test_fancy_units():
    assert pg.fancy_html_units('degC') == '&deg;C'
    assert pg.fancy_html_units('numpty') == 'numpty'


def test_anomaly_and_rank(simple_annual):
    test_text = pg.anomaly_and_rank([simple_annual], 2022)

    assert 'The year 2022 was ranked the 1st highest' in test_text
    assert 'The mean value for 2022 was 2.02&deg;C' in test_text
    assert '(2.02-2.02&deg;C depending' in test_text
    assert '1 data sets were used in this assessment: HadCRUT5' in test_text

    test_text = pg.anomaly_and_rank([simple_annual], 2021)

    assert 'The year 2021 was ranked the 2nd highest' in test_text
    assert 'The mean value for 2021 was 2.02&deg;C' in test_text
    assert '(2.02-2.02&deg;C depending' in test_text
    assert '1 data sets were used in this assessment: HadCRUT5' in test_text


def test_anomaly_and_rank_multiple_datasets(simple_annual, simple_annual_descending):
    test_text = pg.anomaly_and_rank([simple_annual, simple_annual_descending], 2022)

    assert 'The year 2022 was ranked between the 1st and 173rd highest' in test_text
    assert 'The mean value for 2022 was 1.01&deg;C' in test_text
    assert '(0.00-2.02&deg;C depending' in test_text
    assert '2 data sets were used in this assessment: HadCRUT5 and HadCRUT5' in test_text


def test_anomaly_and_rank_no_dataset_raises():
    with pytest.raises(RuntimeError):
        _ = pg.anomaly_and_rank([], 2022)


def test_monthly_value(simple_monthly):
    test_text = pg.max_monthly_value([simple_monthly], 2022)

    assert 'was the 1st highest' in test_text
    assert 'at 2022.0&deg;C.' in test_text

    test_text = pg.max_monthly_value([simple_monthly], 2021)

    assert 'was the 13th highest' in test_text
    assert 'at 2021.0&deg;C.' in test_text


def test_monthly_value_no_dataset_raises():
    with pytest.raises(RuntimeError):
        _ = pg.max_monthly_value([], 2022)


def test_arctic_ice_paragraph(simple_monthly):
    test_text = pg.arctic_ice_paragraph([simple_monthly], 2022)

    assert 'in March 2022 was between 2022.00 and 2022.00&deg;C.' in test_text
    assert 'was the 173rd lowest' in test_text
    assert 'In September the extent was between 2022.00 and 2022.00&deg;C' in test_text
    assert 'This was the 173rd lowest' in test_text
    assert 'Data sets used were: HadCRUT5.'


def test_arctic_ice_paragraph_no_dataset_raises():
    with pytest.raises(RuntimeError):
        _ = pg.arctic_ice_paragraph([], 2022)


def test_glacier(simple_annual):
    dummy_data = 172. - np.array(range(173))
    dummy_data[0] = dummy_data[1] - 0.5
    simple_annual.df['data'] = dummy_data

    test_text = pg.glacier_paragraph([simple_annual], 2022)

    assert '171st consecutive year' in test_text
    assert 'since 1852' in test_text
    assert 'Cumulative glacier loss since 1970 is 0.0&deg;C'


def test_glacier_no_dataset_raises():
    with pytest.raises(RuntimeError):
        _ = pg.glacier_paragraph([], 2022)


def test_greenhouse_gas_paragraph_all_record(mocker):
    all_datasets = []

    for variable in ['co2', 'ch4', 'n2o']:
        m = mocker.MagicMock()
        m.metadata = {}
        m.metadata['display_name'] = 'WDCGG'
        m.metadata['variable'] = variable
        m.get_first_and_last_year.return_value = (1980, 2020)
        m.get_rank_from_year.return_value = 1
        m.get_value_from_year.return_value = 765.432

        all_datasets.append(m)

    test_text = pg.co2_paragraph(all_datasets, 2021)

    assert 'carbon dioxide (CO<sub>2</sub>) at 765.4 &plusmn; 0.2' in test_text
    assert 'methane (CH<sub>4</sub>) at 765 &plusmn; 2' in test_text
    assert 'nitrous oxide (N<sub>2</sub>O) at 765.4 &plusmn; 0.1' in test_text
    assert 'In 2020, greenhouse gas mole fractions reached new highs,' in test_text


def test_greenhouse_gas_paragraph_not_all_record(mocker):
    all_datasets = []

    for variable in ['co2', 'ch4', 'n2o']:
        m = mocker.MagicMock()
        m.metadata = {}
        m.metadata['display_name'] = 'WDCGG'
        m.metadata['variable'] = variable
        m.get_first_and_last_year.return_value = (1980, 2020)
        m.get_rank_from_year.return_value = 2
        m.get_value_from_year.return_value = 765.432

        all_datasets.append(m)

    test_text = pg.co2_paragraph(all_datasets, 2021)

    assert 'In 2020, globally averaged greenhouse gas mole fractions were' in test_text
    assert 'carbon dioxide (CO<sub>2</sub>) at 765.4 &plusmn; 0.2' in test_text
    assert 'methane (CH<sub>4</sub>) at 765 &plusmn; 2' in test_text
    assert 'nitrous oxide (N<sub>2</sub>O) at 765.4 &plusmn; 0.1' in test_text


def test_greenhouse_gas_paragraph_no_datasets(mocker):
    all_datasets = []
    with pytest.raises(RuntimeError):
        _ = pg.co2_paragraph(all_datasets, 2021)


def test_greenhouse_gas_paragraph_no_wdcgg_datasets(mocker):
    all_datasets = []
    for variable in ['co2', 'ch4', 'n2o']:
        m = mocker.MagicMock()
        m.metadata = {}
        m.metadata['display_name'] = 'Nobody'
        m.metadata['variable'] = variable
        m.get_first_and_last_year.return_value = (1980, 2020)
        m.get_rank_from_year.return_value = 1
        m.get_value_from_year.return_value = 765.432
        all_datasets.append(m)

    with pytest.raises(RuntimeError):
        _ = pg.co2_paragraph(all_datasets, 2021)


def test_greenhouse_gas_paragraph_all_record_but_next_year_isnt(mocker):
    all_datasets = []

    for variable in ['co2', 'ch4', 'n2o']:
        m = mocker.MagicMock()
        m.metadata = {}
        m.metadata['display_name'] = 'WDCGG'
        m.metadata['variable'] = variable
        m.get_first_and_last_year.return_value = (1980, 2020)
        m.get_rank_from_year.return_value = 1
        m.get_value_from_year.return_value = 765.432

        all_datasets.append(m)

    m = mocker.MagicMock()
    m.metadata = {}
    m.metadata['display_name'] = 'AnotherCentre'
    m.metadata['variable'] = 'co2'
    m.get_first_and_last_year.return_value = (1980, 2020)
    m.get_rank_from_year.return_value = 2
    m.get_value_from_year.side_effect = [4.0, 5.0]

    all_datasets.append(m)

    test_text = pg.co2_paragraph(all_datasets, 2021)

    assert 'carbon dioxide (CO<sub>2</sub>) at 765.4 &plusmn; 0.2' in test_text
    assert 'methane (CH<sub>4</sub>) at 765 &plusmn; 2' in test_text
    assert 'nitrous oxide (N<sub>2</sub>O) at 765.4 &plusmn; 0.1' in test_text
    assert 'In 2020, greenhouse gas mole fractions reached new highs,' in test_text

    assert 'Real-time data from specific locations' not in test_text


def test_greenhouse_gas_paragraph_all_record_and_next_year_is_too(mocker):
    all_datasets = []

    for variable in ['co2', 'ch4', 'n2o']:
        m = mocker.MagicMock()
        m.metadata = {}
        m.metadata['display_name'] = 'WDCGG'
        m.metadata['variable'] = variable
        m.get_first_and_last_year.return_value = (1980, 2020)
        m.get_rank_from_year.return_value = 1
        m.get_value_from_year.return_value = 765.432

        all_datasets.append(m)

    m = mocker.MagicMock()
    m.metadata = {}
    m.metadata['display_name'] = 'AnotherCentre'
    m.metadata['variable'] = 'co2'
    m.get_first_and_last_year.return_value = (1980, 2020)
    m.get_rank_from_year.return_value = 1
    m.get_value_from_year.side_effect = [6.0, 5.0]

    all_datasets.append(m)

    test_text = pg.co2_paragraph(all_datasets, 2021)

    assert 'carbon dioxide (CO<sub>2</sub>) at 765.4 &plusmn; 0.2' in test_text
    assert 'methane (CH<sub>4</sub>) at 765 &plusmn; 2' in test_text
    assert 'nitrous oxide (N<sub>2</sub>O) at 765.4 &plusmn; 0.1' in test_text
    assert 'In 2020, greenhouse gas mole fractions reached new highs,' in test_text

    assert 'Real-time data from specific locations' in test_text
