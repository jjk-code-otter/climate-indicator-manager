import pytest
from pathlib import Path
import climind.data_manager.processing as dm


class TestDataSet:

    def test_basic_creation(self):
        attributes = {'url': 'test_url',
                      'type': 'test_type',
                      'reader': 'test_reader',
                      'fetcher': 'test_fetcher'}

        ds = dm.DataSet(attributes)

        for key in attributes:
            assert ds.attributes[key] == attributes[key]

    def test_missing_standard_attribute(self):
        attributes = {'url': 'test_url',
                      'reader': 'test_reader',
                      'fetcher': 'test_fetcher'}

        with pytest.raises(KeyError):
            ds = dm.DataSet(attributes)

    def test_match(self):
        attributes = {'url': 'test_url',
                      'type': 'test_type',
                      'reader': 'test_reader',
                      'fetcher': 'test_fetcher'}

        ds = dm.DataSet(attributes)

        metadata_to_match_pass = {'url': 'test_url'}
        metadata_to_match_fail = {'url': 'wrong_url'}

        assert ds.match_metadata(metadata_to_match_pass)
        assert not ds.match_metadata(metadata_to_match_fail)

    def test_match_with_irrelevant_metadata(self):
        attributes = {'url': 'test_url',
                      'type': 'test_type',
                      'reader': 'test_reader',
                      'fetcher': 'test_fetcher'}

        ds = dm.DataSet(attributes)

        metadata_to_match_irrelevant = {'irrelevance': 'meh'}

        assert ds.match_metadata(metadata_to_match_irrelevant)


class TestDataCollection:

    def test_creation_from_file(self):
        dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
        assert isinstance(dc, dm.DataCollection)

        assert dc.global_attributes['name'] == 'HadCRUT5'

    def test_select(self):
        dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
        subdc = dc.match_metadata({'type': 'gridded'})

        for dataset in subdc.datasets:
            assert dataset.attributes['type'] == 'gridded'

    def test_select_without_a_match(self):
        dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
        subdc = dc.match_metadata({'type': 'renault'})
        assert subdc is None

    def test_select_match_global_but_not_dataset(self):
        dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
        subdc = dc.match_metadata({'variable': 'tas',
                                   'type': 'renault'})
        assert subdc is None

    def test_select_no_match_in_global(self):
        dc = dm.DataCollection.from_file(Path('test_data/hadcrut5.json'))
        subdc = dc.match_metadata({'variable': 'mslp'})
        assert subdc is None

    def test_creation_from_empty_dict(self):
        dc = dm.DataCollection({})
        assert isinstance(dc, dm.DataCollection)


class TestDataArchive:

    def test_creation_from_directory(self):
        metadata_dir = Path('test_data')
        da = dm.DataArchive.from_directory(metadata_dir)
        assert isinstance(da, dm.DataArchive)

    def test_select(self):
        metadata_dir = Path('test_data')
        da = dm.DataArchive.from_directory(metadata_dir)

        selected_da = da.select({'type': 'gridded'})

        print(selected_da)
