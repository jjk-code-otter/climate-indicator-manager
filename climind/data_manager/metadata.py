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
from pathlib import Path
from jsonschema import validate, RefResolver
from climind.definitions import ROOT_DIR


def list_match(list_to_match: list, attribute) -> bool:
    """
    If att matches any item in mtm return True, otherwise False

    Parameters
    ----------
    list_to_match: list
        List of metadata to match
    attribute:
        attribute to check against

    Returns
    -------
    bool
        Set to True if attribute matches element in list_to_match, False otherwise
    """
    return attribute in list_to_match


class BaseMetadata:
    """
    Simple class to store metadata and find matches
    """

    def __init__(self, metadata: dict):
        """

        Parameters
        ----------
        metadata : dict
            Dictionary containing the metadata
        """
        self.metadata = metadata

    def __getitem__(self, key):
        if key in self.metadata:
            return self.metadata[key]
        else:
            raise KeyError

    def __setitem__(self, key, item):
        self.metadata[key] = item

    def __contains__(self, key):
        if key in self.metadata:
            return True
        else:
            return False

    def __str__(self):
        out_str = ''
        for key in self.metadata:
            out_str += f"{key}: {str(self[key])}\n"
        return out_str

    def match_metadata(self, metadata_to_match: dict) -> bool:
        """
        Check if metadata match contents of dictionary, metadata_to_match. Only
        definite non-matches are rejected. If a key is not found in the
        dictionary this not counted as a non-match.

        Parameters
        ----------
        metadata_to_match : dict
            Key-value or key-list pairs for match
        """
        match = True

        common_keys = metadata_to_match.keys() & self.metadata.keys()
        for key in common_keys:

            mtm = metadata_to_match[key]
            att = self.metadata[key]

            if isinstance(mtm, list):
                if not list_match(mtm, att):
                    match = False
            else:
                if mtm != att:
                    match = False

        return match

    def fill_string(self, string_to_replace: str, replacement: str):
        """
        Replace string_to_replace with the replacement value in all elements

        Parameters
        ----------
        string_to_replace: str
            string to be replaced in metadata elements
        replacement: str
            replacement string
        Returns
        -------
        None
        """
        for key in self.metadata:
            item = self.metadata[key]
            if isinstance(item, str):
                item = item.replace(string_to_replace, replacement)
                self.metadata[key] = item
            elif isinstance(item, list):
                replacement_list = []
                for entry in item:
                    entry = entry.replace(string_to_replace, replacement)
                    replacement_list.append(entry)
                self.metadata[key] = replacement_list


class CollectionMetadata(BaseMetadata):

    def __init__(self, metadata: dict):
        schema_path = Path(ROOT_DIR) / 'climind' / 'data_manager' / 'metadata_schema.json'
        with open(schema_path) as f:
            metadata_schema = json.load(f)
        resolver = RefResolver(schema_path.as_uri(), metadata_schema)
        validate(metadata, metadata_schema, resolver=resolver)

        super().__init__(metadata)


class DatasetMetadata(BaseMetadata):

    def __init__(self, metadata: dict):
        schema_path = Path(ROOT_DIR) / 'climind' / 'data_manager' / 'dataset_schema.json'
        with open(schema_path) as f:
            metadata_schema = json.load(f)
        validate(metadata, metadata_schema)

        super().__init__(metadata)

    def creation_message(self):
        """
        Add creation message to the history

        Returns
        -------

        """
        download_message = f"Data set created from file {self.metadata['filename']} " \
                           f"downloaded from {self.metadata['url']} " \
                           f"at {self.metadata['last_modified']}"

        self.metadata['history'].append(download_message)


class CombinedMetadata:

    def __init__(self, dataset: DatasetMetadata, collection: CollectionMetadata):

        self.dataset = dataset
        self.collection = collection

    def __getitem__(self, key):
        if key in self.dataset:
            return self.dataset[key]
        elif key in self.collection:
            return self.collection[key]
        else:
            raise KeyError

    def __setitem__(self, key, value):
        if key in self.dataset:
            self.dataset[key] = value
        elif key in self.collection:
            self.collection[key] = value
        else:
            raise KeyError

    def __contains__(self, key):
        if key in self.dataset:
            return True
        elif key in self.collection:
            return True
        else:
            return False

    def __str__(self):
        outstr = ''
        outstr += str(self.collection)
        outstr += '\n'
        outstr += str(self.dataset)
        outstr += '\n'
        return outstr

    def match_metadata(self, metadata_to_match: dict) -> bool:
        """
        Test to see if metadata matches metadata to match. Returns True unless there is a mismatch
        between the required metadata_to_match and the metadata.

        Parameters
        ----------
        metadata_to_match: dict
            Dictionary of metadata terms to match
        Returns
        -------
        bool
            Return True unless an element in metadata_to_match conflicts with an entry in the metadata
        """

        test1 = self.collection.match_metadata(metadata_to_match)
        test2 = self.dataset.match_metadata(metadata_to_match)

        if test1 and test2:
            return True
        else:
            return False

    def write_metadata(self, filename: Path) -> None:
        """
        Write out the metadata in json format to a file specified by filename

        Parameters
        ----------
        filename: Path
            Path of filename to be created
        Returns
        -------
        None
        """

        rebuilt = self.collection.metadata
        rebuilt['datasets'] = [self.dataset.metadata]

        schema_path = Path(ROOT_DIR) / 'climind' / 'data_manager' / 'metadata_schema.json'
        with open(schema_path) as f:
            metadata_schema = json.load(f)
        resolver = RefResolver(schema_path.as_uri(), metadata_schema)
        validate(rebuilt, metadata_schema, resolver=resolver)

        with open(filename, 'w') as out_json:
            json.dump(rebuilt, out_json, indent=4)

    def creation_message(self) -> None:
        """
        Add a creation message to the dataset history and populate the wildcards in the metadata,
        such as AAAA (last modified/download time), YYYY (year), VVVV (version number).

        Returns
        -------
        None
        """
        self.dataset.creation_message()
        last_modified = self['last_modified'][0]
        self.dataset.fill_string('AAAA', last_modified)
        self.collection.fill_string('AAAA', last_modified)

        last_year = last_modified[0:4]
        self.dataset.fill_string('YYYY', last_year)
        self.collection.fill_string('YYYY', last_year)

        version = self['version']
        self.dataset.fill_string('VVVV', version)
        self.collection.fill_string('VVVV', version)
