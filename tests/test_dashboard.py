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
from unittest.mock import call

from pathlib import Path
from zipfile import is_zipfile
from climind.definitions import ROOT_DIR, METADATA_DIR
import climind.data_manager.processing as dm
import climind.web.dashboard as db


@pytest.fixture
def card_metadata():
    metadata = {
        "link_to": None, "title": "Ocean Indicators",
        "selecting": {"type": "timeseries", "variable": "ohc", "time_resolution": "annual"},
        "processing": [{"method": "rebaseline", "args": [1981, 2010]}],
        "plotting": {"function": "neat_plot", "title": "Ocean heat content"}
    }
    return metadata


@pytest.fixture
def tas_card_metadata():
    metadata = {
        "link_to": None, "title": "GMT",
        "selecting": {"type": "timeseries", "variable": "tas", "time_resolution": "monthly"},
        "processing": [{"method": "rebaseline", "args": [1981, 2010]}],
        "plotting": {"function": "neat_plot", "title": "GMT"}
    }
    return metadata


@pytest.fixture
def page_metadata():
    metadata = {
        "id": "dashboard",
        "name": "Key Climate Indicators",
        "template": "front_page",
        "indicators": ["co2", "tas", "ohc",
                       "sea_level", "arctic_ice", "greenland"],
        "links": ["greenhouse_gases", "global_mean_temperature",
                  "ocean_heat_content", "sea_level",
                  "sea_ice_extent", "glaciers_and_ice_sheets"]
    }
    return metadata


@pytest.fixture
def tas_page_metadata():
    metadata = {
        "id": "test_dashboard",
        "name": "Key Climate Indicators",
        "template": "front_page",
        "cards": [
            {
                "link_to": "global_mean_temperature",
                "title": "Global temperature",
                "selecting": {"type": "timeseries", "variable": "tas", "time_resolution": "monthly"},
                "processing": [{"method": "rebaseline", "args": [1981, 2010]},
                               {"method": "make_annual", "args": []},
                               {"method": "add_offset", "args": [0.69]},
                               {"method": "manually_set_baseline", "args": [1850, 1900]}],
                "plotting": {"function": "neat_plot", "title": "Global mean temperature"}
            }
        ],
        "paragraphs": [
            {
                "selecting": {"variable": "arctic_ice", "time_resolution": "monthly"},
                "processing": [{"method": "rebaseline", "args": [1981, 2010]}],
                "writing": {"function": "arctic_ice_paragraph"}
            }
        ]
    }
    return metadata


@pytest.fixture
def test_paragraph_metadata():
    metadata = {
        "selecting": {"variable": "arctic_ice", "time_resolution": "monthly"},
        "processing": [{"method": "rebaseline", "args": [1981, 2010]}],
        "writing": {"function": "arctic_ice_paragraph"}
    }
    return metadata


def test_process_single_dataset(mocker):
    # Need to mock a None return value here because otherwise, ds gets
    # complicated ds.first_method().second_method and ugh.
    ds = mocker.MagicMock()
    ds.first_method.return_value = None
    ds.second_method.return_value = None

    processing_steps = [
        {'method': 'first_method', 'args': ['first_argument', 5.7]},
        {'method': 'second_method', 'args': [10, 11, 12]}
    ]

    _ = db.process_single_dataset(ds, processing_steps)

    ds.first_method.assert_called_once_with(*processing_steps[0]['args'])
    ds.second_method.assert_called_once_with(*processing_steps[1]['args'])


def test_process_single_dataset_with_output(mocker):
    ds = mocker.MagicMock()

    test_return_value = 'test_return_value'
    ds.this_method.return_value = test_return_value

    processing_steps = [
        {'method': 'this_method', 'args': ['first_argument', 5.7]}
    ]

    result = db.process_single_dataset(ds, processing_steps)

    assert result == test_return_value
    ds.this_method.assert_called_once_with(*processing_steps[0]['args'])


def test_paragraph_creation(test_paragraph_metadata):
    paragraph = db.Paragraph(test_paragraph_metadata)
    assert isinstance(paragraph, db.Paragraph)


def test_paragraph_get_and_set(test_paragraph_metadata):
    paragraph = db.Card(test_paragraph_metadata)
    assert paragraph['selecting']['variable'] == 'arctic_ice'
    test_indicator = 'test_indicator'
    paragraph['selecting']['variable'] = test_indicator
    assert paragraph['selecting']['variable'] == test_indicator


def test_process_datasets_para(mocker, test_paragraph_metadata):
    paragraph = db.Paragraph(test_paragraph_metadata)
    tiny1 = Tiny({'name': 'first', 'url': 'first_url', 'citation': 'first et al.',
                  'data_citation': 'doi, first', 'acknowledgement': 'First, thanks'})
    tiny2 = Tiny({'name': 'second', 'url': 'second_url', 'citation': 'second et al.',
                  'data_citation': 'doi, second', 'acknowledgement': 'Second, thanks'})
    paragraph.datasets = [tiny1, tiny2]

    m = mocker.patch("climind.web.dashboard.process_single_dataset", wraps=in_and_out)

    paragraph.process_datasets()

    calls = [call(tiny1, test_paragraph_metadata['processing']),
             call(tiny2, test_paragraph_metadata['processing'])]
    m.assert_has_calls(calls, any_order=True)

    assert len(paragraph.datasets) == 2
    assert paragraph['dataset_metadata']['name'] == 'first'
    assert paragraph['dataset_metadata']['url'] == 'first_url'


def test_render_paragraph(mocker, test_paragraph_metadata):
    paragraph = db.Paragraph(test_paragraph_metadata)
    _ = mocker.patch('climind.stats.paragraphs.arctic_ice_paragraph', wraps=simple_responder)
    paragraph.render(year=2021)
    assert paragraph['text'] == [[], 2021]


def test_render_paragraph_with_kwargs(mocker, test_paragraph_metadata):
    paragraph = db.Paragraph(test_paragraph_metadata)
    _ = mocker.patch('climind.stats.paragraphs.arctic_ice_paragraph', wraps=simple_responder)
    paragraph['writing']['kwargs'] = {'test_kwarg': 'your_message_here'}
    paragraph.render(year=2021)
    assert paragraph['text'] == [[], 2021, 'your_message_here']


def test_process_paragraph(mocker, test_paragraph_metadata):
    """
    This function is kind of a shopping list, so essentially the test is to go through
    the items that are needed in today's shop, mock them and make sure they are all called
    with the right inputs
    """
    paragraph = db.Paragraph(test_paragraph_metadata)

    mock_select_and_read = mocker.patch('climind.web.dashboard.Paragraph.select_and_read_data')
    mock_process_datasets = mocker.patch('climind.web.dashboard.Paragraph.process_datasets')
    mock_render = mocker.patch('climind.web.dashboard.Paragraph.render')

    paragraph.process_paragraph('data_dir', 'archive')

    mock_select_and_read.assert_called_with('data_dir', 'archive')
    mock_process_datasets.assert_called_once()
    mock_render.assert_called_once()


def test_card_creation(card_metadata):
    card = db.Card(card_metadata)
    assert isinstance(card, db.Card)


def test_card_get_and_set(card_metadata):
    card = db.Card(card_metadata)
    assert card['selecting']['variable'] == 'ohc'
    test_indicator = 'test_indicator'
    card['selecting']['variable'] = test_indicator
    assert card['selecting']['variable'] == test_indicator


def simple_responder(*args, **kwargs):
    return_list = []
    for arg in args:
        return_list.append(arg)
    for key in kwargs:
        return_list.append(kwargs[key])

    return return_list


def test_card_plot(mocker, card_metadata):
    card = db.Card(card_metadata)
    _ = mocker.patch('climind.plotters.plot_types.neat_plot', wraps=simple_responder)
    card.plot(Path(""))
    assert card['caption'] == [Path(""), [], "Ocean_Indicators.png", card_metadata['plotting']['title']]


def test_card_plot_with_kwargs(mocker, card_metadata):
    card = db.Card(card_metadata)
    _ = mocker.patch('climind.plotters.plot_types.neat_plot', wraps=simple_responder)
    card['plotting']['kwargs'] = {'test_kwarg': 'your_message_here'}
    card.plot(Path(""))
    assert card['caption'] == [Path(""), [], "Ocean_Indicators.png", card_metadata['plotting']['title'],
                               'your_message_here']


def test_card_csv_write(mocker, card_metadata):
    card = db.Card(card_metadata)
    mockds = mocker.MagicMock()
    mockds.write_csv.return_value = 'test'
    mockds.metadata = {'variable': 'ohc', 'name': 'test_name'}

    card.datasets = [mockds]

    csv_paths = card.make_csv_files(Path('dingo'))

    assert csv_paths == [Path('dingo') / 'ohc_test_name.csv']

    mockds.write_csv.assert_called_with(Path('dingo') / 'ohc_test_name.csv')


def test_make_zip_file(tmpdir, mocker, card_metadata):
    # Make some fake csv files in the temporary directory
    csv_paths = []
    for i in range(3):
        csv_path = Path(tmpdir) / f"testfile{i}.csv"
        with open(csv_path, 'w') as f:
            f.write("content")
        csv_paths.append(csv_path)

    # set up mocker to return paths to fake csv files when asked to make csv files
    _ = mocker.patch('climind.web.dashboard.Card.make_csv_files', return_value=csv_paths)

    # makes the card and use it to create a zipfile
    card = db.Card(card_metadata)
    card.make_zip_file(tmpdir)

    # check that csv files have been deleted/unlinked
    for csv_path in csv_paths:
        assert not csv_path.exists()

    # check that zip file has been created and that it is, in fact, a zip file
    assert (Path(tmpdir) / f'Ocean_Indicators_data_files.zip').exists()
    assert is_zipfile(Path(tmpdir) / f'Ocean_Indicators_data_files.zip')


class Tiny:
    def __init__(self, metadata):
        self.metadata = metadata


def in_and_out(first, _):
    return first


def test_process_datasets(mocker, card_metadata):
    card = db.Card(card_metadata)
    tiny1 = Tiny({'name': 'first', 'url': 'first_url', 'citation': 'first et al.',
                  'data_citation': 'doi, first', 'acknowledgement': 'First, thanks'})
    tiny2 = Tiny({'name': 'second', 'url': 'second_url', 'citation': 'second et al.',
                  'data_citation': 'doi, second', 'acknowledgement': 'Second, thanks'})
    card.datasets = [tiny1, tiny2]

    m = mocker.patch("climind.web.dashboard.process_single_dataset", wraps=in_and_out)

    card.process_datasets()

    calls = [call(tiny1, card_metadata['processing']),
             call(tiny2, card_metadata['processing'])]
    m.assert_has_calls(calls, any_order=True)

    assert len(card.datasets) == 2
    assert card['dataset_metadata'][0]['name'] == 'first'
    assert card['dataset_metadata'][1]['name'] == 'second'


def test_process_card(mocker, card_metadata):
    """
    This function is kind of a shopping list, so essentially the test is to go through
    the items that are needed in today's shop, mock them and make sure they are all called
    with the right inputs
    """
    card = db.Card(card_metadata)

    mock_select_and_read = mocker.patch('climind.web.dashboard.Card.select_and_read_data')
    mock_process_datasets = mocker.patch('climind.web.dashboard.Card.process_datasets')
    mock_plot = mocker.patch('climind.web.dashboard.Card.plot')
    mock_make_zip = mocker.patch('climind.web.dashboard.Card.make_zip_file')

    card.process_card('data_dir', 'figure_dir', 'formatted_data_dir', 'archive')

    mock_select_and_read.assert_called_with('data_dir', 'archive')
    mock_process_datasets.assert_called_once()
    mock_plot.assert_called_with('figure_dir')
    mock_make_zip.assert_called_with('formatted_data_dir')


def test_select_and_read_data(mocker, tas_card_metadata):
    card = db.Card(tas_card_metadata)
    metadata_dir = Path('test_data')

    m2 = mocker.patch('climind.data_manager.processing.DataArchive.read_datasets', return_value=[])

    da = dm.DataArchive.from_directory(metadata_dir)

    card.select_and_read_data(Path('data_dir'), da)

    m2.assert_called_with(Path('data_dir'))

    assert card.datasets == []


# testing pages

def test_page_creation(page_metadata):
    page = db.Page(page_metadata)
    assert isinstance(page, db.Page)


def test_page_get_item(page_metadata):
    page = db.Page(page_metadata)
    assert page['id'] == 'dashboard'
    page['id'] = 'somethingelse'
    assert page['id'] == 'somethingelse'


def test_process_cards(mocker, tas_page_metadata):
    page = db.Page(tas_page_metadata)

    m = mocker.patch('climind.web.dashboard.Card.process_card')

    data_dir = Path('data_dir')
    figure_dir = Path('figure_dir')
    formatted_data_dir = Path('formatted_data_dir')

    _ = page._process_cards(data_dir, figure_dir, formatted_data_dir, 'archive')

    assert m.call_count == 1
    m.assert_called_with(data_dir, figure_dir, formatted_data_dir, 'archive')


def test_process_paragraphs(mocker, tas_page_metadata):
    page = db.Page(tas_page_metadata)

    m = mocker.patch('climind.web.dashboard.Paragraph.process_paragraph')

    data_dir = Path('data_dir')

    _ = page._process_paragraphs(data_dir, 'archive')

    assert m.call_count == 1
    m.assert_called_with(data_dir, 'archive')


def test_page_build_creates_directories_and_webpage(tmpdir, mocker, tas_page_metadata):
    page = db.Page(tas_page_metadata)

    _ = mocker.patch('climind.web.dashboard.Page._process_cards', return_value=[])
    _ = mocker.patch('climind.web.dashboard.Page._process_paragraphs', return_value=[])
    page.build(Path(tmpdir), Path(tmpdir), 'archive')

    assert (Path(tmpdir) / 'figures').exists()
    assert (Path(tmpdir) / 'formatted_data').exists()
    assert (Path(tmpdir) / 'test_dashboard.html')


# testing dashboards

def test_dashboard_from_json():
    json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'key_indicators.json'
    assert json_file.exists()

    dash = db.Dashboard.from_json(json_file, METADATA_DIR)

    assert isinstance(dash, db.Dashboard)

    assert len(dash.pages) == 6 + 1


def test_dashboard_build(mocker, tmpdir):
    m = mocker.patch("climind.web.dashboard.Page.build")
    dash = db.Dashboard({'pages': [0, 1, 2, 3]}, 'archive')
    assert len(dash.pages) == 4

    dash.data_dir = 'data_dir'
    dash.build(tmpdir)

    assert m.call_count == 4

    calls = [
        call(tmpdir, 'data_dir', 'archive'),
        call(tmpdir, 'data_dir', 'archive'),
        call(tmpdir, 'data_dir', 'archive'),
        call(tmpdir, 'data_dir', 'archive')
    ]

    m.assert_has_calls(calls, any_order=True)
