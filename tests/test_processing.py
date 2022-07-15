import pytest
import json
from pathlib import Path
import climind.data_manager.processing as dm


def test_basic_creation():
    attributes = {'url': 'test_url',
                  'type': 'test_type',
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher'}

    ds = dm.DataSet(attributes)

    for key in attributes:
        assert ds.attributes[key] == attributes[key]


def test_missing_standard_attribute():
    attributes = {'url': 'test_url',
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher'}

    with pytest.raises(KeyError):
        ds = dm.DataSet(attributes)


def test_match():
    attributes = {'url': 'test_url',
                  'type': 'test_type',
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher'}

    ds = dm.DataSet(attributes)

    metadata_to_match_pass = {'url': 'test_url'}
    metadata_to_match_fail = {'url': 'wrong_url'}

    assert ds.match_metadata(metadata_to_match_pass)
    assert not ds.match_metadata(metadata_to_match_fail)


def test_match_with_irrelevant_metadata():
    attributes = {'url': 'test_url',
                  'type': 'test_type',
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher'}

    ds = dm.DataSet(attributes)

    metadata_to_match_irrelevant = {'irrelevance': 'meh'}

    assert ds.match_metadata(metadata_to_match_irrelevant)


def test_match_list():
    attributes = {'url': 'test_url',
                  'type': 'test_type',
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher',
                  'variable': 'tas'}

    ds = dm.DataSet(attributes)

    metadata_to_match_pass = {'variable': ['tas', 'ohc']}

    assert ds.match_metadata(metadata_to_match_pass)


def test_no_match_list():
    attributes = {'url': 'test_url',
                  'type': 'test_type',
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher',
                  'variable': 'tas'}

    ds = dm.DataSet(attributes)

    metadata_to_match_pass = {'variable': ['co2', 'ohc']}

    assert not ds.match_metadata(metadata_to_match_pass)


def test_get_fetcher(mocker):
    attributes = {'url': 'test_url',
                  'type': 'test_type',
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher',
                  'variable': 'tas'}

    ds = dm.DataSet(attributes)

    m = mocker.patch("climind.data_manager.processing.get_function", return_value="Match")
    fetcher = ds._get_fetcher()

    m.assert_called_once_with("climind.fetchers", "test_fetcher", "fetch")
    assert fetcher == "Match"


def test_get_reader(mocker):
    attributes = {'url': 'test_url',
                  'type': 'test_type',
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher',
                  'variable': 'tas'}

    ds = dm.DataSet(attributes)

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


def test_read(mocker):
    attributes = {'name': '',
                  'url': ['test_url'],
                  'type': 'test_type',
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher',
                  'variable': 'tas'}

    ds = dm.DataSet(attributes)

    m = mocker.patch('climind.data_manager.processing.DataSet._get_reader',
                     new=simple_return)

    a, b = ds.read_dataset(Path(''))

    assert a == Path('')
    assert b == attributes


# DataCollection tests

def test_creation_from_file():
    dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
    assert isinstance(dc, dm.DataCollection)

    assert dc.global_attributes['name'] == 'HadCRUT5'


def test_select():
    dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
    subdc = dc.match_metadata({'type': 'gridded'})

    for dataset in subdc.datasets:
        assert dataset.attributes['type'] == 'gridded'


def test_select_global_from_list():
    dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
    subdc = dc.match_metadata({'version': ['5.0.1.0', '5.0.2.0']})

    for dataset in subdc.datasets:
        assert dataset.attributes['version'] == '5.0.1.0'


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


def test_creation_from_empty_dict():
    dc = dm.DataCollection({})
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


def test_get_collection_dir(mocker):
    pass


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

    msg = str(selected_da)


def test_archive_read(mocker):
    metadata_dir = Path('test_data')
    da = dm.DataArchive.from_directory(metadata_dir)

    m = mocker.patch("climind.data_manager.processing.DataCollection.read_datasets", return_value=["test"])

    datasets = da.read_datasets(Path(''))

    assert 2 == m.call_count
    assert len(datasets) == 2
    assert datasets[0] == 'test'
    assert datasets[1] == 'test'


def test_archive_download(mocker):
    metadata_dir = Path('test_data')
    da = dm.DataArchive.from_directory(metadata_dir)

    m1 = mocker.patch("climind.data_manager.processing.DataCollection.download")

    da.download(Path('gin'))

    assert m1.call_args_list[0][0][0] == Path('gin')
    assert m1.call_args_list[1][0][0] == Path('gin')

    assert 2 == m1.call_count
