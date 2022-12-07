"""
The fetchers package contains all the scripts needed to download the data sets. There are
specific fetchers for regular URLs, ftp sites and datasets which are not available online.

In addition, some websites and data sets have peculiarities that mean a standard
reader isn't adequate. For example, NOAAGlobalTemp has a fixed directory, but the filename
changes unpredictably as it contains the date of its creation. The fetcher for
NOAAGlobalTemp therefore has to parse the webpage to find the appropriate file and then
download that.

Other datasets require credentials, which are stored in a .env file which is in also in
the fetchers directory, but not part of the package.
"""