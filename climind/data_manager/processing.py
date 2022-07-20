import json
from jsonschema import validate, RefResolver
from pathlib import Path
from climind.definitions import ROOT_DIR


def get_function(module_path: str, script_name: str, function_name: str):
    """
    For a particular module and script in that module, return the function with
    a specified name

    :param module_path:
    :param script_name:
    :param function_name:
    :return:
    """

    ext = '.'.join([module_path, script_name])
    module = __import__(ext, fromlist=[None])
    chosen_fn = getattr(module, function_name)

    return chosen_fn


class DataSet:

    def __init__(self, attributes: dict):
        """
        A single dataset that may be split across multiple files. For example, monthly global mean
        temperature from Berkeley Earth

        Parameters
        ----------
        attributes : dict
            Dictionary containing the metadata. It must contain: url, type, reader, fetcher

        Attributes
        ----------
        name : str
            Name of the data set
        attributes : dict
            Dictionary of attributes
        """

        self.standard_attributes = ['url', 'type', 'reader',
                                    'fetcher']

        schema_path = Path(ROOT_DIR) / 'climind' / 'data_manager' / 'dataset_schema.json'
        with open(schema_path) as f:
            metadata_schema = json.load(f)
        validate(attributes, metadata_schema)

        self.name = ''
        self.attributes = attributes

    def __str__(self):
        out_str = f'{self.name}\n'
        for attr in self.attributes:
            out_str += f'{attr}: {self.attributes[attr]}\n'

        return out_str

    def match_metadata(self, metadata_to_match: dict) -> bool:
        """
        Check if DataSet attributes match contents of dictionary, metadata_to_match.
        Only items that are in the attributes are checked

        Parameters
        ----------
        metadata_to_match : dict
        """
        match = True

        for key in metadata_to_match:

            if key in self.attributes:

                mtm = metadata_to_match[key]
                att = self.attributes[key]

                if isinstance(mtm, list):
                    # go through list, if any item matches then that counts
                    # as a match
                    this_match = False
                    for item in mtm:
                        if item == att:
                            this_match = True

                    if not this_match:
                        match = False

                else:
                    if mtm != att:
                        match = False

        return match

    def download(self, outdir: Path):
        """
        Download the data set using its "fetcher"

        Parameters
        ----------
        outdir : Path
            Directory to which the data set will be downloaded
        Returns
        -------

        """
        print(f"Downloading {self.attributes['url']}")

        fetch_fn = self._get_fetcher()

        for url in self.attributes['url']:
            fetch_fn(url, outdir)

    def _get_fetcher(self):

        fetcher_name = self.attributes['fetcher']
        fetch_fn = get_function('climind.fetchers', fetcher_name, 'fetch')

        return fetch_fn

    def _get_reader(self):
        reader_name = self.attributes['reader']
        reader_fn = get_function('climind.readers', reader_name, 'read_ts')

        return reader_fn

    def read_dataset(self, outdir: Path):
        """
        Read in the dataset and output an object of the appropriate type.

        Parameters
        ----------
        outdir : Path
            Directory in which the data are to be found (dictated by the Collection)

        Returns
        -------
            Object of the appropriate type
        """
        print(f"Reading {self.attributes['name']} using {self.attributes['reader']}")
        reader_fn = self._get_reader()
        return reader_fn(outdir, self.attributes)


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
        global_attributes : dict
            Dictionary containing the attributes that apply to all DataSets in the DataCollection
        datasets : dict
            Dictionary containing all the DataSets
        """
        self.global_attributes = {}
        self.datasets = []

        # copy all metadata except datasets into global attributes
        for key in metadata:
            if key != 'datasets':
                self.global_attributes[key] = metadata[key]

            else:
                # for each dataset in the datasets section create a DataSet
                for item in metadata['datasets']:
                    # Combine global metadata with individual dataset metadata
                    all_metadata = {**self.global_attributes, **item}
                    self.add_dataset(DataSet(all_metadata))

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
        rebuilt = self.global_attributes
        rebuilt['datasets'] = []
        for key in self.datasets:
            for globalkey in self.global_attributes:
                if globalkey in key.attributes:
                    key.attributes.pop(globalkey)
            rebuilt['datasets'].append(key.attributes)

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
        for key in metadata_to_match:
            if key in self.global_attributes:

                mtm = metadata_to_match[key]
                att = self.global_attributes[key]

                if isinstance(mtm, list):
                    this_match = False
                    for item in mtm:
                        if item == att:
                            this_match = True
                    if not this_match:
                        return None

                else:

                    if mtm != att:
                        return None

        out_collection = DataCollection({})
        out_collection.global_attributes = self.global_attributes

        at_least_one_match = False

        for key in self.datasets:
            if key.match_metadata(metadata_to_match):
                out_collection.add_dataset(key)
                at_least_one_match = True

        if not at_least_one_match:
            return None

        return out_collection

    def get_collection_dir(self, data_dir):
        """
        Get the Path to the directory where the data for this collection are stored.
        If the directory does not exist, then create it.

        :param data_dir: Path
            Path to the general data directory for managed data in the project
        :return:
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

    def read_datasets(self, out_dir: Path) -> list:
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
            all_datasets.append(key.read_dataset(collection_dir))

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

    def read_datasets(self, out_dir: Path) -> list:
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
            these_datasets = self.collections[key].read_datasets(out_dir)
            for ds in these_datasets:
                all_datasets.append(ds)

        return all_datasets
