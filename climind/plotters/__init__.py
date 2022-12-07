"""
The plotters module contains the code for plotting datasets. The plotting code
itself is in plot_types which has functions for plotting
:class:`.TimeSeries` data of varying time resolutions
and also :class:`.GridAnnual` data. The plots all return a
string which is the caption of the plot. The plots follow a template, with the following
inputs:

* out_dir
* list of data sets
* image filename
* title for the plot

plot_utils contains a set of functions which support the plotting code including
calculation of trends, ranks, setting tick marks, building captions and so on.
"""