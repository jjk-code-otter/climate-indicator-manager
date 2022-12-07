"""
The scripts and files in the data manager module, are used to create and process
the metadata entities that underpin the dashboards.

There are basic metadata classes (:class:`.BaseMetadata`, :class:`.CollectionMetadata`
and :class:`.DatasetMetadata`)
which contain metadata and allow for simple tasks like checking whether the metadata
they contain matches what's in a dictionary.

Then there are classes (:class:`.DataSet`, :class:`.DataCollection`, :class:`.DataArchive`)
that use the metadata classes
to define data sets, collections of related data sets and data archives. These classes
allow you to select subsets of data, download data sets and read them in.

The metadata themselves are stored in json files in the climind.metadata_files directory.
"""