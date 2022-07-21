import pytest
import json
from pathlib import Path
from climind.data_manager.metadata import DatasetMetadata, CollectionMetadata
import climind.data_manager.processing as dm

from climind.definitions import ROOT_DIR


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
                  'history': '',
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
                  'history': '',
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher'}

    global_attributes = {'name': '',
                         'version': '',
                         'variable': 'ohc',
                         'citation': [''],
                         'data_citation': [''],
                         'colour': '',
                         'zpos': 99}

    dataset_metadata = DatasetMetadata(attributes)
    collection_metadata = CollectionMetadata(global_attributes)

    return dm.DataSet(dataset_metadata, collection_metadata)


@pytest.fixture
def test_collection_metadata():
    global_attributes = {'name': '',
                         'version': '',
                         'variable': '',
                         'citation': [''],
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
    def _two_input_function(a, b):
        assert a == 'test_url'
        assert b == Path('')
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
    we are testing as the test can only exist with the function and so we always know it's there as
    long as we're testing it.
    """
    from climind.data_manager.processing import get_function
    fn = dm.get_function('climind.data_manager', 'processing', 'get_function')

    assert get_function == fn


def simple_return(dummy):
    def fn(a, b):
        return a, b

    return fn


def test_read(mocker, test_dataset, test_attributes):
    ds = test_dataset

    m = mocker.patch('climind.data_manager.processing.DataSet._get_reader',
                     new=simple_return)

    a, b = ds.read_dataset(Path(''))

    assert a == Path('')
    for key in test_attributes:
        assert b[key] == test_attributes[key]


# DataCollection tests

def test_creation_from_file():
    dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
    assert isinstance(dc, dm.DataCollection)

    assert dc.global_attributes['name'] == 'HadCRUT5'


def test_data_collection_to_string():
    dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
    test_string = str(dc)
    assert isinstance(test_string, str)


def test_select():
    dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
    subdc = dc.match_metadata({'type': 'gridded'})

    for dataset in subdc.datasets:
        assert dataset.metadata['type'] == 'gridded'


def test_select_global_from_list():
    dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
    subdc = dc.match_metadata({'version': ['5.0.1.0', '5.0.2.0']})

    for dataset in subdc.datasets:
        assert dataset.metadata['version'] == '5.0.1.0'


def test_select_global_from_list_no_match():
    dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
    subdc = dc.match_metadata({'version': ['5.0.3.0', '5.0.2.0']})

    assert subdc is None


def test_select_without_a_match():
    dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
    subdc = dc.match_metadata({'type': 'renault'})
    assert subdc is None


def test_select_match_global_but_not_dataset():
    dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
    subdc = dc.match_metadata({'variable': 'tas',
                               'type': 'renault'})
    assert subdc is None


def test_select_no_match_in_global():
    dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
    subdc = dc.match_metadata({'variable': 'mslp'})
    assert subdc is None


def test_creation_from_dict_no_data_set(test_collection_metadata):
    dc = dm.DataCollection(test_collection_metadata.metadata)
    assert isinstance(dc, dm.DataCollection)


def test_datacollection_read(mocker):
    dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
    m = mocker.patch("climind.data_manager.processing.DataSet.read_dataset", return_value="test")

    datasets = dc.read_datasets(Path(''))

    assert m.call_args_list[0][0][0] == Path('HadCRUT5')
    assert m.call_args_list[1][0][0] == Path('HadCRUT5')

    assert 2 == m.call_count
    assert len(datasets) == 2
    assert datasets[0] == 'test'
    assert datasets[1] == 'test'


def test_rebuild_metadata():
    dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
    metadata = dc._rebuild_metadata()

    with open(Path('test_data/hadcrut5.json'), 'r') as f:
        original_metadata = json.load(f)

    assert metadata == original_metadata


def test_get_collection_dir(tmp_path):
    """Use the tmp_path fixture to create the collection dir"""
    dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
    test_dir = dc.get_collection_dir(tmp_path)
    assert test_dir == Path(tmp_path / 'HadCRUT5')
    assert test_dir.exists()


def test_to_file(tmp_path):
    dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
    dc.to_file(tmp_path / 'test.json')

    # Check file exists
    assert (tmp_path / 'test.json').exists()

    with open(Path('test_data/hadcrut5.json'), 'r') as f:
        original = json.load(f)

    with open(tmp_path / 'test.json', 'r') as f:
        written_and_read = json.load(f)

    # Check that written metadata is identical to original metadata
    assert original == written_and_read


def test_collection_download(mocker):
    dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
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
    metadata_dir = Path('test_data')
    da = dm.DataArchive.from_directory(metadata_dir)

    m = mocker.patch("climind.data_manager.processing.DataCollection.read_datasets", return_value=["test"])

    datasets = da.read_datasets(Path(''))

    assert 2 == m.call_count
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
