Climate Indicator Manager
=========================

A lightweight package for managing, downloading and processing climate data for use in calculating and presenting 
climate indicators.

It is built on a collection of metadata fies which describe the location and content of individual data collections 
and data sets from those collections. For example, a *collection* might be something like "HadCRUT" and an individual 
*dataset* would be the file containing the monthly global mean temperatures calculated by the providers of "HadCRUT".

The current functionality includes tools to download, read and undertake simple processing of monthly and annual timeseries. 
Currently, simple processing includes: 

1. changing the baseline of the data, 
2. aggregating monthly data into annual data and 
3. calculating running means of the data. 

Various statistics can also be calculated from the timeseries, including rankings for particular years and years associated 
with particular rankings. 

Each step in processing is logged and added to the metadata for the dataset so that .

The package also manages the download of gridded data (for the time being).

Running
=======

The managed data will be stored in a directory specified by the environment variable 
DATADIR. This is easy to set in linux. In windows, do the following:

1. right click on the Windows icon (bottom left of the screen usually) and select "System"
2. Click on "Advanced system settings"
3. Click on "Environment Variables..."
4. Under "User variables for Username" click "New..."
5. For "Variable name" type DATADIR
6. For "Variable value" type the pathname for the directory you want the data to go in.

