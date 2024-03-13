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
"""
The classes and functions in this script describe groupings of metadata. The basic building
block is a :class:`DataSet`, which specifies a file (or files) which contains the data for a single
data set. :class:`DataSet` objects are grouped into :class:`DataCollection` objects, which gather
together all the individual data sets which are derived from a single product. For example,
HadCRUT5 is a product and so it has a corresponding DataCollection made up of several :class:`DataSet`
objects. Finally, a :class:`DataArchive` contains one or more :class:`DataCollection` objects. All
:class:`.DataSet` objects in a :class:`.DataCollection` will be the same variable. However, :class:`.DataCollection`
objects in a :class:`.DataArchive` need not be the same variable.
"""
import json
from jsonschema import validate, RefResolver
from typing import Callable, List, Union
from pathlib import Path
from climind.data_manager.metadata import CollectionMetadata, DatasetMetadata, CombinedMetadata
from climind.definitions import ROOT_DIR


def get_function(module_path: str, script_name: str, function_name: str) -> Callable:
    """
    For a particular module and script in that module, return the function with
    a specified name as a callable object.

    Parameters
    ----------
    module_path: str
        The path to the module written using dot separation between directories
    script_name: str
        The name of the script
    function_name: str
        The name of the function in the script to be returned

    Returns
    -------
    Callable
        Returns the function with the specified function name from the script with
        the specified script name in the specified module path
    """

    ext = '.'.join([module_path, script_name])
    module = __import__(ext, fromlist=[None])
    chosen_fn = getattr(module, function_name)

    return chosen_fn


class DataSet:
    """
    A :class:`.DataSet` contains *metadata* for a single dataset (one that might be split across multiple
    files). For example, NSIDC monthly sea ice extent data is a single data set provided
    in 12 files, one for each month. In contrast, HadCRUT5 monthly global mean temperature
    is a single file. Both of these would be described by a :class:`.DataSet`. They can be used to
    read in the actual data.
    """

    def __init__(self, metadata: DatasetMetadata, global_metadata: CollectionMetadata):
        """
        Create a :class:`.DataSet` from :class:`.DatasetMetadata` and :class:`CollectionMetadata`.

        Parameters
        ----------
        metadata : DatasetMetadata
            :class:`.DatasetMetadata` containing the dataset metadata.
        global_metadata : CollectionMetadata
            :class:`CollectionMetadata` containing the global metadata

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
        Check if there is a mismatch between attributes of :class:`DataSet` and the contents of a dictionary,
        metadata_to_match. Only items that are in the attributes are checked.

        Parameters
        ----------
        metadata_to_match : dict
            Dictionary of key-value or key-list pairs to match. If a key-list is provided then each element of the
            list is checked and a mismatch only occurs if all of the items in the list cause a mismatch.
        Returns
        -------
        bool
            Return True unless there is a mismatch in which case return False
        """
        return self.metadata.match_metadata(metadata_to_match)

    def download(self, out_dir: Path) -> None:
        """
        Download the data set using its "fetcher" function. Fetcher functions are contained in the fetchers
        package.

        Parameters
        ----------
        out_dir : Path
            Directory to which the data set will be downloaded
        Returns
        -------
        None
        """

        fetch_fn = self._get_fetcher()

        for url, filename in zip(self.metadata['url'], self.metadata['filename']):
            print(f"Downloading {url} to filename {filename}")
            fetch_fn(url, out_dir, filename)

    def _get_fetcher(self) -> Callable:
        """
        Get the fetcher function for this dataset. This is the function
        specified in the dataset metadata which downloads the datasets files

        Returns
        -------
        Callable
            Function that will, given appropriate inputs, download the dataset files
        """
        fetcher_name = self.metadata['fetcher']
        fetch_fn = get_function('climind.fetchers', fetcher_name, 'fetch')

        return fetch_fn

    def _get_reader(self) -> Callable:
        """
        Get the reader function for this dataset. This is the function
        specified in the dataset metadata which reads in the dataset and converts
        it to an appropriate internal representation.

        Returns
        -------
        Callable
            Function that will, given appropriate inputs, read in a data file
        """
        reader_name = self.metadata['reader']
        reader_fn = get_function('climind.readers', reader_name, 'read_ts')

        return reader_fn

    def read_dataset(self, out_dir: Union[List[Path], Path], **kwargs):
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
        if type(out_dir) is not list:
            out_dir = [out_dir]

        # print(f"Reading {self.metadata['name']} using {self.metadata['reader']}")
        reader_fn = self._get_reader()
        exceptions = []
        success = False
        for dir in out_dir:
            try:
                self.data = reader_fn(dir, self.metadata, **kwargs)
                success = True
            except Exception as e:
                exceptions.append(str(e))

        if not success:
            exceptions = ' '.join(exceptions)
            raise RuntimeError(f"Error occurred while executing reader_fn: {exceptions}")

        return self.data


class DataCollection:
    """
    A grouping of :class:`DataSet` objects derived from a single product or source. e.g. HadCRUT5.
    This could include, for example, monthly and annual time series along with the
    gridded data.
    """

    def __init__(self, metadata: dict):
        """
        Create :class:`.DataCollection` from a metadata dictionary.

        Parameters
        ----------
        metadata : dict

        Attributes
        ----------
        global_attributes : CollectionMetadata
            Metadata containing the attributes that apply to all DataSets in the
            :class:`.DataCollection`
        datasets : List[DataSet]
            List containing all the :class:`.DataSet` objects in this collection
        """
        global_attributes = {}
        self.datasets = []

        # copy all metadata except datasets into global attributes and create
        # the collection metadata
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
        Given a file path create the :class:`.DataCollection` from metadata in that file

        Parameters
        ----------
        filename : Path
            Filename of the metadata file in json format
        Returns
        -------
        DataCollection
            DataCollection containing all the :class:`.DataSet` objects specified by the
            metadata file
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
        Build the metadata for the :class:`.DataCollection`, bringing together global and dataset metadata

        Returns
        -------
        dict
            A dictionary containing all the metadata from the :class:`.DataCollection`.
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

    def to_file(self, filename: Path) -> None:
        """
        Write the :class:`.DataCollection` metadata to file in json format.

        Parameters
        ----------
        filename: Path
            Path to the file to be written
        Returns
        -------
        None
        """
        rebuilt = self._rebuild_metadata()
        with open(filename, 'w') as f:
            json.dump(rebuilt, f)

    def add_dataset(self, ds: DataSet) -> None:
        """
        Add :class:`.DataSet` object to :class:`.DataCollection`


        Parameters
        ----------
        ds : DataSet
            DataSet to be added
        Returns
        -------
        None
        """
        self.datasets.append(ds)

    def match_metadata(self, metadata_to_match: dict):
        """
        Given a dictionary of metadata keys and required values for each key,
        return a :class:`DataCollection` which contains only data sets matching the specified
        metadata

        Parameters
        ----------
        metadata_to_match : dict
            Dictionary containing key:value pairs that specify the data sets required
            in the output :class:`DataCollection`
        Returns
        -------
        DataCollection
            Return :class:`DataCollection` that matches the metadata_to_match
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

    def get_collection_dir(self, data_dir: Path) -> Path:
        """
        Get the Path to the directory where the data for this :class:`.DataCollection` are stored.
        If the directory does not exist, then create it.

        Parameters
        ----------
        data_dir: Path
            Path to the general data directory for managed data in the project

        Returns
        --------
        Path
            Path to the directory for this :class:`DataCollection`.
        """
        collection_dir = data_dir / self.global_attributes['name']
        collection_dir.mkdir(exist_ok=True)
        return collection_dir

    def download(self, data_dir: Path) -> None:
        """
        Download all the data sets described by :class:`.DataSet` objects in the :class:`.DataCollection`.

        Parameters
        ----------
        data_dir : Path
            Location to which the datasets should be downloaded
        Returns
        -------
        None
        """
        collection_dir = self.get_collection_dir(data_dir)

        for key in self.datasets:
            key.download(collection_dir)

    def read_datasets(self, out_dir: Union[Path, List[Path]], **kwargs) -> list:
        """
        Read all the datasets described by :class:`.DataSet` objects in the :class:`DataCollection`

        Parameters
        ----------
        out_dir : Path
            Directory in which the datasets are found

        Returns
        -------
        list
            Return list of all data sets described in the :class:`DataCollection`.
        """
        if type(out_dir) is list:
            collection_dir = [x / self.global_attributes['name'] for x in out_dir]
        else:
            collection_dir = out_dir / self.global_attributes['name']

        all_datasets = []

        for dataset in self.datasets:
            try:
                read_in_dataset = dataset.read_dataset(collection_dir, **kwargs)
            except Exception as e:
                raise RuntimeError(f"Failed to read {dataset.metadata['name']} with error message {e}")
            else:
                all_datasets.append(read_in_dataset)

        return all_datasets


class DataArchive:
    """
    A set of :class:`DataCollection` objects. A class:`DataArchive` is the starting point for
    the analysis. Particular :class:`DataSet` objects are selected from the class:`DataArchive`
    before plotting or summarising the data.
    """

    def __init__(self):
        """
        Create a :class:`DataArchive` object, initially empty.

        Attributes
        ----------
        collections : dict
            A dictionary containing the :class:`.DataCollection` objects in the archive
        """
        self.collections = {}

    def __str__(self):
        out_str = ''
        for c in self.collections:
            out_str += f'{c}\n'
            out_str += str(self.collections[c])
            out_str += '\n'

        return out_str

    def add_collection(self, data_collection: DataCollection) -> None:
        """
        Add a :class:`DataCollection` to the archive

        Parameters
        ----------
        data_collection : DataCollection
            :class:`DataCollection` to be added to the :class:`DataArchive`
        Returns
        -------
        None
        """
        self.collections[data_collection.global_attributes['name']] = data_collection

    def select(self, metadata_to_match: dict):
        """
        Select datasets from the :class:`DataArchive` that meet the metadata requirements specified
        in the metadata_to_match dictionary.

        Parameters
        ----------
        metadata_to_match : dict
            Metadata to be matched. For each requirement, there should be a key-value pair
        Returns
        -------
        DataArchive
            Returns :class:`DataArchive` containing only data that match the metadata_to_match
        """

        out_arch = DataArchive()

        for c in self.collections:
            selected_collection = self.collections[c].match_metadata(metadata_to_match)
            if selected_collection is not None:
                out_arch.add_collection(selected_collection)

        return out_arch

    @staticmethod
    def from_directory(path_to_dir: Union[List[Path], Path]):
        """
        Create a :class:`DataArchive` from a directory of metadata. The directory should contain a
        set of json files each of which contains a set of metadata describing a :class:`DataCollection`

        Parameters
        ----------
        path_to_dir : Path or List[Path]
            Path to the directory containing the metadata files that will be used
            to populate the :class:`DataArchive` or a list of such Paths.
        Returns
        -------
        DataArchive
            :class:`DataArchive` containing all :class:`DataCollection` objects described in the
            metadata files
        """
        out_archive = DataArchive()

        if type(path_to_dir) is not list:
            path_to_dir = [path_to_dir]

        for single_path in path_to_dir:
            for json_file in single_path.rglob('*.json'):
                dc = DataCollection.from_file(json_file)
                out_archive.add_collection(dc)

        return out_archive

    def download(self, out_dir: Path) -> None:
        """
        Download all files in the :class:`DataArchive`.

        Parameters
        ----------
        out_dir : Path
            Directory to which the files should be downloaded
        Returns
        -------
        None
        """
        for key in self.collections:
            self.collections[key].download(out_dir)

    def read_datasets(self, out_dir: Path, **kwargs) -> list:
        """
        Read all the datasets in the :class:`DataArchive`.

        Parameters
        ----------
        out_dir : Path
            Path of directory containing the data
        Returns
        -------
        list
            List of datasets specified by metadata in the archive.
        """
        all_datasets = []

        for key in self.collections:
            these_datasets = self.collections[key].read_datasets(out_dir, **kwargs)
            for ds in these_datasets:
                all_datasets.append(ds)

        return all_datasets
