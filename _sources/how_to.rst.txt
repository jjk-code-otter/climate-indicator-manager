.. _howto:

Some simple examples
====================

Example 1 - getting some data
=============================

First we need to import some packages.

.. code-block::

  import climind.data_manager.processing as dm
  from climind.config.config import DATA_DIR
  from climind.definitions import METADATA_DIR

Once the packages are imported we can read in the data archive. The default metadata
are stored in the metadata_files directory in the project.

.. code-block::

  archive = dm.DataArchive.from_directory(METADATA_DIR)

To save time, we don't want to download all the data sets in the data archive, so first
we select just timeseries data for the variable tas (Global mean temperature) at monthly resolution.
To do that we use the select method of the data archive.

.. code-block::

  ts_archive = archive.select({'variable': 'tas', 'type': 'timeseries', 'time_resolution': 'monthly'})

Once we have selected this subset of the archive we can then download the data.

.. code-block::

  ts_archive.download(DATA_DIR / "ManagedData" / "Data")

This downloads the selected timeseries to appropriate subdirectories of the Data directory.


Example 2 - plotting a time series
==================================

The first thing to do is to import the appropriate packages from the project

.. code-block::

  from pathlib import Path
  import climind.data_manager.processing as dm
  import climind.plotters.plot_types as pt
  from climind.config.config import DATA_DIR
  from climind.definitions import METADATA_DIR

Once the packages are imported we can read in the data archive. The default metadata
are stored in the metadata_files directory in the project.

.. code-block::

  archive = dm.DataArchive.from_directory(METADATA_DIR)

This archive contains all the colections defined in the METADATA_DIR. We don't want to
read all of these datasets in so the next step is to select a subset. To do this we pass a
dictionary of the required metadata to the select method of the archive. The following snippet
extracts data sets with variable 'tas', type 'timeseries' and time_resolution 'monthly'.

.. code-block::

    ts_archive = archive.select({'variable': 'tas', 'type': 'timeseries', 'time_resolution': 'monthly'})

We will now read in the selected data sets

.. code-block::

    all_datasets = ts_archive.read_datasets(DATA_DIR / "ManagedData" / "Data")

This provides a list of datasets which we can use as the basis of further calculations. In this case,
we will just rebaseline the datasets to the 1981 to 2010 average

.. code-block::

    for ds in all_datasets:
        ds.rebaseline(1981, 2010)

We can now the plot the data

.. code-block::

    pt.neat_plot(Path(''), all_datasets, 'test_plot.png', 'Test plot')

This will produce a file called test_plot.png as well as the same image in .svg and .pdf formats.