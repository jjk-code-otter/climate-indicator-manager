import json
from pathlib import Path
from jsonschema import validate, RefResolver
from climind.definitions import ROOT_DIR


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

        for key in metadata_to_match:
            if key in self.metadata:

                mtm = metadata_to_match[key]
                att = self.metadata[key]

                if isinstance(mtm, list):
                    # go through list, if any item matches then that counts as a match
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

    def match_metadata(self, metadata_to_match):

        test1 = self.collection.match_metadata(metadata_to_match)
        test2 = self.dataset.match_metadata(metadata_to_match)

        if (test1 and test2):
            return True
        else:
            return False
