.. _regional_averages:

Calculating regional averages
==============================

Assuming you have installed the package and set up your DATADIR environment variable. To calculate the WMO
regional association averages, it is necessary to do the following things:

1. Get a CDS API key
2. Download the data
3. Get the shape files
4. Create additional shape files
5. Calculate the regional averages

1. Get a CDS API key
=====================

Follow the instructions provided by C3S to get a Climate Data Store API key. You will need this to download the
ERA5 data.

https://cds.climate.copernicus.eu/how-to-api

2. Download the data
=====================

There are six datasets needed to calculate all the regional series: "HadCRUT5", "NOAA v6", "GISTEMP",
"Berkeley Earth", "ERA5", "JRA-3Q".

To download the gridded data, use `get_grids.py` in `scripts/data_management` and modify the `archive.select`
method like so::

  ts_archive = archive.select({
    'type': 'gridded', 'name': ['HadCRUT5', 'NOAA v6', 'GISTEMP', 'Berkeley Earth', 'ERA5', 'JRA-3Q']
  })

and then run the script. It will take a while to download everything. Sometimes, it won't download a file
first go, or will only download some of the required files. The output of the script lists what has
failed to download. In particular, the JRA-3Q download is quite intermittent. Look in the corresponding data
directory (`DATADIR/ManagedData/Data/JRA-3Q` for JRA-3Q) and remove any files with zero size, then rerun
`get_grids.py` with only JRA-3Q selected::

  ts_archive = archive.select({
    'type': 'gridded', 'name': ['JRA-3Q']
  })

Repeat this process until you have all the files. This process can take a while.

In the case that a file doesn't download at all try the following:

1. Check in the relevant metadata file and copy-paste the URL for the required file into a web browser. If the file
   downloads this way, you can copy it into the relevant directory in DATADIR.
2. Sometimes, all that is needed is to wait a while and try again.
3. Check to see if there is a newer version of that particular dataset.
4. Check to see if the file name or file location have changed.

3. Get the shape files
=======================

Calculating the WMO Regional Associatin averages requires the WMO Regional Association shape files as
well as the Africa subregion shape files. These should all be copied into `DATADIR/ManagedData/Shape_Files`. I
don't know of an online source of these, but anyone doing this calculation will, with high probability, know
someone at WMO who can provide them.

The Natural Earth country files https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip should
be copied to `DATADIR/Natural_Earth` and unzipped.

4. Create additional shape files
=================================

In order to generate area averages from the gridded data for all the specified subregions, it is necessary to first
generate some of the subregions. These are built up as composites of individual countries based on the Natural
Earth definitions. The build these shape files navigate to the scripts directory and run::

  python make_new_regions.py

The script only needs to be run once to generate the shape files for subregion. If it is necessary to rerun it
because there is a change in definitions, there will likely be permission issues as it is not possible to overwrite
the existing shape files. If a rerun is required, first delete (or move) the shapefiles previously created by the code
before running it again.

5. Calculate the regional averages
===================================

The regional averages are calculated by modifying and then running::

  python calculate_wmo_ra_averages.py

There are two modes that the script can be run in "test" mode and "regular" mode. In most cases, `test` should be
set to False. In normal running, the parameters should look something like::

  start_year = 1900
        output_data_dir = "RegionalData"
        output_metadata_dir = "RegionalMetadata"
        datasets_to_use = [
            'HadCRUT5',
            'GISTEMP',
            'NOAA v6',
            'Berkeley Earth',
            'ERA5',
            'JRA-3Q'
        ]

  final_year = 2025


`final_year` should be set to the final year of data you want to calculate the timeseries for assuming you have the
data to do it. The code is set up to run all six datasets in one go (see `datasets_to_use`) but it can be better to
comment out all but one of them at a time, starting with one of the smaller datasets like "HadCRUT5" or "NOAA v6".
That way, if the code is going to fail, it will fail faster. Once everything is working, running all six at once and
then going for a cup of tea and a biscuit is my preferred configuration.

Checking it worked
===================

When the regional average code runs successfully for a dataset, it creates a new metadata file in
`DATADIR/ManagedData/RegionalMetadata` and a data file in a subdirectory of `DATADIR/ManagedData/RegionalData`.
The subdirectory is tagged with the (sub)region name and the dataset name. Output is in the BADC .csv format.

The metadata file contains the processing history and other dataset details. Some of those details are also in
the data file as metadata in the long header.

I usually plot the six data series for a region together and then compare them to what was previously in the reports.


What can go wrong and what to do about it
==========================================

In principle this section could be infinite in length and still not cover all eventualities.

The most common problems are

1. The data files move
2. The data format changes
3. A package update breaks the code

1 is more likely than 2 and both are far more likely than 3. However, all of these have been an issue at one point
or another. 1 and 2 occur in the general running of things, but 3 is more likely to occur if the code has recently
been updated.

If the data files have moved, then you will have to go and find them. The starting point for that process is to
look in the metadata file for the dataset that's causing problems. Most metadata files have a URL and that can be
copied and pasted into your web browser. Note that some URLs have placeholders in them. YYYY should be replaced with
the year and MMMM with the month for the file you are after. Sometime this involves a little guesswork because
the most recent file won't always be immediately obvious.

For metadata files without a URL, you can look at the dataset "fetcher". This is also listed in the metadata file under
`fetcher`. This specifies which fetcher function from the `fetchers` directory should be used to download the data.
If the "fetcher" is listed as "fetcher_no_url" then there is no way I know of to automatically download the data. In
that case, the URL might provide a clue. Some datasets are available online but require you to click on a particular
button in a way that can't be automated. In some cases you might just have to email the lead author for the dataset.

If the data format changes, then you will have to debug the code. Usually, changes relate to how the data are stored
in a netcdf file, so check that the dimension and variable names haven't changed and that the file still contains
the same number of dimensions. Fixing the bugs is up to you. Note that changing the code might affect its ability
to read data you had previously downloaded and processed so don't forget to test any changes on all the data.

If a package update breaks the code then you will have to debug that too. In the past xarray and pandas have changed
how they manage and collapse dimensions. They're more mature now, so it's less likely to be a problem but you never
know.


What does the code actually do?
================================

The calculation of a regional average is relatively simple:

1. Read in a dataset monthly gridded dataset.
2. Regrid the datasets to 1-degree lat-lon resolution either by averaging together all the gridboxes that fall
   into that 1-degree gridbox (if the gridboxes are smaller than 1-degree or don't neatly fit into a 1-degree grid),
   or copying the value from a larger grid box into all the 1-degree gridboxes that fall inside it (if the gridboxes
   are larger than 1-degree).
3. Mask out any 1-degree grid cells that fall outside the shapefile for the chosen region
4. Optionally mask out ocean areas in the same way.
5. Calculate the area average of the non-masked gridboxes.

The calculation is done at a monthly time scale and the monthly regional averages are then averaged to annual
giving each month an equal weight.