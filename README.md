Climate Indicator Manager
=========================

A lightweight package for managing, downloading and processing climate data for use in calculating and presenting
climate indicators.

It is built on a collection of metadata fies which describe the location and content of individual data collections and
data sets from those collections. For example, a *collection* might be something like "HadCRUT" and an individual
*dataset* would be the file containing the monthly global mean temperatures calculated by the providers of "HadCRUT".

The current functionality includes tools to download, read and undertake simple processing of monthly and annual
timeseries. Currently, simple processing includes:

1. changing the baseline of the data,
2. aggregating monthly data into annual data and
3. calculating running means of the data.

Various statistics can also be calculated from the timeseries, including rankings for particular years and years
associated with particular rankings.

Each step in processing is logged and added to the metadata for the dataset so that .

The package also manages the download of gridded data.

Installation
============

Download the code from the repository using your preferred method.

Navigate to the root directory of the repository and type

`pip install .`

This should install the package and necessary dependencies.

Running
=======

The managed data will be stored in a directory specified by the environment variable DATADIR. This is easy to set in
linux. In windows, do the following:

1. right-click on the Windows icon (bottom left of the screen usually) and select "System"
2. Click on "Advanced system settings"
3. Click on "Environment Variables..."
4. Under "User variables for Username" click "New..."
5. For "Variable name" type DATADIR
6. For "Variable value" type the pathname for the directory you want the data to go in.

In addition, if you want to download JRA-55 data from UCAR, CMEMS data or data from the NASA PODAAC, you will need a
valid username and password combo for each of these services. These values should be stored in a file called .env in
the `fetchers` directory of the repository. It should contain two lines for each of the data services:

```
UCAR_EMAIL=youremail@domain.com
UCAR_PSWD=yourpasswordhere
PODAAC_PSWD=anotherpasswordhere
PODAAC_USER=anotherusernamehere
CMEMS_USER=athirdusername
CMEMS_PSWD=yetanotherpassword
```

All three of these services are free to register, but you will have to set up the credentials online.

Downloading data
================

The first thing to do is to download the data. There are two main scripts for downloading data in the scripts
directory. `get_timeseries.py` will download the data which are in the form of time series. `get_grids.py` will download
the gridded data.

The volume of gridded data is considerably larger than the volume of time series data. For some datasets, the whole
gridded dataset is downloaded each time this is run, but for the reanalyses the full dataset is only downloaded once
with subsequent runs of the get_grids.py script only downloading months that have not already been downloaded. The
gridded data are used to calculate custom area averages (
such as the WMO Regional Association averages) and for plotting maps of the data. The key global indicators are all time
series.

Some datasets are not available online (the JRA-55 global mean temperature for example) so you will have to obtain 
these from somewhere else.

Processing the data
===================

In order to generate area averages from the gridded data for specified sub regions, you will need to run navigate to the
scripts directory and run:

`python calculate_wmo_ra_averages.py`

This reads in each of the data sets, regrids it to a standard resolution and then calculates the area averages for the
six WMO Regional Association areas and for the six African sub regions. It can take a while to run because it has to
load and process a lot of reanalysis data.

Building the website
====================

To build the websites, navigate to the scripts directory and run

`python build_dashboard.py`

This builds all the webpages, produces the figures for each web page and prepares the formatted data sets.

Diverse other scripts
=====================

As well as these main scripts, described above, there are others which perform the following tasks:

* `annual_global_temperature_stats.py` which generates some annual plots and statistics
* `arctic_sea_ice_plot.py` which generates some sea ice plots
* `change_per_month_plots.py` which generates some plots based on monthly global mean temperature as well as some stats.
* `five_year_global_temperature_stats.py` which generates some plots and stats based on 5-year running averages of
  global temperature
* `marine_heatwave_plot.py` which generates a plot of marine heatwave and cold spell occurrence.
* `plot_monthly_indicators.py` which generates a set of plots for a range of indicators (not all monthly).
* `plot_monthly_maps.py` which allows for the plotting of monthly temperature anomaly maps.
* `ten_year_global_temperature_stats.py` which generates some plots and stats based on 10-year running averages of
  global temperature