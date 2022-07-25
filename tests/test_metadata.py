import pytest
from jsonschema import ValidationError

from climind.data_manager.metadata import DatasetMetadata, CollectionMetadata, BaseMetadata, CombinedMetadata


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
                  'history': '',
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher'
                  }

    return attributes


@pytest.fixture
def test_collection_attributes():
    attributes = {"name": "HadCRUT5",
                  "version": "5.0.1.0",
                  "variable": "tas",
                  "units": "degC",
                  "citation": [
                      "Morice, C.P., J.J. Kennedy, N.A. Rayner, J.P. Winn, E. Hogan, R.E. Killick, R.J.H. Dunn, T.J. Osborn, P.D. Jones and I.R. Simpson (in press) An updated assessment of near-surface temperature change from 1850: the HadCRUT5 dataset. Journal of Geophysical Research (Atmospheres) doi:10.1029/2019JD032361"],
                  "data_citation": [""],
                  "colour": "#444444",
                  "zpos": 99}

    return attributes


def test_base_metadata_set_and_get():
    bm = BaseMetadata({'flash': 'aha'})
    assert bm['flash'] == 'aha'

    bm['saviour'] = 'universe'
    assert bm['saviour'] == 'universe'


def test_base_metadata_get_missing_key():
    bm = BaseMetadata({'flash': 'aha'})
    with pytest.raises(KeyError):
        value = bm['nonexistentkey']


def test_print_base_metadata():
    bm = BaseMetadata({'flash': 'aha'})

    test_string = str(bm)

    assert 'flash' in test_string
    assert 'aha' in test_string


def test_missing_standard_attribute_in_dataset():
    attributes = {'url': 'test_url',
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher'}

    with pytest.raises(ValidationError):
        ds = DatasetMetadata(attributes)


def test_match(test_dataset_attributes):
    ds = DatasetMetadata(test_dataset_attributes)

    metadata_to_match_pass = {'time_resolution': 'monthly'}
    metadata_to_match_fail = {'time_resolution': 'annual'}

    assert ds.match_metadata(metadata_to_match_pass)
    assert not ds.match_metadata(metadata_to_match_fail)


def test_match_with_irrelevant_metadata(test_dataset_attributes):
    ds = DatasetMetadata(test_dataset_attributes)

    metadata_to_match_irrelevant = {'irrelevance': 'meh'}

    assert ds.match_metadata(metadata_to_match_irrelevant)


def test_match_list(test_dataset_attributes):
    ds = DatasetMetadata(test_dataset_attributes)

    metadata_to_match_pass = {'climatology_start': [1961, 1981]}

    assert ds.match_metadata(metadata_to_match_pass)


def test_no_match_list(test_dataset_attributes):
    ds = DatasetMetadata(test_dataset_attributes)

    metadata_to_match_pass = {'climatology_end': [1900, 2020]}

    assert not ds.match_metadata(metadata_to_match_pass)


def test_collection(test_collection_attributes):
    ds = CollectionMetadata(test_collection_attributes)
    assert ds['version'] == '5.0.1.0'


def test_collection_validation_fail(test_collection_attributes):
    test_collection_attributes['zpos'] = ''
    with pytest.raises(ValidationError):
        ds = CollectionMetadata(test_collection_attributes)


def test_combined(test_dataset_attributes, test_collection_attributes):
    ds = DatasetMetadata(test_dataset_attributes)
    col = CollectionMetadata(test_collection_attributes)

    combo = CombinedMetadata(ds, col)

    assert combo['reader'] == test_dataset_attributes['reader']
    assert combo['variable'] == test_collection_attributes['variable']

def test_comboined_missing_key_raises_error(test_dataset_attributes, test_collection_attributes):
    ds = DatasetMetadata(test_dataset_attributes)
    col = CollectionMetadata(test_collection_attributes)
    combo = CombinedMetadata(ds, col)

    with pytest.raises(KeyError):
        value = combo['dingo_kidneys']

def test_combined_setter(test_dataset_attributes, test_collection_attributes):
    ds = DatasetMetadata(test_dataset_attributes)
    col = CollectionMetadata(test_collection_attributes)
    combo = CombinedMetadata(ds, col)

    combo['reader'] = 'different_reader'
    combo['colour'] = '#333333'

    assert combo['reader'] == 'different_reader'
    assert combo['colour'] == '#333333'


def test_combined_setter_propagates_to_components(test_dataset_attributes, test_collection_attributes):
    ds = DatasetMetadata(test_dataset_attributes)
    col = CollectionMetadata(test_collection_attributes)
    combo = CombinedMetadata(ds, col)

    combo['reader'] = 'different_reader'
    combo['colour'] = '#333333'

    assert ds['reader'] == 'different_reader'
    assert col['colour'] == '#333333'

def test_combined_setter_missing_key_raises_error(test_dataset_attributes, test_collection_attributes):
    ds = DatasetMetadata(test_dataset_attributes)
    col = CollectionMetadata(test_collection_attributes)
    combo = CombinedMetadata(ds, col)

    with pytest.raises(KeyError):
        combo['glitz'] = 'razzledazzle'

def test_combined_contains(test_dataset_attributes, test_collection_attributes):
    ds = DatasetMetadata(test_dataset_attributes)
    col = CollectionMetadata(test_collection_attributes)
    combo = CombinedMetadata(ds, col)

    assert 'reader' in combo
    assert 'colour' in combo

    assert 'glitz' not in combo
