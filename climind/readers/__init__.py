"""
The readers package contains all the scripts needed to read the data sets. Because of the diversity of
data formats, there is roughly one reader per dataset.

Most readers will import the generic_reader script which handles the selection of the
appropriate reaader routines based on the metadata provided.

Individual reader scripts generally have one or more of the following functions:

* read_monthly_ts
* read_annual_ts
* read_monthly_grid
* read_monthly_5x5_grid
* read_monthly_1x1_grid

Each of these function must take a list of filenames and a
:class:`.CombinedMetadata` object as
inputs. These are used to read the data and create an appropriate dataset.
"""