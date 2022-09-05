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
import copy

import pytest
import json
from pathlib import Path

from jsonschema import ValidationError, validate, RefResolver

from climind.definitions import ROOT_DIR
from climind.data_manager.metadata import DatasetMetadata, CollectionMetadata, BaseMetadata, CombinedMetadata, \
    list_match

schema_path = Path(ROOT_DIR) / 'climind' / 'data_manager' / 'dataset_schema.json'
with open(schema_path) as f:
    dataset_schema = json.load(f)

schema_path = Path(ROOT_DIR) / 'climind' / 'data_manager' / 'metadata_schema.json'
with open(schema_path) as f:
    collection_schema = json.load(f)

combined_schema = copy.deepcopy(collection_schema)
combined_schema["properties"]["datasets"]["items"]["$ref"] = "#/$defs/dataset"
combined_schema["$defs"] = {"dataset": dataset_schema}

collection_schema["properties"]["datasets"]["items"]["type"] = "string"


@pytest.fixture
def test_dataset_attributes():
    attributes = {'url': ['test_url'],
                  'filename': ['test_filename', 'test_filename VVVV'],
                  'type': 'gridded',
                  'time_resolution': 'monthly',
                  'space_resolution': 999,
                  'climatology_start': 1961,
                  'climatology_end': 1990,
                  'actual': False,
                  'derived': False,
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher',
                  'history': ['AAAA', 'AAAB', 'BBBB'],
                  'notes': 'This says BBBB'
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
                  "citation_url": ["kttps://notaurul"],
                  "data_citation": [""],
                  "acknowledgement": "Version VVVV of the data set was downloaded AAAA in the year of our lord YYYY",
                  "colour": "#444444",
                  "zpos": 99
                  }

    return attributes


def test_list_match():
    assert list_match(['match', 'not match'], 'match')
    assert list_match(['match', 'match'], 'match')
    assert not list_match(['not match', 'not match'], 'match')


def test_base_metadata_set_and_get():
    bm = BaseMetadata({'flash': 'aha'})
    assert bm['flash'] == 'aha'

    bm['saviour'] = 'universe'
    assert bm['saviour'] == 'universe'


def test_base_metadata_get_missing_key():
    bm = BaseMetadata({'flash': 'aha'})
    with pytest.raises(KeyError):
        _ = bm['nonexistent key']


def test_print_base_metadata():
    bm = BaseMetadata({'flash': 'aha'})

    test_string = str(bm)

    assert 'flash' in test_string
    assert 'aha' in test_string


def tests_fill_string(test_dataset_attributes):
    bm = BaseMetadata(test_dataset_attributes)

    replacement = '3456'
    save_value = copy.deepcopy(bm['history'][1])

    bm.fill_string('AAAA', replacement)
    assert bm['history'][0] == replacement
    assert bm['history'][1] == save_value


def tests_fill_string_again(test_dataset_attributes):
    bm = BaseMetadata(test_dataset_attributes)

    replacement = '99'
    save_value0 = copy.deepcopy(bm['history'][0])
    save_value1 = copy.deepcopy(bm['history'][1])

    bm.fill_string('BBBB', replacement)

    assert bm['history'][0] == save_value0
    assert bm['history'][1] == save_value1
    assert bm['history'][2] == replacement
    assert replacement in bm['notes']
    assert 'BBBB' not in bm['notes']

    return


# DatasetMetadata

def test_missing_standard_attribute_in_dataset():
    attributes = {'url': 'test_url',
                  'reader': 'test_reader',
                  'fetcher': 'test_fetcher'}

    with pytest.raises(ValidationError):
        _ = DatasetMetadata(attributes)


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


def test_creation_message(test_dataset_attributes):
    ds = DatasetMetadata(test_dataset_attributes)
    datestamp = '2099-09-07'
    ds['last_modified'] = datestamp

    history_length = len(ds['history'])

    ds.creation_message()

    # adds an item to the history and that item contains the last_modified attribute
    assert len(ds['history']) == history_length + 1
    assert datestamp in ds['history'][history_length]
    assert ds['url'][0] in ds['history'][history_length]
    assert ds['filename'][0] in ds['history'][history_length]

# CollectionMetadata

def test_collection(test_collection_attributes):
    ds = CollectionMetadata(test_collection_attributes)
    assert ds['version'] == '5.0.1.0'


def test_collection_validation_fail(test_collection_attributes):
    test_collection_attributes['zpos'] = ''
    with pytest.raises(ValidationError):
        _ = CollectionMetadata(test_collection_attributes)


def test_combined(test_dataset_attributes, test_collection_attributes):
    ds = DatasetMetadata(test_dataset_attributes)
    col = CollectionMetadata(test_collection_attributes)

    combo = CombinedMetadata(ds, col)

    assert combo['reader'] == test_dataset_attributes['reader']
    assert combo['variable'] == test_collection_attributes['variable']


def test_combined_missing_key_raises_error(test_dataset_attributes, test_collection_attributes):
    ds = DatasetMetadata(test_dataset_attributes)
    col = CollectionMetadata(test_collection_attributes)
    combo = CombinedMetadata(ds, col)

    with pytest.raises(KeyError):
        _ = combo['dingo_kidneys']


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


def test_combined_write(test_dataset_attributes, test_collection_attributes, tmpdir):
    ds = DatasetMetadata(test_dataset_attributes)
    col = CollectionMetadata(test_collection_attributes)
    combo = CombinedMetadata(ds, col)
    print(tmpdir)
    json_file = Path(tmpdir) / 'test.json'
    combo.write_metadata(json_file)

    assert json_file.exists()

    with open(json_file, 'r') as test_file:
        read_in_json = json.load(test_file)

    schema_path = Path(ROOT_DIR) / 'climind' / 'data_manager' / 'metadata_schema.json'
    with open(schema_path) as f:
        metadata_schema = json.load(f)
    resolver = RefResolver(schema_path.as_uri(), metadata_schema)
    validate(read_in_json, metadata_schema, resolver=resolver)


def test_combined_creation_message(test_dataset_attributes, test_collection_attributes):
    datestamp = '2075-01-19 12:34:56'
    test_dataset_attributes['last_modified'] = [datestamp]

    filled_acknowledgement = test_collection_attributes['acknowledgement']
    filled_acknowledgement = filled_acknowledgement.replace('AAAA', datestamp)
    filled_acknowledgement = filled_acknowledgement.replace('YYYY', '2075')
    filled_acknowledgement = filled_acknowledgement.replace('VVVV', test_collection_attributes['version'])

    ds = DatasetMetadata(test_dataset_attributes)
    col = CollectionMetadata(test_collection_attributes)
    combo = CombinedMetadata(ds, col)

    combo.creation_message()

    assert datestamp in combo['acknowledgement']
    assert combo['history'][0] == datestamp
    assert combo['acknowledgement'] == filled_acknowledgement