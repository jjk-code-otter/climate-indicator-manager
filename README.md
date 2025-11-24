Climate Indicator Manager
=========================

A lightweight package for managing, downloading and processing climate data for use in calculating and presenting
climate indicators, as well as creating dashboards based on these indicators.

It is built on a collection of metadata fies which describe the location and content of individual data collections and
data sets from those collections. For example, a *collection* might be something like "HadCRUT" and an individual
*dataset* would be the file containing the monthly global mean temperatures calculated by the providers of "HadCRUT".

The current functionality includes tools to download, read and undertake simple processing of monthly and annual
timeseries and grids. Currently, simple processing includes:

1. changing the baseline of the data,
2. aggregating monthly data into annual data and
3. calculating running means of the data.

Various statistics can also be calculated from the timeseries, including rankings for particular years and years
associated with particular rankings.

Each step in processing is logged and added to the metadata for the dataset so that processing steps can be traced 
and reproduced.


Installation
============

Download the code from the repository using your preferred method. I use

`git clone https://github.com/jjk-code-otter/climate-indicator-manager.git`

Next create a new conda environment using python 3.13 (I called mine `wmo_plus`) 
as the base then activate the environment

`conda create -n "wmo_plus" python=3.13.5`

`conda activate wmo_plus`

then install the package using

`pip install .`

This should install the necessary dependencies. It might take a while.

You will need to download a couple of different files if you want to calculate regional 
averages from gridded data. These include

- WMO Shape files for the WMO Regional Associations and Africa subregions. 
  I don't know of an online source for these so you will have to ask a friendly person 
  at the WMO.
- The Natural Earth country files https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip

Set up
======

The managed data will be stored in a directory specified by the environment variable DATADIR. This is easy to set in
linux. In windows, do the following:

1. right-click on the Windows icon (bottom left of the screen usually) and select "System"
2. Click on "Advanced system settings"
3. Click on "Environment Variables..."
4. Under "User variables for Username" click "New..."
5. For "Variable name" type DATADIR
6. For "Variable value" type the pathname for the directory you want the data to go in or navigate to the approriate directory using browse.
7. Make sure that the directory exists.

In the `DATADIR` create a directory called `Natural_Earth` and put the Natural Earth shape files in there. 
In `DATADIR` again, create a directory called `Shape_Files` and put the WMO RA shape files and 
subregion files in it.

In addition, if you want to download JRA-3Q data from UCAR, CMEMS data or data from the NASA PODAAC, you will need a
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

All three of these services are free to register, but you will have to set up the credentials online and then store 
those credentials at some location in your file system.

Similarly to access the data from the Copernicus Climate Change service, you will need an API key. 
The instructions provided by CDS are very helpful - https://cds.climate.copernicus.eu/how-to-api

Downloading data
================

The first thing to do is to download the data. There are two main scripts for downloading 
data and both of these are in the `scripts/data_management` directory. `get_timeseries.py` will download individual 
datasets which are in the form of time series. `get_grids.py` will download the gridded data.

To download a particular dataset, change the `name` of the dataset in the `archive.select` call. Multiple datasets 
can be downloaded at once using a list of names. The "correct" names of the datasets are given in the metadata files. 

A collection of regularly updated timeseries can be downloaded by running 
`get_regular_timeseries.py` and daily timeseries can be downloaded by running `get_daily_timeseries.py`. 
This is great when it works, but typically at least one dataset
will fail to download in a way that stops the code from running. I temporarily comment out 
problematic datasets and rerun the script.

The volume of gridded data is considerably larger than the volume of time series data. For 
some datasets, the whole gridded dataset is downloaded each time this is run, but for some of the 
reanalyses the full dataset is only downloaded once with subsequent runs of the `get_grids.py` 
script only downloading months that have not already been downloaded. The gridded data are 
used to calculate custom area averages (such as the WMO Regional Association averages) and 
for plotting maps of the data. The key global indicators are all time series.

Some datasets are not available online (the JRA-55 and JRA-3Q global mean temperature for example) so 
you will have to obtain these from somewhere else or remove them from the processing. Any 
extra dataset files such as these should be copied into the `$DATADIR/ManagedData/Data/` directory 
in an appropriately named subdirectory that corresponds to the unique name given to the 
data set. This can be found in the metadata file for the data set (see below).

Calculating the WMO composite global mean temperature
=====================================================

To calculate this, you will first need to download the six datasets used in the composite global mean: 
"HadCRUT5", "NOAA v6", "GISTEMP", "Berkeley Earth Hires", "ERA5" and "JRA-3Q". These can be downloaded using 
`get_timeseries.py`.

Navigate to the `scripts/global_temperature` directory and run

`annual_global_temperature_stats.py`

This generates output in the `DATADIR` in the `ManagedData` subdirectory. 
Principle outputs appear in `Figures` - which holds all the graphs - and
`reports` which contains the numerical outputs in a digest form.

Pre-processing the data
=======================

For the dashboards, the gridded data need to be pre-processed by running the following from 
the `scripts` directory:

`python regrid_grids.py`

which calculates annual average grids on a consistent 5-degree latitude longitude grid for 
all the gridded data sets. This allows them to be combined into a single estimate for mapping.

In order to generate area averages from the gridded data for specified subregions, you will 
need to navigate to the scripts directory and run:

`python make_new_regions.py` 

You only need to run this the first time to generate the shape files for subregion. If you 
happen to rerun it, you will likely encounter permission issues - you can't write over the 
existing shape files. If you do need to rerun - say because the definitions have changed - then 
you will have to delete (or move) the shapefiles created by the code before running it again. 

Regional area averages are then calculated using:

`python calculate_wmo_ra_averages.py`

You will need to manually specify the end year and which datasets to use in the calculation. The 
regional reports use the main six datasets "HadCRUT5", "NOAA v6", "GISTEMP", "Berkeley Earth", "ERA5", and "JRA-3Q". 
The script reads in each of the gridded data sets, regrids it to a standard (1x1) resolution and then 
calculates the area averages for the six WMO Regional Association areas, the six African 
subregions and other subregions defined by the WMO Regional State of the Climate authors. It can 
take a while to run because it has to load and process a lot of data. The first time 
it runs, it will likely download a shape file of coastlines from natural earth used to identify 
land and ocean areas.


Building the website
====================

To build the websites, download all the necessary data then navigate to the scripts directory and run:

`python build_dashboard.py`

This builds all the webpages, produces the figures for each web page and prepares 
the formatted data sets. These are written to the `DATADIR/ManagedData` directory with 
one directory created for each dashboard. Currently the code is set up to generate four 
dashboards: key indicators to 2021, key indicators to 2022, ocean indicators, and regional 
indicators to 2022.

To display a dashboard on the web, the files in the appropriate directory will need to be 
copied to an appropriate web server.

The dashboard code is written in such a way that it will generate any information that doesn't cause 
an error. The basic dashboards are based on "cards" which are processed one at a time and then used 
to populate the webpages. If a card fails to process a warning will be printed to the screen but it will 
keep running and that card simply won't appear on the dashboard.


Navigating the website
======================

Each dashboard consists of a set of "cards" at the top of the page. These each contain:

- an image, 
- a set of links to images in different formats (png, svg, and pdf)
- a link to a zip file of all the datasets in csv format. 
- a link to "References and processing" which takes you to details of:
  - the datasets used and their references
  - the data file and a checksum for assessing data integrity of the download
  - the processing applied to each dataset 

In some cases there will also be:

- a caption and a button saying "Copy caption" which will save the caption to your clipboard.
- a button inviting you to "Click for more indicators". Clicking such a button will take you to a page with related indicators.


Diverse other scripts
=====================

As well as these main scripts, described above, there are others which perform the following tasks:

* `arctic_sea_ice_plot.py` which generates some sea ice plots used in the State of the Climate report
* `change_per_month_plots.py` which generates some plots based on monthly global mean temperature as well as some stats.
* `five_year_global_temperature_stats.py` which generates some plots and stats based on 5-year running averages of
  global temperature
* `marine_heatwave_plot.py` which generates a plot of marine heatwave and cold spell occurrence.
* `plot_monthly_indicators.py` which generates a set of plots for a range of indicators (not all monthly).
* `plot_monthly_maps.py` which allows for the plotting of monthly temperature anomaly maps.
* `ten_year_global_temperature_stats.py` which generates some plots and stats based on 10-year running averages of
  global temperature for use in the decadal state of the climate report.
  
Adding data sets for an existing variable
=========================================

To add a dataset for an existing variable, you need to 
* create a new collection file in the `metadata` folder
* write a reader function in the `readers` directory. This should correspond to the "reader" entry in the collection metadata.
* write a fetcher function in the `fetchers` directory. This should correspond to the "reader" entry in the collection metadata. This is only necessary if the file(s) can't be downloaded as a simple http(s) or ftp(s) request. For example, some datasets do not have a static URL, or there are a large number of files, or there is an API for accessing the data.

The form of these files should be clear from the other files and function in the respective 
directories, or by perusal of the schemas in the `data_manager` directory. An example metadata file looks like this:

```
{
  "name": "HadCRUT5",
  "display_name": "HadCRUT5",
  "version": "5.0.1.0",
  "variable": "tas",
  "units": "degC",
  "citation": ["Morice, C.P., J.J. Kennedy, N.A. Rayner, J.P. Winn, E. Hogan, R.E. Killick, R.J.H. Dunn, T.J. Osborn, P.D. Jones and I.R. Simpson (in press) An updated assessment of near-surface temperature change from 1850: the HadCRUT5 dataset. Journal of Geophysical Research (Atmospheres) doi:10.1029/2019JD032361"],
  "data_citation": [""],
  "acknowledgement": "HadCRUT.VVVV data were obtained from http://www.metoffice.gov.uk/hadobs/hadcrut5 on AAAA and are © British Crown Copyright, Met Office YYYY, provided under an Open Government License, http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
  "colour": "dimgrey",
  "zpos": 99,
  "datasets": [
    {
      "url": ["https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/analysis/HadCRUT.5.0.1.0.analysis.anomalies.ensemble_mean.nc"],
	  "filename": ["HadCRUT.5.0.1.0.analysis.anomalies.ensemble_mean.nc"],
      "type": "gridded",
      "long_name": "Near surface temperature",
	  "time_resolution": "monthly",
	  "space_resolution": 5.0,
	  "climatology_start": 1961,
	  "climatology_end": 1990,
	  "actual": false,
	  "derived": false,
	  "history": [],
      "reader": "reader_hadcrut_ts",
	  "fetcher": "fetcher_standard_url"
    }
  ]
}
```

The metadata describes a collection of data, in this case "HadCRUT5". HadCRUT5 consists of a number of data sets (only one is listed here) which are listed 
under the "datasets" entry. It's important to populate as much of the metadata file as possible, as this links the outputs of the dashboard back to the initial 
inputs and maintains transparency of the system. The "reader" and "fetcher" specify functions for reading the data and downloading the data which are found in the 'readers' and 'fetchers' directories.

More complicated examples can be found in the repository.

* `name` - this is a **unique** name for this particular collection
* `display_name` - name used to label datasets in this collection in figure legends, captions and text.
* `version` - latest version number for the data set
* `variable` - variable name. `tas` is global surface temperature.
* `units` - units used for this variable. 
* `citation` - a list of citations for papers describing the data set.
* `data_citation` - a list of data citations for the data itself (if such exists).
* `acknowledgement` - many dataset providers request a particular acknowledgement when the data are used.
* `colour` - python colour name or hexadecimal RGB triple, used to represent data from this collection in line graphs
* `zpos` - used to force ordering of lines in plots. Lines with higher zpos values will be drawn over lines with lower zpos values.

The dataset section consists of a lits of dataset metadata:

* `url` - a list of URLs for the files.
* `filename` - a list of the filenames which will be associated with the data set. For example, NSIDC Arctic ice extent has 12 files, one for each month of the year.
* `type` - type of the data, either `timeseries` or `gridded`.
* `long_name` - long descriptive name used in figure captions and other automatically generated text.
* `time_resolution` - either `monthly` or `annual`
* `space_resolution` - for `gridded` data sets this specifies the grid resolution in degrees. Set to 999 for time series data.
* `climatology_start` - first year of the climatology period of the data in the data set.
* `climatology_end` - last year of the climatology period of the data in the data set.
* `actual` - set to True if the file contains actual values, set to False for anomalies.
* `derived` - set to False. During processing, this flag is set to True to indicate that the original data have been further processed within the dashboard software.
* `history` - a list which will hold the details of processing steps
* `reader` - the name of a script in the `climind/readers` directory which will read the data described in the dataset metadata.
* `fetcher` - the name of a script in the `climind/fetchers` direcotry which will download the data described in the dataset metadata.


Adding a new variable
=====================

It is possible to add new variables. For example, there is currently no snow_cover variable.

1. Think of a variable name e.g. `snow_cover`
2. Check that the variable does not already exist. You can do this by looking through the metadata files.
3. Add a new metadata file describing a collection with snow cover data in it.
4. Check that the units are in the `metadata_schema.json` file in `climind.data_manager`. This is used to validate the metadata when it is read in.
5. Add the new variable to the word document in `climind/web/word_documents/key_indicators_texts.docx`. Individual variables 
   appear towards the end of the document. The short `variable` name should appear in `Heading1` style and the text desribing it 
   should appear in `normal` style text. These short descriptions appear on the webpages in the section detailing the datasets and their processing.

That should be sufficient.

Making a new dashboard
======================

A dashboard is created using a dashboard metadata file. These are located in `climind/web/dashboard_metadata`. Each dashboard is split into Pages, which 
each correspond to an html webpage. Each Page consists of a set of Cards and Paragraphs (the capital letters indicate these are represented as classes 
in the underlying code). For examples, please see the `climind/web/dashboard_metadata` directory.

A dashboard metadata file:

```
{
  "name": "Key Indicators",
  "pages": [ ... ]
}
```

The `pages` entry consists of a list of Pages which look something like:

```
{
  "id": "dashboard",
  "name": "Key Climate Indicators",
  "template": "front_page",
  "cards": [ ... ],
  "paragraphs": [ ... ]
},
```

The `template` can be either a `front_page` or a `topic_page`. The front page is intended to be a clean landing page 
for users. More information is provided on topic pages, including e.g. figure captions.

The `cards` entry is made up of one or more cards and the `paragraphs` entry of one or more paragraphs.

A Card, contains an image, links to the image in other format, links to the data in a standard format and a link to another Page. 
The metadata entries look like this:

```
{
  "link_to": "global_mean_temperature", "title": "Global temperature",
  "selecting": {"type": "timeseries", "variable": "tas", "time_resolution": "monthly"},
  "processing":  [{"method": "rebaseline", "args": [1981, 2010]},
                  {"method": "make_annual", "args": []},
                  {"method": "select_year_range", "args":  [1850,2021]},
                  {"method": "add_offset", "args": [0.69]},
                  {"method": "manually_set_baseline", "args": [1850, 1900]}],
  "plotting": {"function": "neat_plot", "title": "Global mean temperature"}
 }
```

The entries say which other page the Card can `link_to` using the `id` of a page and what the `title` of the page should be. 
`selecting` specifies which subset of data you want to plot, with entries here corresponding to entries in the collection metadata. 
`processing` details the processing steps to be applied to each of the selected data sets, with `method` corresponding to a method in the 
relevant data type (at the moment `TimeSeriesMonthly` or `TimeSeriesAnnual`) and `args` being the arguments to pass to the method. 
`plotting` specifies the function to the be used to plot the data (`neat_plot` being the standard type for annual plots) and can also 
be used to pass additional arguments to the plot function. Plotting functions are found in `climind/plotters/plot_types.py`

A Paragraph is similar to a Card, except the output is a paragraph of text. An entry looks something like:

```
{
  "selecting": {"type": "timeseries", "variable": "tas", "time_resolution": "monthly"},
  "processing": [{"method": "rebaseline", "args": [1981, 2010]},
                  {"method": "make_annual", "args": []},
                  {"method": "select_year_range", "args":  [1850,2021]},
                  {"method": "add_offset", "args": [0.69]},
                  {"method": "manually_set_baseline", "args": [1850, 1900]}],
  "writing": {"function": "anomaly_and_rank"}
}
```

`selecting` and `processing` behave as they did for Cards, `writing` is similar to `plotting` and produces the main output. Paragraph writers 
are found in `climind/stats/paragraphs.py`.

Once the dashboard metadata is complete, add an entry to `climind/scripts/build_dashboard.py` along the lines of:

```
json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'new_dashboard.json'
dash = Dashboard.from_json(json_file, METADATA_DIR)

dash_dir = DATA_DIR / 'ManagedData' / 'NewDashboard'
dash_dir.mkdir(exist_ok=True)
dash.build(Path(dash_dir))
```

The `json_file` is the dashboard metadata file. The `dash_dir` is the directory where you want to build the dashboard. `dash.build()` builds the dashboard.

Calculating regional averages
=============================

Regional averages are calculated using `calculate_wmo_ra_averages.py`. This generates a large number of files containing regional averages based 
on the gridded temperature data sets. This takes some time to run.

`python calculate_wmo_ra_averages.py`

Descriptive text
================

In `climind/web/word_documents` there is a Word document that is used to generate text for the 
web pages. The document is called `key_indicators_texts.docx`. This has descriptive text for 
each page on the key indicators dashboard as well as descriptions for each of the variables. 

when changes are made to the word document, these will need to be converted to html by navigating to `climind/web` and running

`python extract_from_word.py`

The word document is structured using the inbuilt "styles".

Each page in the dashboard can have an Introduction text. To do this, add a new `Heading1` style heading in the document 
with text that matches the id of a page in the dashboard. You can then write `normal` style text beneath it. 
Subheadings can be added using `Heading2` style text followed by `normal` text. For example, the "What the IPCC says" 
sections. Hyperlinks can be added and these will be rendered in the webpages.

Individual variable descriptions can also be added here. The method is similar. A Heading1 style heading which matches 
the `variable` name from the metadata file, followed by `normal` style text. Sub-headings do not work for variables. These 
are intended to be short descriptions of the variables.
