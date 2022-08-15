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

import json
from jsonschema import validate, RefResolver
from pathlib import Path
from climind.data_manager.metadata import CollectionMetadata, DatasetMetadata, CombinedMetadata
from climind.definitions import ROOT_DIR


def get_function(module_path: str, script_name: str, function_name: str):
    """
    For a particular module and script in that module, return the function with
    a specified name

    Parameters
    ----------
    module_path: str
        The path to the module
    script_name: str
        The name of the script
    function_name: str
        The name of the function

    Returns
    -------
    function
        Returns the function with the specified function name from the script with
        the specified script name in the specified module path
    """

    ext = '.'.join([module_path, script_name])
    module = __import__(ext, fromlist=[None])
    chosen_fn = getattr(module, function_name)

    return chosen_fn


class DataSet:

    def __init__(self, metadata: DatasetMetadata, global_metadata: CollectionMetadata):
        """
        A single dataset that may be split across multiple files. For example, monthly global mean
        temperature from Berkeley Earth

        Parameters
        ----------
        metadata : DatasetMetadata
            DatasetMetadata containing the dataset metadata.
        global_metadata : CollectionMetadata
            CollectionMetadata containing the global metadata

        Attributes
        ----------
        name : str
            Name of the data set
        metadata : dict
            Dictionary of attributes
        global_metadata : dict
            Dictionary of global attributes inherited from collection
        """
        self.metadata = CombinedMetadata(metadata, global_metadata)
        self.data = None

    def __str__(self):
        out_str = f"{self.metadata['name']}\n"
        out_str += str(self.metadata)

        return out_str

    def match_metadata(self, metadata_to_match: dict) -> bool:
        """
        Check if DataSet attributes match contents of dictionary, metadata_to_match.
        Only items that are in the attributes are checked.

        Parameters
        ----------
        metadata_to_match : dict
            Dictionary of key-value or key-list pairs to match.
        """
        return self.metadata.match_metadata(metadata_to_match)

    def download(self, out_dir: Path):
        """
        Download the data set using its "fetcher"

        Parameters
        ----------
        out_dir : Path
            Directory to which the data set will be downloaded
        Returns
        -------

        """

        fetch_fn = self._get_fetcher()

        for url in self.metadata['url']:
            print(f"Downloading {url}")
            fetch_fn(url, out_dir)

    def _get_fetcher(self):
        """
        Get the fetcher function for this dataset. This is the function
        specified in the dataset metadata which downloads the datasets files

        Returns
        -------
        function
            Function that will, given appropriate inputs, download the dataset files
        """
        fetcher_name = self.metadata['fetcher']
        fetch_fn = get_function('climind.fetchers', fetcher_name, 'fetch')

        return fetch_fn

    def _get_reader(self):
        """
        Get the reader function for this dataset. This is the function
        specified in the dataset metadata which reads in the dataset and converts
        it to an appropriate internal representation.

        Returns
        -------
        function
        """
        reader_name = self.metadata['reader']
        reader_fn = get_function('climind.readers', reader_name, 'read_ts')

        return reader_fn

    def read_dataset(self, out_dir: Path, **kwargs):
        """
        Read in the dataset and output an object of the appropriate type.

        Parameters
        ----------
        out_dir : Path
            Directory in which the data are to be found (dictated by the Collection)

        Returns
        -------
            Object of the appropriate type
        """
        print(f"Reading {self.metadata['name']} using {self.metadata['reader']}")
        reader_fn = self._get_reader()
        self.data = reader_fn(out_dir, self.metadata, **kwargs)
        return self.data


class DataCollection:
    """
    A grouping of data sets derived from a single source. e.g. HadCRUT5. This could include, for example,
    monthly and annual time series and the gridded data.
    """

    def __init__(self, metadata: dict):
        """

        Parameters
        ----------
        metadata : dict

        Attributes
        ----------
        global_attributes : CollectionMetadata
            Metadata containing the attributes that apply to all DataSets in the DataCollection
        datasets : list
            List containing all the DataSets
        """
        global_attributes = {}
        self.datasets = []

        # copy all metadata except datasets into global attributes
        for key in metadata:
            if key != 'datasets':
                global_attributes[key] = metadata[key]

        self.global_attributes = CollectionMetadata(global_attributes)

        for key in metadata:
            if key == 'datasets':
                # for each dataset in the datasets section create a DataSet
                for item in metadata['datasets']:
                    # Combine global metadata with individual dataset metadata
                    dataset_metadata = DatasetMetadata(item)
                    self.add_dataset(DataSet(dataset_metadata, self.global_attributes))

    def __str__(self):
        out_str = f"{self.global_attributes['name']} " \
                  f"version:{self.global_attributes['version']}\n"
        for d in self.datasets:
            out_str += str(d)
        return out_str

    @staticmethod
    def from_file(filename: Path):
        """
        Given a file path create the DataCollection from metadata in that file
        Parameters
        ----------
        filename : Path
            Filename of the metadata file in json format
        Returns
        -------

        """
        with open(filename, 'r') as f:
            metadata_from_file = json.load(f)

        schema_path = Path(ROOT_DIR) / 'climind' / 'data_manager' / 'metadata_schema.json'
        with open(schema_path) as f:
            metadata_schema = json.load(f)

        resolver = RefResolver(schema_path.as_uri(), metadata_schema)
        validate(metadata_from_file, metadata_schema, resolver=resolver)

        return DataCollection(metadata_from_file)

    def _rebuild_metadata(self) -> dict:
        """
        Build the metadata for the collection, bringing together global and dataset metadata

        Returns
        -------
        dict
        """
        rebuilt = self.global_attributes.metadata
        rebuilt['datasets'] = []
        for key in self.datasets:
            rebuilt['datasets'].append(key.metadata.dataset.metadata)

        schema_path = Path(ROOT_DIR) / 'climind' / 'data_manager' / 'metadata_schema.json'
        with open(schema_path) as f:
            metadata_schema = json.load(f)
        resolver = RefResolver(schema_path.as_uri(), metadata_schema)
        validate(rebuilt, metadata_schema, resolver=resolver)

        return rebuilt

    def to_file(self, filename: Path):
        """
        Write the collection metadata to file

        Parameters
        ----------
        filename

        Returns
        -------

        """
        rebuilt = self._rebuild_metadata()
        with open(filename, 'w') as f:
            json.dump(rebuilt, f)

    def add_dataset(self, ds: DataSet) -> None:
        """
        Add dataset to collection

        Parameters
        ----------
        ds : DataSet
            DataSet to be added
        Returns
        -------

        """
        self.datasets.append(ds)

    def match_metadata(self, metadata_to_match: dict):
        """
        Given a dictionary of metadata keys and required values for each key,
        return a DataCollection which contains only data sets matching the specified
        metadata

        Parameters
        ----------
        metadata_to_match : dict
            Dictionary containing key:value pairs that specify the data sets required
            in the output DataCollection
        Returns
        -------
        DataCollection
        """
        if not self.global_attributes.match_metadata(metadata_to_match):
            return None

        out_collection = DataCollection(self.global_attributes.metadata)

        at_least_one_match = False

        for ds in self.datasets:
            if ds.match_metadata(metadata_to_match):
                out_collection.add_dataset(ds)
                at_least_one_match = True

        if not at_least_one_match:
            return None

        return out_collection

    def get_collection_dir(self, data_dir: Path):
        """
        Get the Path to the directory where the data for this collection are stored.
        If the directory does not exist, then create it.

        Parameters
        ----------
        data_dir: Path
            Path to the general data directory for managed data in the project

        Returns
        --------
        Path
            Path to the directory for this DataCollection
        """
        collection_dir = data_dir / self.global_attributes['name']
        collection_dir.mkdir(exist_ok=True)
        return collection_dir

    def download(self, data_dir: Path):
        """
        Download all the data sets in the collection

        Parameters
        ----------
        data_dir : Path
            Location to which the datasets should be downloaded
        Returns
        -------

        """
        collection_dir = self.get_collection_dir(data_dir)

        for key in self.datasets:
            key.download(collection_dir)

    def read_datasets(self, out_dir: Path, **kwargs) -> list:
        """
        Read all the datasets in the DataCollection

        Parameters
        ----------
        out_dir : Path
            Directory in which the datasets are found

        Returns
        -------
        list
        """
        collection_dir = out_dir / self.global_attributes['name']
        collection_dir.mkdir(exist_ok=True)

        all_datasets = []

        for key in self.datasets:
            all_datasets.append(key.read_dataset(collection_dir, **kwargs))

        return all_datasets


class DataArchive:

    def __init__(self):
        """
        A grouping of multiple DataCollections

        Attributes
        ----------
        collections : dict
            A dictionary containing the collections in the archive
        """
        self.collections = {}

    def __str__(self):
        out_str = ''
        for c in self.collections:
            out_str += f'{c}\n'
            out_str += str(self.collections[c])
            out_str += '\n'

        return out_str

    def add_collection(self, data_collection: DataCollection):
        """
        Add a DataCollection to the archive

        Parameters
        ----------
        data_collection : DataCollection
        """
        self.collections[data_collection.global_attributes['name']] = data_collection

    def select(self, metadata_to_match: dict):
        """
        Select datasets from the archive that meet the metadata requirements specified
        in the metadata_to_match dictionary.

        Parameters
        ----------
        metadata_to_match : dict
            Metadata to be matched. For each requirement, there should be a key-value pair
        Returns
        -------
        DataArchive
        """

        out_arch = DataArchive()

        for c in self.collections:
            selected_collection = self.collections[c].match_metadata(metadata_to_match)
            if selected_collection is not None:
                out_arch.add_collection(selected_collection)

        return out_arch

    @staticmethod
    def from_directory(path_to_dir: Path):
        """
        Create a data archive from a directory of metadata. The directory should contain a
        set of json files each of which contains a set of metadata

        Parameters
        ----------
        path_to_dir : Path
        """
        out_archive = DataArchive()

        for json_file in path_to_dir.glob('*.json'):
            dc = DataCollection.from_file(json_file)
            out_archive.add_collection(dc)

        return out_archive

    def download(self, out_dir: Path):
        """
        Download all files in the data archive

        Parameters
        ----------
        out_dir : Path
            Directory to which the files should be downloaded
        """
        for key in self.collections:
            self.collections[key].download(out_dir)

    def read_datasets(self, out_dir: Path, **kwargs) -> list:
        """
        Read all the datasets in the archive

        Parameters
        ----------
        out_dir : Path
            Path of directory containing the data
        Returns
        -------

        """
        all_datasets = []

        for key in self.collections:
            these_datasets = self.collections[key].read_datasets(out_dir, **kwargs)
            for ds in these_datasets:
                all_datasets.append(ds)

        return all_datasets
