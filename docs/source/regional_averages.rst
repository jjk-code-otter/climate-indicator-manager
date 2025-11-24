.. _regional_averages:

Calculating regional averages
==============================

To calculate the WMO regional association averages, it is necessary to do the following things:

1. Get a CDS API key
2. Download the data
3. Get the shape files
4. Create additional shape files
5. Calculate the regional averages

1. Get a CDS API key
=====================

Follow the instructions provided by C3S to get a Climate Data Store API key. You will need this to download the
ERA5 data.

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
first go, or will only download some of the required files. The output of the script will tell you what it has
failed to download. In particular, the JRA-3Q download is quite intermittent. Look in the corresponding data
directory (`DATADIR/ManagedData/Data/JRA-3Q` for JRA-3Q) and remove any files with zero size, then rerun
`get_grids.py` with only JRA-3Q selected::

  ts_archive = archive.select({
    'type': 'gridded', 'name': ['JRA-3Q']
    })

Repeat this process until you have all the files.

3. Get the shape files
=======================

ding