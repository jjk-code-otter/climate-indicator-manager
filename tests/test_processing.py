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
import json
from pathlib import Path
from climind.data_manager.metadata import DatasetMetadata, CollectionMetadata
import climind.data_manager.processing as dm

HADCRUT5_PATH = 'test_data/hadcrut5.json'


@pytest.fixture
def test_attributes():
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
                  'fetcher': 'test_fetcher',
                  'variable': 'ohc'}

    return attributes


@pytest.fixture
def test_dataset():
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
                  'fetcher': 'test_fetcher'}

    global_attributes = {'name': '',
                         'display_name': '',
                         'version': '',
                         'variable': 'ohc',
                         'units': 'zJ',
                         'citation': [''],
                         'citation_url': [''],
                         'data_citation': [''],
                         'colour': '',
                         'zpos': 99}

    dataset_metadata = DatasetMetadata(attributes)
    collection_metadata = CollectionMetadata(global_attributes)

    return dm.DataSet(dataset_metadata, collection_metadata)


@pytest.fixture
def test_collection_metadata():
    global_attributes = {'name': '',
                         'display_name': '',
                         'version': '',
                         'variable': '',
                         'units': '1',
                         'citation': [''],
                         'citation_url': [''],
                         'data_citation': [''],
                         'colour': '',
                         'zpos': 99}

    collection_metadata = CollectionMetadata(global_attributes)

    return collection_metadata


def test_basic_creation(test_attributes, test_dataset):
    ds = test_dataset

    for key in test_attributes:
        assert ds.metadata[key] == test_attributes[key]


def test_dataset_to_str(test_dataset):
    test_string = str(test_dataset)
    assert isinstance(test_string, str)


def test_match(test_dataset):
    metadata_to_match_pass = {'time_resolution': 'monthly'}
    metadata_to_match_fail = {'time_resolution': 'annual'}

    assert test_dataset.match_metadata(metadata_to_match_pass)
    assert not test_dataset.match_metadata(metadata_to_match_fail)


def test_match_with_irrelevant_metadata(test_dataset):
    metadata_to_match_irrelevant = {'irrelevance': 'meh'}
    assert test_dataset.match_metadata(metadata_to_match_irrelevant)


def test_match_list(test_dataset):
    metadata_to_match_pass = {'variable': ['tas', 'ohc']}
    assert test_dataset.match_metadata(metadata_to_match_pass)


def test_no_match_list(test_dataset):
    metadata_to_match_pass = {'variable': ['co2', 'tas']}
    assert not test_dataset.match_metadata(metadata_to_match_pass)


def test_get_fetcher(mocker, test_dataset):
    ds = test_dataset

    m = mocker.patch("climind.data_manager.processing.get_function", return_value="Match")
    fetcher = ds._get_fetcher()

    m.assert_called_once_with("climind.fetchers", "test_fetcher", "fetch")
    assert fetcher == "Match"


def test_download(mocker, test_dataset):
    def _two_input_function(a, b, c):
        assert a == 'test_url'
        assert b == Path('')
        assert c == 'test_filename'
        return

    m = mocker.patch("climind.data_manager.processing.DataSet._get_fetcher",
                     return_value=_two_input_function)

    test_dataset.download(Path(''))


def test_get_reader(mocker, test_attributes):
    ds = dm.DataSet(test_attributes, {})

    m = mocker.patch("climind.data_manager.processing.get_function", return_value="Match")
    fetcher = ds._get_reader()

    m.assert_called_once_with("climind.readers", "test_reader", "read_ts")
    assert fetcher == "Match"


def test_get_function():
    """
    Test that we can recover a specific function from a module and script. We'll use the function
    we are testing as the test can only exist with the function, so we always know it's there as
    long as we're testing it.
    """
    from climind.data_manager.processing import get_function
    fn = dm.get_function('climind.data_manager', 'processing', 'get_function')

    assert get_function == fn


def simple_return(dummy):
    """Simple function that returns a function that returns its two arguments"""

    def fn(a, b):
        return a, b

    return fn


def error_return(dummy):
    """Simple function that returns a function that raises an error"""

    def fn(a, b):
        raise RuntimeError("A simple error")

    return fn


def test_read(mocker, test_dataset, test_attributes):
    ds = test_dataset

    # Mock it so that the get_reader function returns a simple function as specified
    _ = mocker.patch('climind.data_manager.processing.DataSet._get_reader', new=simple_return)

    a, b = ds.read_dataset(Path(''))

    assert a == Path('')
    for key in test_attributes:
        assert b[key] == test_attributes[key]


def test_read_error_handler(mocker, test_dataset, test_attributes):
    ds = test_dataset

    # Mock it so that the get_reader function returns a simple function as specified
    _ = mocker.patch('climind.data_manager.processing.DataSet._get_reader', new=error_return)

    match_phrase = "Error occurred while executing reader_fn: A simple error"
    with pytest.raises(RuntimeError, match=match_phrase):
        _, _ = ds.read_dataset(Path(''))


# DataCollection tests

def test_creation_from_file():
    dc = dm.DataCollection.from_file(Path(HADCRUT5_PATH))
    assert isinstance(dc, dm.DataCollection)

    assert dc.global_attributes['name'] == 'HadCRUT5'


def test_data_collection_to_string():
    dc = dm.DataCollection.from_file(Path(HADCRUT5_PATH))
    test_string = str(dc)
    assert isinstance(test_string, str)


def test_select():
    data_collection = dm.DataCollection.from_file(Path(HADCRUT5_PATH))
    sub_data_collection = data_collection.match_metadata({'type': 'gridded'})

    for dataset in sub_data_collection.datasets:
        assert dataset.metadata['type'] == 'gridded'


def test_select_global_from_list():
    data_collection = dm.DataCollection.from_file(Path(HADCRUT5_PATH))
    sub_data_collection = data_collection.match_metadata({'version': ['5.0.1.0', '5.0.2.0']})

    for dataset in sub_data_collection.datasets:
        assert dataset.metadata['version'] == '5.0.1.0'


def test_select_global_from_list_no_match():
    data_collection = dm.DataCollection.from_file(Path(HADCRUT5_PATH))
    sub_data_collection = data_collection.match_metadata({'version': ['5.0.3.0', '5.0.2.0']})

    assert sub_data_collection is None


def test_select_without_a_match():
    data_collection = dm.DataCollection.from_file(Path(HADCRUT5_PATH))
    sub_data_collection = data_collection.match_metadata({'type': 'renault'})
    assert sub_data_collection is None


def test_select_match_global_but_not_dataset():
    data_collection = dm.DataCollection.from_file(Path(HADCRUT5_PATH))
    sub_data_collection = data_collection.match_metadata({'variable': 'tas',
                                                          'type': 'renault'})
    assert sub_data_collection is None


def test_select_no_match_in_global():
    data_collection = dm.DataCollection.from_file(Path(HADCRUT5_PATH))
    sub_data_collection = data_collection.match_metadata({'variable': 'mslp'})
    assert sub_data_collection is None


def test_creation_from_dict_no_data_set(test_collection_metadata):
    data_collection = dm.DataCollection(test_collection_metadata.metadata)
    assert isinstance(data_collection, dm.DataCollection)


def test_data_collection_read(mocker):
    data_collection = dm.DataCollection.from_file(Path(HADCRUT5_PATH))
    m = mocker.patch("climind.data_manager.processing.DataSet.read_dataset", return_value="test")

    datasets = data_collection.read_datasets(Path(''))

    assert m.call_args_list[0][0][0] == Path('HadCRUT5')
    assert m.call_args_list[1][0][0] == Path('HadCRUT5')

    assert 2 == m.call_count
    assert len(datasets) == 2
    assert datasets[0] == 'test'
    assert datasets[1] == 'test'


def test_data_collection_read_fail(mocker):
    """Specified file does not actually exist, so should fail and raise RuntimeError"""
    data_collection = dm.DataCollection.from_file(Path(HADCRUT5_PATH))
    with pytest.raises(RuntimeError, match="Failed to read HadCRUT5 with error message"):
        _ = data_collection.read_datasets(Path(''))


def test_rebuild_metadata():
    dc = dm.DataCollection.from_file(Path(HADCRUT5_PATH))
    metadata = dc._rebuild_metadata()

    with open(Path(HADCRUT5_PATH), 'r') as f:
        original_metadata = json.load(f)

    assert metadata == original_metadata


def test_get_collection_dir(tmp_path):
    """Use the tmp_path fixture to create the collection dir"""
    dc = dm.DataCollection.from_file(Path(HADCRUT5_PATH))
    test_dir = dc.get_collection_dir(tmp_path)
    assert test_dir == Path(tmp_path / 'HadCRUT5')
    assert test_dir.exists()


def test_to_file(tmp_path):
    dc = dm.DataCollection.from_file(Path(HADCRUT5_PATH))
    dc.to_file(tmp_path / 'test.json')

    # Check file exists
    assert (tmp_path / 'test.json').exists()

    with open(Path(HADCRUT5_PATH), 'r') as f:
        original = json.load(f)

    with open(tmp_path / 'test.json', 'r') as f:
        written_and_read = json.load(f)

    # Check that written metadata is identical to original metadata
    assert original == written_and_read


def test_collection_download(mocker):
    dc = dm.DataCollection.from_file(Path(HADCRUT5_PATH))
    m1 = mocker.patch("climind.data_manager.processing.DataCollection.get_collection_dir", return_value='testing')
    m2 = mocker.patch("climind.data_manager.processing.DataSet.download", return_value=None)
    dc.download(Path(''))

    assert 1 == m1.call_count
    assert 2 == m2.call_count

    assert m2.call_args_list[0][0][0] == 'testing'
    assert m2.call_args_list[1][0][0] == 'testing'


# Data archive tests

def test_creation_from_directory():
    metadata_dir = Path('test_data')
    da = dm.DataArchive.from_directory(metadata_dir)
    assert isinstance(da, dm.DataArchive)


def test_select_from_archive():
    metadata_dir = Path('test_data')
    da = dm.DataArchive.from_directory(metadata_dir)
    selected_da = da.select({'type': 'gridded'})

    assert len(da.collections['HadCRUT5'].datasets) == 2
    assert len(selected_da.collections['HadCRUT5'].datasets) == 1

    assert len(da.collections['GISTEMP'].datasets) == 2
    assert len(selected_da.collections['GISTEMP'].datasets) == 1


def test_archive_read(mocker):
    # The test_data directory contains two metadata files which are used to create the archive
    metadata_dir = Path('test_data')
    da = dm.DataArchive.from_directory(metadata_dir)

    m = mocker.patch("climind.data_manager.processing.DataCollection.read_datasets", return_value=["test"])

    datasets = da.read_datasets(Path(''))

    assert m.call_count == 2
    assert len(datasets) == 2
    assert datasets[0] == 'test'
    assert datasets[1] == 'test'


def test_archive_to_string(mocker):
    metadata_dir = Path('test_data')
    da = dm.DataArchive.from_directory(metadata_dir)
    assert isinstance(str(da), str)


def test_archive_download(mocker):
    metadata_dir = Path('test_data')
    da = dm.DataArchive.from_directory(metadata_dir)

    m1 = mocker.patch("climind.data_manager.processing.DataCollection.download")

    da.download(Path('gin'))

    assert m1.call_args_list[0][0][0] == Path('gin')
    assert m1.call_args_list[1][0][0] == Path('gin')

    assert 2 == m1.call_count
